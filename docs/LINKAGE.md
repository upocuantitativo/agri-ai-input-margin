# Record linkage: FAOSTAT + World Bank + OpenAlex

How three sources with three different country vocabularies become one country-year panel,
which rows survive each step, and why two specific filters are load-bearing.

**The join key is always `(iso3, year)`.** ISO 3166-1 alpha-3 is the pivot; FAOSTAT arrives
as M49 numeric codes, OpenAlex as ISO 3166-1 alpha-2, the World Bank already as alpha-3.

```
World Bank API ──► wb_panel.csv ──┐
  (alpha-3)        17,290 rows     │  pycountry alpha-3 validity filter
                   261 codes       ├──► country_panel.csv ──┐
FAOSTAT bulk ──► M49 → alpha-3 ────┘    13,975 rows          │
  (M49 numeric)    + China fix           215 countries       │  left join on (iso3, year)
                                                             ├──► AI analysis frame
OpenAlex API ──► alpha-2 → alpha-3 ──► ai_panel.csv ─────────┘
  (alpha-2)        + [A-Z]{3} filter     9,290 rows
                                         271 codes
                    World Bank country metadata ──► country_meta.csv (region, income)
```

---

## 1. World Bank → `wb_panel.csv`

`code/01_download_worldbank.py`. Fifteen indicators from
`https://api.worldbank.org/v2/country/all/indicator/{code}`, `format=json`,
`per_page=20000`, `date=1960:2024`. Each JSON record yields
`(countryiso3code, country.value, date, value)`.

The fifteen wide frames are merged **outer** on `["iso3", "country", "year"]`.
Result: 17,290 rows, 261 distinct `iso3` values, of which 325 rows carry an empty
`countryiso3code` (World Bank regional and income aggregates return a blank alpha-3).
No filtering happens at this stage; `wb_panel.csv` is the unfiltered download.

`code/03b_country_meta.py` separately pulls `https://api.worldbank.org/v2/country`
and drops every row whose `region` is literally `"Aggregates"`, giving
`country_meta.csv`: 217 countries with `region` and `income`. The region taxonomy is the
World Bank's current one, in which South Asia is split and Afghanistan and Pakistan sit in
`"Middle East, North Africa, Afghanistan & Pakistan"` — this matters for the HA5 transfer
matrix (Section 6).

---

## 2. FAOSTAT → country series

`code/02_download_faostat.py` fetches five bulk "(Normalized)" ZIPs from
`bulks-faostat.fao.org` (QCL, RFN, RL, RM, ET) and extracts the CSV inside, `latin-1`
encoded. `code/03_build_panel.py` then reduces each domain to `(iso3, year, value)` via
`fao_country_series()`, which applies, in this order:

1. **Item / element / months / unit filter** — e.g. item `"Nutrient nitrogen N (total)"`,
   element `"Use per area of cropland"`; for the temperature domain, `Months == "Meteorological year"`.
2. **`Area Code < 5000`** — FAOSTAT reserves codes ≥ 5000 for aggregates (5000 = World,
   plus continents and economic groupings). This is the primary aggregate filter.
3. **`Area Code ∉ {351}`** — code 351 is FAOSTAT's *"China"* aggregate, which sums mainland
   China, Taiwan, Hong Kong and Macao. It is dropped so that China is not double-counted.
4. **M49 → ISO3.** `Area Code (M49)` is stripped of non-digits, zero-padded to three
   characters, and resolved with `pycountry.countries.get(numeric=...)`, taking `.alpha_3`.
   Rows that do not resolve (dissolved states, FAOSTAT-only entities) are dropped.
5. **The manual "China, mainland" fix.**
   ```python
   M49_OVERRIDE_AREACODE = {41: "CHN"}   # China, mainland -> CHN
   ...
   over = d["Area Code"].map(M49_OVERRIDE_AREACODE)
   d["iso3"] = over.where(over.notna(), iso)
   ```
   FAOSTAT splits China into four entities, and getting exactly one of them into `CHN`
   requires deliberate handling:

   | FAOSTAT `Area Code` | `Area` | `Area Code (M49)` | pycountry resolves to | Fate |
   |---|---|---|---|---|
   | 41 | China, mainland | `'156` | `CHN` | **kept, pinned to `CHN` by the override** |
   | 351 | China | `'159` | *unresolvable* | **excluded by `EXCLUDE_AREACODE = {351}`** |
   | 214 | China, Taiwan Province of | `'158` | `TWN` | kept as `TWN` |

   Area code 351 is the *aggregate* "China", which sums mainland China with the
   separately-reported Chinese territories; leaving it in would double-count the largest
   cereal producer and nitrogen user in the panel. In the FAOSTAT vintage shipped with this project it happens to carry M49
   `159`, which `pycountry` cannot resolve, so it would fall out anyway — the explicit
   exclusion makes the decision deliberate rather than accidental. Symmetrically, the
   `{41: "CHN"}` override takes precedence over the M49 lookup for mainland China; in this
   vintage the lookup would already return `CHN`, so the override is defensive, guarding
   against FAOSTAT releases in which "China, mainland" carries a non-standard M49 code (as
   it has historically) and mainland China would otherwise vanish from every FAOSTAT
   variable while the World Bank spine kept supplying `CHN` rows — yielding a China with
   cereal yields but no fertiliser. You can verify the current mapping with the snippet in
   Section 7.
