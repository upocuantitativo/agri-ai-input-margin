# Supplementary material

Fewer inputs, not more yield: agricultural AI and its digital complements

This file collects the material moved out of the main text to meet the 10,000-word limit. Every number is transcribed from the estimation output deposited in the replication repository, and each table names the JSON file and key that produced it, so that any figure can be traced back to the object that generated it.

## Supplementary figures


Figure S1. World production by major crop group and the core3 aggregate (cereals, roots and tubers, pulses), 1961–2023 (FAOSTAT).

![Figure S1](FigureS1.png)

Figure S2. World cereal yield and its annual growth rate (10-year moving average), 1961–2023 (FAOSTAT).

![Figure S2](FigureS2.png)

Figure S3. Spain: hectares of arable land per tractor, 1961–2009 (FAOSTAT).

![Figure S3](FigureS3.png)

Figure S4. Cereal yield versus nitrogen applied, and partial productivity of nitrogen, 1961–2023.

![Figure S4](FigureS4.png)

Figure S5. σ-convergence: dispersion of log cereal yield across countries, and the absolute β-convergence test.

![Figure S5](FigureS5.png)

Figure S6. Median cereal yield by income group (kg/ha).

![Figure S6](FigureS6.png)

Figure S7. Permutation importance of the predictors in the gradient boosting model (test set).

![Figure S7](FigureS7.png)

Figure S8. Generic versus specific: yield prediction error under the temporal holdout (≥ 2010).

![Figure S8](FigureS8.png)

Figure S9. World agricultural employment (% of total, population-weighted), and agricultural employment versus labour productivity by country-year.

![Figure S9](FigureS9.png)

Figure S10. Partial dependence of log cereal yield on the nitrogen dose and the irrigation share (gradient boosting).

![Figure S10](FigureS10.png)

Figure S11. Event study for nitrogen use efficiency, base year 2015. Pre-2016 coefficients are not jointly null and no discrete break follows 2016, so the parallel-trends assumption fails and the difference-in-differences estimate is reported as descriptive only.

![Figure S11](FigureS11.png)

*Note on resolution:* Figures S1–S10 were produced at 130 dpi and Figure S11 at 200 dpi. They are supplied at source resolution rather than upscaled; they can be regenerated at any resolution from the analysis scripts in the replication repository.


## Supplementary tables

