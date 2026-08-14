# Replication package — agricultural AI, input-use efficiency and digital complements

Replication materials for:

> **"Fewer inputs, not more yield: agricultural AI and its digital complements"**
> Manuel Chaves-Maza (ORCID [0000-0003-2420-8378](https://orcid.org/0000-0003-2420-8378)) and Manuel Chaves Ballester
> Universidad Pablo de Olavide, Seville, Spain
> Submitted to *Economics of Innovation and New Technology* (Taylor & Francis).
> `<TO CONFIRM: article DOI>` · `<TO CONFIRM: repository DOI / Zenodo archive>`

**📊 [Browse every figure in the paper →](https://upocuantitativo.github.io/agri-ai-input-margin/)** — the five kept in the main text and the eleven
moved to the supplement, with the caption and the script behind each one.

---

## 1. What the paper does

There is no international series of on-farm AI adoption, so the claim that "AI will transform
agriculture" has never carried a coefficient. This paper builds one.

It constructs a **country-year measure of agricultural-AI research activity** from OpenAlex
(2000–2024) — works whose title or abstract combines an AI term with an agricultural term,
attributed to countries of author affiliation — and merges it, by ISO3 code and year, with a
**FAOSTAT + World Bank panel of agricultural performance** covering 172 countries from 1961
to 2023 (cereal yield, N/P/K fertiliser, irrigation, tractors, climate, scale).

The finding is that AI's measurable return does **not** appear as yield growth. It appears as
**nitrogen-use-efficiency gains, conditional on predetermined digital complements**:

- One SD of AI specialisation is associated with **+0.050 log points of nitrogen use
  efficiency** (p = 0.014), and only **+0.031** of yield level (p = 0.035).
- That efficiency return is **statistically zero** where digital complements are scarce and
  reaches **−0.229 log points of nitrogen** where they are abundant (interaction p < 0.001).
- The pattern is **not generic to technical change**: the fertiliser wave, the mechanisation
  wave and a non-AI research placebo all show complement dependence of the *opposite sign*,
  on the *output* margin.
- A fitted yield function **does not travel**: mean R² falls from 0.515 within region to
  −0.660 across regions, because the elasticity of yield to nitrogen ranges from +0.368 to
  −0.133 between world regions.

A causal difference-in-differences around the 2016 deep-learning break was attempted and
**failed its pre-trend diagnostics**; it is reported as descriptive and no claim rests on it.
The full event study is in [`docs/SUPPLEMENTARY_TABLES.md`](docs/SUPPLEMENTARY_TABLES.md),
Table S10.

## 2. What is in here that is not in the paper

The manuscript is capped at 10,000 words, so several complete tables were cut. They are all
in **[`docs/SUPPLEMENTARY_TABLES.md`](docs/SUPPLEMENTARY_TABLES.md)**, with every number
traced to the `results/*.json` object that produced it:

| Table | Cut from the paper |
|---|---|
| S1 | Univariate vs full-package predictive R² (H1), including the `year` row the paper dropped |
| S2 | Yield prediction by generalisation regime — OLS / Random Forest / Gradient Boosting, temporal holdout vs country GroupKFold, with RMSE and MAE |
| S3 | Local context — four architectures, in-sample variance decomposition, spatial transfer, and the holdout-cut sensitivity |
| S4 | Gains by technological era: yield, median nitrogen dose, nitrogen use efficiency, %/yr |
| S5 | The eight robustness re-estimations of the nitrogen-efficiency result, with SEs and t-statistics |
| S6 | The full 5 × 5 region-to-region transfer matrix and region-specific nitrogen elasticities |
| S7 | Convergence: σ-divergence (full, weighted, balanced), absolute and conditional β, medians by income group |
| S8 | Traceability of source claims → hypotheses → empirical verdict (the manuscript's Table A1) |
| S9 | The full 25-year world OpenAlex series behind Figure 11 |
| S10 | Event-study coefficients for all three outcomes — the numerical content of Figure 15 |
| S11 | Permutation importance and the pairwise input-interaction coefficients |

That document also ends with a **"Known numeric disagreements"** section listing every point
where `results/*.json` and the manuscript do not match, rather than reconciling them silently.

Two further documents exist only here:

- **[`docs/LINKAGE.md`](docs/LINKAGE.md)** — exactly how the three sources are merged: the
  join keys, the FAOSTAT `Area Code < 5000` and `≠ 351` filters, the M49 → ISO3 mapping via
  `pycountry`, the manual "China, mainland" override, the `[A-Z]{3}` filter that prevents a
  Cartesian blow-up in the World Bank merge, and the sample size of every estimation block.
- **[`docs/OPENALEX_QUERIES.md`](docs/OPENALEX_QUERIES.md)** — the three exact query strings,
  the exact API request, and how counts are attributed to countries (full counting, not
  fractional — with the co-authorship bias that implies).
- **[`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md)** — every variable in every shipped
  CSV and every variable constructed inside the scripts: definition, unit, source, coverage,
  transformation.

## 3. Data sources

| Source | What is taken | Access route | Access date |
|---|---|---|---|
| **FAOSTAT** | QCL (crop production and yield), RFN (fertiliser by nutrient), RL (land use, irrigation), RM (machinery), ET (temperature change) | Bulk "(Normalized)" ZIPs from `bulks-faostat.fao.org` | `<TO CONFIRM: FAOSTAT access date>` — the downloaded files in the author's working tree are timestamped **2026-06-29** |
| **World Bank** | 15 WDI indicators (yield, land, employment, value added, population, …) plus 9 digital/human-capital indicators; and the country metadata endpoint for region and income | `api.worldbank.org/v2` | `<TO CONFIRM: World Bank access date>` — timestamped **2026-06-29** (core indicators) and **2026-08-07** (digital complements) |
| **OpenAlex** | Counts of works per country and year for four queries, 2000–2024 | `api.openalex.org/works`, `group_by=authorships.countries` | `<TO CONFIRM: OpenAlex access date>` — timestamped **2026-08-07** |

File timestamps are evidence of the download date only if the files were not touched
afterwards; treat them as a strong hint, not a confirmed access date.

All three are open-access and require no credentials. OpenAlex asks for a `mailto` parameter
to enter its polite pool; `code/11_download_ai_indicators.py` hard-codes one at the `MAILTO`
constant — **replace it with your own address before re-running**.

> **OpenAlex is not versioned.** Re-running the queries will not reproduce the shipped counts
> exactly: OpenAlex continuously ingests records, back-fills abstracts and re-resolves
> affiliations. Expect the shape of the series to replicate and the levels to drift, most in
> recent years. See [`docs/OPENALEX_QUERIES.md`](docs/OPENALEX_QUERIES.md) §7.

## 4. Repository layout

```
.
├── README.md
├── LICENSE-CODE                 MIT — everything under code/
├── LICENSE-DATA                 CC BY 4.0 — data/, results/, figures/, docs/
├── CITATION.cff
├── requirements.txt
├── .gitignore
├── code/                        the pipeline, in run order
├── data/processed/              10 CSVs (10.3 MB) — the complete input to every analysis step
├── results/                     7 JSONs — every estimate reported in the paper
├── figures/                     fig1 … fig15 (PNG)
└── docs/
    ├── DATA_DICTIONARY.md
    ├── LINKAGE.md
    ├── SUPPLEMENTARY_TABLES.md
    └── OPENALEX_QUERIES.md
```

`data/raw/` is **not shipped**: it is ~715 MB, dominated by FAOSTAT's `faostat_QCL.csv`
(545 MB), which exceeds the 50 MB per-file ceiling applied to this repository. Steps 1, 2 and
11 regenerate it exactly. Everything from step 3 onward runs from the shipped
`data/processed/` CSVs alone.

## 5. Requirements

Python 3.10 or later. Tested on **Python 3.13.2, Windows 11**.

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

`linearmodels` is **not** required — the panel regressions use `statsmodels` OLS with
`C(iso3)` and `C(year)` dummies and cluster-robust standard errors, not a dedicated panel
library.

## 6. Run order

**Run every script from the repository root.** Some scripts resolve paths relative to the
working directory and others relative to their own location; both conventions resolve
correctly only when the working directory is the repository root.

```bash
# ---- Layer 1: acquisition (network; regenerates data/raw/, ~715 MB) -------------
python code/01_download_worldbank.py        # 15 WDI indicators      -> data/raw/wb_*.csv, data/processed/wb_panel.csv
python code/02_download_faostat.py          # 5 FAOSTAT bulk ZIPs    -> data/raw/faostat_*.csv
python code/11_download_ai_indicators.py    # OpenAlex + 9 WDI       -> data/processed/ai_panel.csv

# ---- Layer 2: panel construction ------------------------------------------------
python code/03_build_panel.py               # -> country_panel.csv, world_*.csv, qcl_world_raw.csv, spain_series.csv
python code/03b_country_meta.py             # -> country_meta.csv

# ---- Layer 3: analysis (each writes one JSON to results/ and its figures) --------
python code/04_macro_trends.py              # H2  -> results/04_macro_trends.json      + fig1-fig4
python code/05_convergence.py               # H6  -> results/05_convergence.json       + fig5, fig6
python code/06_yield_models.py              # H1, H3, H4 -> results/06_yield_models.json + fig7, fig8
python code/07_labor.py                     # H5  -> results/07_labor.json             + fig9
python code/08_robustness.py                # robustness -> results/08_robustness.json + fig10
python code/10_revision_analyses.py         # spatial transfer, interactions, convergence -> results/10_revision_analyses.json
python code/12_ai_observable.py             # HA1-HA5 + ROB -> results/12_ai_observable.json + fig11-fig15
```

**To skip the network entirely, start at Layer 3.** The shipped `data/processed/` CSVs are
exactly the output of Layers 1 and 2, so `04`, `05`, `06`, `07`, `08`, `10` and `12` run
immediately on a fresh clone with no downloads at all. This is the recommended path for
verifying the paper's numbers, and it is the only path that reproduces them exactly — see
§13 on source drift.

Two convenience flags:

```bash
python code/11_download_ai_indicators.py --build-only   # rebuild ai_panel.csv from cached data/raw/openalex_*.csv
```

`code/09_build_docx.py`, `code/09b_build_docx_en.py` and `code/13_build_docx_v2.py` assemble
the manuscript DOCX from a markdown source in `article/`. **That source is not shipped here**
(it is the manuscript itself), so these three scripts will fail on a fresh clone. They are
included only for completeness of the pipeline. `code/_explore.py` and `code/_coverage.py`
are ad-hoc helpers, not part of the reported analysis.

### Expected runtime

Indicative, on a recent laptop. Network-bound steps depend entirely on your connection.

| Step | Approximate time | Dominant cost |
|---|---|---|
| `01_download_worldbank.py` | 1–3 min | 15 API calls with 0.5 s spacing |
| `02_download_faostat.py` | 10–40 min | ~715 MB of ZIP downloads, QCL alone is 545 MB unzipped |
| `11_download_ai_indicators.py` | 3–8 min | 100 OpenAlex calls with 0.35 s spacing, plus 9 WDI calls |
| `03_build_panel.py` | 3–8 min | chunked read of the 545 MB QCL file |
| `03b_country_meta.py` | seconds | one API call |
| `04`, `05`, `07`, `08` | under 1 min each | plotting |
| `06_yield_models.py` | 5–15 min | 400-tree Random Forest × 5 GroupKFold folds, plus 15-repeat permutation importance |
| `10_revision_analyses.py` | 2–6 min | three GroupKFold sweeps |
| `12_ai_observable.py` | 5–15 min | ~40 fixed-effects OLS fits with `C(iso3)` dummies, plus 5 regional gradient-boosting models |
| **Layer 3 only, from shipped CSVs** | **15–40 min total** | — |

All models are seeded (`random_state = 42`, or `0` in the HA5 transfer block), so re-runs on
the shipped CSVs are deterministic.

## 7. What each results file contains

| File | Size | Blocks | Feeds |
|---|---|---|---|
| `results/04_macro_trends.json` | 2 KB | `produccion_mundial` (the *core3* aggregate, 1,373 → 4,174 Mt, ×3.04); `rendimiento_cereal_mundial.por_decada` (decadal yield growth, 2.94 % → 1.21 %/yr); `mecanizacion_espana` (229 → 12 ha/tractor); `nitrogeno_rendimientos_decrecientes` (world N 11.5 → 111.6 Mt; partial productivity 117.8 → 37.9) | §4.2, Figures 1–4 |
| `results/05_convergence.json` | 1 KB | `sigma_convergencia` (SD of log-yield 0.580 → 0.909); `beta_convergencia` (β = +0.00092, p = 0.579); `rendimiento_mediano_por_renta` (medians by income group) | §4.6, Figures 5–6, Table S7 |
| `results/06_yield_models.json` | 4 KB | `muestra` (8,364 obs / 172 countries / 1961–2023); `testA_ML_vs_OLS` (both regimes); `testB_importancia`; `testB_r2_univariante`; `testC_generico_vs_especifico` (four architectures); `descomposicion_varianza` | §4.1, §4.3, §4.4; Tables 2–4; Tables S1–S3, S11 |
| `results/07_labor.json` | 1 KB | `empleo_agricola_mundial` (42.8 % 1991 → 27.3 % 2024); `regresion_FE_empleo_vs_productividad` (−0.327, mechanically contaminated); `correlacion_mecanizacion_empleo` (−0.379) | §4.5, Figure 9 |
| `results/08_robustness.json` | 1 KB | `dependencia_parcial_N` (high-dose slope 38 % of low-dose); `sensibilidad_corte_holdout` (cuts 2005/2010/2015); `sigma_convergencia_ponderada_pob` (0.468 → 0.603) | §4.13, Figure 10, Tables S3, S7 |
| `results/10_revision_analyses.json` | 3 KB | `C2_transferencia_espacial_…` (three specifications under GroupKFold); `I1_complementariedad` (pairwise input interactions); `H6_panel_balanceado`; `I3_beta_convergencia` (absolute and conditional); `H5_empleo_vs_mecanizacion_exogena` | §4.1, §4.4, §4.5, §4.6; Tables S3, S7, S11 |
| `results/12_ai_observable.json` | 37 KB | `A_descriptivos_IA` (25-year world series); `HA1_…`; `HA2_margen_de_valor_y_complementariedad` (volume, specialisation, horse race, interaction, marginal effects); `HA3_test_diferencial_entre_oleadas` (four waves + NUE margin); `HA4_DiD_y_comparacion_de_eras` (DiD, event study, era growth rates); `HA5_no_transferibilidad_…` (transfer matrix, elasticities); `ROB_robustez` (nine specifications) | §4.7–§4.13; Tables 5–7; Tables S4–S6, S9, S10 |

Key names inside the JSONs are in Spanish (the analysis was written in Spanish); the mapping
to the paper's English terminology is given in
[`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) and in the table below.

## 8. Figure and table → script → JSON key

**Figures**

| Fig. | File | Subject | Script | JSON key |
|---|---|---|---|---|
| 1 | `fig1_produccion_mundial.png` | World production by major crop group | `04_macro_trends.py` | `04_macro_trends.json` → `produccion_mundial` |
| 2 | `fig2_desaceleracion_rendimiento.png` | Deceleration of world cereal-yield growth | `04_macro_trends.py` | `04_macro_trends.json` → `rendimiento_cereal_mundial.por_decada` |
| 3 | `fig3_mecanizacion_espana.png` | Spain: hectares of arable land per tractor, 1961–2009 | `04_macro_trends.py` | `04_macro_trends.json` → `mecanizacion_espana` |
| 4 | `fig4_nitrogeno.png` | Yield vs nitrogen; declining partial productivity of N | `04_macro_trends.py` | `04_macro_trends.json` → `nitrogeno_rendimientos_decrecientes` |
| 5 | `fig5_convergencia.png` | σ- and β-convergence of yields across countries | `05_convergence.py` | `05_convergence.json` → `sigma_convergencia`, `beta_convergencia` |
| 6 | `fig6_rendimiento_por_renta.png` | Median cereal yield by income group | `05_convergence.py` | `05_convergence.json` → `rendimiento_mediano_por_renta` |
| 7 | `fig7_importancia.png` | Permutation importance, gradient boosting | `06_yield_models.py` | `06_yield_models.json` → `testB_importancia` |
| 8 | `fig8_generico_vs_especifico.png` | Prediction error: generic vs specific architectures | `06_yield_models.py` | `06_yield_models.json` → `testC_generico_vs_especifico` |
| 9 | `fig9_empleo.png` | World agricultural employment and labour productivity | `07_labor.py` | `07_labor.json` (all blocks) |
| 10 | `fig10_dependencia_parcial.png` | Partial dependence: diminishing marginal returns to N | `08_robustness.py` | `08_robustness.json` → `dependencia_parcial_N` |
| 11 | `fig11_ai_emergence.png` | Emergence of agricultural AI: world works and share of world research | `12_ai_observable.py` | `12_ai_observable.json` → `A_descriptivos_IA.serie_mundial` |
| 12 | `fig12_ai_margin.png` | Where the value of AI appears; marginal effect on N by complement percentile | `12_ai_observable.py` | `12_ai_observable.json` → `HA2_margen_de_valor_y_complementariedad` |
| 13 | `fig13_wave_comparison.png` | Is complement dependence generic? Four technological waves | `12_ai_observable.py` | `12_ai_observable.json` → `HA3_test_diferencial_entre_oleadas` |
| 14 | `fig14_era_comparison.png` | Gains by technological era | `12_ai_observable.py` | `12_ai_observable.json` → `HA4_DiD_y_comparacion_de_eras.crecimiento_anual_pct_por_era` |
| 15 | `fig15_event_study.png` | Event study for nitrogen use efficiency, base year 2015 | `12_ai_observable.py` | `12_ai_observable.json` → `HA4_DiD_y_comparacion_de_eras.DiD.log_nue.estudio_de_eventos` |

**Tables in the published paper**

| Table | Subject | Script | JSON key | Full version here |
|---|---|---|---|---|
| 1 | Hypothesis → analysis → metric map | — | — | — |
| 2 | H1: univariate vs package R² | `06_yield_models.py` | `06_yield_models.json` → `testB_r2_univariante` | [S1](docs/SUPPLEMENTARY_TABLES.md#table-s1) |
| 3 | H3: yield prediction by regime | `06_yield_models.py` | `06_yield_models.json` → `testA_ML_vs_OLS` | [S2](docs/SUPPLEMENTARY_TABLES.md#table-s2) |
| 4 | H4: local context, both regimes | `06_yield_models.py`, `10_revision_analyses.py` | `06…` → `testC_generico_vs_especifico`, `descomposicion_varianza`; `10…` → `C2_transferencia_espacial_generico_vs_especifico` | [S3](docs/SUPPLEMENTARY_TABLES.md#table-s3) |
| 5 | HA2: where AI's value appears | `12_ai_observable.py` | `12…` → `HA2_margen_de_valor_y_complementariedad` (`margen_especializacion`, `carrera_IA_vs_investigacion_general`, `condicional_a_complementos`) | — (in the paper in full) |
| 6 | HA3: complement dependence across four waves | `12_ai_observable.py` | `12…` → `HA3_test_diferencial_entre_oleadas` | — (in the paper in full) |
| 7 | HA4: gains by technological era | `12_ai_observable.py` | `12…` → `HA4_DiD_y_comparacion_de_eras.crecimiento_anual_pct_por_era` | [S4](docs/SUPPLEMENTARY_TABLES.md#table-s4) |
| A1 | Traceability: claim → hypothesis → verdict | — | — | [S8](docs/SUPPLEMENTARY_TABLES.md#table-s8) |

**In-text results with no table in the paper**

| Manuscript section | Result | JSON key | Full version here |
|---|---|---|---|
| §4.5 | Employment recomposition | `07_labor.json` (all); `10_revision_analyses.json` → `H5_empleo_vs_mecanizacion_exogena` | — |
| §4.6 | Convergence | `05_convergence.json`; `08_robustness.json` → `sigma_convergencia_ponderada_pob`; `10_revision_analyses.json` → `H6_panel_balanceado`, `I3_beta_convergencia` | [S7](docs/SUPPLEMENTARY_TABLES.md#table-s7) |
| §4.7 | Emergence of the AI variable | `12_ai_observable.json` → `A_descriptivos_IA` | [S9](docs/SUPPLEMENTARY_TABLES.md#table-s9) |
| §4.8 | HA1, unconditional AI → yield | `12_ai_observable.json` → `HA1_efecto_incondicional_IA_sobre_rendimiento` | — |
| §4.11 | The failed DiD and its event study | `12_ai_observable.json` → `HA4_DiD_y_comparacion_de_eras.DiD` | [S10](docs/SUPPLEMENTARY_TABLES.md#table-s10) |
| §4.12 | HA5, non-transferability | `12_ai_observable.json` → `HA5_no_transferibilidad_de_la_funcion_aprendida` | [S6](docs/SUPPLEMENTARY_TABLES.md#table-s6) |
| §4.13 | The eight robustness re-estimations | `12_ai_observable.json` → `ROB_robustez` | [S5](docs/SUPPLEMENTARY_TABLES.md#table-s5) |

## 9. Verifying the headline numbers without re-running the pipeline

```bash
python - <<'PY'
import json
r = json.load(open("results/12_ai_observable.json", encoding="utf-8"))
ha2 = r["HA2_margen_de_valor_y_complementariedad"]
print("common sample:", ha2["muestra_comun"])
print("NUE, specialisation:", ha2["margen_especializacion"]["log_nue"]["z_spec"])
print("horse race, non-AI:", ha2["carrera_IA_vs_investigacion_general"]["log_nue"]["z_res_investigacion_no_IA"])
me = ha2["condicional_a_complementos"]["log_n_x"]["efectos_marginales"]
print("N dose at P10:", me["p10"]["efecto_marginal"], "at P90:", me["p90"]["efecto_marginal"])
h5 = r["HA5_no_transferibilidad_de_la_funcion_aprendida"]
print("transfer R2 within/across:", h5["R2_medio_misma_region_holdout_temporal"],
                                    h5["R2_medio_otra_region"])
PY
```

Expected: common sample 3,659 obs / 169 countries; NUE coefficient +0.0496 (p = 0.0143);
non-AI research on NUE −0.0256 (p = 0.8468); marginal effect on the nitrogen dose +0.0245 at
P10 and −0.2293 at P90; transfer R² 0.5152 within region, −0.6603 across.

## 10. Licensing

- **Code** (`code/`) — MIT, see [`LICENSE-CODE`](LICENSE-CODE).
- **Derived data, results, figures and documentation** (`data/`, `results/`, `figures/`,
  `docs/`) — Creative Commons Attribution 4.0 International, see
  [`LICENSE-DATA`](LICENSE-DATA).

The derived data are transformations of FAOSTAT, World Bank Open Data and OpenAlex, each of
which carries its own terms. FAOSTAT data are released under CC BY-NC-SA 3.0 IGO; World Bank
Open Data under CC BY 4.0; OpenAlex is released into the public domain under CC0. Users
redistributing the FAOSTAT-derived columns should observe FAOSTAT's non-commercial and
share-alike terms, which are more restrictive than the CC BY 4.0 applied to this package's
own contribution. `<TO CONFIRM: whether the journal or institution requires a different
licence for the replication package>`

## 11. Citation

See [`CITATION.cff`](CITATION.cff). Author identity, ORCID, contact address and DOIs are
marked `<TO CONFIRM>` and must be completed before the package is cited or archived.

## 12. Ethics, funding and AI-use statements

Reproduced from the manuscript:

- **Funding.** This research received no specific grant from any funding agency in the
  public, commercial, or not-for-profit sectors.
- **Ethics.** The study uses publicly available secondary data (FAOSTAT, World Bank,
  OpenAlex); no ethical approval was required, as no human participants or personal data
  were involved.
- **Conflicts of interest.** The author declares none.
- **Generative AI.** A generative AI assistant (Anthropic Claude) was used to help draft
  data-acquisition and analysis code and to improve the language of the manuscript. It was
  not used to generate the hypotheses, the empirical results, the data, the figures or the
  substantive conclusions; the author reviewed and edited all content and takes full
  responsibility for it.

## 13. Known limitations of this package

1. **`data/raw/` is not included** (~715 MB; `faostat_QCL.csv` alone is 545 MB). Regenerate
   it with steps 01, 02 and 11, or start from the shipped `data/processed/` CSVs.
2. **OpenAlex counts will drift** on re-download; the database is unversioned. See
   [`docs/OPENALEX_QUERIES.md`](docs/OPENALEX_QUERIES.md) §7.
3. **FAOSTAT revises historical series.** Re-downloading a later FAOSTAT vintage will shift
   some figures; the shipped `data/processed/` CSVs are the exact vintage behind the paper.
4. **The tractor series ends in 2009**, which is why the mechanisation wave is dated
   1961–2009 throughout.
5. **The AI measure is research activity, not on-farm adoption.** It is an upstream proxy for
   capability and orientation. The manuscript's Section 5.5 argues the resulting attenuation
   biases the conditional estimates towards zero rather than manufacturing them.
6. **The three DOCX-assembly scripts will not run** on a fresh clone, because the manuscript
   markdown they read is not shipped here.
7. **JSON keys and code comments are in Spanish.** The English mapping is in
   [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) and §7–§8 above.
