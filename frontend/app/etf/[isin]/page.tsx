import { AppShell } from "@/components/app-shell";
import { ETFDetail } from "@/components/etf-detail";

export default async function ETFPage({params}:{params:Promise<{isin:string}>}){const {isin}=await params;return <AppShell><ETFDetail isin={isin}/></AppShell>}
