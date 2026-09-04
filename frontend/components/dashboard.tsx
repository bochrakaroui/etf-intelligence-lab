"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowUpRight, CircleAlert, Database, Landmark, Layers3, Radio, ShieldCheck } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { apiRequest, type ApiETF, type ApiStats } from "@/lib/api";
import { anomalies as previewAnomalies, etfs as previewEtfs, issuerAum, providers as previewProviders, snapshots } from "@/lib/demo-data";

const previewExchanges = [{ name: "Xetra", value: 174 }, { name: "LSE", value: 146 }, { name: "Paris", value: 82 }, { name: "SIX", value: 66 }, { name: "Milan", value: 54 }, { name: "A'dam", value: 23 }];
const tooltips = { contentStyle: { background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, fontSize: 11 }, cursor: { fill: "var(--accent-soft)" } };

function money(value: number | null, currency = "EUR") {
  if (value === null) return "Not available";
  const symbol = currency === "EUR" ? "\u20ac" : currency === "GBP" ? "\u00a3" : currency === "USD" ? "$" : `${currency} `;
  return value >= 1000 ? `${symbol}${(value / 1000).toFixed(value >= 10000 ? 1 : 2)}B` : `${symbol}${value.toFixed(0)}M`;
}

function text(value: unknown, fallback = "") { return typeof value === "string" ? value : fallback; }
function number(value: unknown, fallback = 0) { return typeof value === "number" ? value : fallback; }

