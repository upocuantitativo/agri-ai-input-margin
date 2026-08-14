# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 4 -- Download World Bank country metadata (region, income) -> data/processed/country_meta.csv
#
# Copied verbatim from the author's working tree (analysis/03b_country_meta.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/03b_country_meta.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""Descarga metadatos de pais (region, nivel de renta) del Banco Mundial."""
import os, requests, pandas as pd
PROC = "data/processed"
r = requests.get("https://api.worldbank.org/v2/country",
                 params={"format": "json", "per_page": 400}, timeout=60)
data = r.json()[1]
rows = []
for d in data:
    rows.append({
        "iso3": d["id"],
        "country": d["name"],
        "region": d["region"]["value"],
        "region_id": d["region"]["id"],
        "income": d["incomeLevel"]["value"],
        "income_id": d["incomeLevel"]["id"],
    })
df = pd.DataFrame(rows)
# quitar agregados (region == 'Aggregates')
df = df[df["region"] != "Aggregates"].reset_index(drop=True)
df.to_csv(os.path.join(PROC, "country_meta.csv"), index=False, encoding="utf-8")
print("country_meta.csv:", df.shape)
print(df["region"].value_counts())
print(df["income"].value_counts())
