# OpenAlex queries and country attribution

The paper's identifying variable is built entirely from four OpenAlex `/works` calls per
year. This document gives the exact query strings, the exact request, the attribution rule,
and what the resulting counts do and do not mean.

Source: `code/11_download_ai_indicators.py`, functions `oa_group_by_country()` and
`download_openalex()`.

Access date of the shipped counts: `<TO CONFIRM: OpenAlex access date>` — the raw
`data/raw/openalex_*.csv` files in the author's working tree are timestamped
**2026-08-07 23:07–23:09 (UTC+02:00)**, which is the download date if the files were not
touched afterwards. The manuscript's reference list cites *OpenAlex (2025) … accessed 2026*,
which is consistent.

---

## 1. The term lists

Defined once at the top of the script and combined into queries:

```python
AI_TERMS = ('"artificial intelligence" OR "machine learning" OR "deep learning" '
            'OR "neural network"')

AG_TERMS = ('agriculture OR agricultural OR crop OR farming OR farm OR agronomy '
            'OR agronomic')

PA_TERMS = ('"precision agriculture" OR "smart farming" OR "digital agriculture" '
            'OR "precision farming" OR "site-specific management"')
```

Multi-word concepts are double-quoted, so they are matched as phrases; single words are
matched as terms. The AI list is deliberately narrow (four canonical method labels) and the
agricultural list deliberately broad (seven stems), because the intent is to capture
*agricultural work that uses AI methods*, not *AI work that happens to mention food*.

## 2. The four queries

```python
QUERIES = {
    "ai_ag":        f"({AI_TERMS}) AND ({AG_TERMS})",
    "ai_all":       f"({AI_TERMS})",
    "precision_ag": f"({PA_TERMS})",
    "works_all":    None,          # no topical filter: the denominator
}
```

Fully expanded, the three topical queries are:

**1 — `ai_ag`, the main exposure measure → column `oa_ai_ag`**

```
("artificial intelligence" OR "machine learning" OR "deep learning" OR "neural network") AND (agriculture OR agricultural OR crop OR farming OR farm OR agronomy OR agronomic)
```

**2 — `precision_ag`, the alternative exposure → column `oa_precision_ag`**

```
("precision agriculture" OR "smart farming" OR "digital agriculture" OR "precision farming" OR "site-specific management")
```

**3 — `ai_all`, AI in any field, used only to build the non-AI placebo → column `oa_ai_all`**

```
("artificial intelligence" OR "machine learning" OR "deep learning" OR "neural network")
```

**4 — `works_all`, no filter → column `oa_works_all`.** Every work indexed by OpenAlex with
that publication year. It is the denominator of the specialisation measure and, minus
`oa_ai_all`, the numerator of the non-AI research placebo.

## 3. The exact request

For each query and each year in `range(2000, 2025)`:

```
GET https://api.openalex.org/works
    ?filter=publication_year:{YEAR},title_and_abstract.search:{QUERY}
    &group_by=authorships.countries
    &per_page=200
    &mailto=<TO CONFIRM: contact e-mail for the OpenAlex polite pool>
```

For `works_all` the `title_and_abstract.search` clause is omitted and only
`publication_year` is filtered.

Notes on the request that matter for replication:

- **`title_and_abstract.search`** searches title and abstract only — never full text,
  never keywords or concept tags. A work whose abstract is missing from OpenAlex can only
  match on its title.
- **`group_by=authorships.countries`** returns aggregate counts per country, not a work
  list; the endpoint returns at most 200 groups, which comfortably exceeds the number of
  countries appearing in any single year, so no pagination of groups is needed.
- **`per_page=200`** applies to the group list, not to works.
- **`mailto`** puts the request in OpenAlex's polite pool. The shipped script hard-codes a
  personal address at `MAILTO` in `code/11_download_ai_indicators.py`; **replace it with
  your own before re-running**.
- Each call is retried up to 5 times with backoff `4 × attempt` seconds; a call that fails
  five times returns an empty frame and a world total of 0 for that year, which would show
  up as a hole in the series. The shipped series has no such hole.
- `time.sleep(0.35)` between year requests. Four queries × 25 years = 100 requests; the
  whole OpenAlex download takes roughly 2–5 minutes.

## 4. How counts are attributed to countries

Three steps, and each one has a consequence worth stating.

**(a) OpenAlex side — full counting, not fractional.** `authorships.countries` is a
multi-valued field: a work with authors affiliated in Spain, Brazil and the United States
belongs to the Spain group, the Brazil group *and* the United States group. OpenAlex counts
it once in each. There is no fractional allocation and no lead-author rule.

> **Consequence.** Country counts do not sum to the world total, and they over-count
> internationally co-authored work relative to domestic work. The bias favours countries
> with high international co-authorship rates. The manuscript states this explicitly in
> Section 5.5 and it is one reason the paper's claims rest on within-country variation
> conditional on complements rather than on cross-country levels.

