FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ETF_LAB_DATA_DIR=/app/data/snapshots \
    ETF_LAB_DATABASE_PATH=/app/data/demo/etf_lab.duckdb

WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY data ./data
COPY scripts ./scripts

RUN python scripts/generate_demo_dataset.py
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
