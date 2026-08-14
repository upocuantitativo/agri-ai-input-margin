# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step aux -- Ad-hoc exploration helper, not part of the reported pipeline.
#
# Copied verbatim from the author's working tree (analysis/_explore.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/_explore.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
import pandas as pd
try:
    import pycountry
    print("pycountry OK")
    HAS_PYC = True
except Exception as e:
    print("pycountry NO:", e)
    HAS_PYC = False

rm = pd.read_csv("data/raw/faostat_RM.csv", encoding="latin-1", low_memory=False)
sub = rm[rm["Item"].str.contains("tractor", case=False, na=False)]
print("\nTractor items x elements x unit:")
print(sub.groupby(["Item", "Element", "Unit"]).size())

rl = pd.read_csv("data/raw/faostat_RL.csv", encoding="latin-1", low_memory=False)
w = rl[rl["Area"] == "World"][["Area Code", "Area", "Area Code (M49)"]].drop_duplicates()
print("\nWorld rows:\n", w.head())
ac = rl[["Area Code", "Area"]].drop_duplicates().sort_values("Area Code")
print("\nArea codes 4900-5400:")
print(ac[(ac["Area Code"] >= 4900) & (ac["Area Code"] <= 5400)].to_string())
print("\nN distinct area codes < 5000:", (ac["Area Code"] < 5000).sum())
