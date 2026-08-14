# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Replication package: agri-ai-input-margin
# Pipeline step 12 -- AI block HA1-HA5 + robustness -> results/12_ai_observable.json, figures 11-15
#
# Copied verbatim from the author's working tree (analysis/12_ai_observable.py); this header
# comment is the only modification. Run from the REPOSITORY ROOT, e.g.
#     python code/12_ai_observable.py
# because some scripts resolve paths relative to the working directory and
# others relative to their own location; both conventions resolve correctly
# only when the working directory is the repository root.
# ---------------------------------------------------------------------------
"""
12_ai_observable.py

RESPUESTA DIRECTA A LA CRITICA DEL REVISOR.

  (i) "Sin una variable de IA observable, el estudio no puede aislar el efecto
       especifico de la IA, lo que hace incontrastable la tesis central."
  (ii) "La conclusion se extiende a cualquier tecnologia emergente en vez de
        ofrecer una idea especifica y novedosa sobre la IA."

Se construye una variable de IA OBSERVABLE pais-anio (2000-2024) y se contrasta
una tesis ESPECIFICA de la IA: a diferencia de las oleadas incorporadas, cuyo
valor se manifesto en el NIVEL de produccion, el valor de la IA se manifiesta en
el MARGEN DE INSUMOS -misma cosecha con menos insumos- y ese margen es el que
depende de los complementos.

Bloques:
  A    Descriptivos de la variable de IA observable.
  HA1  Efecto INCONDICIONAL de la IA sobre el rendimiento (narrativa
       algoritmo-centrica): FE dos vias.
  HA2  DONDE aparece el valor: descomposicion del margen (rendimiento / N / NUE)
       y condicionamiento a complementos PREDETERMINADOS (2000-2005).
  HA3  TEST DIFERENCIAL entre oleadas: fertilizante, mecanizacion, IA y un
       placebo de investigacion no-IA. Si la dependencia de complementos fuese
       generica, el patron seria el mismo en las cuatro.
  HA4  DiD de tratamiento continuo (exposicion pre-2016 x post-2016), estudio de
       eventos y comparacion EN PARALELO de las ganancias por era.
  HA5  NO TRANSFERIBILIDAD como propiedad especifica de la funcion aprendida.
  ROB  Robustez: exposicion alternativa, anios de corte, exclusion de CHN/IND/USA,
       control de renta y exposicion placebo.

Salida: results/12_ai_observable.json + figures/fig11-fig14.
"""
import os, json, warnings
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats as st
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import r2_score

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
PROC = os.path.join(HERE, "..", "data", "processed")
RES = os.path.join(HERE, "..", "results")
FIG = os.path.join(HERE, "..", "figures")
os.makedirs(RES, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

COMP_VARS = ["internet_users_pct", "broadband_per100", "mobile_subs_per100",
             "tertiary_enrol_pct", "electricity_rural_pct"]
R = {}


def z(s):
    s = pd.to_numeric(s, errors="coerce")
    return (s - s.mean()) / s.std(ddof=0)


def fe_ols(df, formula, cluster="iso3"):
    return smf.ols(formula, data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df[cluster]})


def coef(m, name):
    if name not in m.params.index:
        return None
    return {"b": float(m.params[name]), "se": float(m.bse[name]),
            "t": float(m.tvalues[name]), "p": float(m.pvalues[name])}


def marginal(m, main, inter, levels):
    """Efecto marginal de `main` a distintos valores del moderador."""
    V = m.cov_params()
    b1, b3 = m.params[main], m.params[inter]
    out = {}
    for k, c in levels.items():
        est = b1 + b3 * c
        var = (V.loc[main, main] + c**2 * V.loc[inter, inter]
               + 2 * c * V.loc[main, inter])
        se = float(np.sqrt(max(var, 0)))
        t = float(est / se) if se else np.nan
        out[k] = {"moderador": float(c), "efecto_marginal": float(est),
                  "se": se, "t": t, "p": float(2 * (1 - st.norm.cdf(abs(t))))}
    return out


