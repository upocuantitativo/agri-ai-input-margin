# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 5 -- Macro trends and H2 descriptives -> results/04_macro_trends.json, figures 1-4
#
# Copied verbatim from the author's working tree (analysis/04_macro_trends.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/04_macro_trends.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""
04_macro_trends.py
Contrasta los claims macro del documento "Paralelismos":
 - produccion mundial de grandes grupos 1.800 -> 4.600 Mt
 - desaceleracion del crecimiento del rendimiento cereal (3,2%/anio -> 1,5%/anio)
 - mecanizacion en Espana (ha por tractor)
 - rendimientos decrecientes del nitrogeno (productividad parcial del N)
"""
import os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROC = "data/processed"; FIG = "figures"; RES = "results"
os.makedirs(FIG, exist_ok=True); os.makedirs(RES, exist_ok=True)
plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                     "grid.alpha": .3, "axes.spines.top": False, "axes.spines.right": False})
results = {}

def cagr(v0, v1, years):
    if v0 is None or v1 is None or v0 <= 0 or v1 <= 0 or years <= 0:
        return None
    return (v1 / v0) ** (1 / years) - 1

# ============ 1) Produccion mundial por gran grupo ============
prod = pd.read_csv(os.path.join(PROC, "world_production_long.csv"), encoding="utf-8")
prod = prod.dropna(subset=["Value", "Year"])
groups = {
    "Cereals, primary": "Cereales",
    "Roots and Tubers, Total": "Raices y tuberculos",
    "Pulses, Total": "Legumbres",
    "Oilcrops, Oil Equivalent": "Oleaginosas (eq. aceite)",
}
gdf = prod[prod["Item"].isin(groups.keys())].copy()
piv = gdf.pivot_table(index="Year", columns="Item", values="Value", aggfunc="sum")
# total de los 4 grupos comparables al claim FAO (cereales+raices+legumbres+oleaginosas)
# usamos cereales+raices+legumbres en peso primario; oleaginosas en eq. aceite es menor:
core3 = [c for c in ["Cereals, primary", "Roots and Tubers, Total", "Pulses, Total"] if c in piv.columns]
piv["TOTAL_core3_Mt"] = piv[core3].sum(axis=1) / 1e6   # toneladas -> millones de t
piv["Cereals_Mt"] = piv["Cereals, primary"] / 1e6 if "Cereals, primary" in piv else np.nan

y0, y1 = int(piv.index.min()), int(piv.index.max())
prod_first = float(piv.loc[y0, "TOTAL_core3_Mt"])
prod_last = float(piv.loc[y1, "TOTAL_core3_Mt"])
results["produccion_mundial"] = {
    "claim_documento": "1.800 -> 4.600 millones t (cereales+raices/tuberculos+legumbres+oleaginosas)",
    "anio_inicial": y0, "anio_final": y1,
    "total_core3_inicial_Mt": round(prod_first, 1),
    "total_core3_final_Mt": round(prod_last, 1),
    "cereales_inicial_Mt": round(float(piv.loc[y0, "Cereals_Mt"]), 1),
    "cereales_final_Mt": round(float(piv.loc[y1, "Cereals_Mt"]), 1),
    "factor_multiplicador_core3": round(prod_last / prod_first, 2),
}

fig, ax = plt.subplots(figsize=(7, 4.2))
for item, lab in groups.items():
    if item in piv.columns:
        ax.plot(piv.index, piv[item] / 1e6, label=lab, lw=1.8)
ax.plot(piv.index, piv["TOTAL_core3_Mt"], label="Total (cereales+raíces+legumbres)", lw=2.5, color="k", ls="--")
ax.set_xlabel("Año"); ax.set_ylabel("Producción mundial (millones t)")
ax.set_title("Producción agroalimentaria mundial por gran grupo de cultivo (FAOSTAT)")
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_produccion_mundial.png")); plt.close(fig)

# ============ 2) Desaceleracion del rendimiento cereal mundial ============
yld = pd.read_csv(os.path.join(PROC, "world_yield_long.csv"), encoding="utf-8")
cyld = yld[(yld["Item"] == "Cereals, primary") & (yld["Element"] == "Yield")].dropna(subset=["Value", "Year"])
cyld = cyld.groupby("Year", as_index=False)["Value"].mean().sort_values("Year")
cyld["Year"] = cyld["Year"].astype(int)
# CAGR por decada
decades = [(1961, 1970), (1971, 1980), (1981, 1990), (1991, 2000), (2001, 2010), (2011, 2023)]
dec_rows = []
for a, b in decades:
    sub = cyld[(cyld["Year"] >= a) & (cyld["Year"] <= b)]
    if len(sub) >= 2:
        v0 = sub.iloc[0]["Value"]; v1 = sub.iloc[-1]["Value"]
        n = sub.iloc[-1]["Year"] - sub.iloc[0]["Year"]
        # tasa por regresion log-lineal (mas robusta)
        slope = np.polyfit(sub["Year"], np.log(sub["Value"]), 1)[0]
        dec_rows.append({"decada": f"{a}-{b}", "cagr_endpoints_%": round(100*cagr(v0, v1, n), 2),
                         "tasa_loglineal_%/anio": round(100*slope, 2)})
results["rendimiento_cereal_mundial"] = {
    "claim_documento": "crecimiento del rendimiento cereal se desacelero de 3,2%/anio (1960) a 1,5%/anio (2000)",
    "unidad": str(cyld_unit) if (cyld_unit := yld[yld['Item']=='Cereals, primary']['Unit'].dropna().iloc[0]) else "",
    "por_decada": dec_rows,
}
# rolling 15-anios growth
cyld["logy"] = np.log(cyld["Value"])
cyld["roll_growth_%"] = cyld["logy"].diff().rolling(10, center=True).mean() * 100

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
ax[0].plot(cyld["Year"], cyld["Value"], color="seagreen", lw=2)  # FAOSTAT Value ya viene en kg/ha (verificado en Unit)
ax[0].set_title("Rendimiento cereal mundial"); ax[0].set_xlabel("Año"); ax[0].set_ylabel("kg/ha")
ax[1].plot(cyld["Year"], cyld["roll_growth_%"], color="firebrick", lw=2)
ax[1].axhline(0, color="gray", lw=.8)
ax[1].set_title("Tasa de crecimiento anual (media móvil 10 años)")
ax[1].set_xlabel("Año"); ax[1].set_ylabel("%/año")
fig.suptitle("Desaceleración del crecimiento del rendimiento cerealista (FAOSTAT)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig2_desaceleracion_rendimiento.png")); plt.close(fig)

# ============ 3) Mecanizacion Espana ============
esp = pd.read_csv(os.path.join(PROC, "spain_series.csv"), encoding="utf-8")
esp = esp.sort_values("year")
esp["ha_por_tractor"] = (esp["arable_kha"] * 1000) / esp["tractors"]
mech = esp.dropna(subset=["tractors", "arable_kha"])[["year", "tractors", "arable_kha", "ha_por_tractor"]]
def val_at(df, col, yr):
    s = df[df["year"] == yr]
    return float(s[col].iloc[0]) if len(s) else None
results["mecanizacion_espana"] = {
    "claim_documento": "600 ha/tractor (1958) -> ~50 ha/tractor (finales 70s); FAOSTAT tractores desde 1961",
    "ha_por_tractor_1961": round(val_at(mech, "ha_por_tractor", 1961), 0) if val_at(mech, "ha_por_tractor", 1961) else None,
    "ha_por_tractor_1978": round(val_at(mech, "ha_por_tractor", 1978), 0) if val_at(mech, "ha_por_tractor", 1978) else None,
    "ha_por_tractor_2009": round(val_at(mech, "ha_por_tractor", 2009), 0) if val_at(mech, "ha_por_tractor", 2009) else None,
    "tractores_1961": val_at(mech, "tractors", 1961),
    "tractores_2009": val_at(mech, "tractors", 2009),
}
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(mech["year"], mech["ha_por_tractor"], color="darkorange", lw=2, marker="o", ms=3)
ax.set_yscale("log")
ax.set_title("España: hectáreas de tierra arable por tractor (FAOSTAT, 1961-2009)")
ax.set_xlabel("Año"); ax.set_ylabel("ha arable / tractor (log)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig3_mecanizacion_espana.png")); plt.close(fig)

# ============ 4) Rendimientos decrecientes del nitrogeno (mundo) ============
wn = pd.read_csv(os.path.join(PROC, "world_N.csv"), encoding="utf-8")  # n_total_t_world
mn = wn.merge(cyld[["Year", "Value"]].rename(columns={"Year": "year", "Value": "cereal_yield_kg_ha"}),
              on="year", how="inner").dropna()
# FAOSTAT Value ya viene en kg/ha (Unit='kg/ha' verificado); no dividir por 10
# productividad parcial: rendimiento por unidad de N total (proxy escala mundial)
mn["yield_per_Mt_N"] = mn["cereal_yield_kg_ha"] / (mn["n_total_t_world"] / 1e6)
res_N = {
    "claim_documento": "rendimientos decrecientes / efecto rebote: mas insumos con retornos marginales menores",
    "N_mundial_inicial_Mt": round(float(mn["n_total_t_world"].iloc[0]) / 1e6, 1),
    "N_mundial_final_Mt": round(float(mn["n_total_t_world"].iloc[-1]) / 1e6, 1),
    "anio_ini": int(mn["year"].iloc[0]), "anio_fin": int(mn["year"].iloc[-1]),
}
# correlacion rendimiento ~ log(N) y curvatura
import numpy as np
x = np.log(mn["n_total_t_world"]); y = mn["cereal_yield_kg_ha"]
b1 = np.polyfit(x, y, 1); res_N["pendiente_rendimiento_vs_logN"] = round(float(b1[0]), 1)
res_N["productividad_parcial_N_ini"] = round(float(mn["yield_per_Mt_N"].iloc[0]), 3)
res_N["productividad_parcial_N_fin"] = round(float(mn["yield_per_Mt_N"].iloc[-1]), 3)
results["nitrogeno_rendimientos_decrecientes"] = res_N

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
ax[0].plot(mn["n_total_t_world"]/1e6, mn["cereal_yield_kg_ha"], color="purple", lw=1.6, marker=".")
ax[0].set_xlabel("Uso mundial de N (millones t)"); ax[0].set_ylabel("Rendimiento cereal (kg/ha)")
ax[0].set_title("Rendimiento vs nitrógeno aplicado (curva de respuesta)")
ax[1].plot(mn["year"], mn["yield_per_Mt_N"], color="teal", lw=2)
ax[1].set_xlabel("Año"); ax[1].set_ylabel("kg/ha por Mt de N")
ax[1].set_title("Productividad parcial del nitrógeno (decreciente)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig4_nitrogeno.png")); plt.close(fig)

# guardar
with open(os.path.join(RES, "04_macro_trends.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(json.dumps(results, ensure_ascii=False, indent=2))
print("\nFiguras: fig1..fig4 guardadas.")
