"use client";

import { useEffect, useState } from "react";
import { apiRequest, type ApiHealth } from "@/lib/api";

export function LiveApiIndicator(){
  const [health,setHealth]=useState<ApiHealth|null>(null);
  useEffect(()=>{apiRequest<ApiHealth>("/health").then(setHealth).catch(()=>setHealth(null))},[]);
  return <div className="fixed bottom-3 right-3 z-30 rounded-full border hairline bg-[var(--surface)]/95 px-3 py-1.5 text-[9px] shadow-md backdrop-blur"><span className={`mr-1.5 inline-block size-1.5 rounded-full ${health?"bg-[var(--accent)]":"bg-amber-500"}`}/>{health?`DuckDB API · ${health.snapshot}`:"Local demo · API optional"}</div>
}
