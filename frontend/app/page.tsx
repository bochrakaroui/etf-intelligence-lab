import Link from "next/link";
import { Activity, ArrowRight, GitBranch, Radar, ShieldCheck } from "lucide-react";

const bars = [58, 84, 47, 72, 91, 63, 77, 52, 88, 69, 95, 81];

export default function LandingPage() {
  return (
    <main>
      <nav className="mx-auto flex max-w-[1440px] items-center justify-between px-6 py-6 lg:px-12">
        <Link href="/" className="flex items-center gap-3 font-semibold tracking-[-0.03em]">
          <span className="grid size-8 place-items-center rounded-md bg-[var(--ink)] text-xs text-[var(--paper)]">EI</span>
          ETF Intelligence Lab
        </Link>
        <div className="hidden items-center gap-8 text-sm text-[var(--muted)] md:flex">
          <a href="#capabilities">Capabilities</a>
          <Link href="/architecture">Architecture</Link>
          <span className="rounded-full border hairline px-3 py-1.5 text-xs">Demo / Synthetic</span>
        </div>
        <Link href="/dashboard" className="rounded-md bg-[var(--ink)] px-4 py-2.5 text-sm font-medium text-[var(--paper)]">Open lab</Link>
      </nav>

      <section className="mx-auto grid min-h-[720px] max-w-[1440px] items-center gap-16 px-6 py-16 lg:grid-cols-[0.82fr_1.18fr] lg:px-12 lg:py-24">
        <div>
          <div className="mb-7 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">
            <span className="size-1.5 rounded-full bg-[var(--accent)]" /> Financial data intelligence
          </div>
          <h1 className="max-w-2xl text-5xl font-semibold leading-[0.98] tracking-[-0.065em] sm:text-6xl xl:text-7xl">
            ETF data, made observable.
          </h1>
          <p className="mt-7 max-w-xl text-lg leading-8 text-[var(--muted)]">
            Explore, compare and audit ETF datasets through similarity search, anomaly detection and data observability.
          </p>
          <div className="mt-10 flex flex-wrap items-center gap-3">
            <Link href="/dashboard" className="flex items-center gap-2 rounded-md bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white">
              Explore dataset <ArrowRight size={15} />
            </Link>
            <Link href="/architecture" className="rounded-md border hairline bg-[var(--surface)] px-5 py-3 text-sm font-semibold">View architecture</Link>
          </div>
          <div className="mt-14 grid grid-cols-3 gap-7 border-t hairline pt-6 text-sm">
            <div><div className="metric-value text-2xl font-semibold">4,860</div><div className="mt-1 text-[var(--muted)]">ETFs modeled</div></div>
            <div><div className="metric-value text-2xl font-semibold">12,740</div><div className="mt-1 text-[var(--muted)]">Listings</div></div>
            <div><div className="metric-value text-2xl font-semibold">96.4</div><div className="mt-1 text-[var(--muted)]">Health score</div></div>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-xl border hairline bg-[var(--surface)] shadow-[0_30px_90px_rgba(17,26,33,0.13)]">
          <div className="flex items-center justify-between border-b hairline px-5 py-3">
            <div className="flex items-center gap-2 text-xs font-semibold"><Activity size={14} className="text-[var(--accent)]" /> DATASET COMMAND CENTER</div>
            <div className="mono text-[10px] text-[var(--muted)]">SNAPSHOT 2026-08-28</div>
          </div>
          <div className="grid grid-cols-3 border-b hairline">
            {[['Tracked AUM','€2.84T','+2.7%'],['Completeness','98.6%','+0.4 pp'],['Active anomalies','17','−5']].map(([label,value,delta]) => (
              <div key={label} className="border-r hairline p-5 last:border-r-0">
                <div className="text-[11px] uppercase tracking-wider text-[var(--muted)]">{label}</div>
                <div className="metric-value mt-2 text-2xl font-semibold">{value}</div>
                <div className="mt-1 text-xs text-[var(--accent)]">{delta} vs prior</div>
              </div>
            ))}
          </div>
          <div className="grid gap-0 lg:grid-cols-[1.35fr_0.65fr]">
            <div className="border-r hairline p-5">
              <div className="mb-5 flex items-center justify-between"><span className="text-sm font-semibold">AUM coverage trend</span><span className="text-xs text-[var(--muted)]">12 snapshots</span></div>
              <div className="flex h-52 items-end gap-2 border-b hairline pb-1">
                {bars.map((height, index) => <div key={index} className="relative flex-1 rounded-t-sm bg-[var(--accent-soft)]" style={{height: `${height}%`}}><div className="absolute inset-x-0 bottom-0 rounded-t-sm bg-[var(--accent)] opacity-70" style={{height: `${Math.max(35,height-18)}%`}} /></div>)}
              </div>
              <div className="mt-3 flex justify-between text-[10px] text-[var(--muted)]"><span>JUL 13</span><span>AUG 28</span></div>
            </div>
            <div className="p-5">
              <div className="text-sm font-semibold">Provider reliability</div>
              <div className="mt-5 space-y-4">
                {[['Atlas Index','98'],['Northstar AM','96'],['Helix Funds','94'],['Meridian','89']].map(([name,score]) => (
                  <div key={name}><div className="mb-1.5 flex justify-between text-xs"><span>{name}</span><span className="mono">{score}</span></div><div className="h-1.5 rounded-full bg-[var(--line)]"><div className="h-full rounded-full bg-[var(--accent)]" style={{width: `${score}%`}} /></div></div>
                ))}
              </div>
            </div>
          </div>
          <div className="noise flex items-center justify-between border-t hairline px-5 py-4 text-xs text-[var(--muted)]"><span>All metrics are computed from synthetic demo records.</span><span className="text-[var(--accent)]">Lineage verified ✓</span></div>
        </div>
      </section>

      <section id="capabilities" className="border-y hairline bg-[var(--surface)]">
        <div className="mx-auto grid max-w-[1440px] md:grid-cols-2 xl:grid-cols-4">
          {[
            [Radar,'Explainable similarity','Weighted signals show exactly why two funds are alike.'],
            [ShieldCheck,'Data observability','Freshness, completeness and validity at provider level.'],
            [Activity,'Anomaly detection','Rules and ML surface unusual records with human context.'],
            [GitBranch,'Data lineage','Trace a metric from source snapshot to analytical output.'],
          ].map(([Icon,title,copy],i) => {
            const Glyph = Icon as typeof Radar;
            return <div key={String(title)} className="border-b border-r hairline p-8 md:last:border-b-0 xl:border-b-0"><Glyph size={19} className="text-[var(--accent)]"/><h2 className="mt-8 font-semibold tracking-tight">{String(title)}</h2><p className="mt-2 text-sm leading-6 text-[var(--muted)]">{String(copy)}</p><div className="mono mt-8 text-[10px] text-[var(--muted)]">0{i+1}</div></div>;
          })}
        </div>
      </section>
    </main>
  );
}