# =========================================================== carga y montaje
def load():
    cp = pd.read_csv(os.path.join(PROC, "country_panel.csv"))
    ai = pd.read_csv(os.path.join(PROC, "ai_panel.csv"))
    meta = pd.read_csv(os.path.join(PROC, "country_meta.csv"))
    df = cp.merge(ai, on=["iso3", "year"], how="left")
    df = df.merge(meta[["iso3", "region", "income"]], on="iso3", how="left")

    # ---- variable de IA OBSERVABLE ---------------------------------------
    # Dos medidas complementarias:
    #   VOLUMEN        obras de IA agricola por millon de habitantes
    #   ESPECIALIZACION cuota (por mil) de la produccion cientifica nacional
    #                   dedicada a IA agricola -> practicamente ortogonal al
    #                   tamano del sistema de investigacion, y por tanto la
    #                   medida que identifica algo especifico de la IA
    df["pop_mn"] = df["population"] / 1e6
    df["ai_ag_pc"] = df["oa_ai_ag"] / df["pop_mn"]
    df["pa_pc"] = df["oa_precision_ag"] / df["pop_mn"]
    df["ai_ag_share"] = 1000 * df["oa_ai_ag"] / df["oa_works_all"].replace(0, np.nan)
    df["log_ai_ag"] = np.log1p(df["ai_ag_pc"])
    df["log_ai_spec"] = np.log1p(df["ai_ag_share"])
    df["log_pa"] = np.log1p(df["pa_pc"])
    df["log_nonai_res"] = np.log1p(
        (df["oa_works_all"] - df["oa_ai_all"]).clip(lower=0) / df["pop_mn"])

    # ---- resultado y insumos ---------------------------------------------
    df["log_yield"] = np.log(df["cereal_yield_kg_ha"].replace(0, np.nan))
    df["log_n"] = np.log1p(df["n_kg_ha"])
    df["log_p"] = np.log1p(df["p_kg_ha"])
    df["log_k"] = np.log1p(df["k_kg_ha"])
    df["log_area"] = np.log1p(df["arable_kha"])
    df["irr"] = df["irrig_share_cropland"]
    df["log_mech"] = np.log1p(df["tractors_per_1000ha_arable"])
    df["log_gdp"] = np.log(df["gdp_pc_const2015"].replace(0, np.nan))
    # eficiencia del nitrogeno: kg de grano por kg de N aplicado.
    # Se usan logaritmos EXACTOS (no log1p) para que la descomposicion del
    # margen sea aditiva por construccion: log_nue = log_yield - log_n_x
    df["nue"] = df["cereal_yield_kg_ha"] / df["n_kg_ha"].replace(0, np.nan)
    df.loc[df["n_kg_ha"] < 1, "nue"] = np.nan
    df["log_nue"] = np.log(df["nue"].replace(0, np.nan))
    df["log_n_x"] = np.where(df["n_kg_ha"] >= 1, np.log(df["n_kg_ha"]), np.nan)

    # ---- complementos PREDETERMINADOS (media 2000-2005) -------------------
    pre = (df[(df.year >= 2000) & (df.year <= 2005)][["iso3"] + COMP_VARS]
           .groupby("iso3").mean())
    pre["comp_pre"] = pre.apply(z).mean(axis=1)
    df = df.merge(pre[["comp_pre"]].reset_index(), on="iso3", how="left")

    # ---- exposicion PRE-tratamiento a la IA (media 2010-2015) -------------
    exp_ = (df[(df.year >= 2010) & (df.year <= 2015)]
            .groupby("iso3")["log_ai_ag"].mean().rename("exposure").reset_index())
    exp_pa = (df[(df.year >= 2010) & (df.year <= 2015)]
              .groupby("iso3")["log_pa"].mean().rename("exposure_pa").reset_index())
    exp_pl = (df[(df.year >= 2010) & (df.year <= 2015)]
              .groupby("iso3")["log_nonai_res"].mean()
              .rename("exposure_placebo").reset_index())
    for e in (exp_, exp_pa, exp_pl):
        df = df.merge(e, on="iso3", how="left")
    return df


# ============================================== (A) descriptivos de la IA
def block_A(df):
    d = df[(df.year >= 2000) & (df.year <= 2024)]
    world = d.groupby("year").agg(ai_ag=("oa_ai_ag", "sum"),
                                  pa=("oa_precision_ag", "sum"),
                                  allw=("oa_works_all", "sum")).reset_index()
    world["share_permil"] = 1000 * world.ai_ag / world.allw

    def g(a, b, col="ai_ag"):
        s = world[(world.year >= a) & (world.year <= b)]
        return float(np.polyfit(s.year, np.log(s[col]), 1)[0] * 100)

    late = d[(d.year >= 2019) & (d.year <= 2023)]
    by_inc = late.groupby("income")["ai_ag_pc"].median()

    R["A_descriptivos_IA"] = {
        "definicion": ("Obras indexadas en OpenAlex cuyo titulo o resumen combina "
                       "terminos de IA (artificial intelligence, machine learning, "
                       "deep learning, neural network) con terminos agricolas, "
                       "contadas por pais de afiliacion y anio (2000-2024)."),
        "obras_mundo_2000": int(world.loc[world.year == 2000, "ai_ag"].iloc[0]),
        "obras_mundo_2024": int(world.loc[world.year == 2024, "ai_ag"].iloc[0]),
        "multiplicador_2000_2024": float(world.loc[world.year == 2024, "ai_ag"].iloc[0]
                                         / world.loc[world.year == 2000, "ai_ag"].iloc[0]),
        "cuota_permil_2000": float(world.loc[world.year == 2000, "share_permil"].iloc[0]),
        "cuota_permil_2024": float(world.loc[world.year == 2024, "share_permil"].iloc[0]),
        "crecimiento_anual_pct_2000_2015": g(2000, 2015),
        "crecimiento_anual_pct_2016_2024": g(2016, 2024),
        "precision_ag_2000": int(world.loc[world.year == 2000, "pa"].iloc[0]),
        "precision_ag_2024": int(world.loc[world.year == 2024, "pa"].iloc[0]),
        "mediana_obras_por_millon_2019_2023_por_renta":
            {k: round(float(v), 4) for k, v in by_inc.items() if pd.notna(k)},
        "serie_mundial": world.to_dict("records"),
    }
    return world


