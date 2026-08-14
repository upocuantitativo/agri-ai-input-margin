# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 7 -- Yield models H1/H3/H4 -> results/06_yield_models.json, figures 7-8
#
# Copied verbatim from the author's working tree (analysis/06_yield_models.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/06_yield_models.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""
06_yield_models.py  -- ANALISIS CENTRAL
Contrasta:
 (Doc 1)  ML mejora la prediccion del rendimiento frente a metodos tradicionales (OLS).
 (Doc 2 / autor)  La productividad depende de un PAQUETE de insumos, no de un factor unico.
 (Autor)  La IA ESPECIFICA (local) supera a la IA GENERICA (integral): comparacion
          modelo global vs modelos regionales vs calibracion local + efectos fijos.

Target: log(rendimiento cereal, kg/ha). Panel pais-anio FAOSTAT+World Bank.
Validacion: holdout temporal (train<=2009, test>=2010) y GroupKFold por pais.
"""
import os, json, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROC = "data/processed"; FIG = "figures"; RES = "results"
plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                     "grid.alpha": .3, "axes.spines.top": False, "axes.spines.right": False})
RNG = 42
results = {}

# ---------- datos ----------
panel = pd.read_csv(os.path.join(PROC, "country_panel.csv"), encoding="utf-8")
meta = pd.read_csv(os.path.join(PROC, "country_meta.csv"), encoding="utf-8")
df = panel.merge(meta[["iso3", "region", "income"]], on="iso3", how="left")

FEATS = ["n_kg_ha", "p_kg_ha", "k_kg_ha", "irrig_share_cropland", "temp_anom", "arable_kha", "year"]
TARGET = "cereal_yield_kg_ha"
d = df.dropna(subset=[TARGET] + FEATS + ["region"]).copy()
d = d[d[TARGET] > 0]
d["log_arable"] = np.log(d["arable_kha"].clip(lower=1))
FEATS = ["n_kg_ha", "p_kg_ha", "k_kg_ha", "irrig_share_cropland", "temp_anom", "log_arable", "year"]
d["y"] = np.log(d[TARGET])
print("Muestra modelable:", d.shape, "| paises:", d["iso3"].nunique(), "| años", int(d.year.min()), "-", int(d.year.max()))
results["muestra"] = {"n": int(len(d)), "paises": int(d["iso3"].nunique()),
                      "anio_min": int(d.year.min()), "anio_max": int(d.year.max()),
                      "features": FEATS, "target": "log(cereal_yield_kg_ha)"}

def metrics_logspace(y_true_log, y_pred_log):
    rmse_log = np.sqrt(mean_squared_error(y_true_log, y_pred_log))
    r2 = r2_score(y_true_log, y_pred_log)
    yt = np.exp(y_true_log); yp = np.exp(y_pred_log)
    rmse_kg = np.sqrt(mean_squared_error(yt, yp))
    mae_kg = mean_absolute_error(yt, yp)
    return {"rmse_log": round(rmse_log, 4), "r2": round(r2, 4),
            "rmse_kg_ha": round(rmse_kg, 1), "mae_kg_ha": round(mae_kg, 1)}

# split temporal
tr = d[d["year"] <= 2009].copy()
te = d[d["year"] >= 2010].copy()
print("Train<=2009:", len(tr), " Test>=2010:", len(te))

def make_model(kind):
    num = Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())])
    if kind == "ols":
        est = LinearRegression()
        pre = ColumnTransformer([("num", num, FEATS)])
    elif kind == "rf":
        est = RandomForestRegressor(n_estimators=400, max_depth=None, min_samples_leaf=3,
                                    n_jobs=-1, random_state=RNG)
        pre = ColumnTransformer([("num", Pipeline([("imp", SimpleImputer(strategy="median"))]), FEATS)])
    elif kind == "hgb":
        est = HistGradientBoostingRegressor(max_iter=500, learning_rate=0.05,
                                            max_depth=None, l2_regularization=1.0, random_state=RNG)
        pre = ColumnTransformer([("num", Pipeline([("imp", SimpleImputer(strategy="median"))]), FEATS)])
    return Pipeline([("pre", pre), ("est", est)])

# ============ TEST A: ML vs OLS ============
testA = {"holdout_temporal": {}, "groupkfold_pais": {}}
for kind, name in [("ols", "OLS (lineal)"), ("rf", "Random Forest"), ("hgb", "Gradient Boosting")]:
    mdl = make_model(kind)
    mdl.fit(tr[FEATS], tr["y"])
    pred = mdl.predict(te[FEATS])
    testA["holdout_temporal"][name] = metrics_logspace(te["y"].values, pred)

# GroupKFold por pais
gkf = GroupKFold(n_splits=5)
for kind, name in [("ols", "OLS (lineal)"), ("rf", "Random Forest"), ("hgb", "Gradient Boosting")]:
    r2s, rmses = [], []
    for tri, tei in gkf.split(d[FEATS], d["y"], groups=d["iso3"]):
        mdl = make_model(kind)
        mdl.fit(d.iloc[tri][FEATS], d.iloc[tri]["y"])
        pred = mdl.predict(d.iloc[tei][FEATS])
        r2s.append(r2_score(d.iloc[tei]["y"], pred))
        rmses.append(np.sqrt(mean_squared_error(np.exp(d.iloc[tei]["y"]), np.exp(pred))))
    testA["groupkfold_pais"][name] = {"r2_medio": round(float(np.mean(r2s)), 4),
                                      "r2_sd": round(float(np.std(r2s)), 4),
                                      "rmse_kg_ha_medio": round(float(np.mean(rmses)), 1)}
results["testA_ML_vs_OLS"] = testA

# ============ TEST B: paquete vs factor unico ============
best = make_model("hgb"); best.fit(tr[FEATS], tr["y"])
# permutation importance en test
pi = permutation_importance(best, te[FEATS], te["y"], n_repeats=15, random_state=RNG, n_jobs=-1)
imp = sorted(zip(FEATS, pi.importances_mean, pi.importances_std), key=lambda t: -t[1])
results["testB_importancia"] = {"permutation_importance_test": [
    {"feature": f, "importancia": round(float(m), 4), "sd": round(float(s), 4)} for f, m, s in imp]}
# R2 univariante (cada feature solo) vs full
uni = {}
for f in FEATS:
    m1 = Pipeline([("pre", ColumnTransformer([("num", SimpleImputer(strategy="median"), [f])])),
                   ("est", HistGradientBoostingRegressor(max_iter=300, learning_rate=.05,
                                                         l2_regularization=1.0, random_state=RNG))])
    m1.fit(tr[[f]], tr["y"])
    uni[f] = round(float(r2_score(te["y"], m1.predict(te[[f]]))), 4)
full_r2 = testA["holdout_temporal"]["Gradient Boosting"]["r2"]
results["testB_r2_univariante"] = {"r2_cada_feature_sola": uni, "r2_paquete_completo": full_r2,
    "interpretacion": "Ningun factor unico alcanza el R2 del paquete completo -> la productividad es un paquete."}

# figura importancia
fig, ax = plt.subplots(figsize=(7, 4))
fs = [f for f, _, _ in imp][::-1]; vs = [m for _, m, _ in imp][::-1]
ax.barh(fs, vs, color="steelblue")
ax.set_title("Importancia por permutación (test) — modelo Gradient Boosting")
ax.set_xlabel("Caída de R² al permutar la variable")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig7_importancia.png")); plt.close(fig)

# ============ TEST C: generico vs especifico ============
testC = {}
# C1 GENERICO (global, solo inputs)
gen = make_model("hgb"); gen.fit(tr[FEATS], tr["y"])
pred_gen = gen.predict(te[FEATS])
testC["1_generico_global"] = metrics_logspace(te["y"].values, pred_gen)

# C2 REGIONAL (un modelo por region, solo inputs)
preds_reg = np.full(len(te), np.nan)
te_idx = te.reset_index(drop=True)
for reg in d["region"].dropna().unique():
    trr = tr[tr["region"] == reg]; ter_mask = (te_idx["region"] == reg).values
    if len(trr) < 50 or ter_mask.sum() == 0:
        continue
    mr = make_model("hgb"); mr.fit(trr[FEATS], trr["y"])
    preds_reg[ter_mask] = mr.predict(te_idx.loc[ter_mask, FEATS])
mask = ~np.isnan(preds_reg)
testC["2_regional"] = metrics_logspace(te_idx["y"].values[mask], preds_reg[mask])
testC["2_regional"]["cobertura_test"] = round(float(mask.mean()), 3)

# C3 LOCAL: generico + calibracion local (offset = residuo medio de entrenamiento por pais)
tr_res = tr.copy(); tr_res["resid"] = tr["y"].values - gen.predict(tr[FEATS])
offset = tr_res.groupby("iso3")["resid"].mean()
glob_off = float(tr_res["resid"].mean())
te_off = te["iso3"].map(offset).fillna(glob_off).values
pred_local = pred_gen + te_off
testC["3_local_calibrado"] = metrics_logspace(te["y"].values, pred_local)

# C4 INPUTS + GEOGRAFIA (un HGB con pais/region/renta como categoricas)
cat = ["iso3", "region", "income"]
pre4 = ColumnTransformer([
    ("num", SimpleImputer(strategy="median"), FEATS),
    ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5, sparse_output=False), cat)])
m4 = Pipeline([("pre", pre4), ("est", HistGradientBoostingRegressor(
    max_iter=500, learning_rate=.05, l2_regularization=1.0, random_state=RNG))])
trc = tr.dropna(subset=cat); tec = te.dropna(subset=cat)
m4.fit(trc[FEATS + cat], trc["y"])
pred4 = m4.predict(tec[FEATS + cat])
testC["4_inputs_mas_geografia"] = metrics_logspace(tec["y"].values, pred4)

# reduccion de error local vs generico
rg = testC["1_generico_global"]["rmse_kg_ha"]
rl = testC["3_local_calibrado"]["rmse_kg_ha"]
r4 = testC["4_inputs_mas_geografia"]["rmse_kg_ha"]
testC["reduccion_error"] = {
    "rmse_generico_kg_ha": rg,
    "rmse_local_calibrado_kg_ha": rl,
    "reduccion_local_vs_generico_%": round(100 * (rg - rl) / rg, 1),
    "rmse_inputs+geografia_kg_ha": r4,
    "reduccion_geo_vs_generico_%": round(100 * (rg - r4) / rg, 1),
    "interpretacion": "Una calibracion local trivial (offset por pais) y/o anadir geografia "
                      "reduce el error frente al modelo generico -> apoya la tesis de modelos "
                      "especificos por area/region frente a una IA generica/integral.",
}
results["testC_generico_vs_especifico"] = testC

# ---- descomposicion de varianza (OLS): inputs vs efectos fijos de pais ----
import statsmodels.api as sm
dd = d.copy()
Xnum = sm.add_constant(StandardScaler().fit_transform(dd[FEATS]))
r2_inputs = sm.OLS(dd["y"].values, Xnum).fit().rsquared
fe = pd.get_dummies(dd["iso3"], drop_first=True).astype(float).values
Xfe = np.column_stack([Xnum, fe])
r2_inputs_fe = sm.OLS(dd["y"].values, Xfe).fit().rsquared
fe_only = sm.add_constant(fe)
r2_fe = sm.OLS(dd["y"].values, fe_only).fit().rsquared
results["descomposicion_varianza"] = {
    "r2_solo_inputs_genericos": round(float(r2_inputs), 4),
    "r2_inputs_mas_efectos_pais": round(float(r2_inputs_fe), 4),
    "r2_solo_efectos_pais": round(float(r2_fe), 4),
    "ganancia_por_especificidad_local": round(float(r2_inputs_fe - r2_inputs), 4),
    "interpretacion": "La especificidad local (efectos fijos de pais) explica una fraccion "
                      "sustancial de la varianza del rendimiento que un modelo generico de "
                      "insumos NO captura."}

# figura comparativa generico vs especifico
fig, ax = plt.subplots(figsize=(7.2, 4.2))
labels = ["Genérico\n(global, inputs)", "Regional\n(por región)", "Local\n(calibrado)", "Inputs+\nGeografía"]
vals = [testC["1_generico_global"]["rmse_kg_ha"], testC["2_regional"]["rmse_kg_ha"],
        testC["3_local_calibrado"]["rmse_kg_ha"], testC["4_inputs_mas_geografia"]["rmse_kg_ha"]]
bars = ax.bar(labels, vals, color=["#b22222", "#d2851a", "#2e8b57", "#1f6f8b"])
ax.set_ylabel("RMSE test (kg/ha)  ↓ mejor")
ax.set_title("Genérico vs específico: error de predicción del rendimiento (holdout ≥2010)")
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v, f"{v:.0f}", ha="center", va="bottom", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig8_generico_vs_especifico.png")); plt.close(fig)

with open(os.path.join(RES, "06_yield_models.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(json.dumps(results, ensure_ascii=False, indent=2))
