# Data dictionary

Every variable in `data/processed/` and every variable constructed inside the analysis
scripts: name, definition, unit, source, coverage in the shipped files, and transformation.

Coverage figures below are the **non-missing counts in the shipped CSVs**, not the
estimation samples. Estimation samples are listed in [`LINKAGE.md`](LINKAGE.md).

Conventions used throughout:

- `iso3` — ISO 3166-1 alpha-3 country code. The join key, together with `year`.
- `year` — calendar year (integer). FAOSTAT "meteorological year" for the temperature anomaly.
- `kha` suffix — thousand hectares (FAOSTAT native unit for land-use areas).
- Logs written `log1p(x)` are `ln(1+x)`; logs written `ln(x)` are exact and drop non-positive values.

---

## 1. `data/processed/country_panel.csv` — the main analytical panel

13,975 rows × 29 columns · 215 ISO3 codes · years 1960–2024 · 2.9 MB.
Built by `code/03_build_panel.py` from `wb_panel.csv` (spine) left-joined to FAOSTAT country series.
This is the file every analysis script except `12_ai_observable.py`'s AI block reads first.

| Variable | Definition | Unit | Source | Coverage in file | Transformation |
|---|---|---|---|---|---|
| `iso3` | Country code | — | pycountry (ISO 3166-1 alpha-3) | 13,975 | Join key |
| `country` | Country name as returned by the World Bank API | — | World Bank | 13,975 | — |
| `year` | Calendar year | year | — | 13,975, 1960–2024 | Join key |
| `cereal_yield_kg_ha` | Cereal yield | kg/ha | World Bank `AG.YLD.CREL.KG` (FAO origin) | 10,343 · 1961–2024 | Target; enters as `ln(yield)` |
| `cereal_prod_mt` | Cereal production | tonnes | World Bank `AG.PRD.CREL.MT` | 10,397 · 1961–2024 | — |
| `cereal_area_ha` | Land under cereal production | ha | World Bank `AG.LND.CREL.HA` | 10,397 · 1961–2024 | Weight for the area-weighted world yield in HA4 |
| `fert_kg_ha_arable` | Fertiliser consumption per arable hectare | kg/ha | World Bank `AG.CON.FERT.ZS` | 10,161 · 1961–2023 | Not used in the reported models (FAOSTAT RFN preferred) |
| `arable_land_ha` | Arable land | ha | World Bank `AG.LND.ARBL.HA` | 11,871 · 1961–2023 | — |
| `agri_land_pct` | Agricultural land | % of land area | World Bank `AG.LND.AGRI.ZS` | 12,060 · 1961–2023 | — |
| `irrigated_pct_agri` | Agricultural irrigated land | % of agricultural land | World Bank `AG.LND.IRIG.AG.ZS` | 1,214 · 1990–2023 | Too sparse to use; FAOSTAT `irrig_share_cropland` used instead |
| `agri_empl_pct` | Employment in agriculture | % of total employment | World Bank `SL.AGR.EMPL.ZS` (ILO modelled) | 6,315 · 1991–2024 | Outcome in H5 |
| `agri_va_pct_gdp` | Agriculture value added | % of GDP | World Bank `NV.AGR.TOTL.ZS` | 8,866 · 1960–2024 | — |
| `agri_va_per_worker` | Agriculture value added per worker | constant 2015 US$ | World Bank `NV.AGR.EMPL.KD` | 5,417 · 1991–2024 | Regressor in H5, entered in logs; **mechanically linked to `agri_empl_pct`** (shared worker count) |
| `rural_pop_pct` | Rural population | % of total | World Bank `SP.RUR.TOTL.ZS` | 13,975 · 1960–2024 | — |
| `population` | Total population | persons | World Bank `SP.POP.TOTL` | 13,945 · 1960–2024 | Denominator for AI works per million |
| `forest_pct` | Forest area | % of land area | World Bank `AG.LND.FRST.ZS` | 7,029 · 1990–2023 | Control, not in the reported models |
| `n_total_t` | Nitrogen N, agricultural use, total | tonnes of nutrient N | FAOSTAT RFN, item "Nutrient nitrogen N (total)", element "Agricultural Use" | 9,961 · 1961–2023 | World aggregate used for the ×10 claim in H2 |
| `n_kg_ha` | Nitrogen N per area of cropland | kg N/ha cropland | FAOSTAT RFN, element "Use per area of cropland" | 9,939 · 1961–2023 | Core input; `log_n = log1p`, `log_n_x = ln` (obs. with `n_kg_ha < 1` dropped) |
| `p_kg_ha` | Phosphate P₂O₅ per area of cropland | kg P₂O₅/ha cropland | FAOSTAT RFN | 9,658 · 1961–2023 | `log_p = log1p` |
| `k_kg_ha` | Potash K₂O per area of cropland | kg K₂O/ha cropland | FAOSTAT RFN | 9,437 · 1961–2023 | `log_k = log1p`. **Data note:** the FAOSTAT series contains one slightly negative value (min −0.13); it is left as delivered |
| `arable_kha` | Arable land | 1,000 ha | FAOSTAT RL, item "Arable land", element "Area" | 11,871 · 1961–2023 | Scale control; `log_arable = ln(clip(x,1))` in `06`, `log_area = log1p` in `12` |
| `cropland_kha` | Cropland | 1,000 ha | FAOSTAT RL, item "Cropland" | 11,997 · 1961–2023 | Denominator of `irrig_share_cropland` |
| `agri_land_kha` | Agricultural land | 1,000 ha | FAOSTAT RL, item "Agricultural land" | 12,060 · 1961–2023 | — |
| `irrig_equip_kha` | Area equipped for irrigation | 1,000 ha | FAOSTAT RL, item "Land area equipped for irrigation" | 9,925 · 1961–2023 | "Equipped" ≠ "actually irrigated"; see caveat below |
| `irrig_actual_kha` | Agriculture area actually irrigated | 1,000 ha | FAOSTAT RL | 1,181 · 1990–2023 | Too sparse to use |
| `tractors` | Agricultural tractors in use | units | FAOSTAT RM, item "Agricultural tractors", element "In Use" | 6,310 · **1961–2009** | FAOSTAT discontinued the in-use series after 2009 |
| `temp_anom` | Temperature change, meteorological year | °C relative to the 1951–1980 baseline | FAOSTAT ET, element "Temperature change", Months = "Meteorological year" | 11,977 · 1961–2024 | Climate control, entered in levels |
| `tractors_per_1000ha_arable` | Mechanisation intensity | tractors per 1,000 ha arable | Derived | 6,259 · 1961–2009 | `tractors / arable_kha`; `log_mech = log1p` |
| `irrig_share_cropland` | Share of cropland equipped for irrigation | % | Derived | 9,925 · 1961–2023 | `100 × irrig_equip_kha / cropland_kha`. **Can exceed 100** (max 450) where equipped area includes agricultural land that is not cropland; used as delivered, entered as `irr` |