6. **Duplicate collapse.** `groupby(["iso3", "year"])["value"].mean()`. Any residual
   many-to-one situation (two FAOSTAT areas mapping to one ISO3) is averaged, not summed.

The eleven resulting series (N total, N/P/K per cropland hectare, arable, cropland,
agricultural land, equipped irrigation, actual irrigation, tractors, temperature anomaly)
are merged pairwise **outer** on `(iso3, year)`.

---

## 3. `country_panel.csv` — the main panel

`code/03_build_panel.py`, final merge:

```python
wb["is_country"] = wb["iso3"].apply(lambda c: pycountry.countries.get(alpha_3=str(c)) is not None)
wb_countries    = wb[wb["is_country"]]
panel           = wb_countries.merge(fao, on=["iso3", "year"], how="left")
```

The **World Bank frame is the spine and FAOSTAT is joined left onto it**, so the panel's
universe of country-years is the World Bank's. `pycountry` validity is what removes the
World Bank aggregates: `WLD`, `EUU`, `ARB`, `LIC`, `OED` and the rest are not ISO 3166-1
alpha-3 codes and therefore fail the test, along with the 325 blank-code rows.

| Step | Rows | Distinct `iso3` |
|---|---|---|
| `wb_panel.csv` as downloaded | 17,290 | 261 (incl. aggregates and blanks) |
| after pycountry alpha-3 validity filter | 13,975 | 215 |
| `country_panel.csv` (after left-joining FAOSTAT) | 13,975 | 215 |

Two derived columns are added here: `tractors_per_1000ha_arable = tractors / arable_kha`
and `irrig_share_cropland = 100 × irrig_equip_kha / cropland_kha`.

### The modellable yield panel: 8,364 observations, 172 countries, 1961–2023

`code/06_yield_models.py` joins `country_meta.csv` on `iso3` and then drops any row missing
the target or any of the seven features:

```python
FEATS  = ["n_kg_ha", "p_kg_ha", "k_kg_ha", "irrig_share_cropland",
          "temp_anom", "arable_kha", "year"]
d = df.dropna(subset=["cereal_yield_kg_ha"] + FEATS + ["region"])
d = d[d["cereal_yield_kg_ha"] > 0]
```

This listwise deletion — driven mainly by the potash series (9,437 non-missing) and the
equipped-irrigation series (9,925) — takes 13,975 country-years down to **8,364
observations from 172 countries, 1961–2023**. This is the sample reported in the paper's
Section 3.1 and the sample underlying H1–H4 and HA5.

> 172 countries here versus 215 in `country_panel.csv`: 43 codes have no country-year with
> the complete input package (small island states, micro-states, and countries whose
> FAOSTAT fertiliser series is empty).

---

## 4. OpenAlex → `ai_panel.csv`

`code/11_download_ai_indicators.py`. Four queries × 25 years (2000–2024) against
`https://api.openalex.org/works` with `group_by=authorships.countries`; see
[`OPENALEX_QUERIES.md`](OPENALEX_QUERIES.md) for the query strings and the attribution rule.
Each group key is a URL ending in an alpha-2 code; keys whose tail is not exactly two
characters are discarded.

**ISO2 → ISO3.**

```python
def iso2_to_iso3(c):
    try:    return pycountry.countries.get(alpha_2=c).alpha_3
    except: return None
```

Unmappable codes are dropped. The four query frames are merged **outer** on `(iso2, year)`,
missing counts are filled with `0` (a country absent from a group-by for a given year and
query genuinely published zero such works), the alpha-3 column is created, and
`groupby(["iso3", "year"]).sum()` collapses any alpha-2 codes that resolve to the same
alpha-3.

