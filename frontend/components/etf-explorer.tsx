"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Search, SlidersHorizontal } from "lucide-react";
import { createColumnHelper, flexRender, getCoreRowModel, type SortingState, useReactTable } from "@tanstack/react-table";
import { apiRequest, type ApiETFPage } from "@/lib/api";
import { etfs as previewEtfs } from "@/lib/demo-data";
import type { ETF } from "@/types";

type Dimensions = { issuers: string[]; asset_classes: string[]; currencies: string[] };
type RawETF = {
  isin: string; name: string; issuer: string; asset_class: string; category: string; benchmark: string;
  aum_millions: number | null; aum_currency?: string; fund_currency?: string; ter: number; age_years: number;
  exchanges: string[]; tickers: string[]; quality_score: number; provider: string; replication_method: "Physical" | "Sampling" | "Synthetic";
  distribution_policy: "Accumulating" | "Distributing"; domicile: string;
};

const toETF = (item: RawETF): ETF => ({
  isin: item.isin, name: item.name, issuer: item.issuer, assetClass: item.asset_class,
  category: item.category, benchmark: item.benchmark, aum: item.aum_millions,
  currency: item.aum_currency || item.fund_currency || "EUR", ter: item.ter, age: item.age_years,
  exchanges: item.exchanges || [], tickers: item.tickers || [], quality: item.quality_score,
  provider: item.provider, freshness: 0, replication: item.replication_method,
  distribution: item.distribution_policy, domicile: item.domicile,
});

function aum(value: number | null, currency: string) {
  if (value === null) return "Not available";
  const prefix = currency === "EUR" ? "\u20ac" : currency === "GBP" ? "\u00a3" : currency === "USD" ? "$" : `${currency} `;
  return value >= 1000 ? `${prefix}${(value / 1000).toFixed(value >= 10000 ? 1 : 2)}B` : `${prefix}${value.toFixed(0)}M`;
}

const helper = createColumnHelper<ETF>();
const columns = [
  helper.accessor("name", { header: "ETF", cell: (info) => <div><Link href={`/etf/${info.row.original.isin}`} className="font-medium hover:text-[var(--accent)]">{info.getValue()}</Link><div className="mono mt-1 text-[9px] text-[var(--muted)]">{info.row.original.isin}</div></div> }),
  helper.accessor("issuer", { header: "Issuer" }),
  helper.accessor("assetClass", { header: "Asset class", cell: (info) => <span className="rounded bg-[var(--paper)] px-2 py-1 text-[10px]">{info.getValue()}</span> }),
  helper.accessor("aum", { header: "Reported AUM", cell: (info) => <span className="mono font-medium">{aum(info.getValue(), info.row.original.currency)}</span> }),
  helper.accessor("ter", { header: "TER", cell: (info) => <span className="mono">{info.getValue().toFixed(2)}%</span> }),
  helper.accessor("age", { header: "Age", cell: (info) => <span className="mono">{info.getValue().toFixed(1)}y</span> }),
  helper.accessor("exchanges", { header: "Listings", cell: (info) => info.getValue().length }),
  helper.accessor("quality", { header: "Quality", cell: (info) => <div className="flex items-center gap-2"><div className="h-1 w-12 rounded bg-[var(--line)]"><div className="h-full rounded bg-[var(--accent)]" style={{ width: `${info.getValue()}%` }}/></div><span className="mono text-[10px]">{info.getValue()}</span></div> }),
];
const sortFields: Record<string, string> = { name: "name", issuer: "issuer", aum: "aum_millions", ter: "ter", age: "age_years", exchanges: "listing_count" };