export function Dashboard() {
  const [stats, setStats] = useState<ApiStats | null>(null);
  const [apiState, setApiState] = useState<"loading" | "live" | "preview">("loading");

  useEffect(() => {
    let active = true;
    apiRequest<ApiStats>("/api/stats")
      .then((payload) => { if (active) { setStats(payload); setApiState("live"); } })
      .catch(() => { if (active) setApiState("preview"); });
    return () => { active = false; };
  }, []);

  const previewAum = useMemo(() => previewEtfs.reduce((sum, item) => sum + (item.aum || 0), 0), []);
  const listingCount = previewEtfs.reduce((sum, item) => sum + item.exchanges.length, 0);
  const metrics = [
    ["Unique ETFs", String(stats?.unique_isins ?? previewEtfs.length), stats ? "latest snapshot" : "preview sample", Landmark],
    ["Exchange listings", String(stats?.listing_count ?? listingCount), stats ? "normalized rows" : "preview sample", Layers3],
    ["Reported AUM", money(stats?.total_reported_aum_millions ?? previewAum), "original currencies", Database],
    ["Dataset health", `${stats?.dataset_health ?? 96} / 100`, "rule-based score", ShieldCheck],
    ["Open anomalies", String(stats?.anomaly_count ?? previewAnomalies.length), "explained signals", CircleAlert],
    ["Latest snapshot", stats?.latest_snapshot ?? "2026-08-28", apiState === "live" ? "API connected" : "preview fallback", Radio],
  ] as const;

  const issuerData = stats?.aum_by_issuer?.slice(0, 8) ?? issuerAum;
  const exchangeData = stats?.listings_by_exchange?.slice(0, 6) ?? previewExchanges;
  const providerRows: Array<Record<string, unknown>> = stats?.providers?.slice(0, 4) ?? previewProviders.map((item) => ({ provider: item.name, reliability_score: item.score, completeness: item.completeness, anomaly_rate: item.anomalies }));
  const anomalyRows: Array<Record<string, unknown>> = stats?.recent_anomalies?.slice(0, 4) ?? previewAnomalies.map((item) => ({ ...item, severity: item.severity.toLowerCase() }));
  const insightRows = stats?.insights ?? [
    "Preview mode uses the bundled synthetic sample while the local API is unavailable.",
    "Start FastAPI to recompute every dashboard metric from the generated snapshots.",
    "AUM values are displayed in their reported currencies without FX conversion.",
    "All anomaly labels include a deterministic rule or explainable model reason.",
  ];
  const largest: Array<ApiETF | typeof previewEtfs[number]> = stats?.largest_etfs?.slice(0, 6) ?? previewEtfs.slice(0, 6);
  const firstIsin = stats?.largest_etfs?.[0]?.isin ?? previewEtfs[0].isin;
  const firstAnomalyIsin = text(anomalyRows[0]?.isin, firstIsin);

  return <div className="mx-auto max-w-[1500px]">
    <div className="flex flex-col justify-between gap-5 xl:flex-row xl:items-end">
      <div><p className="text-xs font-semibold uppercase tracking-[.16em] text-[var(--accent)]">Dataset command center</p><h1 className="mt-2 text-3xl font-semibold tracking-[-.045em]">ETF Intelligence Lab</h1><p className="mt-2 text-sm text-[var(--muted)]">Entity resolution, quality controls, explainable analytics, and snapshot history in one local workspace.</p></div>
      <div className="flex items-center gap-2"><span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider ${apiState === "live" ? "bg-emerald-500/10 text-emerald-600" : apiState === "preview" ? "bg-amber-500/10 text-amber-600" : "bg-[var(--paper)] text-[var(--muted)]"}`}>{apiState === "live" ? "Live API data" : apiState === "preview" ? "Preview fallback" : "Connecting"}</span><Link href="/history" className="rounded-md border hairline bg-[var(--surface)] px-4 py-2.5 text-xs font-semibold">Compare snapshots</Link><Link href="/explorer" className="rounded-md bg-[var(--ink)] px-4 py-2.5 text-xs font-semibold text-[var(--paper)]">Explore ETFs</Link></div>
    </div>

    <div className="mt-7 grid overflow-hidden rounded-lg border hairline bg-[var(--surface)] sm:grid-cols-2 xl:grid-cols-6">{metrics.map(([label, value, delta, Icon]) => <div key={label} className="border-b border-r hairline p-4 last:border-r-0 xl:border-b-0"><div className="flex items-center justify-between text-[10px] uppercase tracking-wider text-[var(--muted)]"><span>{label}</span><Icon size={14}/></div><div className="metric-value mt-5 text-2xl font-semibold">{value}</div><div className={`mt-1.5 text-[11px] ${label === "Open anomalies" ? "text-[var(--warning)]" : "text-[var(--accent)]"}`}>{delta}</div></div>)}</div>

    <div className="mt-5 grid gap-5 xl:grid-cols-[1.55fr_1fr]">
      <section className="rounded-lg border hairline bg-[var(--surface)] p-5"><div className="flex items-start justify-between"><div><h2 className="text-sm font-semibold">Reported AUM by issuer</h2><p className="mt-1 text-xs text-[var(--muted)]">Top synthetic fund families; values are not FX-converted</p></div><span className="rounded border hairline px-2 py-1 text-[10px] text-[var(--muted)]">Reported view</span></div><div className="mt-7 h-[270px]"><ResponsiveContainer width="100%" height="100%"><BarChart data={issuerData} margin={{ left: -20, right: 8 }}><CartesianGrid stroke="var(--line)" vertical={false}/><XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "var(--muted)" }}/><YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "var(--muted)" }}/><Tooltip {...tooltips}/><Bar dataKey="value" fill="var(--accent)" radius={[3, 3, 0, 0]}/></BarChart></ResponsiveContainer></div></section>
      <section className="rounded-lg border hairline bg-[var(--surface)] p-5"><div className="flex items-center justify-between"><div><h2 className="text-sm font-semibold">Health trend</h2><p className="mt-1 text-xs text-[var(--muted)]">Completeness and quality over demo snapshots</p></div><Link href="/observability" className="text-xs font-medium text-[var(--accent)]">Open observability &#8599;</Link></div><div className="mt-7 h-[270px]"><ResponsiveContainer width="100%" height="100%"><AreaChart data={snapshots}><defs><linearGradient id="health" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="var(--accent)" stopOpacity={.25}/><stop offset="95%" stopColor="var(--accent)" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="var(--line)" vertical={false}/><XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "var(--muted)" }} tickFormatter={(value) => value.slice(5)}/><YAxis domain={[85, 100]} axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "var(--muted)" }}/><Tooltip {...tooltips}/><Area dataKey="health" stroke="var(--accent)" fill="url(#health)" strokeWidth={2}/><Area dataKey="coverage" stroke="#8398a0" fill="transparent" strokeDasharray="4 4"/></AreaChart></ResponsiveContainer></div></section>
    </div>

    <div className="mt-5 grid gap-5 xl:grid-cols-[1fr_1fr_1.15fr]">
      <section className="rounded-lg border hairline bg-[var(--surface)] p-5"><h2 className="text-sm font-semibold">Listings by exchange</h2><p className="mt-1 text-xs text-[var(--muted)]">Where the current universe trades</p><div className="mt-5 space-y-3">{exchangeData.map((item, index) => <div key={item.name} className="grid grid-cols-[72px_1fr_32px] items-center gap-3 text-xs"><span className="truncate">{item.name}</span><div className="h-1.5 rounded-full bg-[var(--paper)]"><div className="h-full rounded-full bg-[var(--accent)]" style={{ width: `${item.value / Math.max(exchangeData[0]?.value ?? 1, 1) * 100}%`, opacity: 1 - index * .09 }}/></div><span className="mono text-right text-[10px] text-[var(--muted)]">{item.value}</span></div>)}</div></section>
      <section className="rounded-lg border hairline bg-[var(--surface)]"><div className="flex items-center justify-between border-b hairline p-5"><div><h2 className="text-sm font-semibold">Provider reliability</h2><p className="mt-1 text-xs text-[var(--muted)]">Weighted operational score</p></div><Link href="/observability" className="text-xs text-[var(--accent)]">View all</Link></div><div>{providerRows.map((provider, index) => { const name = text(provider.provider, text(provider.name, `Provider ${index + 1}`)); const score = number(provider.reliability_score, number(provider.score)); return <div key={name} className="flex items-center justify-between border-b hairline px-5 py-3 last:border-0"><div><div className="text-xs font-medium">{name}</div><div className="mt-1 text-[10px] text-[var(--muted)]">{number(provider.completeness).toFixed(1)}% complete &middot; {number(provider.anomaly_rate, number(provider.anomalies))} anomaly rate</div></div><div className={`mono text-sm font-semibold ${score < 85 ? "text-[var(--warning)]" : "text-[var(--accent)]"}`}>{score}</div></div>; })}</div></section>
      <section className="rounded-lg border hairline bg-[var(--surface)]"><div className="flex items-center justify-between border-b hairline p-5"><div><h2 className="text-sm font-semibold">Recent anomalies</h2><p className="mt-1 text-xs text-[var(--muted)]">Rules + explainable ML signals</p></div><Link href="/anomalies" className="text-xs text-[var(--accent)]">Inspect all</Link></div><div>{anomalyRows.map((anomaly, index) => { const severity = text(anomaly.severity, "low").toLowerCase(); const isin = text(anomaly.isin); return <Link href={`/etf/${isin}`} key={text(anomaly.id, `${isin}-${index}`)} className="flex gap-3 border-b hairline px-5 py-3 last:border-0 hover:bg-[var(--paper)]"><span className={`mt-1 size-2 shrink-0 rounded-full ${severity === "high" ? "bg-red-500" : severity === "medium" ? "bg-amber-500" : "bg-slate-400"}`}/><div className="min-w-0"><div className="flex items-center justify-between gap-2"><span className="truncate text-xs font-medium">{text(anomaly.title, "Data quality signal")}</span><span className="text-[9px] uppercase text-[var(--muted)]">{severity}</span></div><div className="mono mt-1 text-[9px] text-[var(--muted)]">{isin} &middot; {text(anomaly.observed)}</div></div></Link>; })}</div></section>
    </div>

    <section className="mt-5 rounded-lg border hairline bg-[var(--surface)] p-5"><div className="flex items-center justify-between"><div><h2 className="text-sm font-semibold">Automated insights</h2><p className="mt-1 text-xs text-[var(--muted)]">Deterministic observations computed from the active snapshot</p></div><span className="rounded-full bg-[var(--accent-soft)] px-2 py-1 text-[9px] font-semibold text-[var(--accent)]">NO LLM</span></div><div className="mt-5 grid gap-px overflow-hidden rounded-md bg-[var(--line)] md:grid-cols-2 xl:grid-cols-4">{insightRows.slice(0, 4).map((item, index) => <div key={item} className="bg-[var(--paper)] p-4"><span className="mono text-[10px] text-[var(--accent)]">0{index + 1}</span><p className="mt-3 text-xs leading-5">{item}</p></div>)}</div></section>

    <section className="mt-5"><div className="mb-3 flex items-center justify-between"><h2 className="text-sm font-semibold">Try these</h2><span className="text-[10px] uppercase tracking-wider text-[var(--muted)]">60-second product tour</span></div><div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">{[["Explore the largest ETF", `/etf/${firstIsin}`], ["Find similar ETFs", `/network?isin=${firstIsin}`], ["Inspect an anomaly", `/etf/${firstAnomalyIsin}`], ["See provider health", "/observability"], ["Compare ETFs", "/compare"]].map(([label, href], index) => <Link key={label} href={href} className="group flex items-center justify-between rounded-lg border hairline bg-[var(--surface)] p-4 text-xs font-medium hover:border-[var(--accent)]"><span><span className="mono mr-2 text-[9px] text-[var(--muted)]">0{index + 1}</span>{label}</span><ArrowUpRight size={14} className="text-[var(--muted)] group-hover:text-[var(--accent)]"/></Link>)}</div></section>

    <section className="mt-5 overflow-hidden rounded-lg border hairline bg-[var(--surface)]"><div className="flex items-center justify-between border-b hairline p-5"><div><h2 className="text-sm font-semibold">Largest ETFs</h2><p className="mt-1 text-xs text-[var(--muted)]">Reported AUM, no cross-currency conversion</p></div><Link href="/explorer" className="text-xs text-[var(--accent)]">Open explorer</Link></div><div className="overflow-x-auto"><table className="w-full min-w-[720px] text-left text-xs"><thead className="bg-[var(--paper)] text-[10px] uppercase tracking-wider text-[var(--muted)]"><tr><th className="px-5 py-3 font-medium">ETF</th><th className="px-4 py-3 font-medium">Asset class</th><th className="px-4 py-3 font-medium">Reported AUM</th><th className="px-4 py-3 font-medium">Listings</th><th className="px-4 py-3 font-medium">Quality</th></tr></thead><tbody>{largest.map((item) => { const live = "aum_millions" in item; const name = live ? item.name : item.name; const aum = live ? item.aum_millions : item.aum; const currency = live ? item.currency : item.currency; const assetClass = live ? item.asset_class : item.assetClass; const listingTotal = live ? item.listing_count : item.exchanges.length; const quality = live ? item.quality_score : item.quality; return <tr key={item.isin} className="border-t hairline hover:bg-[var(--paper)]"><td className="px-5 py-3"><Link href={`/etf/${item.isin}`} className="font-medium">{name}</Link><div className="mono mt-1 text-[9px] text-[var(--muted)]">{item.isin}</div></td><td className="px-4 py-3"><span className="rounded bg-[var(--paper)] px-2 py-1">{assetClass}</span></td><td className="mono px-4 py-3 font-medium">{money(aum, currency)}</td><td className="px-4 py-3">{listingTotal}</td><td className="px-4 py-3"><span className="text-[var(--accent)]">{quality}</span><span className="text-[var(--muted)]"> / 100</span></td></tr>; })}</tbody></table></div></section>
  </div>;
}