# ============================ (HA1) efecto incondicional: narrativa algoritmica
def block_HA1(df):
    d = df[(df.year >= 2000) & (df.year <= 2023)].copy()
    need = ["log_yield", "log_ai_ag", "log_n", "log_p", "log_k", "irr",
            "log_area", "temp_anom"]
    d = d.dropna(subset=need).copy()
    d["z_ai"] = z(d["log_ai_ag"])
    m = fe_ols(d, "log_yield ~ z_ai + log_n + log_p + log_k + irr + log_area "
                  "+ temp_anom + C(iso3) + C(year)")
    R["HA1_efecto_incondicional_IA_sobre_rendimiento"] = {
        "n_obs": int(m.nobs), "n_paises": int(d.iso3.nunique()),
        "periodo": [int(d.year.min()), int(d.year.max())],
        "especificacion": "FE pais + FE anio, EE agrupados por pais, insumos controlados",
        "z_ai": coef(m, "z_ai"),
        "lectura": ("La narrativa algoritmo-centrica predice un efecto claro sobre "
                    "el NIVEL de rendimiento. El coeficiente es pequeno y fragil."),
    }
    return d


# ============ (HA2) donde aparece el valor: margen de insumos y complementos
def block_HA2(df):
    d = df[(df.year >= 2000) & (df.year <= 2023)].copy()
    d["z_ai"] = z(d["log_ai_ag"])         # volumen
    d["z_spec"] = z(d["log_ai_spec"])     # especializacion
    d["z_res"] = z(d["log_nonai_res"])    # capacidad investigadora general
    d["z_comp"] = z(d["comp_pre"])
    ctrl = "log_area + temp_anom + C(iso3) + C(year)"

    # MUESTRA COMUN a los tres margenes: la descomposicion es exactamente
    # aditiva (log_nue = log_yield - log_n_x) solo si la muestra es identica
    common = ["log_yield", "log_n_x", "log_nue", "z_ai", "z_spec", "z_res",
              "log_area", "temp_anom"]
    s = d.dropna(subset=common).copy()

    labels = {"log_yield": "rendimiento (nivel de produccion)",
              "log_n_x": "dosis de nitrogeno (insumo)",
              "log_nue": "eficiencia del nitrogeno (kg grano / kg N)"}
    out = {"muestra_comun": {"n_obs": int(len(s)), "n_paises": int(s.iso3.nunique()),
                             "periodo": [int(s.year.min()), int(s.year.max())]},
           "margen_volumen": {}, "margen_especializacion": {},
           "carrera_IA_vs_investigacion_general": {},
           "condicional_a_complementos": {}}

    for y in ["log_yield", "log_n_x", "log_nue"]:
        m = fe_ols(s, f"{y} ~ z_ai + {ctrl}")
        out["margen_volumen"][y] = {"etiqueta": labels[y], "z_ai": coef(m, "z_ai")}

        m1 = fe_ols(s, f"{y} ~ z_spec + {ctrl}")
        out["margen_especializacion"][y] = {"etiqueta": labels[y],
                                            "z_spec": coef(m1, "z_spec")}

        # carrera de caballos: la especializacion en IA frente a la capacidad
        # investigadora general (test de que el efecto es ESPECIFICO de la IA)
        m2 = fe_ols(s, f"{y} ~ z_spec + z_res + {ctrl}")
        out["carrera_IA_vs_investigacion_general"][y] = {
            "etiqueta": labels[y], "z_spec": coef(m2, "z_spec"),
            "z_res_investigacion_no_IA": coef(m2, "z_res")}

        # condicional a complementos predeterminados
        m3 = fe_ols(s, f"{y} ~ z_spec + z_spec:z_comp + {ctrl}")
        lv = {"p10": s.z_comp.quantile(.10), "p50": s.z_comp.quantile(.50),
              "p90": s.z_comp.quantile(.90)}
        out["condicional_a_complementos"][y] = {
            "etiqueta": labels[y], "z_spec": coef(m3, "z_spec"),
            "interaccion": coef(m3, "z_spec:z_comp"),
            "efectos_marginales": marginal(m3, "z_spec", "z_spec:z_comp", lv)}

    out["correlacion_especializacion_vs_investigacion_general"] = float(
        s[["z_spec", "z_res"]].corr().iloc[0, 1])
    out["identidad_contable"] = ("log_nue = log_yield - log_n_x, de modo que el "
                                 "efecto sobre la eficiencia es exactamente la "
                                 "diferencia entre el efecto sobre el producto y "
                                 "el efecto sobre el insumo.")
    out["nota_complementos"] = ("Complementos PREDETERMINADOS: media 2000-2005 de "
                                "internet, banda ancha, movil, matricula terciaria "
                                "y electrificacion rural, anteriores a la "
                                "irrupcion de la IA de 2016.")
    out["lectura"] = ("El valor de la IA no aparece como un salto en el nivel de "
                      "rendimiento sino en el margen de eficiencia; el ahorro de "
                      "insumos es la parte que depende de los complementos.")
    R["HA2_margen_de_valor_y_complementariedad"] = out
    return d


