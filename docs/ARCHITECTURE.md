# Proposed architecture

```text
Sanitized CSV / Parquet snapshots
                |
                v
        Polars adapter layer
  schema mapping + safe-field allowlist
                |
                v
      DuckDB analytical store
    ETF + Listing + Snapshot tables
         |                 |
         v                 v
 explainable similarity   quality rules
 TF-IDF + structured      + Isolation Forest
         |                 |
         +--------+--------+
                  v
          FastAPI service layer
     pagination, filtering, caching
                  |
                  v
          Next.js App Router UI
 dashboard / explorer / detail / network
 compare / observability / history / copilot
```

## Decisions

- **Isolation:** `etf-intelligence-lab/` has its own dependency manifests, tests, containers, data, and CI. Runtime code never imports the source pipeline.
- **Polars:** columnar normalization and Parquet writes are fast and memory-efficient for tens of thousands of rows.
- **DuckDB:** embedded analytical SQL avoids operating a database service while supporting scans, aggregates, filters, and Parquet interoperability.
- **FastAPI:** typed, self-documenting endpoints expose a narrow data contract and keep analytical computation off the browser.
- **Next.js:** App Router provides an accessible, responsive product shell with direct routes for every recruiter-facing capability.
- **Similarity:** a transparent weighted cosine model combines TF-IDF, categorical matches, numeric proximity, and exchange overlap. Each component is returned with its contribution.
- **Anomalies:** deterministic rules carry human-readable explanations. Isolation Forest only adds a secondary “unusual multivariate profile” signal with the contributing unusual features shown.
- **No required persistence:** generated Parquet and DuckDB artifacts are reproducible. This keeps local and free-tier deployment simple.
- **Optional AI:** the copilot maps supported intents to deterministic functions. No dataset is sent to an LLM and no API key is required.

## Public data flow

1. `scripts/generate_demo_dataset.py` creates realistic synthetic snapshots, or `scripts/import_pipeline_snapshot.py` sanitizes an explicitly supplied export.
2. The adapter validates and normalizes allowed columns into Parquet.
3. The bootstrap service creates/replaces local DuckDB tables and analytical views.
4. Quality, anomaly, provider, similarity, and snapshot-diff services read normalized records.
5. FastAPI returns paginated JSON; the frontend never downloads the full dataset.

## Deployment design

- Frontend: Vercel-compatible Next.js build with `NEXT_PUBLIC_API_URL`.
- Backend: Dockerized FastAPI service suitable for Render, Railway, or Fly.io.
- Data: a small checked-in synthetic Parquet/JSON snapshot or generated during image build; no external database is required.
- Full local stack: Docker Compose with health checks and dependency ordering.

