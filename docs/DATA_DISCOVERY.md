# Data discovery

## Scope and safety boundary

ETF Intelligence Lab treats the existing seven-country pipeline as a read-only data producer. The application does not import pipeline modules, call upstream sources, or expose source URLs, credentials, workstation paths, provider adapters, logs, or internal failure details. A standalone adapter reads only exported snapshots and emits a deliberately limited public schema. The checked-in application data is synthetic and labelled `DEMO / SYNTHETIC`.

## Discovered outputs

The repository contains 26 dated aggregate snapshots from `2026-07-13` through `2026-08-28` under:

```text
pipeline_runs/<snapshot-date>/all_exchange_etf_listings.csv
```

The aggregate is listing-grained: an ISIN intentionally appears more than once when a fund trades on multiple exchanges. Snapshot sizes range from 4,512 to 12,194 rows. The newest published file inspected contains 12,187 listing rows and 4,568 unique ISINs.

The repository also contains dated operational artifacts under `pipeline_artifacts/<snapshot-date>/`:

| Artifact | Grain | Useful public capability |
| --- | --- | --- |
| `completeness_report.json` | dataset/run | coverage, freshness, country completeness |
| `quality_report.json` | dataset/run | acceptance state and issue counts |
| `provider_health.json` | provider/run | provider health and row-count continuity |
| `quality_issues.csv` | issue | explained deterministic anomalies |
| `dataset_changes.csv` | field change | historical dataset diff |
| `universe_changes.csv` | listing change | additions, removals, unresolved records |
| `fund_fact_provenance.csv` | ISIN/source | provenance without publishing source URLs |
| `listing_date_audit.csv` | listing | date validation and retrieval time |
| `lifecycle_audit.csv` | listing/event | lifecycle and listing state |
| `aum_audit.csv` | ISIN | AUM scope, freshness, and resolution status |
| `run_manifest.json` | run/step | pipeline observability and duration |

The current aggregate fields are:

| Field | Meaning | Latest coverage |
| --- | --- | ---: |
| `ticker` | exchange ticker | 100% |
| `exchange_code` | normalized exchange/country code | 100% |
| `name` | ETF name | 100% |
| `isin` | fund identifier | 100% |
| `listing_date` | exchange listing date | 99.79% |
| `trading_currency` | listing currency | 100% |
| `asset_class` | broad fund classification | 99.96% |
| `ter` | total expense ratio | 99.98% |
| `aum` | selected official AUM amount | 99.58% |
| `partial_aum` | share-class AUM when available | 33.97% |
| `total_aum` | total fund AUM when available | 99.58% |
| `exchange` | exchange display name | 100% |
| `issuer` | public issuer/fund provider | 100% |
| `aum_date` | official AUM as-of date | 99.58% |

The pipeline documentation defines a 15th field, `aum_currency`, between `total_aum` and `exchange`. A staged 2026-08-28 candidate has that field, while the accepted publication inspected does not. The adapter therefore accepts both 14- and 15-column forms and never infers AUM currency from trading currency. Missing AUM currency remains unknown.

## Safe normalized model

Only these fields cross the portfolio boundary:

```text
ETF: isin, name, issuer, asset_class, category, strategy, benchmark,
     domicile, fund_currency, aum_millions, aum_currency, inception_date,
     age_years, replication_method, distribution_policy, ter

Listing: isin, exchange, exchange_code, ticker, trading_currency,
         listing_date, country

SourceMetadata: public_provider_label, snapshot_date, retrieved_at,
                freshness_days, completeness_score, validation_status
```

`category`, `strategy`, `benchmark`, `domicile`, `fund_currency`, `inception_date`, `replication_method`, and `distribution_policy` are not present in the aggregate. They remain nullable for imported snapshots and are populated only by the synthetic demo generator.

## Fields deliberately excluded

The public adapter drops source URLs, local paths, provider directory keys, adapter names, HTTP status, raw error text, attempted-source details, authentication data, and raw upstream payloads. Public provider names may be retained where they are already issuer-facing; demo mode uses fictional provider labels.

## Features supported by available data

- Dashboard counts, AUM totals/distribution, issuer/exchange/currency breakdowns, age and freshness views.
- Search, filtering, sorting, pagination, ETF detail, listing coverage, and normalized-record inspection.
- Explainable similarity using asset class, issuer, currency, exchange overlap, AUM, age, TER, and ETF-name TF-IDF. Demo-only descriptive fields add benchmark/category signals.
- Deterministic validation and anomaly rules for identifiers, missing/zero AUM, dates, duplicates, freshness, currency consistency, and listing count.
- Isolation Forest as a secondary, explained multivariate signal.
- Provider reliability derived from completeness, freshness, validity, uniqueness, and anomaly rate.
- Snapshot diffs because multiple dated aggregate files exist.
- Data lineage from sanitized snapshot to normalized entity and analytics products.

## Missing data and limitations

- The aggregate does not contain returns, price/NAV history, holdings, risk metrics, ESG metrics, flows, or benchmark constituents. The application must not imply portfolio-performance analysis.
- AUM units are treated as millions according to the pipeline audit contract. Currency conversion is intentionally not performed, so cross-currency AUM totals are labelled “reported AUM” and are analytical approximations.
- `aum_currency` is absent in one accepted schema variant; totals with unknown AUM currency remain visible as unknown, not imputed.
- Inception date is unavailable. Imported fund age uses the earliest observed listing date and is labelled accordingly.
- Provider health reflects data-delivery reliability, not investment-manager quality.
- Historical changes may reflect source/coverage changes rather than economic events; diff output identifies changes but does not claim causality.

