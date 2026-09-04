"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Activity, BarChart3, Boxes, Command, GitCompareArrows, History, LayoutDashboard, Menu, Moon, Network, Search, ShieldCheck, Sparkles, Sun, X } from "lucide-react";
import { etfs } from "@/lib/demo-data";

const nav = [
  ["Dashboard","/dashboard",LayoutDashboard],["ETF Explorer","/explorer",Search],["Similarity Map","/network",Network],
  ["Compare","/compare",GitCompareArrows],["Anomalies","/anomalies",Activity],["Observability","/observability",ShieldCheck],
  ["History","/history",History],["Data Copilot","/copilot",Sparkles],["Architecture","/architecture",Boxes],
] as const;

export function AppShell({children}:{children:React.ReactNode}) {
  const pathname=usePathname(); const router=useRouter();
  const [palette,setPalette]=useState(false); const [mobile,setMobile]=useState(false); const [dark,setDark]=useState(false); const [query,setQuery]=useState("");
  useEffect(()=>{const key=(event:KeyboardEvent)=>{if((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==="k"){event.preventDefault();setPalette(v=>!v)}if(event.key==="Escape")setPalette(false)};window.addEventListener("keydown",key);return()=>window.removeEventListener("keydown",key)},[]);
  const results=etfs.filter(etf=>`${etf.name} ${etf.isin} ${etf.issuer}`.toLowerCase().includes(query.toLowerCase())).slice(0,5);
  const go=(href:string)=>{router.push(href);setPalette(false);setMobile(false)};
  return <div className={dark?"theme-dark min-h-screen":"min-h-screen"} style={dark?{"--ink":"#edf4f1","--muted":"#95a6a1","--line":"#293b3d","--paper":"#0d1517","--surface":"#121e20","--accent":"#54c3a7","--accent-soft":"#163f37"} as React.CSSProperties:undefined}>
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)] lg:grid lg:grid-cols-[240px_1fr]">
      <aside className={`${mobile?"fixed inset-0 z-40 block":"hidden"} border-r hairline bg-[var(--surface)] lg:sticky lg:top-0 lg:block lg:h-screen`}>
        <div className="flex h-full flex-col p-4">
          <div className="flex items-center justify-between px-2 py-2"><Link href="/" className="flex items-center gap-3 text-sm font-semibold tracking-tight"><span className="grid size-8 place-items-center rounded-md bg-[var(--ink)] text-[10px] text-[var(--paper)]">EI</span><span>ETF Intelligence<br/>Lab</span></Link><button onClick={()=>setMobile(false)} className="lg:hidden"><X size={18}/></button></div>
          <button onClick={()=>setPalette(true)} className="mt-6 flex w-full items-center justify-between rounded-md border hairline bg-[var(--paper)] px-3 py-2.5 text-left text-xs text-[var(--muted)]"><span className="flex items-center gap-2"><Search size={14}/>Find anything</span><span className="mono rounded border hairline px-1.5 py-0.5 text-[9px]">⌘K</span></button>
          <nav className="mt-6 space-y-1">{nav.map(([label,href,Icon])=><Link key={href} href={href} onClick={()=>setMobile(false)} className={`flex items-center gap-3 rounded-md px-3 py-2.5 text-sm ${pathname===href||pathname.startsWith(`${href}/`)?"bg-[var(--accent-soft)] font-medium text-[var(--accent)]":"text-[var(--muted)] hover:bg-[var(--paper)] hover:text-[var(--ink)]"}`}><Icon size={16}/>{label}</Link>)}</nav>
          <div className="mt-auto rounded-lg border hairline bg-[var(--paper)] p-3"><div className="flex items-center gap-2 text-xs font-semibold text-[var(--accent)]"><span className="size-1.5 rounded-full bg-[var(--accent)]"/> DEMO MODE</div><p className="mt-2 text-[11px] leading-4 text-[var(--muted)]">Synthetic ETF records. No private source data or credentials.</p></div>
        </div>
      </aside>
      <div className="min-w-0">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b hairline bg-[color:var(--paper)]/95 px-4 backdrop-blur lg:px-8"><div className="flex items-center gap-3"><button className="lg:hidden" onClick={()=>setMobile(true)}><Menu size={19}/></button><div className="hidden items-center gap-2 text-xs text-[var(--muted)] sm:flex"><BarChart3 size={14}/><span>Snapshot</span><strong className="font-medium text-[var(--ink)]">28 Aug 2026</strong><span className="ml-1 rounded-full bg-[var(--accent-soft)] px-2 py-0.5 text-[10px] text-[var(--accent)]">HEALTHY</span></div></div><div className="flex items-center gap-2"><span className="hidden text-[11px] text-[var(--muted)] md:block">API synced 2m ago</span><button onClick={()=>setDark(v=>!v)} aria-label="Toggle theme" className="grid size-9 place-items-center rounded-md border hairline bg-[var(--surface)]">{dark?<Sun size={15}/>:<Moon size={15}/>}</button><button onClick={()=>setPalette(true)} className="grid size-9 place-items-center rounded-md border hairline bg-[var(--surface)]"><Command size={15}/></button></div></header>
        <main className="px-4 py-6 lg:px-8 lg:py-8">{children}</main>
      </div>
    </div>
    {palette&&<div className="fixed inset-0 z-50 flex justify-center bg-black/45 p-4 pt-[12vh]" onMouseDown={()=>setPalette(false)}><div className="h-fit w-full max-w-xl overflow-hidden rounded-xl border hairline bg-[var(--surface)] shadow-2xl" onMouseDown={e=>e.stopPropagation()}><div className="flex items-center gap-3 border-b hairline px-4"><Search size={17} className="text-[var(--muted)]"/><input autoFocus value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search ETFs, ISINs, or navigate…" className="w-full bg-transparent py-4 text-sm outline-none"/></div><div className="max-h-[420px] overflow-auto p-2">{!query&&<><div className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-[var(--muted)]">Navigate</div>{nav.slice(0,6).map(([label,href,Icon])=><button key={href} onClick={()=>go(href)} className="flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm hover:bg-[var(--paper)]"><Icon size={15}/>{label}</button>)}</>}{query&&<><div className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-[var(--muted)]">ETF results</div>{results.map(etf=><button key={etf.isin} onClick={()=>go(`/etf/${etf.isin}`)} className="flex w-full items-center justify-between rounded-md px-3 py-3 text-left hover:bg-[var(--paper)]"><span><span className="block text-sm font-medium">{etf.name}</span><span className="mono mt-1 block text-[10px] text-[var(--muted)]">{etf.isin} · {etf.issuer}</span></span><span className="text-xs text-[var(--accent)]">Open</span></button>)}</>}</div><div className="flex justify-between border-t hairline px-4 py-2 text-[10px] text-[var(--muted)]"><span>↑↓ navigate · enter select</span><span>esc close</span></div></div></div>}
  </div>;
}
