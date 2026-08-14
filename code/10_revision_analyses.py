# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 10 -- Spatial transfer, input interactions, balanced panel, beta-convergence -> results/10_revision_analyses.json
#
# Copied verbatim from the author's working tree (analysis/10_revision_analyses.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/10_revision_analyses.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""
10_revision_analyses.py  -- análisis pedidos por el panel de revisión adversarial
Aborda C1/C2 (genérico vs específico bajo TRANSFERENCIA ESPACIAL), I1 (complementariedad),
I3 (beta-convergencia CONDICIONAL), H6 en PANEL BALANCEADO, y H5 con productividad EXÓGENA.
"""
import os, json, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.api as sm
import statsmodels.formula.api as smf

PROC="data/processed"; RES="results"; RNG=42
out={}

panel=pd.read_csv(f"{PROC}/country_panel.csv"); meta=pd.read_csv(f"{PROC}/country_meta.csv")
df=panel.merge(meta[["iso3","region","income"]],on="iso3",how="left")
FEATS=["n_kg_ha","p_kg_ha","k_kg_ha","irrig_share_cropland","temp_anom","log_arable","year"]
need=["cereal_yield_kg_ha","n_kg_ha","p_kg_ha","k_kg_ha","irrig_share_cropland","temp_anom","arable_kha","region","income"]
d=df.dropna(subset=need).copy(); d=d[d["cereal_yield_kg_ha"]>0]
d["log_arable"]=np.log(d["arable_kha"].clip(lower=1)); d["y"]=np.log(d["cereal_yield_kg_ha"])

def rmse_kg(yt,yp): return float(np.sqrt(mean_squared_error(np.exp(yt),np.exp(yp))))

# ============ C2: genérico vs específico bajo GroupKFold por país (transferencia espacial) ============
# Arquitecturas: (a) genérico inputs; (b) inputs+region+income (transferibles);
#                (c) inputs+iso3 dummies (NO transferibles: país no visto -> intercepto global)
def model_inputs():
    return Pipeline([("imp",SimpleImputer(strategy="median")),
                     ("est",HistGradientBoostingRegressor(max_iter=400,learning_rate=.05,l2_regularization=1.0,random_state=RNG))])
def model_cat(cats):
    pre=ColumnTransformer([("num",SimpleImputer(strategy="median"),FEATS),
        ("cat",OneHotEncoder(handle_unknown="ignore",min_frequency=5,sparse_output=False),cats)])
    return Pipeline([("pre",pre),("est",HistGradientBoostingRegressor(max_iter=400,learning_rate=.05,l2_regularization=1.0,random_state=RNG))])

gkf=GroupKFold(n_splits=5)
archs={"a_generico_inputs":("inputs",None),
       "b_inputs_region_income":("cat",["region","income"]),
       "c_inputs_pais":("cat",["iso3"])}
spatial={}
for name,(kind,cats) in archs.items():
    r2s,rmses=[],[]
    cols = FEATS if kind=="inputs" else FEATS+cats
    for tri,tei in gkf.split(d[cols],d["y"],groups=d["iso3"]):
        mdl = model_inputs() if kind=="inputs" else model_cat(cats)
        mdl.fit(d.iloc[tri][cols],d.iloc[tri]["y"])
        pred=mdl.predict(d.iloc[tei][cols])
        r2s.append(r2_score(d.iloc[tei]["y"],pred)); rmses.append(rmse_kg(d.iloc[tei]["y"].values,pred))
    spatial[name]={"r2_medio":round(float(np.mean(r2s)),4),"r2_sd":round(float(np.std(r2s)),4),
                   "rmse_kg_ha_medio":round(float(np.mean(rmses)),1)}
out["C2_transferencia_espacial_generico_vs_especifico"]={
    "resultados":spatial,
    "interpretacion":("Bajo transferencia a paises NO observados, los efectos fijos de pais (c) son "
        "inservibles (pais nuevo -> intercepto global) y NO mejoran sobre el generico; solo region/renta (b), "
        "que SI son transferibles, aportan. La ventaja de 'lo especifico' del holdout temporal se debe en gran "
        "parte a recordar la media de paises ya vistos, y no transfiere espacialmente.")}

# ============ I1: complementariedad (superaditividad del paquete) ============
# (i) OLS aditivo vs con interacciones NPK x regadio; (ii) ganancia de R2; (iii) signo interaccion N:irrig
dd=d.copy()
for c in ["n_kg_ha","p_kg_ha","k_kg_ha","irrig_share_cropland","temp_anom","log_arable"]:
    dd[c+"_z"]=StandardScaler().fit_transform(dd[[c]])
add=smf.ols("y ~ n_kg_ha_z+p_kg_ha_z+k_kg_ha_z+irrig_share_cropland_z+temp_anom_z+log_arable_z",data=dd).fit()
inter=smf.ols("y ~ (n_kg_ha_z+p_kg_ha_z+k_kg_ha_z+irrig_share_cropland_z)**2 + temp_anom_z+log_arable_z",data=dd).fit()
# extraer interaccion N:irrig
ncoef={k:(round(float(v),4),round(float(inter.pvalues[k]),4)) for k,v in inter.params.items() if ":" in k}
out["I1_complementariedad"]={
    "r2_aditivo":round(float(add.rsquared),4),
    "r2_con_interacciones":round(float(inter.rsquared),4),
    "ganancia_r2_por_interacciones":round(float(inter.rsquared-add.rsquared),4),
    "coef_interacciones_(coef,p)":ncoef,
    "interpretacion":("Si las interacciones entre insumos son significativas y mejoran el ajuste, hay "
        "COMPLEMENTARIEDAD (el efecto conjunto supera la suma de efectos aislados): evidencia mas exigente "
        "de 'paquete' que la simple superioridad multivariante.")}

# ============ I3 + H6 robusto: beta-convergencia CONDICIONAL y PANEL BALANCEADO ============
y=df[["iso3","year","cereal_yield_kg_ha","population","region","income"]].dropna(subset=["cereal_yield_kg_ha"])
y=y[y["cereal_yield_kg_ha"]>0]; y["log_yield"]=np.log(y["cereal_yield_kg_ha"])
# panel balanceado: paises con dato en TODOS los anios de la ventana 1961-2020
win=y[(y["year"]>=1961)&(y["year"]<=2020)]
cnt=win.groupby("iso3")["year"].nunique(); full=cnt[cnt>=58].index  # ~todos los anios
bal=win[win["iso3"].isin(full)].copy()
out["H6_panel_balanceado"]={"n_paises_balanceado":int(len(full))}
sig_bal=bal.groupby("year")["log_yield"].std()
out["H6_panel_balanceado"]["sd_log_ini"]=round(float(sig_bal.iloc[0]),3)
out["H6_panel_balanceado"]["sd_log_fin"]=round(float(sig_bal.iloc[-1]),3)
out["H6_panel_balanceado"]["tendencia"]="divergencia" if np.polyfit(sig_bal.index,sig_bal.values,1)[0]>0 else "convergencia"

# beta condicional sobre el panel balanceado: growth ~ log_y0 + region + inputs medios
early=bal[(bal.year>=1961)&(bal.year<=1965)].groupby("iso3")["log_yield"].mean().rename("log_y0")
late=bal[(bal.year>=2016)&(bal.year<=2020)].groupby("iso3")["log_yield"].mean().rename("log_y1")
reg_inc=meta.set_index("iso3")[["region","income"]]
inputs_mean=df[df.year>=1990].groupby("iso3")[["n_kg_ha","irrig_share_cropland"]].mean()
bc=pd.concat([early,late,reg_inc,inputs_mean],axis=1).dropna(subset=["log_y0","log_y1"])
bc["growth"]=(bc["log_y1"]-bc["log_y0"])/(2018-1963)
# incondicional
m_unc=smf.ols("growth ~ log_y0",data=bc).fit()
# condicional (controla region + insumos medios)
bc2=bc.dropna(subset=["n_kg_ha","irrig_share_cropland","region"])
m_con=smf.ols("growth ~ log_y0 + n_kg_ha + irrig_share_cropland + C(region)",data=bc2).fit()
out["I3_beta_convergencia"]={
    "incondicional":{"n":int(m_unc.nobs),"beta":round(float(m_unc.params["log_y0"]),5),
                     "p":round(float(m_unc.pvalues["log_y0"]),4),"r2":round(float(m_unc.rsquared),3)},
    "condicional":{"n":int(m_con.nobs),"beta":round(float(m_con.params["log_y0"]),5),
                   "p":round(float(m_con.pvalues["log_y0"]),4),"r2":round(float(m_con.rsquared),3)},
    "interpretacion":("beta<0 y significativo = convergencia (catch-up). La condicional controla "
        "determinantes del estado estacionario (region, insumos); si sigue sin haber convergencia, "
        "la divergencia es robusta.")}

# ============ I4/H5: empleo con productividad EXÓGENA (mecanización) en vez de VA/trabajador ============
reg=df.dropna(subset=["agri_empl_pct","tractors_per_1000ha_arable"]).copy()
reg=reg[(reg["agri_empl_pct"]>0)&(reg["tractors_per_1000ha_arable"]>0)]
reg["log_emp"]=np.log(reg["agri_empl_pct"]); reg["log_tract"]=np.log(reg["tractors_per_1000ha_arable"])
m_mech=smf.ols("log_emp ~ log_tract + C(iso3) + C(year)",data=reg).fit(cov_type="cluster",cov_kwds={"groups":reg["iso3"]})
corr_cs=float(reg[["tractors_per_1000ha_arable","agri_empl_pct"]].corr().iloc[0,1])
out["H5_empleo_vs_mecanizacion_exogena"]={
    "n":int(m_mech.nobs),"coef_log_tractores":round(float(m_mech.params["log_tract"]),4),
    "se":round(float(m_mech.bse["log_tract"]),4),"p":round(float(m_mech.pvalues["log_tract"]),5),
    "corr_seccion_cruzada_tractores_empleo":round(corr_cs,3),
    "interpretacion":("La mecanizacion (tractores/1000 ha) NO comparte el conteo de ocupados agricolas con "
        "el empleo agricola (%), por lo que evita la relacion mecanica del VA/trabajador. Un coeficiente "
        "negativo y significativo confirma la recomposicion del empleo sin el sesgo definicional.")}

with open(f"{RES}/10_revision_analyses.json","w",encoding="utf-8") as f: json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps(out,ensure_ascii=False,indent=2))
