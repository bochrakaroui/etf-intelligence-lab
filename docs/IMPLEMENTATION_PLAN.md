# Implementation plan and directory structure

## Product slices

1. Define the privacy boundary, discovered schema, normalized models, and adapters.
2. Generate deterministic demo snapshots and build the DuckDB analytical layer.
3. Expose statistics, ETF search/detail, providers, anomalies, history, comparison, network, and copilot APIs.
4. Build the landing page and dense command-center dashboard.
5. Add explorer, ETF detail, explainable similarity network, and comparison flows.
6. Add observability, lineage, history diff, and local deterministic copilot.
7. Add tests, Docker, CI, deployment instructions, and recruiter-focused documentation.

## Target structure

```text
etf-intelligence-lab/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── analytics/
│   │   ├── core/
│   │   ├── data_quality/
│   │   ├── ml/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── types/
├── data/
│   ├── demo/
│   └── snapshots/
├── scripts/
├── docs/
├── .github/workflows/
├── docker-compose.yml
└── README.md
```

## Acceptance strategy

- Unit tests cover normalization, validation, scoring, similarity, anomalies, diffs, and API contracts.
- Frontend lint, type-check, and production build must pass.
- Backend tests must pass with deterministic seeds.
- Containers receive health checks and no credentials.
- Every visible control routes, filters, searches, compares, or explains real computed demo data.