The full tables cut from the main text. Every number here is transcribed from `results/*.json`;
the JSON file and key are named under each table so any figure can be traced to the object
that produced it. Where the manuscript and the JSON disagree, both are reported — see
[Known numeric disagreements](#known-numeric-disagreements) at the end.

Rounding convention: coefficients and R² to four decimals as stored; p-values to four
decimals, or `<0.001` when smaller. The manuscript rounds more aggressively; these are the
underlying values.

**Contents**

| Table | Subject | Hypothesis | Source |
|---|---|---|---|
| [S1](#table-s1) | Univariate vs full-package predictive R² | H1 | `06_yield_models.json` |
| [S2](#table-s2) | Yield prediction by generalisation regime | H3 | `06_yield_models.json` |
| [S3](#table-s3) | Local context: temporal extrapolation vs spatial transfer | H4 | `06`, `08`, `10` |
| [S4](#table-s4) | Gains by technological era | HA4 | `12_ai_observable.json` |
| [S5](#table-s5) | Eight robustness re-estimations of the nitrogen-efficiency result | HA2/HA4 | `12_ai_observable.json` |
| [S6](#table-s6) | Region-to-region transfer matrix and nitrogen elasticities | HA5 | `12_ai_observable.json` |
| [S7](#table-s7) | Convergence: σ, absolute and conditional β | H6 | `05`, `08`, `10` |
| [S8](#table-s8) | Traceability: source claim → hypothesis → verdict | all | manuscript Table A1 |
| [S9](#table-s9) | World OpenAlex series, 2000–2024 | HA1–HA4 | `12_ai_observable.json` |
| [S10](#table-s10) | Event-study coefficients, base year 2015 | HA4 | `12_ai_observable.json` |
| [S11](#table-s11) | Permutation importance and input-interaction coefficients | H1 | `06`, `10` |
| [S12](#table-s12) | Hypothesis to analysis to metric map | all | study design |

---

### Table S1

### Univariate versus full-package predictive power (H1)

Out-of-sample R² on the temporal holdout (train ≤ 2009, test ≥ 2010), target `ln(cereal
yield kg/ha)`. Each univariate model is a `HistGradientBoostingRegressor` fitted on that
single feature alone, so the comparison is like-for-like with the full-package model and not
a linear-vs-nonlinear artefact.

| Predictor | Variable | R² alone |
|---|---|---|
| Nitrogen | `n_kg_ha` | 0.3405 |
| Potassium | `k_kg_ha` | 0.2042 |
| Phosphorus | `p_kg_ha` | 0.1398 |
| Share of cropland equipped for irrigation | `irrig_share_cropland` | 0.0266 |
| Year (trend alone) | `year` | −0.0079 |
| Temperature anomaly | `temp_anom` | −0.0159 |
| Scale | `log_arable` | −0.0791 |
| **Full package (all seven)** | — | **0.6741** |

*Note.* No single input reaches half the explanatory power of the package; the best of them,
nitrogen, reaches 0.3405 against 0.6741, and three features are individually worse than
predicting the sample mean. Source: `results/06_yield_models.json`,
`testB_r2_univariante`. The manuscript's Table 2 reports the same figures but omits the
`year` row, which is restored here.

---

### Table S2

### Yield prediction by generalisation regime (H3)

Same feature set, same target, two validation protocols. **Temporal holdout**: train on
years ≤ 2009, test on years ≥ 2010 — extrapolation to the future of known countries.
**Country GroupKFold** (5 folds, grouped by `iso3`): every test country is absent from
training — transfer to unobserved places. R² is in log space; RMSE and MAE are
back-transformed to kg/ha.

**Panel A — temporal holdout (train ≤ 2009, test ≥ 2010)**

| Model | RMSE (log) | R² | RMSE (kg/ha) | MAE (kg/ha) |
|---|---|---|---|---|
| OLS (linear) | 0.6711 | 0.3392 | 3,312.3 | 1,706.7 |
| Random Forest | 0.4913 | 0.6458 | 2,680.7 | 1,150.8 |
| **Gradient Boosting** | **0.4713** | **0.6741** | **2,590.8** | **1,127.6** |

**Panel B — country GroupKFold (5 folds, unobserved countries)**

| Model | Mean R² | SD of R² across folds | Mean RMSE (kg/ha) |
|---|---|---|---|
| **OLS (linear)** | **0.4488** | 0.0335 | 2,095.4 |
| Random Forest | 0.4011 | 0.0610 | 2,015.1 |
| Gradient Boosting | 0.4157 | 0.0970 | 2,021.3 |

*Note.* The ranking reverses between regimes: gradient boosting beats OLS by 0.335 of R²
when extrapolating in time, but sits 0.033 *below* OLS when transferring to unseen
countries, with a fold-to-fold SD (0.097) three times the OLS SD (0.034) — the intervals
overlap, so the defensible claim is that the machine-learning advantage *vanishes within
sampling error* under spatial transfer, not that it reverses. The two regimes are not
equally hard, so levels are not comparable across panels; only the within-panel ranking is.
Source: `results/06_yield_models.json`, `testA_ML_vs_OLS`.

---

### Table S3

### Local context: temporal extrapolation versus spatial transfer, all architectures (H4)

**Panel A — temporal holdout, four architectures** (gradient boosting throughout)

| Architecture | RMSE (log) | R² | RMSE (kg/ha) | MAE (kg/ha) |
|---|---|---|---|---|
| 1. Generic global (inputs only) | 0.4713 | 0.6741 | 2,590.8 | 1,127.6 |
| 2. Regional (one model per region) | 0.4085 | 0.7551 | 1,901.5 | 891.0 |
| 3. Local calibration (global model + per-country offset) | 0.4477 | 0.7058 | 2,527.1 | 1,078.9 |
| **4. Inputs + geography, pooled (country, region, income)** | **0.3777** | **0.7906** | **1,832.1** | **770.0** |

Error reduction relative to the generic global model: local calibration **2.5 %**;
inputs + geography **29.3 %**. Regional test coverage is 1.00, i.e. every test observation
belongs to a region seen in training.

**Panel B — in-sample variance decomposition (OLS with country dummies)**

| Specification | R² (in sample) |
|---|---|
| Generic inputs only | 0.4751 |
| Country fixed effects only | 0.7442 |
| Inputs + country fixed effects | 0.8658 |
| **Gain attributable to local specificity** | **+0.3907** |

**Panel C — spatial transfer (country GroupKFold, unobserved countries)**

| Specification | Geography transferable? | Mean R² | SD | Mean RMSE (kg/ha) |
|---|---|---|---|---|
| (a) Generic inputs only | — | 0.4199 | 0.0968 | 2,015.6 |
| (b) Inputs + region + income | yes | 0.4637 | 0.1490 | 1,843.6 |
| (c) Inputs + country effects | no | 0.5006 | 0.0399 | 1,830.9 |

Total gain from specificity under spatial transfer: **+0.0807 of R²** (a → c), against
**+0.3907** in the in-sample decomposition.

**Panel D — sensitivity of the temporal-holdout result to the cut-off year**

| Holdout cut | RMSE generic (kg/ha) | R² generic | RMSE inputs+geography | R² inputs+geography | Error reduction |
|---|---|---|---|---|---|
| ≥ 2005 | 2,517.6 | 0.6236 | 2,023.5 | 0.7540 | 19.6 % |
| ≥ 2010 | 2,586.4 | 0.6839 | 1,935.3 | 0.7913 | 25.2 % |
| ≥ 2015 | 2,137.5 | 0.7408 | 1,530.3 | 0.8256 | 28.4 % |

*Note.* Local context is a first-order predictor under temporal extrapolation (+0.12 of R²,
−29 % error), and the in-sample decomposition attributes +0.39 of R² to country effects —
but only +0.08 of that survives the move to unobserved countries, and the three
spatial-transfer specifications are statistically close (the 0.4637 ± 0.1490 and
0.5006 ± 0.0399 intervals overlap widely). An unseen test country receives no coefficient of
its own, so specification (c)'s small edge comes from country effects de-confounding the
input slopes during training, not from remembering country means. Sources:
`results/06_yield_models.json` (`testC_generico_vs_especifico`, `descomposicion_varianza`),
`results/10_revision_analyses.json` (`C2_transferencia_espacial_generico_vs_especifico`),
`results/08_robustness.json` (`sensibilidad_corte_holdout`).

---

### Table S4

### Gains by technological era (HA4)

Log-linear annual growth rates, %/year, fitted by OLS of `ln(x)` on year within each era.
World cereal yield is the cereal-area-weighted mean across countries; nitrogen dose and
nitrogen use efficiency are cross-country **medians** of the national values.

| Indicator | Green Revolution 1961–1990 | Post-Green-Revolution 1991–2015 | AI era 2016–2023 |
|---|---|---|---|
| World cereal yield | +2.3320 | +1.4865 | **+0.7362** |
| Median nitrogen dose (kg N/ha cropland) | +7.5803 | +1.5565 | **−1.5174** |
| Median nitrogen use efficiency (kg grain / kg N) | −2.4516 | +0.8191 | **+2.2325** |

*Note.* The eras are mirror images. The Green Revolution bought output with inputs — yield
grew fastest (+2.33 %/yr) while nitrogen use grew three times faster still (+7.58 %/yr), so
efficiency *fell* (−2.45 %/yr). The AI era is the first in the six decades of the series in
which the median national nitrogen dose declines (−1.52 %/yr) and it records the fastest
efficiency improvement of the whole period (+2.23 %/yr), on the weakest yield growth
(+0.74 %/yr). This comparison is **descriptive**: it is an era-by-era accounting of
aggregates, not an estimate of AI's effect. Source: `results/12_ai_observable.json`,
`HA4_DiD_y_comparacion_de_eras.crecimiento_anual_pct_por_era`.

---

### Table S5

### The eight robustness re-estimations of the nitrogen-efficiency result

All rows estimate the same object: the coefficient on `exposure × 1{year ≥ cut}` in a
two-way fixed-effects regression of `ln(nitrogen use efficiency)`, with `log_area` and
`temp_anom` as controls, `C(iso3)` and `C(year)` dummies, and standard errors clustered by
country. Row 0 is the baseline; rows 1–8 change exactly one thing each.

| # | Specification | What changes | n | b | SE | t | p |
|---|---|---|---|---|---|---|---|
| 0 | **Baseline** — specialisation exposure, cut 2016 | — | 3,794 | **0.0985** | 0.0433 | 2.277 | 0.0228 |
| 1 | Volume normalisation | works per million inhabitants instead of share of national output | 3,738 | 0.1143 | 0.0316 | 3.622 | <0.001 |
| 2 | Precision-agriculture query | narrow exposure (`precision agriculture`, `smart farming`, …) | 3,738 | 0.0657 | 0.0255 | 2.577 | 0.0100 |
| 3 | Cut year 2015 | `post = 1{year ≥ 2015}` | 3,794 | 0.1029 | 0.0442 | 2.325 | 0.0201 |
| 4 | Cut year 2017 | `post = 1{year ≥ 2017}` | 3,794 | 0.0981 | 0.0431 | 2.279 | 0.0227 |
| 5 | Excluding CHN, IND, USA | three largest producers dropped | 3,722 | 0.0992 | 0.0438 | 2.266 | 0.0235 |
| 6 | Controlling income per capita | `+ log_gdp` (constant 2015 US$) | 3,727 | 0.1001 | 0.0421 | 2.378 | 0.0174 |
| 7 | Region-specific linear trends | `+ C(region):year` | 3,794 | 0.1237 | 0.0428 | 2.888 | 0.0039 |
| 8 | **Placebo** — non-AI research exposure, entered alone | exposure built from total works minus AI works | 3,738 | 0.1518 | 0.0473 | 3.210 | 0.0013 |

*Note.* The efficiency association survives every perturbation at the 5 % level, with point
estimates between +0.066 and +0.124. **Row 8 does not pass cleanly and is reported as a
failure**: a placebo exposure built from non-AI research output also produces a significant
efficiency coefficient when entered *alone*, and a larger one than AI's. This is why the
paper's attribution to AI rests on the horse race of manuscript Table 2 panel B — where the
two exposures are entered *jointly* and AI carries the efficiency margin (+0.0496, p = 0.0143)
while generic research capacity does not (−0.0256, p = 0.8468) — and not on this block.
Sample sizes vary because each specification drops on its own regressors. Source:
`results/12_ai_observable.json`, `ROB_robustez`.

---

### Table S6

### Region-to-region transfer matrix and region-specific nitrogen elasticities (HA5)

**Panel A — transfer matrix.** R² of a gradient-boosting yield model **trained on the row
region** and **evaluated on the column region**. Diagonal cells (bold) are a temporal
holdout *within* the region (train ≤ 2009, test ≥ 2010); off-diagonal cells train on all
years of the row region and evaluate on all years of the column region. Negative R² means
the model predicts worse than the target region's own mean.

| Train ↓ / Test → | MENA+AFG+PAK | Sub-Saharan Africa | Europe & Central Asia | Latin America & Caribbean | East Asia & Pacific |
|---|---|---|---|---|---|
| **MENA+AFG+PAK** | **0.6846** | −0.7421 | −3.2398 | −1.7807 | −1.7166 |
| **Sub-Saharan Africa** | −0.0288 | **0.3756** | −1.9179 | −2.1042 | −0.4023 |
| **Europe & Central Asia** | −0.1982 | −0.2880 | **0.5236** | −0.7552 | −0.1438 |
| **Latin America & Caribbean** | 0.2691 | −0.2214 | −0.2575 | **0.5882** | 0.3660 |
| **East Asia & Pacific** | 0.1183 | −0.1470 | −0.0298 | 0.0134 | **0.4039** |

| Summary | Value |
|---|---|
| Mean R², same region (temporal holdout) | **0.5152** |
| Mean R², other region (spatial transfer) | **−0.6603** |
| Absolute drop | **1.1755** |
| Regions in the matrix | 5 |

**Panel B — region-specific nitrogen elasticities.** Coefficient on `log_n` in
`ln(yield) ~ log_n + log_p + log_k + irr + log_area + temp_anom + C(year)`, estimated
separately within each region.

| Region | Elasticity of yield w.r.t. nitrogen |
|---|---|
| Middle East, North Africa, Afghanistan & Pakistan | **+0.3677** |
| Europe & Central Asia | +0.2938 |
| Latin America & Caribbean | +0.1415 |
| East Asia & Pacific | +0.0058 |
| **Sub-Saharan Africa** | **−0.1327** |
| Range | −0.1327 to +0.3677 |

*Note.* Of the twenty off-diagonal cells, sixteen are negative: a model trained elsewhere is
usually worse than using the target region's mean, and in the worst case (MENA → Europe &
Central Asia) it is worse by more than three R² points. Panel B gives the mechanical cause —
the input-response function is not merely imprecise across regions but changes sign, so a
model that learned the MENA elasticity (+0.37) encodes a wrongly-signed mapping when moved
to Sub-Saharan Africa (−0.13). South Asia (273 observations) and North America (126) fall
below the 300-observation threshold and are excluded from the matrix; see
[`LINKAGE.md`](LINKAGE.md) §6. Source: `results/12_ai_observable.json`,
`HA5_no_transferibilidad_de_la_funcion_aprendida`.

---

### Table S7

### Convergence results (H6)

**Panel A — σ-convergence**: cross-country standard deviation of `ln(cereal yield)`.

| Sample | Countries | SD at start | SD at end | Period | Verdict |
|---|---|---|---|---|---|
| Full panel | 150 | 0.580 | 0.909 | 1961 → 2024 | **σ-divergence** |
| Population-weighted | — | 0.468 | 0.603 | 1961 → 2024 | divergence |
| Balanced panel | 142 | 0.583 | 0.884 | 1961 → 2024 | divergence |

Trend in the full-panel SD: **+0.00544 per year**.

**Panel B — β-convergence**: growth of `ln(yield)` regressed on initial `ln(yield)`.
β < 0 means catch-up.

| Specification | Source | n | β | p | R² | Verdict |
|---|---|---|---|---|---|---|
| Absolute (original estimate) | `05_convergence.json` | 144 | **+0.00092** | 0.5791 | 0.002 | no convergence |
| Absolute (balanced-panel re-estimate) | `10_revision_analyses.json` | 142 | **+0.00206** | 0.2481 | 0.010 | no convergence |
| **Conditional** (controls: region, mean inputs) | `10_revision_analyses.json` | 136 | **−0.00721** | **0.0068** | 0.209 | **convergence to country-specific steady states** |

**Panel C — median cereal yield by income group (kg/ha)**

| Income group | 1961–65 | 2018–22 | Ratio |
|---|---|---|---|
| High income | 1,853 | 5,522 | ×2.98 |
| Upper middle income | 1,185 | 3,433 | ×2.90 |
| Lower middle income | 958 | 1,971 | ×2.06 |
| **Low income** | **807** | **1,164** | **×1.44** |
| Not classified | 945 | 3,082 | ×3.26 |

*Note.* Dispersion rises by 57 % over six decades and the result holds when weighting by
population and when restricting to a balanced panel, so the divergence is not a composition
artefact. Absolute β-convergence is flat and insignificant under both estimates; conditional
β-convergence is negative and significant, so each country converges towards **its own**
steady state and those steady states differ by region and input endowment. The distributive
consequence is Panel C: the absolute gap between high- and low-income medians widens from
1,046 to 4,358 kg/ha. The two absolute-β rows are two different scripts on two different
samples (144 vs 142 countries); the manuscript quotes the second. Sources:
`results/05_convergence.json`, `results/08_robustness.json`
(`sigma_convergencia_ponderada_pob`), `results/10_revision_analyses.json`
(`H6_panel_balanceado`, `I3_beta_convergencia`).

---

### Table S8

### Traceability: source claim → hypothesis → empirical verdict

This is Table A1 of the manuscript, relocated here. Claims (a)–(l) are the propositions the
study set out to test, drawn from three prior documents by the author: a normative
introductory essay on the role of AI in agriculture; *"Artificial Intelligence in
Agriculture: Digital Transformation and Precision Agriculture"*; and *"Parallels between the
change AI will bring to agriculture and previous agricultural technological revolutions"*.

| # | Claim of the framework | Hypothesis | Empirical verdict | Evidence |
|---|---|---|---|---|
| (a) | AI is a package, not an isolated algorithm | H1 | **Supported** — inputs non-separable, with significant interactions | [S1](#table-s1), [S11](#table-s11) |
| (b) | Diminishing returns / deceleration | H2 | **Supported** — yield growth 2.9 % → 1.2 %/yr; partial productivity of N −68 % | `04_macro_trends.json`, `08_robustness.json` |
| (c) | Machine learning improves prediction | H3 | **Partial** — yes under temporal extrapolation; dilutes in spatial transfer | [S2](#table-s2) |
| (d) | Specific/local AI beats generic/integral AI | H4 | **Partial** — local context is first-order, but the superiority of *decentralised* modelling is not proven | [S3](#table-s3) |
| (e) | Technology recomposes employment | H5 | **Supported as a descriptive pattern**; within-country causal evidence weak | `07_labor.json`, `10_revision_analyses.json` |
| (f) | Without inclusion, technology widens inequalities | H6 | **Supported in its absolute version** (σ-divergence); convergence only conditional | [S7](#table-s7) |
| (g) | Adoption depends on institutional complements | H7 | **Supported documentarily** — not tested against data in this study | — |
| (h) | The algorithm is not the scarce factor | HA1 | **Supported** — 0.031 log points per SD on the yield level (p = 0.047) | `12_ai_observable.json` `HA1_…` |
| (i) | Value appears as input saving, conditional on complements | HA2 | **Supported** — +0.0496 on NUE (p = 0.014); zero at low complements, −0.2293 on N at high | manuscript Table 2 |
| (j) | Complement dependence is AI-specific, not generic | HA3 | **Supported** — opposite sign and margin vs the embodied waves and the placebo | manuscript Table 3 |
| (k) | The AI era trades output growth for input efficiency | HA4 | **Supported descriptively**; the causal DiD **fails** its pre-trend diagnostics | [S4](#table-s4), [S10](#table-s10) |
| (l) | A learned function does not transfer | HA5 | **Supported** — R² 0.5152 → −0.6603 across regions | [S6](#table-s6) |

*Note.* Three of the twelve verdicts are qualified rather than clean confirmations — (c),
(d) and (k) — and the study reports the failure in each case rather than the favourable
half. The evidence column points to the supplementary table or JSON object holding the
underlying numbers.

---

### Table S9

### World OpenAlex series, 2000–2024

The full annual series behind Figure 1 of the submitted version and behind every growth figure quoted in Section
4.7 of the manuscript. `ai_ag` = works matching (AI terms) AND (agricultural terms);
`precision_ag` = the narrow precision-agriculture query; `all works` = all indexed works;
`share` = 1,000 × ai_ag / all works.

| Year | `ai_ag` | `precision_ag` | All indexed works | Share (‰) |
|---|---|---|---|---|
| 2000 | 69 | 129 | 1,553,179 | 0.0444 |
| 2001 | 57 | 135 | 1,627,635 | 0.0350 |
| 2002 | 73 | 179 | 2,058,044 | 0.0355 |
| 2003 | 93 | 214 | 2,091,559 | 0.0445 |
| 2004 | 119 | 224 | 2,250,671 | 0.0529 |
| 2005 | 102 | 191 | 2,506,998 | 0.0407 |
| 2006 | 133 | 204 | 2,851,383 | 0.0466 |
| 2007 | 152 | 277 | 3,032,055 | 0.0501 |
| 2008 | 203 | 289 | 3,348,272 | 0.0606 |
| 2009 | 240 | 326 | 3,600,584 | 0.0667 |
| 2010 | 291 | 333 | 3,847,693 | 0.0756 |
| 2011 | 364 | 445 | 4,183,660 | 0.0870 |
| 2012 | 399 | 406 | 4,379,561 | 0.0911 |
| 2013 | 411 | 429 | 4,671,811 | 0.0880 |
| 2014 | 483 | 403 | 4,919,202 | 0.0982 |
| 2015 | 607 | 603 | 5,080,633 | 0.1195 |
| 2016 | 786 | 647 | 5,266,625 | 0.1492 |
| 2017 | 1,151 | 931 | 5,550,038 | 0.2074 |
| 2018 | 1,821 | 1,214 | 6,048,825 | 0.3011 |
| 2019 | 3,389 | 1,720 | 6,555,968 | 0.5169 |
| 2020 | 5,371 | 2,269 | 7,536,795 | 0.7126 |
| 2021 | 8,092 | 2,710 | 7,811,826 | 1.0359 |
| 2022 | 11,493 | 3,286 | 8,288,810 | 1.3866 |
| 2023 | 15,272 | 4,516 | 8,251,924 | 1.8507 |
| **2024** | **21,100** | **6,315** | 8,282,047 | **2.5477** |

| Derived quantity | Value |
|---|---|
| `ai_ag` multiplier 2000 → 2024 | ×305.80 |
| Share multiplier 2000 → 2024 | ×57.35 |
| Log-linear growth 2000–2015 | **15.83 %/year** |
| Log-linear growth 2016–2024 | **42.45 %/year** |

**Median agricultural-AI works per million inhabitants, 2019–2023, by income group**

| Income group | Median works per million |
|---|---|
| High income | 1.7545 |
| Upper middle income | 0.3517 |
| Lower middle income | 0.1738 |
| Not classified | 0.1622 |
| **Low income** | **0.0000** |

*Note.* Growth is not merely the expansion of the scientific literature: the *share* of world
research devoted to agricultural AI rises 57-fold, and the growth rate nearly triples after
2016, which is what justifies dating the wave from that year. The capability is absent from
the median low-income country. 2024 counts are provisional in any OpenAlex snapshot; see
[`OPENALEX_QUERIES.md`](OPENALEX_QUERIES.md) §7. Source: `results/12_ai_observable.json`,
`A_descriptivos_IA`.

---

### Table S10

### Event-study coefficients, base year 2015 (HA4)

Coefficients on `predetermined AI exposure × 1{year = t}` with 2015 omitted, so each entry
reads as a deviation from 2015. Two-way fixed effects, `log_area` and `temp_anom` as
controls, standard errors clustered by country. This is the numerical content of Figure S11 of the submitted version
and the diagnostic on which the paper's difference-in-differences is **rejected** as a
causal design.

| Year | ln(yield) b (p) | ln(N dose) b (p) | ln(NUE) b (p) |
|---|---|---|---|
| 2006 | −0.0279 (0.608) | 0.0865 (0.272) | −0.1144 (0.190) |
| 2007 | −0.0131 (0.839) | **0.1469 (0.018)** | −0.1600 (0.092) |
| 2008 | −0.0643 (0.234) | 0.1257 (0.151) | −0.1900 (0.070) |
| 2009 | 0.0028 (0.953) | **0.1229 (0.040)** | −0.1202 (0.127) |
| 2010 | 0.0390 (0.309) | **0.1797 (0.002)** | −0.1407 (0.076) |
| 2011 | 0.0098 (0.749) | **0.1077 (0.041)** | −0.0980 (0.106) |
| 2012 | 0.0021 (0.945) | 0.0610 (0.239) | −0.0589 (0.352) |
| 2013 | 0.0206 (0.555) | 0.0392 (0.379) | −0.0186 (0.764) |
| 2014 | −0.0292 (0.399) | 0.0649 (0.081) | **−0.0941 (0.045)** |
| *2015* | *base year (omitted)* | | |
| 2016 | −0.0102 (0.634) | 0.0209 (0.627) | −0.0311 (0.445) |
| 2017 | 0.0370 (0.387) | 0.0160 (0.751) | 0.0210 (0.757) |
| 2018 | 0.0144 (0.663) | 0.0358 (0.443) | −0.0214 (0.710) |
| 2019 | 0.0316 (0.351) | 0.0045 (0.935) | 0.0271 (0.664) |
| 2020 | 0.0537 (0.112) | 0.0023 (0.967) | 0.0514 (0.443) |
| 2021 | **0.0950 (0.011)** | 0.0545 (0.311) | 0.0405 (0.551) |
| 2022 | **0.0825 (0.029)** | 0.0958 (0.108) | −0.0133 (0.857) |
| 2023 | 0.0670 (0.091) | 0.0831 (0.135) | −0.0161 (0.826) |

| Pre-trend diagnostic (pre-2015 coefficients) | ln(yield) | ln(N dose) | ln(NUE) |
|---|---|---|---|
| Number significant at 5 % (of 9) | 0 | **4** | 1 |
| Minimum p-value | 0.234 | **0.002** | 0.045 |

**Difference-in-differences point estimates on the same sample** (n = 3,738, 169 countries),
exposure × post-2016:

| Outcome | b | SE | p | With non-AI research controlled: AI | non-AI |
|---|---|---|---|---|---|
| ln(yield) | 0.0464 | 0.0270 | 0.086 | 0.0467 (p = 0.084) | 0.0087 (p = 0.626) |
| ln(N dose) | −0.0485 | 0.0346 | 0.161 | −0.0536 (p = 0.113) | −0.1468 (p = 0.002) |
| ln(NUE) | **0.0948** | 0.0431 | **0.028** | 0.1003 (p = 0.011) | 0.1555 (p = 0.001) |

*Note.* **The parallel-trends assumption fails.** Four of the nine pre-2016 coefficients on
the nitrogen dose are individually significant (2007, 2009, 2010, 2011), and no discrete
break appears after 2016 — the post-period efficiency coefficients are small and
insignificant throughout. The DiD estimate therefore reflects convergence of pre-existing
differential trends, not an effect of the 2016 break, and the manuscript reports it as
descriptive only. None of the paper's AI-specific claims rest on it. Source:
`results/12_ai_observable.json`, `HA4_DiD_y_comparacion_de_eras.DiD`.

---

### Table S11

### Permutation importance and input-interaction coefficients (H1)

**Panel A — permutation importance**, gradient-boosting model, measured on the temporal
holdout test set (15 repeats). The value is the drop in R² when the feature is permuted.

| Feature | Importance | SD |
|---|---|---|
| `n_kg_ha` (nitrogen) | 0.4471 | 0.0180 |
| `irrig_share_cropland` (irrigation) | 0.2641 | 0.0141 |
| `log_arable` (scale) | 0.2534 | 0.0111 |
| `k_kg_ha` (potassium) | 0.0975 | 0.0069 |
| `p_kg_ha` (phosphorus) | 0.0524 | 0.0049 |
| `temp_anom` (climate) | 0.0089 | 0.0023 |
| `year` (trend) | 0.0000 | 0.0000 |

**Panel B — pairwise input interactions**, added to an additive linear model of `ln(yield)`
on standardised N, P, K and irrigation.

| Interaction | Coefficient | p |
|---|---|---|
| N × K | **−0.1221** | <0.001 |
| N × irrigation | **−0.1243** | <0.001 |
| N × P | **−0.0483** | <0.001 |
| K × irrigation | **+0.0689** | <0.001 |
| P × irrigation | +0.0138 | 0.077 |
| P × K | +0.0002 | 0.968 |

| Model | R² (in sample) |
|---|---|
| Additive | 0.4583 |
| With pairwise interactions | 0.5415 |
| **Gain from interactions** | **+0.0832** |

*Note.* The interactions are jointly and individually significant, so productivity is
non-separable — but the dominant ones are **negative**, indicating substitutability and
saturation at high doses rather than synergy. The correct reading of H1 is therefore that
productivity is irreducibly multivariate, not that the package is super-additive; the
negative signs are the same diminishing-returns phenomenon as H2, seen in cross-input form.
Sources: `results/06_yield_models.json` (`testB_importancia`),
`results/10_revision_analyses.json` (`I1_complementariedad`).

---

### Known numeric disagreements

Where `results/*.json` and `article/manuscrito_EN_v2.md` do not match, or where two scripts
estimate the same object differently. **None of these changes a substantive conclusion**,
but all are recorded rather than silently reconciled.

| # | Quantity | `results/*.json` | Manuscript | Assessment |
|---|---|---|---|---|
| 1 | **HA1 sample size** | `12_ai_observable.json` → `n_obs = 3716` | §4.8 of the submitted version states 3,716 (corrected) | **Genuine disagreement of one observation.** Re-running the HA1 listwise deletion on the shipped CSVs reproduces **3,716**. The manuscript figure equals the HA3 sample (3,715), which is one row smaller because HA3 also requires a defined complement index `z_comp`. The estimate (+0.0308, p = 0.0467) is unaffected. |
| 2 | **Absolute β-convergence** | `05_convergence.json`: β = +0.00092, p = 0.579, n = 144 · `10_revision_analyses.json`: β = +0.00206, p = 0.248, n = 142 | §4.6 quotes β = +0.002, p = 0.25 | **Two scripts, two samples** (144 vs 142 countries; the second is the balanced panel). Both are reported in [S7](#table-s7). Both are flat and insignificant, so the verdict — no absolute convergence — is identical. |
| 3 | **Yield × complements interaction (HA2 panel C)** | `−0.004465`, p = 0.6426 | Table 2 of the submitted version: −0.004 (p = 0.643) | **Rounding only.** −0.004465 rounds to −0.004 at three decimals; the manuscript prints −0.005. Both are statistically indistinguishable from zero, which is the claim being made. |
| 4 | **Inputs-only R² under spatial transfer** | `06_yield_models.json` GroupKFold GB: 0.4157, RMSE 2,021.3 · `10_revision_analyses.json`: 0.4199, RMSE 2,015.6 | Tables S2 and S3 below use 0.42 / 2,021 and 0.42 / 2,016 respectively | **Two scripts estimating the same object** with slightly different pipelines. Both round to R² = 0.42, so the manuscript's two tables are consistent to the precision printed, but the RMSEs differ by 6 kg/ha. Both are given in [S2](#table-s2) and [S3](#table-s3). |
| 5 | **DiD coefficient on nitrogen efficiency** | `HA4…DiD`: +0.0948, n = 3,738, p = 0.028 · `ROB_robustez` baseline: +0.0985, n = 3,794, p = 0.023 | §4.11 quotes +0.095; §4.13's alternatives are all relative to the ROB baseline | **Not a contradiction**: the same specification on two samples. `block_HA4` imposes the three-outcome common sample; `block_ROB` drops only on `log_nue` and the two controls, recovering 56 country-years. Both are reported, in [S10](#table-s10) and [S5](#table-s5) respectively. |
| 6 | **Univariate R² for `year`** | −0.0079 | the submitted manuscript omits the row | **Omission, not conflict.** Restored in [S1](#table-s1). |

Two further points of interpretation, flagged because a replicator will meet them:

- **The `05_convergence.json` σ-convergence panel reports 150 countries** while the β panel
  reports n = 144 and the balanced panel 142. These are three different restrictions of the
  same panel (any-year presence, endpoints present, all-years present), not three attempts
  at the same number.
- **`irrig_share_cropland` exceeds 100 % for some country-years** (maximum 450). This is a
  property of the FAOSTAT source — area *equipped for irrigation* can include agricultural
  land that is not cropland — and it is used as delivered, unclipped, in every model.


### Table S12

#### Hypothesis to analysis to metric map

| Hypothesis | Analysis | Main metric |
|---|---|---|
| H1 package | Univariate R² of each input vs. full package; permutation importance; interaction test | R² (temporal holdout); ΔR² from interactions |
| H2 diminishing returns | Decadal yield growth rates; partial productivity of N; partial dependence | %/year; kg·ha⁻¹/Mt N; partial-dependence (PD) slope |
| H3 ML vs. traditional | OLS vs. Random Forest vs. Gradient Boosting under two regimes | R², root mean squared error (RMSE) in temporal holdout and country GroupKFold |
| H4 local context | Inputs-only vs. +geography model, under temporal holdout and spatial transfer; variance decomposition | RMSE; R²; transferable vs. non-transferable ΔR² |
| H5 employment | Panel regression with country and year fixed effects; exogenous measure (mechanisation) | association (sign, significance) |
| H6 inequality | σ-convergence (full and balanced panel) and absolute and conditional β-convergence | standard deviation (SD) of log-yield; β |
| HA1 algorithm not scarce | Two-way FE of log yield on AI intensity, inputs controlled | coefficient per SD of AI |
| HA2 margin and conditionality | Common-sample decomposition into yield, nitrogen dose and nitrogen efficiency; interaction with predetermined complements; horse race vs. non-AI research | coefficient per SD; interaction; marginal effects at P10/P50/P90 |
| HA3 not generic | Same interaction specification applied to fertiliser, mechanisation, AI and a non-AI placebo | sign and size of technology × complements interaction |
| HA4 era comparison | Era growth rates of yield, nitrogen dose and nitrogen efficiency; continuous-treatment DiD with event study | %/year; DiD coefficient; pre-trend diagnostics |
| HA5 transferability | Train-on-region, test-on-region transfer matrix; region-specific nitrogen elasticities | R² within vs. across region; elasticity range |

*Note:* H7 (adoption is conditioned by institutional complements) is supported documentarily and is not tested against data in this study.

### Table numbering

The submitted manuscript contains Tables 1 (data blocks), 2 (HA2, where the value of AI appears) and 3 (HA3, four technological waves), and Figures 1–5. The three pre-AI results tables of earlier drafts are Tables S1–S3 here, and the earlier Figures 1–10 are Figures S1–S10.
