# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 6 -- Convergence tests (H6) -> results/05_convergence.json, figures 5-6
#
# Copied verbatim from the author's working tree (analysis/05_convergence.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/05_convergence.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""
05_convergence.py
Test de la hipotesis H2 ("amplifica desigualdades territoriales"):
 - sigma-convergencia: dispersion del log-rendimiento entre paises en el tiempo
 - beta-convergencia: crecimiento del rendimiento vs nivel inicial (catch-up?)
"""
import os, json
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROC = "data/processed"; FIG = "figures"; RES = "results"
plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                     "grid.alpha": .3, "axes.spines.top": False, "axes.spines.right": False})

panel = pd.read_csv(os.path.join(PROC, "country_panel.csv"), encoding="utf-8")
meta = pd.read_csv(os.path.join(PROC, "country_meta.csv"), encoding="utf-8")
df = panel.merge(meta[["iso3", "region", "income"]], on="iso3", how="left")

y = df[["iso3", "country", "year", "cereal_yield_kg_ha", "region", "income", "population"]].copy()
y = y[(y["cereal_yield_kg_ha"] > 0) & y["cereal_yield_kg_ha"].notna()]
y["log_yield"] = np.log(y["cereal_yield_kg_ha"])

# paises con cobertura suficiente (>= 40 anios entre 1961-2022)
cov = y[(y["year"] >= 1961) & (y["year"] <= 2022)].groupby("iso3")["year"].nunique()
keep = cov[cov >= 40].index
yk = y[y["iso3"].isin(keep)].copy()
results = {"n_paises_panel_convergencia": int(len(keep))}

# -------- sigma-convergencia --------
sig = yk.groupby("year").agg(sd_logyield=("log_yield", "std"),
                             cv=("cereal_yield_kg_ha", lambda s: s.std()/s.mean()),
                             n=("log_yield", "size")).reset_index()
sig = sig[sig["n"] >= 30]
# tendencia de la dispersion
sl_sd = np.polyfit(sig["year"], sig["sd_logyield"], 1)[0]
results["sigma_convergencia"] = {
    "sd_logyield_inicial": round(float(sig.iloc[0]["sd_logyield"]), 3),
    "anio_inicial": int(sig.iloc[0]["year"]),
    "sd_logyield_final": round(float(sig.iloc[-1]["sd_logyield"]), 3),
    "anio_final": int(sig.iloc[-1]["year"]),
    "pendiente_sd_por_anio": round(float(sl_sd), 5),
    "interpretacion": "sigma-divergencia (dispersion crece)" if sl_sd > 0 else "sigma-convergencia (dispersion cae)",
}

# -------- beta-convergencia --------
early = yk[(yk["year"] >= 1961) & (yk["year"] <= 1965)].groupby("iso3")["log_yield"].mean().rename("log_y0")
late = yk[(yk["year"] >= 2018) & (yk["year"] <= 2022)].groupby("iso3")["log_yield"].mean().rename("log_y1")
bc = pd.concat([early, late], axis=1).dropna()
T = (2020 - 1963)
bc["growth"] = (bc["log_y1"] - bc["log_y0"]) / T
X = sm.add_constant(bc["log_y0"])
m = sm.OLS(bc["growth"], X).fit()
beta = float(m.params["log_y0"])
results["beta_convergencia"] = {
    "n": int(len(bc)),
    "coef_log_y0": round(beta, 5),
    "p_value": round(float(m.pvalues["log_y0"]), 4),
    "r2": round(float(m.rsquared), 3),
    "interpretacion": ("beta-convergencia (los paises con menor rendimiento inicial crecen mas rapido)"
                       if beta < 0 else
                       "beta-divergencia (los avanzados crecen mas, brecha se amplia)"),
}
# tasa de convergencia implicita si beta<0
if beta < 0:
    lam = -np.log(1 + beta * T) / T
    results["beta_convergencia"]["velocidad_lambda_%/anio"] = round(float(100*lam), 2)

# -------- divergencia por nivel de renta (mediana de rendimiento por grupo) --------
inc_trend = (yk.groupby(["year", "income"])["cereal_yield_kg_ha"].median().reset_index())
piv_inc = inc_trend.pivot(index="year", columns="income", values="cereal_yield_kg_ha")
results["rendimiento_mediano_por_renta"] = {
    str(col): {"1961_65": round(float(piv_inc.loc[1961:1965, col].mean()), 0) if col in piv_inc else None,
               "2018_22": round(float(piv_inc.loc[2018:2022, col].mean()), 0) if col in piv_inc else None}
    for col in piv_inc.columns
}

# -------- figuras --------
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
ax[0].plot(sig["year"], sig["sd_logyield"], color="navy", lw=2)
ax[0].set_title("σ-convergencia: dispersión del log-rendimiento entre países")
ax[0].set_xlabel("Año"); ax[0].set_ylabel("SD( log rendimiento )")
ax[1].scatter(bc["log_y0"], bc["growth"]*100, s=14, alpha=.6, color="darkred")
xs = np.linspace(bc["log_y0"].min(), bc["log_y0"].max(), 50)
ax[1].plot(xs, (m.params["const"] + beta*xs)*100, color="black", lw=2)
ax[1].set_title(f"β-convergencia (β={beta:.4f}, p={m.pvalues['log_y0']:.3f})")
ax[1].set_xlabel("log rendimiento inicial (1961-65)"); ax[1].set_ylabel("crecimiento anual (%)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig5_convergencia.png")); plt.close(fig)

fig, ax = plt.subplots(figsize=(7.5, 4.4))
for col in piv_inc.columns:
    ax.plot(piv_inc.index, piv_inc[col], lw=1.8, label=col)
ax.set_title("Rendimiento cerealista mediano por grupo de renta (kg/ha)")
ax.set_xlabel("Año"); ax.set_ylabel("kg/ha"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig6_rendimiento_por_renta.png")); plt.close(fig)

with open(os.path.join(RES, "05_convergence.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(json.dumps(results, ensure_ascii=False, indent=2))