**Caveats carried into the paper.** (i) The tractor series ends in 2009, which is why the
mechanisation wave in HA3 is dated 1961–2009. (ii) "Equipped for irrigation" is an
infrastructure stock, not water actually applied, so absolute irrigation magnitudes should
be read with care. (iii) Fertiliser is measured per hectare of *cropland* while yield is
measured per hectare of *cereal* area; the ratio `nue` therefore mixes denominators and is a
national efficiency index, not an agronomic partial factor productivity.

---

## 2. `data/processed/ai_panel.csv` — OpenAlex + digital complements

9,290 rows × 15 columns · 271 `iso3` values · years 1990–2024 · 0.9 MB.
Built by `code/11_download_ai_indicators.py`.

> The 271 codes include World Bank **aggregates** (`WLD`, `EUU`, `ARB`, income groups …),
> because the World Bank cleaning step keeps any code matching `[A-Z]{3}`. Aggregates are
> eliminated later, at the merge into `country_panel.csv` — see [`LINKAGE.md`](LINKAGE.md).

| Variable | Definition | Unit | Source | Coverage in file | Transformation |
|---|---|---|---|---|---|
| `iso3` | Country **or aggregate** code | — | World Bank API / pycountry (from OpenAlex ISO2) | 9,290 | Join key |
| `year` | Calendar year | year | — | 9,290 · 1990–2024 | Join key |
| `internet_users_pct` | Individuals using the internet | % of population | World Bank `IT.NET.USER.ZS` | 6,774 · 1990–2024 | Complement 1/5 |
| `mobile_subs_per100` | Mobile cellular subscriptions | per 100 people | World Bank `IT.CEL.SETS.P2` | 8,497 · 1990–2024 | Complement 2/5 |
| `broadband_per100` | Fixed broadband subscriptions | per 100 people | World Bank `IT.NET.BBND.P2` | 5,247 · 1998–2024 | Complement 3/5 |
| `rd_pct_gdp` | R&D expenditure | % of GDP | World Bank `GB.XPD.RSDV.GD.ZS` | 3,139 · 1996–2024 | Downloaded, not used in reported models (too sparse) |
| `researchers_per_mn` | Researchers in R&D | per million people | World Bank `SP.POP.SCIE.RD.P6` | 2,425 · 1996–2024 | Downloaded, not used (too sparse) |
| `tertiary_enrol_pct` | Gross tertiary enrolment ratio | % | World Bank `SE.TER.ENRR` | 5,134 · 1990–2024 | Complement 4/5 |
| `electricity_rural_pct` | Rural access to electricity | % of rural population | World Bank `EG.ELC.ACCS.RU.ZS` | 7,570 · 1990–2024 | Complement 5/5 |
| `gdp_pc_const2015` | GDP per capita | constant 2015 US$ | World Bank `NY.GDP.PCAP.KD` | 8,609 · 1990–2024 | `log_gdp = ln`; income control in the robustness block |
| `upper_secondary_pct` | Population with upper-secondary education | % | World Bank `SE.SEC.CUAT.UP.ZS` | 2,357 · 1990–2024 | Downloaded, not used (too sparse) |
| `oa_ai_ag` | Works whose title/abstract matches (AI terms) AND (agricultural terms) | count of works | OpenAlex `/works`, `group_by=authorships.countries` | 5,013 · 2000–2024 | Numerator of both AI measures |
| `oa_ai_all` | Works matching AI terms (any field) | count of works | OpenAlex | 5,013 · 2000–2024 | Subtracted from `oa_works_all` to build the non-AI placebo |
| `oa_precision_ag` | Works matching the narrower precision-agriculture query | count of works | OpenAlex | 5,013 · 2000–2024 | Alternative exposure |
| `oa_works_all` | All indexed works (no topical filter) | count of works | OpenAlex | 5,013 · 2000–2024 | Denominator of the specialisation measure |

