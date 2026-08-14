# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 9 -- Robustness of the pre-AI block -> results/08_robustness.json, figure 10
#
# Copied verbatim from the author's working tree (analysis/08_robustness.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/08_robustness.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""
08_robustness.py  -- chequeos de robustez
 (a) Dependencia parcial del rendimiento respecto a N (rendimientos decrecientes micro).
 (b) Sensibilidad del hallazgo generico-vs-especifico al anio de corte del holdout.
 (c) sigma-convergencia ponderada por poblacion (robustez de H2).
"""
import os, json, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.inspection import PartialDependenceDisplay
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROC="data/processed"; FIG="figures"; RES="results"
plt.rcParams.update({"figure.dpi":130,"font.size":10,"axes.grid":True,"grid.alpha":.3,
                     "axes.spines.top":False,"axes.spines.right":False})
RNG=42; out={}

panel=pd.read_csv(f"{PROC}/country_panel.csv"); meta=pd.read_csv(f"{PROC}/country_meta.csv")
df=panel.merge(meta[["iso3","region","income"]],on="iso3",how="left")
FEATS=["n_kg_ha","p_kg_ha","k_kg_ha","irrig_share_cropland","temp_anom","log_arable","year"]
d=df.dropna(subset=["cereal_yield_kg_ha","n_kg_ha","p_kg_ha","k_kg_ha","irrig_share_cropland","temp_anom","arable_kha"]).copy()
d=d[d["cereal_yield_kg_ha"]>0]; d["log_arable"]=np.log(d["arable_kha"].clip(lower=1)); d["y"]=np.log(d["cereal_yield_kg_ha"])

# (a) dependencia parcial N e irrigacion
tr=d[d.year<=2009]
base=Pipeline([("imp",SimpleImputer(strategy="median")),
               ("est",HistGradientBoostingRegressor(max_iter=500,learning_rate=.05,l2_regularization=1.0,random_state=RNG))])
base.fit(tr[FEATS],tr["y"])
fig,ax=plt.subplots(1,2,figsize=(11,4.2))
PartialDependenceDisplay.from_estimator(base,tr[FEATS],["n_kg_ha"],ax=ax[0])
ax[0].set_title("Dependencia parcial: N (kg/ha)"); ax[0].set_ylabel("log rendimiento (parcial)")
PartialDependenceDisplay.from_estimator(base,tr[FEATS],["irrig_share_cropland"],ax=ax[1])
ax[1].set_title("Dependencia parcial: % regadío")
fig.suptitle("Rendimientos marginales decrecientes de los insumos (Gradient Boosting)")
fig.tight_layout(); fig.savefig(f"{FIG}/fig10_dependencia_parcial.png"); plt.close(fig)
# pendiente de la PD de N en tramo bajo vs alto
from sklearn.inspection import partial_dependence
pd_n=partial_dependence(base,tr[FEATS],["n_kg_ha"],grid_resolution=40)
gx=pd_n["grid_values"][0]; gy=pd_n["average"][0]
lo=np.polyfit(gx[:10],gy[:10],1)[0]; hi=np.polyfit(gx[-10:],gy[-10:],1)[0]
out["dependencia_parcial_N"]={"pendiente_tramo_bajo":round(float(lo),5),
    "pendiente_tramo_alto":round(float(hi),5),
    "ratio_alto_sobre_bajo":round(float(hi/lo),3) if lo!=0 else None,
    "interpretacion":"la respuesta marginal del rendimiento al N decae a dosis altas (rendimientos decrecientes)"}

# (b) sensibilidad generico vs especifico al corte
def metrics(yt,yp): return {"r2":round(float(r2_score(yt,yp)),4),
    "rmse_kg_ha":round(float(np.sqrt(mean_squared_error(np.exp(yt),np.exp(yp)))),1)}
cat=["iso3","region","income"]
sens=[]
for cut in [2005,2010,2015]:
    tr2=d[d.year<=cut].dropna(subset=cat); te2=d[d.year>cut].dropna(subset=cat)
    gen=Pipeline([("imp",SimpleImputer(strategy="median")),
                  ("est",HistGradientBoostingRegressor(max_iter=400,learning_rate=.05,l2_regularization=1.0,random_state=RNG))])
    gen.fit(tr2[FEATS],tr2["y"]); pg=gen.predict(te2[FEATS])
    pre=ColumnTransformer([("num",SimpleImputer(strategy="median"),FEATS),
        ("cat",OneHotEncoder(handle_unknown="ignore",min_frequency=5,sparse_output=False),cat)])
    geo=Pipeline([("pre",pre),("est",HistGradientBoostingRegressor(max_iter=400,learning_rate=.05,l2_regularization=1.0,random_state=RNG))])
    geo.fit(tr2[FEATS+cat],tr2["y"]); pgeo=geo.predict(te2[FEATS+cat])
    mg=metrics(te2["y"].values,pg); mgeo=metrics(te2["y"].values,pgeo)
    sens.append({"corte":cut,"rmse_generico":mg["rmse_kg_ha"],"r2_generico":mg["r2"],
                 "rmse_inputs+geo":mgeo["rmse_kg_ha"],"r2_inputs+geo":mgeo["r2"],
                 "reduccion_error_%":round(100*(mg["rmse_kg_ha"]-mgeo["rmse_kg_ha"])/mg["rmse_kg_ha"],1)})
out["sensibilidad_corte_holdout"]=sens

# (c) sigma-convergencia ponderada por poblacion
y=df[["iso3","year","cereal_yield_kg_ha","population"]].dropna()
y=y[y["cereal_yield_kg_ha"]>0]; y["logy"]=np.log(y["cereal_yield_kg_ha"])
def wstd(g):
    w=g["population"].values; x=g["logy"].values
    if w.sum()<=0 or len(x)<30: return np.nan
    mu=np.average(x,weights=w); return np.sqrt(np.average((x-mu)**2,weights=w))
sig=y.groupby("year").apply(wstd).dropna()
out["sigma_convergencia_ponderada_pob"]={
    "sd_ini":round(float(sig.iloc[0]),3),"anio_ini":int(sig.index[0]),
    "sd_fin":round(float(sig.iloc[-1]),3),"anio_fin":int(sig.index[-1]),
    "tendencia":"divergencia" if np.polyfit(sig.index,sig.values,1)[0]>0 else "convergencia"}

with open(f"{RES}/08_robustness.json","w",encoding="utf-8") as f: json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps(out,ensure_ascii=False,indent=2)); print("\nfig10 guardada.")