export function ETFExplorer() {
  const [query, setQuery] = useState("");
  const [issuer, setIssuer] = useState("");
  const [assetClass, setAssetClass] = useState("");
  const [currency, setCurrency] = useState("");
  const [minAum, setMinAum] = useState("");
  const [page, setPage] = useState(1);
  const [pageCount, setPageCount] = useState(1);
  const [total, setTotal] = useState(previewEtfs.length);
  const [rows, setRows] = useState<ETF[]>(previewEtfs);
  const [source, setSource] = useState<"loading" | "api" | "preview">("loading");
  const [sorting, setSorting] = useState<SortingState>([{ id: "aum", desc: true }]);
  const [dimensions, setDimensions] = useState<Dimensions>({ issuers: [], asset_classes: [], currencies: [] });
  const pageSize = 12;

  useEffect(() => { apiRequest<Dimensions>("/api/dimensions").then(setDimensions).catch(() => undefined); }, []);
  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
      if (query.trim()) params.set("search", query.trim());
      if (issuer) params.set("issuer", issuer);
      if (assetClass) params.set("asset_class", assetClass);
      if (currency) params.set("currency", currency);
      if (minAum) params.set("min_aum", minAum);
      const sorted = sorting[0];
      params.set("sort", sortFields[sorted?.id] || "aum_millions");
      params.set("order", sorted?.desc === false ? "asc" : "desc");
      apiRequest<ApiETFPage>(`/api/etfs?${params}`, { signal: controller.signal }).then((payload) => {
        setRows((payload.items as unknown as RawETF[]).map(toETF)); setTotal(payload.total); setPageCount(payload.pages); setSource("api");
      }).catch((error) => {
        if (error instanceof DOMException && error.name === "AbortError") return;
        const filtered = previewEtfs.filter((item) => {
          const matchesText = `${item.name} ${item.isin} ${item.issuer} ${item.benchmark}`.toLowerCase().includes(query.toLowerCase());
          return matchesText && (!issuer || item.issuer === issuer) && (!assetClass || item.assetClass === assetClass) && (!currency || item.currency === currency) && (!minAum || Number(item.aum || 0) >= Number(minAum));
        });
        setRows(filtered); setTotal(filtered.length); setPageCount(1); setSource("preview");
      });
    }, 220);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [query, issuer, assetClass, currency, minAum, page, sorting]);

  const table = useReactTable({ data: rows, columns, state: { sorting }, manualSorting: true, onSortingChange: (next) => { setSorting(next); setPage(1); }, getCoreRowModel: getCoreRowModel() });
  const issuers = dimensions.issuers.length ? dimensions.issuers : [...new Set(previewEtfs.map((item) => item.issuer))];
  const assets = dimensions.asset_classes.length ? dimensions.asset_classes : [...new Set(previewEtfs.map((item) => item.assetClass))];
  const currencies = dimensions.currencies.length ? dimensions.currencies : [...new Set(previewEtfs.map((item) => item.currency))];
  const resetPage = () => setPage(1);
  const clear = () => { setQuery(""); setIssuer(""); setAssetClass(""); setCurrency(""); setMinAum(""); resetPage(); };

  return <div className="mx-auto max-w-[1500px]">
    <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end"><div><p className="text-xs font-semibold uppercase tracking-[.16em] text-[var(--accent)]">ETF explorer</p><h1 className="mt-2 text-3xl font-semibold tracking-[-.045em]">Interrogate the universe</h1><p className="mt-2 text-sm text-[var(--muted)]">Search normalized entities and trace every result back to its snapshot.</p></div><div className="flex items-center gap-2 text-xs text-[var(--muted)]"><span className={`size-1.5 rounded-full ${source === "api" ? "bg-emerald-500" : source === "preview" ? "bg-amber-500" : "bg-slate-400"}`}/>{total} entities &middot; {source === "api" ? "server-paginated API" : source === "preview" ? "preview fallback" : "connecting"}</div></div>
    <section className="mt-7 overflow-hidden rounded-lg border hairline bg-[var(--surface)]">
      <div className="grid gap-2 border-b hairline p-4 lg:grid-cols-[1fr_repeat(4,auto)_auto]"><label className="flex items-center gap-2 rounded-md border hairline bg-[var(--paper)] px-3"><Search size={15} className="text-[var(--muted)]"/><input value={query} onChange={(event) => { setQuery(event.target.value); resetPage(); }} className="w-full bg-transparent py-2.5 text-sm outline-none" placeholder="Search name, ISIN, issuer, benchmark..."/></label>{[[issuer, setIssuer, "All issuers", issuers], [assetClass, setAssetClass, "All asset classes", assets], [currency, setCurrency, "All currencies", currencies]].map(([value, setter, label, options]) => <select key={String(label)} value={String(value)} onChange={(event) => { (setter as (value: string) => void)(event.target.value); resetPage(); }} className="rounded-md border hairline bg-[var(--surface)] px-3 py-2 text-xs"><option value="">{String(label)}</option>{(options as string[]).map((option) => <option key={option}>{option}</option>)}</select>)}<label className="flex items-center gap-2 rounded-md border hairline px-3"><span className="text-[10px] text-[var(--muted)]">MIN AUM</span><input value={minAum} onChange={(event) => { setMinAum(event.target.value); resetPage(); }} type="number" className="w-16 bg-transparent py-2 text-xs outline-none" placeholder="0"/></label><button onClick={clear} className="rounded-md border hairline px-3 py-2 text-xs">Clear</button></div>
      <div className="overflow-x-auto"><table className="w-full min-w-[980px] text-left text-xs"><thead className="bg-[var(--paper)] text-[10px] uppercase tracking-wider text-[var(--muted)]">{table.getHeaderGroups().map((group) => <tr key={group.id}>{group.headers.map((header) => <th key={header.id} className="px-4 py-3 font-medium"><button className="flex items-center gap-1" onClick={header.column.getToggleSortingHandler()}>{flexRender(header.column.columnDef.header, header.getContext())}{header.column.getIsSorted() === "asc" ? " \u2191" : header.column.getIsSorted() === "desc" ? " \u2193" : ""}</button></th>)}</tr>)}</thead><tbody>{table.getRowModel().rows.map((row) => <tr key={row.id} className="border-t hairline hover:bg-[var(--paper)]">{row.getVisibleCells().map((cell) => <td key={cell.id} className="px-4 py-3.5">{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>)}</tr>)}</tbody></table></div>
      <div className="flex items-center justify-between border-t hairline px-4 py-3 text-xs"><span className="text-[var(--muted)]">{total ? `Rows ${(page - 1) * pageSize + 1}\u2013${Math.min(page * pageSize, total)} of ${total}` : "No matching ETFs"}</span><div className="flex items-center gap-2"><button disabled={page === 1} onClick={() => setPage((value) => value - 1)} className="rounded border hairline px-3 py-1.5 disabled:opacity-30">Previous</button><span className="mono text-[10px] text-[var(--muted)]">{page} / {pageCount}</span><button disabled={page >= pageCount} onClick={() => setPage((value) => value + 1)} className="rounded border hairline px-3 py-1.5 disabled:opacity-30">Next</button></div></div>
    </section><div className="mt-3 flex items-center gap-2 text-[10px] text-[var(--muted)]"><SlidersHorizontal size={12}/>{source === "api" ? "Filtering, ordering, and pagination run as parameterized DuckDB queries." : "Start FastAPI to query the full universe; this fallback is the bundled preview sample."}</div>
  </div>;
}

