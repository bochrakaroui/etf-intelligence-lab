const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export type ApiHealth = { status: string; service: string; mode: string; snapshot: string };

export type ApiETF = {
  isin: string;
  name: string;
  issuer: string;
  asset_class: string;
  category: string;
  benchmark: string;
  replication: string;
  distribution: string;
  currency: string;
  ter: number;
  aum_millions: number | null;
  inception_date: string;
  listing_count: number;
  exchanges: string[];
  tickers: string[];
  quality_score: number;
  provider: string;
};

export type ApiETFPage = {
  items: ApiETF[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type ApiStats = {
  unique_isins: number;
  listing_count: number;
  total_reported_aum_millions: number;
  dataset_health: number;
  anomaly_count: number;
  latest_snapshot: string;
  aum_by_issuer: Array<{ name: string; value: number }>;
  listings_by_exchange: Array<{ name: string; value: number }>;
  insights: string[];
  providers: Array<Record<string, string | number | boolean>>;
  recent_anomalies: Array<Record<string, string | number | boolean>>;
  largest_etfs: ApiETF[];
};
