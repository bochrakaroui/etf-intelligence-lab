# ML and scoring methods

## Explainable ETF similarity

ETF Intelligence Lab uses a transparent weighted model. It does not compare names alone and does not require a hosted embedding service.

| Signal | Weight | Method |
| --- | ---: | --- |
| Semantic characteristics | 25% | TF-IDF cosine similarity over name, category, strategy, benchmark, and asset class |
| Asset-class match | 20% | exact normalized categorical match |
| Benchmark match | 13% | exact normalized match |
| Category match | 12% | exact normalized match |
| Fund currency | 8% | exact normalized match |
| Exchange overlap | 7% | Jaccard overlap of exchange sets |
| AUM scale | 7% | proximity of `log1p(AUM)` values |
| Issuer match | 5% | exact normalized match |
| Fund age | 3% | bounded numerical proximity |

Each feature produces a value between 0 and 1. The API returns `weight × value` as percentage-point contributions. Contributions sum to the reported similarity score, which makes every recommendation auditable. Missing data contributes zero; it is never imputed solely to raise similarity.

## Anomaly detection

Deterministic rules are the primary system because they map directly to a corrective action:

- invalid ISIN format/checksum;
- missing, negative, or suspicious zero AUM;
- invalid or future listing dates;
- duplicate `(isin, exchange_code, ticker)` keys;
- unsupported currency codes;
- stale observations;
- unusually broad exchange coverage.

Isolation Forest is a secondary signal over log AUM, TER, age, and listing count. It uses a fixed random seed and a conservative contamination rate. An alert is never presented as “the model said so”: the response identifies the feature with the greatest absolute distance from the dataset median. Deterministic high-severity alerts suppress duplicate ML alerts for the same entity.

## ETF quality score

The ETF-level score is intentionally coarse and transparent:

| Dimension | Weight |
| --- | ---: |
| Identifier completeness and checksum | 25% |
| AUM presence and currency | 20% |
| Listing completeness | 15% |
| Snapshot freshness | 15% |
| Currency/date consistency | 15% |
| Source confidence | 10% |

Sub-scores are whole numbers and the final result is rounded to a whole number. It measures record quality, not investment quality.

## Provider reliability score

```text
30% completeness
+ 25% freshness
+ 15% schema/value consistency
+ 10% listing-key uniqueness
+ 15% identifier/value validity
+  5% inverse anomaly rate
```

Provider reliability describes the operational quality of a data feed. It must not be interpreted as a rating of an asset manager or its products.

## Dataset health

The global health score is the arithmetic mean of five visible component scores: completeness, freshness, consistency, uniqueness, and validity. The UI exposes every component and links directly to provider evidence. No hidden “AI confidence” is included.

## Determinism

- Demo generation uses seed `20260828`.
- Isolation Forest uses `random_state=42`.
- Similarity weights are fixed in source and returned by the API.
- Comparison summaries and automated insights are template-based calculations.
- Local copilot intents call deterministic functions and require no LLM or API key.

