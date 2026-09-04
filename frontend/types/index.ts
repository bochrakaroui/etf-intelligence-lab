export type ETF = {
  isin: string;
  name: string;
  issuer: string;
  assetClass: string;
  category: string;
  benchmark: string;
  aum: number | null;
  currency: string;
  ter: number;
  age: number;
  exchanges: string[];
  tickers: string[];
  quality: number;
  provider: string;
  freshness: number;
  replication: "Physical" | "Sampling" | "Synthetic";
  distribution: "Accumulating" | "Distributing";
  domicile: string;
};

export type Anomaly = {
  id: string;
  isin: string;
  severity: "High" | "Medium" | "Low";
  type: string;
  title: string;
  explanation: string;
  observed: string;
  expected: string;
};

export type Provider = {
  name: string;
  score: number;
  completeness: number;
  freshness: number;
  consistency: number;
  anomalies: number;
  records: number;
};
