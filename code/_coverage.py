# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step aux -- Ad-hoc coverage check helper, not part of the reported pipeline.
#
# Copied verbatim from the author's working tree (analysis/_coverage.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/_coverage.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
import pandas as pd, numpy as np
panel = pd.read_csv("data/processed/country_panel.csv", encoding="utf-8")
cols = ["cereal_yield_kg_ha","n_kg_ha","p_kg_ha","k_kg_ha","irrig_share_cropland",
        "tractors_per_1000ha_arable","temp_anom","arable_kha","fert_kg_ha_arable",
        "irrigated_pct_agri","agri_empl_pct","agri_va_per_worker"]
print("Filas totales:", len(panel), "| años:", panel['year'].min(), panel['year'].max())
print("\nCobertura no-nula por variable (global y >=2010):")
for c in cols:
    if c in panel:
        n_all = panel[c].notna().sum()
        n_recent = panel[(panel['year']>=2010)][c].notna().sum()
        yrs = panel.loc[panel[c].notna(),'year']
        print(f"  {c:30s} n={n_all:6d}  n>=2010={n_recent:5d}  años {int(yrs.min()) if len(yrs) else '-'}-{int(yrs.max()) if len(yrs) else '-'}")
# muestra modelable con paquete largo (sin tractores)
core = ["cereal_yield_kg_ha","n_kg_ha","irrig_share_cropland","temp_anom"]
m = panel.dropna(subset=core)
print("\nMuestra con [yield,N,irrig,temp]:", len(m), "filas,", m['iso3'].nunique(), "paises, años", int(m['year'].min()),"-",int(m['year'].max()))
core2 = core + ["tractors_per_1000ha_arable"]
m2 = panel.dropna(subset=core2)
print("+ tractores:", len(m2), "filas, años", int(m2['year'].min()),"-",int(m2['year'].max()))
core3 = ["cereal_yield_kg_ha","n_kg_ha","irrig_share_cropland","temp_anom","p_kg_ha","k_kg_ha"]
m3 = panel.dropna(subset=core3)
print("paquete NPK+irrig+temp:", len(m3), "filas, años", int(m3['year'].min()),"-",int(m3['year'].max()))
