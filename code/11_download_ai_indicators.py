# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 11 -- OpenAlex queries + digital-complement WDI indicators -> data/processed/ai_panel.csv
#
# Copied verbatim from the author's working tree (analysis/11_download_ai_indicators.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/11_download_ai_indicators.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""
11_download_ai_indicators.py

Construye un panel pais-anio de VARIABLES DE IA OBSERVABLES, que es lo que
faltaba en la primera version del articulo (critica del revisor: "sin una
variable de IA observable, el estudio no puede aislar el efecto especifico
de la inteligencia artificial").

Tres bloques:
  A) OpenAlex  -> intensidad de I+D en IA aplicada a agricultura, IA general
                  y produccion cientifica total (denominador), por pais y anio.
  B) World Bank -> complementos digitales y de capital humano (internet, banda
                  ancha, movil, I+D/PIB, investigadores, terciaria, electricidad
                  rural, PIB pc).
  C) Union en data/processed/ai_panel.csv

Salidas:
  data/raw/openalex_ai_ag.csv, openalex_ai_all.csv, openalex_works_all.csv,
  data/raw/openalex_precision_ag.csv
  data/raw/wb_<name>.csv (nuevos indicadores)
  data/processed/ai_panel.csv
"""
import os, time, json, sys
import requests
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
PROC = os.path.join(HERE, "..", "data", "processed")
os.makedirs(RAW, exist_ok=True)
os.makedirs(PROC, exist_ok=True)

MAILTO = "manolochaves@gmail.com"
YEARS = list(range(2000, 2025))

# ---------------------------------------------------------------- A) OpenAlex
OA_BASE = "https://api.openalex.org/works"

AI_TERMS = ('"artificial intelligence" OR "machine learning" OR "deep learning" '
            'OR "neural network"')
AG_TERMS = ('agriculture OR agricultural OR crop OR farming OR farm OR agronomy '
            'OR agronomic')
PA_TERMS = ('"precision agriculture" OR "smart farming" OR "digital agriculture" '
            'OR "precision farming" OR "site-specific management"')

QUERIES = {
    "ai_ag":        f"({AI_TERMS}) AND ({AG_TERMS})",
    "ai_all":       f"({AI_TERMS})",
    "precision_ag": f"({PA_TERMS})",
    "works_all":    None,          # sin filtro tematico: denominador
}


def oa_group_by_country(year, query):
    """Devuelve DataFrame iso2/count para un anio y una consulta."""
    filt = [f"publication_year:{year}"]
    if query:
        filt.append("title_and_abstract.search:" + query)
    params = {
        "filter": ",".join(filt),
        "group_by": "authorships.countries",
        "per_page": 200,
        "mailto": MAILTO,
    }
    for attempt in range(5):
        try:
            r = requests.get(OA_BASE, params=params, timeout=90)
            r.raise_for_status()
            j = r.json()
            rows = []
            for g in j.get("group_by", []):
                iso2 = g["key"].rstrip("/").split("/")[-1]
                if len(iso2) != 2:
                    continue
                rows.append({"iso2": iso2, "year": year, "count": g["count"]})
            return pd.DataFrame(rows), j["meta"]["count"]
        except Exception as e:
            print(f"    intento {attempt+1} fallo ({year}): {e}")
            time.sleep(4 * (attempt + 1))
    return pd.DataFrame(columns=["iso2", "year", "count"]), 0


def download_openalex():
    world = {}
    for name, query in QUERIES.items():
        print(f"\nOpenAlex :: {name}")
        frames, wtot = [], []
        for y in YEARS:
            df, total = oa_group_by_country(y, query)
            frames.append(df)
            wtot.append({"year": y, "world_count": total})
            print(f"  {y}: {total:>9,} obras mundo | {len(df)} paises")
            time.sleep(0.35)
        out = pd.concat(frames, ignore_index=True)
        out.to_csv(os.path.join(RAW, f"openalex_{name}.csv"), index=False,
                   encoding="utf-8")
        world[name] = pd.DataFrame(wtot)
        world[name].to_csv(os.path.join(RAW, f"openalex_{name}_world.csv"),
                           index=False, encoding="utf-8")
    return world


# ------------------------------------------------------------- B) World Bank
WB_INDICATORS = {
    "IT.NET.USER.ZS":     "internet_users_pct",
    "IT.CEL.SETS.P2":     "mobile_subs_per100",
    "IT.NET.BBND.P2":     "broadband_per100",
    "GB.XPD.RSDV.GD.ZS":  "rd_pct_gdp",
    "SP.POP.SCIE.RD.P6":  "researchers_per_mn",
    "SE.TER.ENRR":        "tertiary_enrol_pct",
    "EG.ELC.ACCS.RU.ZS":  "electricity_rural_pct",
    "NY.GDP.PCAP.KD":     "gdp_pc_const2015",
    "SE.SEC.CUAT.UP.ZS":  "upper_secondary_pct",
}
WB_BASE = "https://api.worldbank.org/v2/country/all/indicator/{code}"


def wb_fetch(code):
    params = {"format": "json", "per_page": 20000, "date": "1990:2024"}
    for attempt in range(4):
        try:
            r = requests.get(WB_BASE.format(code=code), params=params, timeout=90)
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, list) or len(data) < 2 or data[1] is None:
                return None
            rows = [{"iso3": d["countryiso3code"], "country": d["country"]["value"],
                     "year": int(d["date"]), "value": d["value"]} for d in data[1]]
            return pd.DataFrame(rows)
        except Exception as e:
            print(f"  [{code}] intento {attempt+1} fallo: {e}")
            time.sleep(3 * (attempt + 1))
    return None


def _clean_wb(df, name):
    """iso3 valido (3 letras, sin agregados vacios) y sin duplicados pais-anio.

    La API del Banco Mundial devuelve algunas filas con countryiso3code vacio
    (agregados regionales); si no se filtran, el merge multiple genera un
    producto cartesiano de miles de millones de filas.
    """
    df = df.rename(columns={"value": name})[["iso3", "year", name]].copy()
    df["iso3"] = df["iso3"].astype(str).str.strip()
    df = df[df["iso3"].str.fullmatch(r"[A-Z]{3}")]
    df = df.drop_duplicates(subset=["iso3", "year"], keep="first")
    return df


def download_worldbank(use_cache=True):
    frames = {}
    for code, name in WB_INDICATORS.items():
        path = os.path.join(RAW, f"wb_{name}.csv")
        if use_cache and os.path.exists(path):
            print(f"World Bank :: {name} (cache)")
            df = pd.read_csv(path)
        else:
            print(f"World Bank :: {code} ({name})")
            df = wb_fetch(code)
            if df is None or df.empty:
                print("   -> VACIO")
                continue
            df.to_csv(path, index=False, encoding="utf-8")
            time.sleep(0.4)
        frames[name] = _clean_wb(df, name)
        print(f"   -> {len(frames[name])} filas limpias")
    panel = None
    for name, df in frames.items():
        panel = df if panel is None else panel.merge(df, on=["iso3", "year"], how="outer")
    return panel


# ------------------------------------------------------------------ C) Union
def build_panel(wb_panel):
    import pycountry

    def iso2_to_iso3(c):
        try:
            return pycountry.countries.get(alpha_2=c).alpha_3
        except Exception:
            return None

    oa = None
    for name in QUERIES:
        df = pd.read_csv(os.path.join(RAW, f"openalex_{name}.csv"))
        df = df.rename(columns={"count": f"oa_{name}"})
        oa = df if oa is None else oa.merge(df, on=["iso2", "year"], how="outer")
    oa["iso3"] = oa["iso2"].map(iso2_to_iso3)
    oa = oa.dropna(subset=["iso3"]).drop(columns=["iso2"])
    for c in [c for c in oa.columns if c.startswith("oa_")]:
        oa[c] = oa[c].fillna(0)
    oa = oa.groupby(["iso3", "year"], as_index=False).sum(numeric_only=True)

    panel = wb_panel.merge(oa, on=["iso3", "year"], how="outer")
    panel = panel.sort_values(["iso3", "year"]).reset_index(drop=True)
    out = os.path.join(PROC, "ai_panel.csv")
    panel.to_csv(out, index=False, encoding="utf-8")
    print(f"\nPanel IA guardado: {out}  shape={panel.shape}")
    print("Columnas:", list(panel.columns))
    return panel


if __name__ == "__main__":
    # --build-only reutiliza los CSV crudos ya descargados
    if "--build-only" not in sys.argv:
        download_openalex()
    wb = download_worldbank(use_cache=True)
    build_panel(wb)