**(b) Key parsing.** Each group key is a URL such as
`https://openalex.org/countries/ES`; the script takes the last path segment and keeps it
only if it is exactly two characters:

```python
iso2 = g["key"].rstrip("/").split("/")[-1]
if len(iso2) != 2:
    continue
```

This silently discards OpenAlex's "unknown country" group, so works with no resolvable
author affiliation contribute to `oa_works_all` at the world level but to no country.

**(c) ISO2 → ISO3 via pycountry.**

```python
def iso2_to_iso3(c):
    try:    return pycountry.countries.get(alpha_2=c).alpha_3
    except: return None
```

Rows that do not resolve are dropped. After mapping, `groupby(["iso3", "year"]).sum()`
collapses any alpha-2 codes that resolve to the same alpha-3, and missing counts across the
four query frames are filled with `0` — a country absent from a given year's group-by
genuinely published zero matching works that year.

## 5. From counts to the regression variables

| Variable | Formula | Role |
|---|---|---|
| `ai_ag_pc` | `oa_ai_ag / (population / 1e6)` | **Volume**: agricultural-AI works per million inhabitants |
| `ai_ag_share` | `1000 × oa_ai_ag / oa_works_all` | **Specialisation**: agricultural-AI works per 1,000 of the country's works |
| `pa_pc` | `oa_precision_ag / (population / 1e6)` | Alternative exposure (narrow query) |
| `log_nonai_res` | `log1p(max(oa_works_all − oa_ai_all, 0) / (population / 1e6))` | Non-AI research capacity: the placebo and the horse-race rival |

All four enter the regressions as `log1p(·)`, then standardised within the estimation
sample. **Specialisation is the identifying measure.** Dividing by the country's own total
output removes the size of the national research system: in the estimation sample the
correlation between standardised specialisation and standardised non-AI research capacity
is **r = 0.14**, which is what allows the two to be entered simultaneously in the horse race
of Table 5, panel B, without collinearity.

`population` comes from the World Bank (`SP.POP.TOTL`), not from OpenAlex.

## 6. What the series looks like

From `results/12_ai_observable.json`, block `A_descriptivos_IA` (full 25-year series in
[`SUPPLEMENTARY_TABLES.md`](SUPPLEMENTARY_TABLES.md), Table S9):

| | 2000 | 2024 | Ratio |
|---|---|---|---|
| `ai_ag` world works | 69 | 21,100 | ×305.8 |
| `precision_ag` world works | 129 | 6,315 | ×48.9 |
| `ai_ag` share of all indexed works (‰) | 0.0444 | 2.5477 | ×57.4 |

Log-linear growth: **15.83 %/year over 2000–2015**, **42.45 %/year over 2016–2024** — the
break that motivates treating 2016 as the onset of the wave.

## 7. Caveats a replicator should expect

1. **OpenAlex is not versioned and not frozen.** Re-running these queries will not
   reproduce the shipped counts exactly. OpenAlex continuously ingests new records,
   back-fills abstracts, corrects affiliations and re-resolves institutions, all of which
   move historical counts. Expect the *shape* of the series to replicate and the *levels*
   to drift, with the largest drift in the most recent years.
2. **2024 is incomplete in any snapshot.** Indexing of a publication year continues for
   years afterwards. The 2024 figure will rise in later snapshots.
3. **Coverage of non-English venues improved over the period**, which mechanically inflates
   growth in the raw series. The manuscript flags this in Section 5.5 and is the stated
   reason the argument rests on cross-country conditional structure rather than on the
   aggregate time trend.
4. **This is a research-activity proxy, not adoption.** It measures a country's capability
   and orientation towards agricultural AI. A country can publish without deploying, and
   deploy imported tools without publishing. The manuscript's Section 5.5 argues that both
   forms of slippage attenuate the conditional estimates towards zero rather than
   manufacture them.
5. **Phrase matching is literal.** "AI for agriculture" written as "artificial intelligence
   in cropping systems" matches; written as "AI in cropping systems" does not, because the
   bare acronym is not in `AI_TERMS`. This was a deliberate precision-over-recall choice
   (the bare token "AI" is far too noisy) and it biases the counts downward, uniformly.

## 8. Re-running only the OpenAlex step

```bash
# from the repository root
python code/11_download_ai_indicators.py                # OpenAlex + World Bank complements
python code/11_download_ai_indicators.py --build-only   # rebuild ai_panel.csv from cached raw CSVs
```

`--build-only` skips the OpenAlex download and reassembles `data/processed/ai_panel.csv`
from whatever is already in `data/raw/openalex_*.csv`. The World Bank block always uses the
`data/raw/wb_*.csv` cache when present (`download_worldbank(use_cache=True)`); delete those
files to force a fresh download.