# ===================== (HA3) test diferencial entre oleadas tecnologicas
def block_HA3(df):
    out = {}

    def wave(d, tech, comps, years, controls, outcome="log_yield"):
        s = d[(d.year >= years[0]) & (d.year <= years[1])].copy()
        s["z_comp"] = s[comps].apply(z).mean(axis=1, skipna=True)
        s["z_tech"] = z(s[tech])
        need = [outcome, "z_tech", "z_comp", "iso3", "year"] + controls
        s = s.dropna(subset=need)
        if len(s) < 200:
            return None
        f = (f"{outcome} ~ z_tech * z_comp + " + " + ".join(controls)
             + " + C(iso3) + C(year)")
        m = fe_ols(s, f)
        b1 = float(m.params["z_tech"]); b3 = float(m.params["z_tech:z_comp"])
        return {"periodo": list(years), "resultado": outcome,
                "n_obs": int(m.nobs), "n_paises": int(s.iso3.nunique()),
                "tecnologia": tech, "complementos": comps,
                "efecto_medio_z_tech": coef(m, "z_tech"),
                "interaccion": coef(m, "z_tech:z_comp"),
                "efecto_marginal_complementos_bajos_-1SD": b1 - b3,
                "efecto_marginal_complementos_altos_+1SD": b1 + b3,
                "dependencia_complementos_b3_entre_b1": (b3 / b1) if b1 else None}

    d = df.copy()
    base_ctrl = ["log_p", "log_k", "log_area", "temp_anom"]
    ai_ctrl = ["log_n", "log_p", "log_k", "irr", "log_area", "temp_anom"]

    out["oleada_fertilizante_1961_1990"] = wave(
        d, "log_n", ["irr", "log_mech"], (1961, 1990), base_ctrl)
    out["oleada_mecanizacion_1961_2009"] = wave(
        d, "log_mech", ["irr", "log_n"], (1961, 2009), base_ctrl)
    out["oleada_IA_2000_2023"] = wave(
        d, "log_ai_ag", COMP_VARS, (2000, 2023), ai_ctrl)
    out["placebo_investigacion_no_IA_2000_2023"] = wave(
        d, "log_nonai_res", COMP_VARS, (2000, 2023), ai_ctrl)

    # el mismo test sobre el MARGEN DE INSUMOS (eficiencia del nitrogeno)
    out["margen_insumos_NUE"] = {
        "oleada_fertilizante_1961_1990": wave(
            d, "log_n", ["irr", "log_mech"], (1961, 1990),
            ["log_area", "temp_anom"], outcome="log_nue"),
        "oleada_IA_2000_2023": wave(
            d, "log_ai_ag", COMP_VARS, (2000, 2023),
            ["log_area", "temp_anom"], outcome="log_nue"),
    }

    out["comparacion_dependencia"] = {
        k: v["dependencia_complementos_b3_entre_b1"]
        for k, v in out.items() if isinstance(v, dict) and "interaccion" in v}
    out["lectura"] = ("Si 'el valor esta en los complementos' fuese generico a "
                      "cualquier tecnologia, el signo y la magnitud de la "
                      "dependencia serian equivalentes en las cuatro columnas. "
                      "Las oleadas incorporadas y el placebo muestran dependencia "
                      "POSITIVA sobre el nivel de rendimiento; la IA la muestra "
                      "NEGATIVA sobre el nivel y POSITIVA sobre el ahorro de "
                      "insumos: es un patron especifico, no generico.")
    R["HA3_test_diferencial_entre_oleadas"] = out
    return out


