# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 1 -- Download World Bank WDI indicators -> data/raw/wb_*.csv, data/processed/wb_panel.csv
#
# Copied verbatim from the author's working tree (analysis/01_download_worldbank.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/01_download_worldbank.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""
01_download_worldbank.py
Descarga un panel pais-anio desde la API del Banco Mundial (muchos indicadores
agricolas proceden de FAO). Robusto: reintentos, paginacion, guarda CSV crudos
y un panel ancho consolidado.
"""
import os, time, json, sys
import requests
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
PROC = os.path.join(HERE, "..", "data", "processed")
os.makedirs(RAW, exist_ok=True)
os.makedirs(PROC, exist_ok=True)

# Indicadores: codigo -> nombre corto
INDICATORS = {
    "AG.YLD.CREL.KG":    "cereal_yield_kg_ha",        # Cereal yield (kg/ha) - fuente FAO
    "AG.PRD.CREL.MT":    "cereal_prod_mt",            # Cereal production (metric tons)
    "AG.LND.CREL.HA":    "cereal_area_ha",            # Land under cereal production (ha)
    "AG.CON.FERT.ZS":    "fert_kg_ha_arable",         # Fertilizer consumption (kg/ha arable) desde ~2002
    "AG.LND.ARBL.HA":    "arable_land_ha",            # Arable land (ha)
    "AG.LND.AGRI.ZS":    "agri_land_pct",             # Agricultural land (% of land area)
    "AG.LND.IRIG.AG.ZS": "irrigated_pct_agri",        # Agricultural irrigated land (% of total agri land)
    "AG.LND.TRAC.ZS":    "tractors_per_100km2",       # Agricultural machinery, tractors per 100 sq km arable
    "SL.AGR.EMPL.ZS":    "agri_empl_pct",             # Employment in agriculture (% of total employment)
    "NV.AGR.TOTL.ZS":    "agri_va_pct_gdp",           # Agriculture value added (% GDP)
    "NV.AGR.EMPL.KD":    "agri_va_per_worker",        # Ag value added per worker (const 2015 US$)
    "SP.RUR.TOTL.ZS":    "rural_pop_pct",             # Rural population (%)
    "SP.POP.TOTL":       "population",                # Population total
    "EN.CLC.PRCP.MM":    "precip_mm",                 # Average precipitation (mm/yr) -- puede no existir
    "AG.LND.FRST.ZS":    "forest_pct",                # Forest area (%) (control)
}

BASE = "https://api.worldbank.org/v2/country/all/indicator/{code}"

def fetch_indicator(code):
    params = {"format": "json", "per_page": 20000, "date": "1960:2024"}
    url = BASE.format(code=code)
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, list) or len(data) < 2 or data[1] is None:
                print(f"  [{code}] sin datos / formato inesperado: {str(data)[:200]}")
                return None
            recs = data[1]
            rows = []
            for d in recs:
                rows.append({
                    "iso3": d["countryiso3code"],
                    "country": d["country"]["value"],
                    "year": int(d["date"]),
                    "value": d["value"],
                })
            df = pd.DataFrame(rows)
            return df
        except Exception as e:
            print(f"  [{code}] intento {attempt+1} fallo: {e}")
            time.sleep(3 * (attempt + 1))
    return None

def main():
    frames = {}
    for code, name in INDICATORS.items():
        print(f"Descargando {code} ({name}) ...")
        df = fetch_indicator(code)
        if df is None or df.empty:
            print(f"  -> VACIO {code}")
            continue
        df.to_csv(os.path.join(RAW, f"wb_{name}.csv"), index=False, encoding="utf-8")
        df = df.rename(columns={"value": name})[["iso3", "country", "year", name]]
        frames[name] = df
        print(f"  -> {len(df)} filas, anios {df['year'].min()}-{df['year'].max()}")
        time.sleep(0.5)

    # merge en panel ancho
    panel = None
    for name, df in frames.items():
        if panel is None:
            panel = df
        else:
            panel = panel.merge(df, on=["iso3", "country", "year"], how="outer")
    panel = panel.sort_values(["iso3", "year"]).reset_index(drop=True)
    out = os.path.join(PROC, "wb_panel.csv")
    panel.to_csv(out, index=False, encoding="utf-8")
    print(f"\nPanel guardado: {out}  shape={panel.shape}")
    print("Columnas:", list(panel.columns))

if __name__ == "__main__":
    main()