**The `[A-Z]{3}` filter on the World Bank side — and why it is load-bearing.**
The nine digital-complement indicators are cleaned before merging:

```python
def _clean_wb(df, name):
    df = df.rename(columns={"value": name})[["iso3", "year", name]]
    df["iso3"] = df["iso3"].astype(str).str.strip()
    df = df[df["iso3"].str.fullmatch(r"[A-Z]{3}")]          # <-- the filter
    df = df.drop_duplicates(subset=["iso3", "year"], keep="first")
    return df
```

The script's own docstring records the failure this prevents:

> *"La API del Banco Mundial devuelve algunas filas con countryiso3code vacio (agregados
> regionales); si no se filtran, el merge multiple genera un producto cartesiano de miles
> de millones de filas."*
> (The World Bank API returns some rows with an empty `countryiso3code` — regional
> aggregates. If they are not filtered out, the multi-way merge produces a Cartesian
> product of billions of rows.)

The mechanism: the blank code `""` is not a unique key. Nine indicators each contributing
hundreds of blank-code rows for the same `year` are merged outer on `(iso3, year)`; the
blank group in frame *k* matches *every* blank row of the same year in frame *k+1*, and the
row count multiplies at each of the eight successive merges. `str.fullmatch(r"[A-Z]{3}")`
removes blanks and lowercase/malformed codes in one step; `drop_duplicates` on
`(iso3, year)` guarantees each frame is keyed one-row-per-country-year, which makes every
subsequent merge one-to-one.

Note that this filter is **not** a country filter: it keeps World Bank aggregates such as
`WLD`, `EUU` and `ARB`, which are perfectly valid `[A-Z]{3}` strings. That is why
`ai_panel.csv` carries 271 distinct codes against `country_panel.csv`'s 215. The aggregates
are eliminated one step later, in Section 5.

Final assembly: `wb_panel.merge(oa, on=["iso3", "year"], how="outer")` → `ai_panel.csv`,
9,290 rows × 15 columns, 1990–2024 (World Bank indicators from 1990, OpenAlex counts from
2000).

---

## 5. The AI analysis frame

`code/12_ai_observable.py`, `load()`:

```python
df = country_panel.merge(ai_panel, on=["iso3", "year"], how="left")
df = df.merge(country_meta[["iso3", "region", "income"]], on="iso3", how="left")
```

The join is **left on `country_panel`**, which is the step that discards the World Bank
aggregates carried in `ai_panel.csv`: `WLD` and friends have no row in `country_panel.csv`
(they failed the pycountry test in Section 3), so they never enter the AI analysis frame.
Both frames are keyed one-row-per-`(iso3, year)`, so the join is one-to-one and the row
count of `country_panel.csv` is preserved exactly.

### Resulting estimation samples

Each block applies its own listwise deletion on the variables it needs.

| Block | Restriction | Obs. | Countries | Period |
|---|---|---|---|---|
| Yield models H1/H3/H4, and HA5 | target + 7 features + `region` non-missing | **8,364** | **172** | 1961–2023 |
| HA1 (unconditional AI → yield) | `log_yield`, `log_ai_ag`, `log_n`, `log_p`, `log_k`, `irr`, `log_area`, `temp_anom` | 3,716 ⚠ | 168 | 2000–2023 |
| HA2 (margin decomposition) | **common sample**: `log_yield`, `log_n_x`, `log_nue`, `z_ai`, `z_spec`, `z_res`, `log_area`, `temp_anom` all non-missing | **3,659** | **169** | 2000–2023 |
| HA3, AI wave | `log_yield`, `z_tech`, `z_comp`, `log_n`, `log_p`, `log_k`, `irr`, `log_area`, `temp_anom` | 3,715 | 168 | 2000–2023 |
| HA3, fertiliser wave | same form, technology = `log_n`, complements = `irr` + `log_mech` | 3,441 | 136 | 1961–1990 |
| HA3, mechanisation wave | technology = `log_mech`, complements = `irr` + `log_n` | 4,686 | 158 | 1961–2009 |
| HA3, non-AI placebo | technology = `log_nonai_res` | 3,715 | 168 | 2000–2023 |
| HA4 DiD / event study | common sample on the three outcomes + `z_exp`, `z_res`, `log_area`, `temp_anom` | 3,738 | 169 | 2000–2023 |
| Robustness block, baseline | `log_nue`, `z_e`, `log_area`, `temp_anom` only (no common-sample restriction) | 3,794 | — | 2000–2023 |