# ============ (HA4) DiD de tratamiento continuo + comparacion por eras
def block_HA4(df):
    d = df[(df.year >= 2000) & (df.year <= 2023)].copy()
    # exposicion PREDETERMINADA por especializacion en IA agricola (2010-2015)
    sp = (d[(d.year >= 2010) & (d.year <= 2015)].groupby("iso3")
          .apply(lambda g: 1000 * g.oa_ai_ag.sum() / max(g.oa_works_all.sum(), 1))
          .rename("exposure_spec").reset_index())
    d = d.merge(sp, on="iso3", how="left")
    d["z_exp"] = z(np.log1p(d["exposure_spec"]))
    d["z_res"] = z(d["exposure_placebo"])
    d["post"] = (d.year >= 2016).astype(int)
    ctrl = "log_area + temp_anom + C(iso3) + C(year)"
    res = {}
    labels = {"log_yield": "rendimiento (log)", "log_n_x": "dosis de N (log)",
              "log_nue": "eficiencia del N (log)"}

    common = ["log_yield", "log_n_x", "log_nue", "z_exp", "z_res",
              "log_area", "temp_anom"]
    base = d.dropna(subset=common).copy()

    for y in ["log_yield", "log_n_x", "log_nue"]:
        m = fe_ols(base, f"{y} ~ z_exp:post + {ctrl}")
        k = [x for x in m.params.index if "z_exp" in x][0]
        # con control de capacidad investigadora general
        m_hr = fe_ols(base, f"{y} ~ z_exp:post + z_res:post + {ctrl}")
        k1 = [x for x in m_hr.params.index if "z_exp" in x][0]
        k2 = [x for x in m_hr.params.index if "z_res" in x][0]
        res[y] = {"etiqueta": labels[y], "n_obs": int(m.nobs),
                  "n_paises": int(base.iso3.nunique()),
                  "DiD_exposicion_x_post2016": coef(m, k),
                  "DiD_controlando_investigacion_general": {
                      "IA": coef(m_hr, k1), "investigacion_no_IA": coef(m_hr, k2)}}
        # ---- estudio de eventos, base 2015 --------------------------------
        # La exposicion es invariante en el tiempo y queda absorbida por los FE
        # de pais, de modo que las 18 interacciones estarian identificadas en
        # NIVEL y no en desviacion. Se omite explicitamente el anio base para
        # que los coeficientes se lean como desviaciones respecto a 2015.
        s2 = base[base.year >= 2006].copy()
        BASE_YR, cols = 2015, []
        for yr in sorted(s2.year.unique()):
            if yr == BASE_YR:
                continue
            c = f"ev_{yr}"
            s2[c] = s2["z_exp"] * (s2["year"] == yr).astype(float)
            cols.append(c)
        try:
            m2 = fe_ols(s2, f"{y} ~ " + " + ".join(cols) +
                        " + log_area + temp_anom + C(iso3) + C(year)")
            ev = {int(c.split("_")[1]): {"b": float(m2.params[c]),
                                         "se": float(m2.bse[c]),
                                         "p": float(m2.pvalues[c])}
                  for c in cols if c in m2.params.index}
            res[y]["estudio_de_eventos"] = dict(sorted(ev.items()))
            pre_p = [v["p"] for yr, v in ev.items() if yr < BASE_YR]
            res[y]["pre_tendencia_min_p_antes_de_2015"] = (
                float(min(pre_p)) if pre_p else None)
            res[y]["pre_tendencia_n_significativos_antes_de_2015"] = int(
                sum(1 for p in pre_p if p < 0.05))
        except Exception as e:
            res[y]["estudio_de_eventos_error"] = str(e)

    # ---------------- comparacion EN PARALELO de las ganancias por era -------
    full = df.dropna(subset=["cereal_yield_kg_ha"]).copy()
    w = (full.groupby("year")
         .apply(lambda g: np.average(g.cereal_yield_kg_ha,
                                     weights=g.cereal_area_ha.fillna(0) + 1e-9))
         .rename("yield_w").reset_index())
    nu = (full.dropna(subset=["nue"]).groupby("year")["nue"]
          .median().rename("nue_med").reset_index())
    nw = (full.dropna(subset=["n_kg_ha"]).groupby("year")["n_kg_ha"]
          .median().rename("n_med").reset_index())

    def rate(a, b, s, col):
        x = s[(s.year >= a) & (s.year <= b)].dropna(subset=[col])
        x = x[x[col] > 0]
        return float(np.polyfit(x.year, np.log(x[col]), 1)[0] * 100) if len(x) >= 5 else None

    eras = [("revolucion_verde_1961_1990", 1961, 1990),
            ("post_revolucion_verde_1991_2015", 1991, 2015),
            ("era_IA_2016_2023", 2016, 2023)]
    R["HA4_DiD_y_comparacion_de_eras"] = {
        "definicion_exposicion": ("especializacion predeterminada: cuota (por mil) "
                                  "de la produccion cientifica nacional dedicada a "
                                  "IA agricola en 2010-2015, previa al corte"),
        "corte": 2016,
        "DiD": res,
        "crecimiento_anual_pct_por_era": {
            "rendimiento_cereal_mundial": {k: rate(a, b, w, "yield_w") for k, a, b in eras},
            "eficiencia_del_nitrogeno_mediana": {k: rate(a, b, nu, "nue_med") for k, a, b in eras},
            "dosis_de_nitrogeno_mediana": {k: rate(a, b, nw, "n_med") for k, a, b in eras},
        },
        "veredicto_pretendencias": (
            "FALLA. El estudio de eventos normalizado a 2015 muestra "
            "coeficientes previos significativos (4 de 9 en la dosis de N) y "
            "ausencia de salto posterior a 2016. El DiD NO admite lectura "
            "causal: se reporta como asociacion descriptiva. La evidencia "
            "especifica de la IA descansa en la estructura de "
            "complementariedad de HA2, no en este corte temporal."),
        "lectura": ("Comparacion en paralelo: la Revolucion Verde compro "
                    "rendimiento a costa de la eficiencia de insumos; la era de la "
                    "IA muestra la imagen especular -sin aceleracion del "
                    "rendimiento pero con la mayor mejora de eficiencia del "
                    "periodo-. La comparacion de eras es descriptiva."),
    }
    return d


