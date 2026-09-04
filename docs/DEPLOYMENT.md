# Deployment

The application has no required external database or credentials. The checked-in dataset is deterministic and synthetic.

## Local Docker deployment

```bash
python scripts/generate_demo_dataset.py
docker compose up --build
```

Open `http://localhost:3000`. FastAPI and OpenAPI are available at `http://localhost:8000` and `http://localhost:8000/docs`.

## Frontend on Vercel

1. Push only the `etf-intelligence-lab` project to a Git repository.
2. Import the repository in Vercel.
3. Set the root directory to `frontend` and keep the detected Next.js settings.
4. Add `NEXT_PUBLIC_API_URL=https://<your-backend-host>`.
5. Deploy. Confirm `/dashboard`, `/explorer`, and a dynamic `/etf/<isin>` route.

The frontend retains a local synthetic fallback when the API is temporarily unavailable; the bottom-right indicator makes the current mode explicit.

## Backend on Render

1. Create a new Web Service from the repository.
2. Select Docker and set the Dockerfile path to `backend/Dockerfile` with repository root as build context.
3. Set `ETF_LAB_CORS_ORIGINS` to the Vercel production URL.
4. Use the free/small instance class and deploy.
5. Verify `https://<service>/health` and `https://<service>/docs`.

The same Dockerfile runs on Railway or Fly.io. Expose port `8000`; a persistent volume is optional because DuckDB is rebuilt deterministically from snapshots.

## Production snapshot import

Never mount the private scraping repository into the deployed service. Export a reviewed CSV and sanitize it offline:

```bash
python scripts/import_pipeline_snapshot.py /path/to/export.csv \
  --snapshot-date 2026-08-28 \
  --output data/snapshots/2026-08-28/etf_snapshot.csv
```

Review the output for public-release approval, rebuild the backend image, and keep source audit files outside the public repository.

## Security checklist

- Confirm only synthetic or explicitly approved sanitized snapshots are committed.
- Search for credentials, source URLs, local absolute paths, and upstream payloads before pushing.
- Restrict CORS to the deployed frontend URL.
- Do not add API keys for local copilot mode.
- Treat provider reliability as data-feed quality, never investment advice.