The three exact query strings and the country-attribution rule are in
[`OPENALEX_QUERIES.md`](OPENALEX_QUERIES.md).

---

## 3. Other processed files

| File | Rows | Content | Built by | Used by |
|---|---|---|---|---|
| `wb_panel.csv` | 17,290 × 16 | Raw wide World Bank panel before the pycountry country filter; same columns as the World Bank block of `country_panel.csv`, but 261 codes including aggregates | `01_download_worldbank.py` | `03_build_panel.py` |
| `country_meta.csv` | 217 × 6 | `iso3`, `country`, `region`, `region_id`, `income`, `income_id`. World Bank classification, aggregates already removed | `03b_country_meta.py` | `06`, `10`, `12` |
| `qcl_world_raw.csv` | 45,733 × 6 | FAOSTAT QCL rows for `Area Code == 5000` (World) only, extracted from the 545 MB bulk file | `03_build_panel.py` | `04_macro_trends.py` |
| `world_production_long.csv` | 17,832 × 6 | QCL World subset, `Element == "Production"` | `03_build_panel.py` | `04` (Figure 1, *core3* aggregate) |
| `world_yield_long.csv` | 10,711 × 6 | QCL World subset, `Element == "Yield"` | `03_build_panel.py` | `04` (Figure 2, decadal yield growth) |
| `world_N.csv` | 64 × 2 | `year`, `n_total_t_world` — world nitrogen agricultural use | `03_build_panel.py` | `04` (Figure 4, partial productivity of N) |
| `world_temp.csv` | 66 × 2 | `year`, `temp_anom_world` | `03_build_panel.py` | `04` |
| `spain_series.csv` | 66 × 7 | Spain (FAOSTAT area code 203): `n_kg_ha`, `tractors`, `arable_kha`, `irrig_equip_kha`, `agri_land_kha`, `temp_anom` | `03_build_panel.py` | `04` (Figure 3, ha per tractor) |