# ============ (HA5) no transferibilidad de la funcion aprendida
def block_HA5(df):
    d = df.dropna(subset=["log_yield", "log_n", "log_p", "log_k", "irr",
                          "log_area", "temp_anom", "region"]).copy()
    feats = ["log_n", "log_p", "log_k", "irr", "log_area", "temp_anom"]
    regions = [r for r in d.region.dropna().unique() if (d.region == r).sum() >= 300]

    mat, diag, off = {}, [], []
    for tr in regions:
        A = d[d.region == tr]
        mdl = HistGradientBoostingRegressor(random_state=0, max_iter=300)
        mdl.fit(A[feats], A["log_yield"])
        mat[tr] = {}
        for te in regions:
            if tr == te:
                trn, tst = A[A.year <= 2009], A[A.year >= 2010]
                if len(tst) < 50:
                    continue
                m2 = HistGradientBoostingRegressor(random_state=0, max_iter=300)
                m2.fit(trn[feats], trn["log_yield"])
                r2 = r2_score(tst["log_yield"], m2.predict(tst[feats]))
                diag.append(r2)
            else:
                B = d[d.region == te]
                r2 = r2_score(B["log_yield"], mdl.predict(B[feats]))
                off.append(r2)
            mat[tr][te] = float(r2)

    el = {}
    for r in regions:
        s = d[d.region == r]
        try:
            m = smf.ols("log_yield ~ log_n + log_p + log_k + irr + log_area "
                        "+ temp_anom + C(year)", data=s).fit()
            el[r] = float(m.params["log_n"])
        except Exception:
            pass

    R["HA5_no_transferibilidad_de_la_funcion_aprendida"] = {
        "matriz_R2_entrenar_en_fila_evaluar_en_columna": mat,
        "R2_medio_misma_region_holdout_temporal": float(np.mean(diag)) if diag else None,
        "R2_medio_otra_region": float(np.mean(off)) if off else None,
        "caida_absoluta_R2": float(np.mean(diag) - np.mean(off)) if diag and off else None,
        "n_regiones": len(regions),
        "elasticidad_del_nitrogeno_por_region": el,
        "rango_elasticidad_N": [float(min(el.values())), float(max(el.values()))] if el else None,
        "lectura": ("Un artefacto incorporado conserva su productividad al cruzar "
                    "una frontera; una funcion aprendida no, porque su rendimiento "
                    "depende del entorno de datos que la genero. La heterogeneidad "
                    "de la funcion de respuesta a insumos entre regiones es la "
                    "causa mecanica de esa no transferibilidad."),
    }
    return mat


