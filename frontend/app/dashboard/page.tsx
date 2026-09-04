import Link from "next/link";

export default function DashboardPage() {
  return (
    <main className="min-h-screen p-6 lg:p-10">
      <div className="mx-auto max-w-[1500px]">
        <header className="flex items-center justify-between border-b hairline pb-5">
          <Link href="/" className="font-semibold tracking-[-0.03em]">ETF Intelligence Lab</Link>
          <span className="rounded-full bg-[var(--accent-soft)] px-3 py-1 text-xs text-[var(--accent)]">Demo dataset ready</span>
        </header>
        <div className="py-12">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--accent)]">Command center</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-[-0.05em]">Portfolio data at a glance</h1>
          <p className="mt-3 text-[var(--muted)]">The full analytical workspace is being connected to the standalone API.</p>
        </div>
      </div>
    </main>
  );
}