`qcl_world_raw.csv`, `world_production_long.csv` and `world_yield_long.csv` keep the raw
FAOSTAT column names: `Area Code`, `Item`, `Element`, `Year`, `Unit`, `Value`.

---

## 4. Variables constructed inside the scripts (never written to disk)

### 4.1 Yield-model features (`code/06_yield_models.py`, `code/10_revision_analyses.py`)

| Name | Definition | Notes |
|---|---|---|
| `y` | `ln(cereal_yield_kg_ha)` | Target. Observations with yield ≤ 0 dropped |
| `log_arable` | `ln(max(arable_kha, 1))` | Scale feature |
| Feature set | `n_kg_ha`, `p_kg_ha`, `k_kg_ha`, `irrig_share_cropland`, `temp_anom`, `log_arable`, `year` | Seven features; the "full package" of H1 |
| `region`, `income` | World Bank classification, one-hot encoded | The *transferable* geography in H4 |
| `iso3` dummies | Country fixed effects | The *non-transferable* geography in H4 |

Missing features are median-imputed and standardised **inside** the scikit-learn pipeline, so
the imputer and scaler are fitted on training folds only (no leakage). Random seed 42.
Models: `LinearRegression`; `RandomForestRegressor(n_estimators=400, min_samples_leaf=3)`;
`HistGradientBoostingRegressor(max_iter=500, learning_rate=0.05, l2_regularization=1.0)`.

### 4.2 AI-block variables (`code/12_ai_observable.py`)

| Name | Definition | Unit | Notes |
|---|---|---|---|
| `pop_mn` | `population / 1e6` | millions | Denominator |
| `ai_ag_pc` | `oa_ai_ag / pop_mn` | works per million people | **Volume** normalisation |
| `ai_ag_share` | `1000 × oa_ai_ag / oa_works_all` | works per 1,000 works | **Specialisation** normalisation; `oa_works_all == 0` → missing |
| `pa_pc` | `oa_precision_ag / pop_mn` | works per million | Alternative exposure |
| `log_ai_ag` | `log1p(ai_ag_pc)` | — | Volume measure, standardised to `z_ai` |
| `log_ai_spec` | `log1p(ai_ag_share)` | — | **Identifying measure**, standardised to `z_spec` |
| `log_pa` | `log1p(pa_pc)` | — | — |
| `log_nonai_res` | `log1p(max(oa_works_all − oa_ai_all, 0) / pop_mn)` | — | Non-AI research capacity; standardised to `z_res`. Placebo and horse-race regressor |
| `log_yield` | `ln(cereal_yield_kg_ha)` | — | Output margin |
| `nue` | `cereal_yield_kg_ha / n_kg_ha`, set missing when `n_kg_ha < 1` | kg grain per kg N | Nitrogen use efficiency |
| `log_nue` | `ln(nue)` | — | Efficiency margin |
| `log_n_x` | `ln(n_kg_ha)` where `n_kg_ha ≥ 1`, else missing | — | Input margin. **Exact** log so that `log_nue ≡ log_yield − log_n_x` |
| `log_n`, `log_p`, `log_k`, `log_area`, `log_mech`, `log_gdp` | `log1p` of the corresponding level (`log_gdp` is exact `ln`) | — | Controls |
| `irr` | `irrig_share_cropland` | % | Control / complement in the pre-AI waves |
| `comp_pre` | Country mean of `internet_users_pct`, `broadband_per100`, `mobile_subs_per100`, `tertiary_enrol_pct`, `electricity_rural_pct` over **2000–2005**, each standardised first, then averaged across the five | z-score | **Predetermined** complement index; time-invariant. Standardised again to `z_comp` |
| `exposure` | Country mean of `log_ai_ag` over **2010–2015** | — | Predetermined volume exposure for the DiD |
| `exposure_spec` | `log1p(1000 × Σ oa_ai_ag / Σ oa_works_all)` over **2010–2015** | — | Predetermined specialisation exposure; the DiD baseline |
| `exposure_pa` | Country mean of `log_pa` over 2010–2015 | — | Precision-agriculture exposure |
| `exposure_placebo` | Country mean of `log_nonai_res` over 2010–2015 | — | Non-AI research placebo exposure |
| `post` | `1{year ≥ cut}`, cut ∈ {2015, 2016, 2017} | 0/1 | DiD post indicator |