# ================================================================ robustez
def block_ROB(df):
    d = df[(df.year >= 2000) & (df.year <= 2023)].copy()
    ctrl = "log_area + temp_anom + C(iso3) + C(year)"
    out = {}

    def did(s, expcol, cut, extra=""):
        s = s.copy()
        s["z_e"] = z(s[expcol]); s["post"] = (s.year >= cut).astype(int)
        s = s.dropna(subset=["log_nue", "z_e", "log_area", "temp_anom"])
        m = fe_ols(s, f"log_nue ~ z_e:post + {ctrl}{extra}")
        k = [x for x in m.params.index if "z_e" in x][0]
        return {"n_obs": int(m.nobs), **coef(m, k)}

    sp = (d[(d.year >= 2010) & (d.year <= 2015)].groupby("iso3")
          .apply(lambda g: 1000 * g.oa_ai_ag.sum() / max(g.oa_works_all.sum(), 1))
          .rename("exposure_spec").reset_index())
    d = d.merge(sp, on="iso3", how="left")
    d["exposure_spec"] = np.log1p(d["exposure_spec"])

    out["base_NUE_especializacion_corte2016"] = did(d, "exposure_spec", 2016)
    out["exposicion_por_volumen"] = did(d, "exposure", 2016)
    out["exposicion_alternativa_agricultura_de_precision"] = did(d, "exposure_pa", 2016)
    out["placebo_exposicion_investigacion_no_IA"] = did(d, "exposure_placebo", 2016)
    out["corte_2015"] = did(d, "exposure_spec", 2015)
    out["corte_2017"] = did(d, "exposure_spec", 2017)
    out["sin_CHN_IND_USA"] = did(d[~d.iso3.isin(["CHN", "IND", "USA"])],
                                 "exposure_spec", 2016)
    out["controlando_renta_pc"] = did(d.dropna(subset=["log_gdp"]),
                                      "exposure_spec", 2016, extra=" + log_gdp")
    out["controlando_tendencias_por_region"] = did(
        d.dropna(subset=["region"]), "exposure_spec", 2016, extra=" + C(region):year")
    out["lectura"] = ("El efecto sobre la eficiencia del nitrogeno sobrevive a los "
                      "anios de corte, a la exclusion de los tres mayores "
                      "productores, al control de renta y a tendencias por region. "
                      "La exposicion placebo (investigacion no-IA) tiene tambien "
                      "efecto propio: la atribucion especifica a la IA descansa en "
                      "la carrera de caballos de HA2, no en este bloque.")
    R["ROB_robustez"] = out
    return out