> ⚠ **`results/12_ai_observable.json` reports `n_obs = 3716` for HA1, while the manuscript
> text (Section 4.8) states 3,715.** Re-running the HA1 listwise deletion on the shipped
> processed CSVs reproduces **3,716**. The manuscript figure appears to be the HA3 sample
> size (3,715), which differs because HA3 additionally drops the single country-year with
> no non-missing digital complement at all and therefore an undefined `z_comp`. The
> substantive estimate (+0.031 log points, p = 0.047) is unaffected. See
> [`SUPPLEMENTARY_TABLES.md`](SUPPLEMENTARY_TABLES.md), "Known numeric disagreements".

> **Why the AI sample is 3,659.** HA2 is not a subset of HA1/HA3: it drops the P, K and
> irrigation controls but adds `log_n_x` and `log_nue`, which are set missing whenever
> `n_kg_ha < 1`. Requiring only yield, the three AI measures and the two controls leaves
> 3,966 country-years; 307 of those have no defined nitrogen dose or efficiency, giving
> **3,659**. Restricting all three outcomes to the same rows is what makes the
> decomposition `log_nue ≡ log_yield − log_n_x` hold exactly in the coefficients — the
> identity the paper's Table 5 leans on.

> **Why the robustness baseline is 3,794.** `block_ROB` drops only on `log_nue` and the two
> controls, not on the three-outcome common sample, so it recovers the 56 country-years that
> HA4's DiD sample loses. This is why the DiD efficiency coefficient appears as +0.0948
> (n = 3,738) in the HA4 block and +0.0985 (n = 3,794) as the robustness baseline. They are
> the same specification on slightly different samples, not a discrepancy.

---

## 6. The HA5 region partition

`block_HA5` uses the same 8,364-observation pool and keeps only World Bank regions with at
least 300 observations:

```python
regions = [r for r in d.region.dropna().unique() if (d.region == r).sum() >= 300]
```

| Region | Observations in the pool | In the transfer matrix? |
|---|---|---|
| Sub-Saharan Africa | 2,080 | yes |
| Europe & Central Asia | 2,004 | yes |
| Latin America & Caribbean | 1,783 | yes |
| Middle East, North Africa, Afghanistan & Pakistan | 1,076 | yes |
| East Asia & Pacific | 1,022 | yes |
| South Asia | 273 | **no** — below the 300 threshold |
| North America | 126 | **no** — below the 300 threshold |

Hence "5 regions" in the results JSON and a 5 × 5 matrix. Note that under the current World
Bank taxonomy South Asia contains only 6 countries (Afghanistan and Pakistan having moved to
the MENA grouping), which is why it falls below the threshold. Diagonal cells are a temporal
holdout *within* the region (train ≤ 2009, test ≥ 2010); off-diagonal cells train on the
whole of the row region and evaluate on the whole of the column region.

---

## 7. Reproducing the linkage checks

```bash
python - <<'PY'
import pandas as pd, numpy as np
cp   = pd.read_csv("data/processed/country_panel.csv")
ai   = pd.read_csv("data/processed/ai_panel.csv")
meta = pd.read_csv("data/processed/country_meta.csv")

print("country_panel", cp.shape, cp.iso3.nunique(), "codes")
print("ai_panel     ", ai.shape, ai.iso3.nunique(), "codes (incl. WB aggregates)")
print("keys unique  ", cp.duplicated(['iso3','year']).sum(), ai.duplicated(['iso3','year']).sum())
print("CHN fertiliser non-missing:", cp.loc[cp.iso3=='CHN','n_kg_ha'].notna().sum())
print("aggregates dropped by the left join:",
      sorted(set(ai.iso3) - set(cp.iso3))[:12], "...")

d = cp.merge(meta[['iso3','region','income']], on='iso3', how='left')
F = ['n_kg_ha','p_kg_ha','k_kg_ha','irrig_share_cropland','temp_anom','arable_kha','year']
s = d.dropna(subset=['cereal_yield_kg_ha']+F+['region'])
s = s[s.cereal_yield_kg_ha > 0]
print("modellable panel:", len(s), "obs /", s.iso3.nunique(), "countries",
      int(s.year.min()), "-", int(s.year.max()))
PY
```

Expected: `country_panel (13975, 29) 215 codes`; `ai_panel (9290, 15) 271 codes`;
zero duplicate keys in both; a non-zero count of Chinese fertiliser observations (the
"China, mainland" override working); and `modellable panel: 8364 obs / 172 countries 1961 - 2023`.