**The accounting identity.** Because `log_nue = log_yield − log_n_x` uses exact logarithms,
and because HA2 is estimated on a sample where all three outcomes are non-missing, the
coefficient on the efficiency margin is *exactly* the yield coefficient minus the nitrogen
coefficient. This is why the common-sample restriction (3,659 observations) matters and is
enforced explicitly in `block_HA2`.

**Standardisation.** `z(x) = (x − mean(x)) / sd(x)` with `ddof=0`, computed on the analysis
subset in force at that point in the script. All reported AI coefficients are therefore
"per standard deviation of the AI measure **within the estimation sample**".

### 4.3 Estimation conventions for every regression in `12_ai_observable.py`

- `statsmodels` OLS with `C(iso3)` and `C(year)` dummies — two-way fixed effects.
- Standard errors clustered by `iso3` (`cov_type="cluster"`).
- Marginal effects at P10/P50/P90 of `z_comp` with delta-method standard errors
  (`Var = V₁₁ + c²V₃₃ + 2cV₁₃`) and normal-approximation p-values.
- The event study omits the base year 2015 explicitly, so coefficients read as deviations
  from 2015; the time-invariant exposure itself is absorbed by the country fixed effects.

---

## 5. Data not shipped

`data/raw/` is **excluded** from this repository. It totals ~715 MB, dominated by
`faostat_QCL.csv` (545 MB), which exceeds any reasonable repository limit and exceeds the
50 MB per-file ceiling applied here. Every raw file is regenerated exactly by running
`code/01_download_worldbank.py`, `code/02_download_faostat.py` and
`code/11_download_ai_indicators.py`. The processed CSVs shipped here are the complete input
to every analysis script from step 4 onward, so the raw layer is only needed to re-derive
them from scratch.

| Excluded raw file | Size | Regenerated by |
|---|---|---|
| `faostat_QCL.csv` | 545 MB | `code/02_download_faostat.py` |
| `faostat_ET.csv` | 65 MB | `code/02_download_faostat.py` |
| `faostat_RL.csv` | 49 MB | `code/02_download_faostat.py` |
| `faostat_RFN.csv` | 35 MB | `code/02_download_faostat.py` |
| `faostat_RM.csv` | 20 MB | `code/02_download_faostat.py` |
| `wb_*.csv` (23 files) | ~9 MB total | `code/01_download_worldbank.py`, `code/11_download_ai_indicators.py` |
| `openalex_*.csv` (8 files) | ~0.2 MB total | `code/11_download_ai_indicators.py` |