# ================================================================== figuras
def figures(world):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # fig11 - irrupcion de la IA agricola
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].plot(world.year, world.ai_ag, marker="o", ms=3, color="#1f4e79")
    ax[0].set_yscale("log")
    ax[0].set_title("AI-in-agriculture publications (world)")
    ax[0].set_xlabel("Year"); ax[0].set_ylabel("Works (log scale)")
    ax[0].axvline(2016, ls="--", c="grey", lw=1); ax[0].grid(alpha=.3)
    ax[1].plot(world.year, world.share_permil, marker="s", ms=3, color="#c0504d")
    ax[1].set_title("Share of world research output (per 1,000 works)")
    ax[1].set_xlabel("Year"); ax[1].set_ylabel("Per 1,000")
    ax[1].axvline(2016, ls="--", c="grey", lw=1); ax[1].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig11_ai_emergence.png"), dpi=200)
    plt.close(fig)

    # fig12 - donde aparece el valor de la IA (margen) y su condicionalidad
    h = R["HA2_margen_de_valor_y_complementariedad"]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    ys = ["log_yield", "log_n_x", "log_nue"]
    labs = ["Yield\n(output level)", "Nitrogen dose\n(input)", "Nitrogen efficiency\n(output/input)"]
    b = [h["margen_especializacion"][y]["z_spec"]["b"] for y in ys]
    se = [h["margen_especializacion"][y]["z_spec"]["se"] for y in ys]
    cols = ["#8fa9c4", "#c0504d", "#1f4e79"]
    ax[0].bar(labs, b, yerr=[1.96 * x for x in se], capsize=5, color=cols)
    ax[0].axhline(0, c="k", lw=.8)
    ax[0].set_ylabel("Effect of +1 SD of AI specialisation (log points)")
    ax[0].set_title("Where the value of AI shows up")
    ax[0].grid(alpha=.3, axis="y")
    mg = h["condicional_a_complementos"]["log_n_x"]["efectos_marginales"]
    ks = ["p10", "p50", "p90"]
    bb = [mg[k]["efecto_marginal"] for k in ks]
    ss = [mg[k]["se"] for k in ks]
    ax[1].errorbar(range(3), bb, yerr=[1.96 * x for x in ss], fmt="o", ms=7,
                   capsize=5, color="#c0504d")
    ax[1].axhline(0, c="k", lw=.8)
    ax[1].set_xticks(range(3))
    ax[1].set_xticklabels(["Low\ncomplements", "Median", "High\ncomplements"])
    ax[1].set_ylabel("Effect of AI on nitrogen dose (log points)")
    ax[1].set_title("Input saving requires complements")
    ax[1].grid(alpha=.3, axis="y")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig12_ai_margin.png"), dpi=200)
    plt.close(fig)

    # fig13 - dependencia de complementos por oleada
    h3 = R["HA3_test_diferencial_entre_oleadas"]
    lab = {"oleada_fertilizante_1961_1990": "Fertiliser\n1961-1990",
           "oleada_mecanizacion_1961_2009": "Mechanisation\n1961-2009",
           "oleada_IA_2000_2023": "AI\n2000-2023",
           "placebo_investigacion_no_IA_2000_2023": "Placebo:\nnon-AI research"}
    ks = [k for k in lab if h3.get(k)]
    vals = [h3[k]["interaccion"]["b"] for k in ks]
    errs = [1.96 * h3[k]["interaccion"]["se"] for k in ks]
    cols = ["#8fa9c4", "#8fa9c4", "#c0504d", "#bdbdbd"]
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    ax.bar([lab[k] for k in ks], vals, yerr=errs, capsize=5,
           color=[cols[list(lab).index(k)] for k in ks])
    ax.axhline(0, c="k", lw=.8)
    ax.set_ylabel("Technology x complements interaction\n(effect on log yield)")
    ax.set_title("Is complement dependence generic? Waves compared")
    ax.grid(alpha=.3, axis="y")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig13_wave_comparison.png"), dpi=200)
    plt.close(fig)

    # fig14 - ganancias por era
    e = R["HA4_DiD_y_comparacion_de_eras"]["crecimiento_anual_pct_por_era"]
    labs = ["Green Revolution\n1961-1990", "Post-GR\n1991-2015", "AI era\n2016-2023"]
    x = np.arange(3); wdt = .38
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    ax.bar(x - wdt/2, list(e["rendimiento_cereal_mundial"].values()), wdt,
           label="Cereal yield", color="#1f4e79")
    ax.bar(x + wdt/2, list(e["eficiencia_del_nitrogeno_mediana"].values()), wdt,
           label="Nitrogen use efficiency", color="#c0504d")
    ax.set_xticks(x); ax.set_xticklabels(labs)
    ax.axhline(0, c="k", lw=.8); ax.set_ylabel("Annual growth (%)")
    ax.set_title("Gains by technological era, compared")
    ax.legend(); ax.grid(alpha=.3, axis="y")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig14_era_comparison.png"), dpi=200)
    plt.close(fig)

    # fig15 - estudio de eventos: diagnostico honesto de pre-tendencias
    ev = R["HA4_DiD_y_comparacion_de_eras"]["DiD"]["log_nue"].get(
        "estudio_de_eventos", {})
    if ev:
        yrs = sorted(int(k) for k in ev)
        b = [ev[str(y) if str(y) in ev else y]["b"] for y in yrs]
        se = [ev[str(y) if str(y) in ev else y]["se"] for y in yrs]
        fig, ax = plt.subplots(figsize=(8, 4.2))
        ax.errorbar(yrs, b, yerr=[1.96 * x for x in se], fmt="o", ms=4,
                    capsize=3, color="#1f4e79")
        ax.axhline(0, c="k", lw=.8)
        ax.axvline(2015.5, ls="--", c="#c0504d", lw=1.2)
        ax.set_xlabel("Year (base = 2015)")
        ax.set_ylabel("AI exposure x year (log nitrogen efficiency)")
        ax.set_title("Event study: pre-trends do not support a causal 2016 break")
        ax.grid(alpha=.3)
        fig.tight_layout()
        fig.savefig(os.path.join(FIG, "fig15_event_study.png"), dpi=200)
        plt.close(fig)


if __name__ == "__main__":
    df = load()
    world = block_A(df)
    block_HA1(df)
    block_HA2(df)
    block_HA3(df)
    block_HA4(df)
    block_HA5(df)
    block_ROB(df)
    figures(world)
    out = os.path.join(RES, "12_ai_observable.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=2, ensure_ascii=False, default=str)
    print("Guardado:", out)
    for k in R:
        print(" -", k)
