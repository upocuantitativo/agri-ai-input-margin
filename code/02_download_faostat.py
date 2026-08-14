# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 2 -- Download FAOSTAT bulk datasets (QCL, RFN, RL, RM, ET) -> data/raw/faostat_*.csv
#
# Copied verbatim from the author's working tree (analysis/02_download_faostat.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/02_download_faostat.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""
02_download_faostat.py
Descarga datasets FAOSTAT (bulk normalizado), los extrae y guarda el CSV crudo.
Robusto: reintentos, streaming a disco, manejo de zips.
"""
import os, io, zipfile, time
import requests
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
os.makedirs(RAW, exist_ok=True)

DATASETS = {
    "RFN": "https://bulks-faostat.fao.org/production/Inputs_FertilizersNutrient_E_All_Data_(Normalized).zip",
    "ET":  "https://bulks-faostat.fao.org/production/Environment_Temperature_change_E_All_Data_(Normalized).zip",
    "RL":  "https://bulks-faostat.fao.org/production/Inputs_LandUse_E_All_Data_(Normalized).zip",
    "RM":  "https://bulks-faostat.fao.org/production/Investment_Machinery_E_All_Data_(Normalized).zip",
    "QCL": "https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip",
}

def download(code, url):
    print(f"Descargando {code} ...")
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=300, stream=True)
            r.raise_for_status()
            buf = io.BytesIO()
            for chunk in r.iter_content(chunk_size=1 << 16):
                if chunk:
                    buf.write(chunk)
            buf.seek(0)
            z = zipfile.ZipFile(buf)
            # el csv principal es el (Normalized).csv
            csvname = [n for n in z.namelist() if n.lower().endswith(".csv") and "normalized" in n.lower()]
            if not csvname:
                csvname = [n for n in z.namelist() if n.lower().endswith(".csv")]
            name = csvname[0]
            z.extract(name, RAW)
            src = os.path.join(RAW, name)
            dst = os.path.join(RAW, f"faostat_{code}.csv")
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(src, dst)
            sz = os.path.getsize(dst) / 1e6
            print(f"  -> {code}: {name} -> faostat_{code}.csv ({sz:.1f} MB)")
            return dst
        except Exception as e:
            print(f"  [{code}] intento {attempt+1} fallo: {e}")
            time.sleep(5 * (attempt + 1))
    print(f"  -> FALLO {code}")
    return None

def main():
    for code, url in DATASETS.items():
        p = download(code, url)
        if p:
            try:
                df = pd.read_csv(p, encoding="latin-1", nrows=5)
                print("     cols:", list(df.columns))
            except Exception as e:
                print("     (no se pudo leer cabecera:", e, ")")

if __name__ == "__main__":
    main()
