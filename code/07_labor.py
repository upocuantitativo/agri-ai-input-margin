# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 8 -- Employment recomposition (H5) -> results/07_labor.json, figure 9
#
# Copied verbatim from the author's working tree (analysis/07_labor.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/07_labor.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""
07_labor.py
Contrasta el claim de "recomposicion de ocupaciones" (Doc 2): la mecanizacion y el
aumento de productividad del trabajo van acompanados de caida del empleo agricola.
 - serie global del empleo agricola (% del total)
 - regresion con efectos fijos de pais: log(empleo agricola %) ~ log(VA por trabajador)
 - mecanizacion (tractores/1000 ha) vs empleo agricola
"""
import os, json, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROC = "data/processed"; FIG = "figures"; RES = "results"
plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                     "grid.alpha": .3, "axes.spines.top": False, "axes.spines.right": False})
results = {}

panel = pd.read_csv(os.path.join(PROC, "country_panel.csv"), encoding="utf-8")
meta = pd.read_csv(os.path.join(PROC, "country_meta.csv"), encoding="utf-8")
df = panel.merge(meta[["iso3", "region", "income"]], on="iso3", how="left")

# ---- 1) serie global empleo agricola (poblacional ponderada via WB world ya filtrado: usamos media ponderada por poblacion) ----
g = df.dropna(subset=["agri_empl_pct", "population"])
emp_world = (g.assign(num=g["agri_empl_pct"]*g["population"])
              .groupby("year").agg(num=("num","sum"), pop=("population","sum")))
emp_world["empleo_agri_pct_mundial"] = emp_world["num"]/emp_world["pop"]
ew = emp_world.reset_index()
results["empleo_agricola_mundial"] = {
    "anio_ini": int(ew["year"].min()), "valor_ini_%": round(float(ew["empleo_agri_pct_mundial"].iloc[0]),1),
    "anio_fin": int(ew["year"].max()), "valor_fin_%": round(float(ew["empleo_agri_pct_mundial"].iloc[-1]),1),
}

# ---- 2) panel FE: log(empleo) ~ log(VA por trabajador) ----
reg = df.dropna(subset=["agri_empl_pct", "agri_va_per_worker"]).copy()
reg = reg[(reg["agri_empl_pct"]>0) & (reg["agri_va_per_worker"]>0)]
reg["log_emp"] = np.log(reg["agri_empl_pct"])
reg["log_va"] = np.log(reg["agri_va_per_worker"])
# efectos fijos de pais y de anio
m = smf.ols("log_emp ~ log_va + C(iso3) + C(year)", data=reg).fit(
    cov_type="cluster", cov_kwds={"groups": reg["iso3"]})
results["regresion_FE_empleo_vs_productividad"] = {
    "n": int(m.nobs),
    "coef_log_va": round(float(m.params["log_va"]), 4),
    "se": round(float(m.bse["log_va"]), 4),
    "p_value": round(float(m.pvalues["log_va"]), 5),
    "interpretacion": ("elasticidad negativa: al subir el valor anadido por trabajador agricola, "
                       "el empleo agricola (% del total) cae -> recomposicion ocupacional"),
    "lectura": "una subida del 10% en VA por trabajador se asocia con un cambio de "
               f"{round(float(m.params['log_va'])*10,2)}% en el empleo agricola (%)",
}

# ---- 3) mecanizacion vs empleo (cross-section donde hay tractores, <=2009) ----
mech = df.dropna(subset=["tractors_per_1000ha_arable", "agri_empl_pct"])
if len(mech) > 30:
    cm = mech[["tractors_per_1000ha_arable","agri_empl_pct"]].corr().iloc[0,1]
    results["correlacion_mecanizacion_empleo"] = {
        "n": int(len(mech)), "corr_tractores_vs_empleo_agri": round(float(cm),3)}

# ---- figuras ----
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
ax[0].plot(ew["year"], ew["empleo_agri_pct_mundial"], color="darkgreen", lw=2.2)
ax[0].set_title("Empleo agrícola mundial (% del total, ponderado por población)")
ax[0].set_xlabel("Año"); ax[0].set_ylabel("% del empleo total")
# scatter VA/worker vs empleo
s = reg.sample(min(3000, len(reg)), random_state=1)
ax[1].scatter(s["log_va"], s["log_emp"], s=8, alpha=.25, color="slateblue")
ax[1].set_title("Empleo agrícola vs productividad del trabajo (país-año)")
ax[1].set_xlabel("log(valor añadido por trabajador agrícola)")
ax[1].set_ylabel("log(empleo agrícola, %)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig9_empleo.png")); plt.close(fig)

with open(os.path.join(RES, "07_labor.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(json.dumps(results, ensure_ascii=False, indent=2))
