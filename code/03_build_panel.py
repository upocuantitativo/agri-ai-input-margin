# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 3 -- Merge World Bank spine + FAOSTAT -> data/processed/country_panel.csv, world_*.csv, spain_series.csv
#
# Copied verbatim from the author's working tree (analysis/03_build_panel.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/03_build_panel.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""
03_build_panel.py
Construye los paneles analiticos:
  - country_panel.csv : panel pais-anio (World Bank spine + FAOSTAT N, tierra,
                        regadio, tractores, temperatura). Solo paises reales.
  - world_series.csv  : series globales (produccion por gran grupo de cultivo,
                        rendimiento cereal mundial, N mundial) para los claims macro.
  - spain_series.csv  : serie detallada de Espana (mecanizacion, regadio...).
"""
import os, re
import numpy as np
import pandas as pd
import pycountry

RAW = "data/raw"
PROC = "data/processed"
os.makedirs(PROC, exist_ok=True)

# ---------- helpers FAOSTAT ----------
M49_OVERRIDE_AREACODE = {41: "CHN"}      # China, mainland -> CHN
EXCLUDE_AREACODE = {351, 41 + 0}         # 351 = China aggregate (incl. Taiwan/HK/Macao)
# (mantendremos 41 via override; excluimos 351)
EXCLUDE_AREACODE = {351}

def m49_to_iso3(m49_raw):
    if pd.isna(m49_raw):
        return None
    s = re.sub(r"\D", "", str(m49_raw))
    if not s:
        return None
    try:
        c = pycountry.countries.get(numeric=s.zfill(3))
        return c.alpha_3 if c else None
    except Exception:
        return None

def fao_country_series(df, item=None, element=None, months=None, unit_filter=None,
                       value_name="value"):
    """Filtra FAOSTAT a paises reales y devuelve [iso3, year, value_name]."""
    d = df.copy()
    if item is not None:
        d = d[d["Item"] == item]
    if element is not None:
        d = d[d["Element"] == element]
    if months is not None and "Months" in d.columns:
        d = d[d["Months"] == months]
    if unit_filter is not None:
        d = d[d["Unit"] == unit_filter]
    d = d[d["Area Code"] < 5000]                       # quita agregados
    d = d[~d["Area Code"].isin(EXCLUDE_AREACODE)]
    # iso3
    iso = d["Area Code (M49)"].apply(m49_to_iso3)
    over = d["Area Code"].map(M49_OVERRIDE_AREACODE)
    d["iso3"] = over.where(over.notna(), iso)
    d = d[d["iso3"].notna()]
    d["year"] = pd.to_numeric(d["Year"], errors="coerce")
    d["value"] = pd.to_numeric(d["Value"], errors="coerce")
    out = (d.groupby(["iso3", "year"], as_index=False)["value"].mean()
             .rename(columns={"value": value_name}))
    return out

def fao_world_series(df, item=None, element=None, months=None, value_name="value"):
    d = df.copy()
    if item is not None:
        d = d[d["Item"] == item]
    if element is not None:
        d = d[d["Element"] == element]
    if months is not None and "Months" in d.columns:
        d = d[d["Months"] == months]
    d = d[d["Area Code"] == 5000]
    d["year"] = pd.to_numeric(d["Year"], errors="coerce")
    d["value"] = pd.to_numeric(d["Value"], errors="coerce")
    out = (d.groupby("year", as_index=False)["value"].mean()
             .rename(columns={"value": value_name}))
    return out

# ---------- 1) World Bank spine ----------
wb = pd.read_csv(os.path.join(PROC, "wb_panel.csv"), encoding="utf-8")
def is_country(iso3):
    try:
        return pycountry.countries.get(alpha_3=str(iso3)) is not None
    except Exception:
        return False
wb["is_country"] = wb["iso3"].apply(is_country)
wb_countries = wb[wb["is_country"]].drop(columns=["is_country"]).copy()
print("WB countries panel:", wb_countries.shape, "| n paises:", wb_countries["iso3"].nunique())

# ---------- 2) FAOSTAT series ----------
print("Cargando FAOSTAT RFN/RL/RM/ET ...")
rfn = pd.read_csv(os.path.join(RAW, "faostat_RFN.csv"), encoding="latin-1", low_memory=False)
rl  = pd.read_csv(os.path.join(RAW, "faostat_RL.csv"),  encoding="latin-1", low_memory=False)
rm  = pd.read_csv(os.path.join(RAW, "faostat_RM.csv"),  encoding="latin-1", low_memory=False)
et  = pd.read_csv(os.path.join(RAW, "faostat_ET.csv"),  encoding="latin-1", low_memory=False)

fao_parts = []
fao_parts.append(fao_country_series(rfn, "Nutrient nitrogen N (total)", "Agricultural Use", value_name="n_total_t"))
fao_parts.append(fao_country_series(rfn, "Nutrient nitrogen N (total)", "Use per area of cropland", value_name="n_kg_ha"))
fao_parts.append(fao_country_series(rfn, "Nutrient phosphate P2O5 (total)", "Use per area of cropland", value_name="p_kg_ha"))
fao_parts.append(fao_country_series(rfn, "Nutrient potash K2O (total)", "Use per area of cropland", value_name="k_kg_ha"))
fao_parts.append(fao_country_series(rl, "Arable land", "Area", value_name="arable_kha"))
fao_parts.append(fao_country_series(rl, "Cropland", "Area", value_name="cropland_kha"))
fao_parts.append(fao_country_series(rl, "Agricultural land", "Area", value_name="agri_land_kha"))
fao_parts.append(fao_country_series(rl, "Land area equipped for irrigation", "Area", value_name="irrig_equip_kha"))
fao_parts.append(fao_country_series(rl, "Agriculture area actually irrigated", "Area", value_name="irrig_actual_kha"))
fao_parts.append(fao_country_series(rm, "Agricultural tractors", "In Use", value_name="tractors"))
fao_parts.append(fao_country_series(et, element="Temperature change", months="Meteorological year", value_name="temp_anom"))

fao = fao_parts[0]
for p in fao_parts[1:]:
    fao = fao.merge(p, on=["iso3", "year"], how="outer")
fao["year"] = fao["year"].astype("Int64")
print("FAOSTAT country series:", fao.shape, "| n paises:", fao["iso3"].nunique())

# ---------- 3) merge country panel ----------
panel = wb_countries.merge(fao, on=["iso3", "year"], how="left")
# derivadas
panel["tractors_per_1000ha_arable"] = panel["tractors"] / (panel["arable_kha"])  # tractores por 1000 ha
panel["irrig_share_cropland"] = 100 * panel["irrig_equip_kha"] / panel["cropland_kha"]
panel = panel.sort_values(["iso3", "year"]).reset_index(drop=True)
panel.to_csv(os.path.join(PROC, "country_panel.csv"), index=False, encoding="utf-8")
print("country_panel.csv:", panel.shape)

# ---------- 4) world series (Track A) ----------
# 4a FAOSTAT N mundial + temperatura mundial
wsr = fao_world_series(rfn, "Nutrient nitrogen N (total)", "Agricultural Use", value_name="n_total_t_world")
wtemp = fao_world_series(et, element="Temperature change", months="Meteorological year", value_name="temp_anom_world")
# 4b QCL produccion mundial por gran grupo (chunked, 545MB)
print("Procesando QCL (chunked) para produccion mundial por grupo y rendimiento cereal mundial ...")
groups = {}      # item -> {year: production_t}
world_cer_yield = {}
qcl_path = os.path.join(RAW, "faostat_QCL.csv")
want_items = ["Cereals, Total", "Cereals", "Roots and Tubers, Total", "Roots and tubers, Total",
              "Pulses, Total", "Treenuts, Total", "Oilcrops, Cake Equivalent", "Oilcrops, Oil Equivalent",
              "Oilcrops", "Vegetables Primary", "Fruit Primary", "Sugar Crops Primary"]
usecols = ["Area Code", "Item", "Element", "Year", "Unit", "Value"]
reader = pd.read_csv(qcl_path, encoding="latin-1", usecols=usecols, low_memory=False, chunksize=500_000)
world_rows = []
for ch in reader:
    w = ch[ch["Area Code"] == 5000]
    if w.empty:
        continue
    world_rows.append(w)
wq = pd.concat(world_rows, ignore_index=True)
print("  QCL World subset:", wq.shape)
wq.to_csv(os.path.join(PROC, "qcl_world_raw.csv"), index=False, encoding="utf-8")
# produccion por grupo
prod = wq[(wq["Element"] == "Production")].copy()
prod["Year"] = pd.to_numeric(prod["Year"], errors="coerce")
prod["Value"] = pd.to_numeric(prod["Value"], errors="coerce")
items_avail = sorted(prod["Item"].unique())
print("  Items de produccion disponibles (muestra):",
      [i for i in items_avail if any(g.split(",")[0] in i for g in want_items)][:40])
# rendimiento cereal mundial (Yield) -> Item "Cereals, Total" Element "Yield"
yld = wq[(wq["Element"] == "Yield")].copy()
yld["Year"] = pd.to_numeric(yld["Year"], errors="coerce")
yld["Value"] = pd.to_numeric(yld["Value"], errors="coerce")

# guardar tablas crudas mundiales para el siguiente script
prod.to_csv(os.path.join(PROC, "world_production_long.csv"), index=False, encoding="utf-8")
yld.to_csv(os.path.join(PROC, "world_yield_long.csv"), index=False, encoding="utf-8")
wsr.to_csv(os.path.join(PROC, "world_N.csv"), index=False, encoding="utf-8")
wtemp.to_csv(os.path.join(PROC, "world_temp.csv"), index=False, encoding="utf-8")

# ---------- 5) Spain detailed ----------
def fao_one_country(df, area_code, **kw):
    d = df[df["Area Code"] == area_code]
    return d
esp_parts = {}
ESP = 203  # FAOSTAT area code for Spain
for label, (df, item, elem, mon) in {
    "n_kg_ha":        (rfn, "Nutrient nitrogen N (total)", "Use per area of cropland", None),
    "tractors":       (rm,  "Agricultural tractors", "In Use", None),
    "arable_kha":     (rl,  "Arable land", "Area", None),
    "irrig_equip_kha":(rl,  "Land area equipped for irrigation", "Area", None),
    "agri_land_kha":  (rl,  "Agricultural land", "Area", None),
    "temp_anom":      (et,  None, "Temperature change", "Meteorological year"),
}.items():
    d = df[df["Area Code"] == ESP]
    if item: d = d[d["Item"] == item]
    if elem: d = d[d["Element"] == elem]
    if mon and "Months" in d.columns: d = d[d["Months"] == mon]
    s = d.assign(year=pd.to_numeric(d["Year"], errors="coerce"),
                 value=pd.to_numeric(d["Value"], errors="coerce")) \
         .groupby("year", as_index=False)["value"].mean().rename(columns={"value": label})
    esp_parts[label] = s
esp = None
for label, s in esp_parts.items():
    esp = s if esp is None else esp.merge(s, on="year", how="outer")
esp = esp.sort_values("year")
esp.to_csv(os.path.join(PROC, "spain_series.csv"), index=False, encoding="utf-8")
print("spain_series.csv:", esp.shape)

print("\nLISTO. Ficheros en data/processed/:")
for f in sorted(os.listdir(PROC)):
    print("  ", f, round(os.path.getsize(os.path.join(PROC, f))/1e6, 2), "MB")
