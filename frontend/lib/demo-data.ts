import type { Anomaly, ETF, Provider } from "@/types";

export const etfs: ETF[] = [
  { isin:"IE1000000663", name:"Atlas Global Large Cap UCITS ETF", issuer:"Atlas Index", assetClass:"Equity", category:"Global Large Cap", benchmark:"Global Developed 1000", aum:12840, currency:"EUR", ter:.12, age:13.4, exchanges:["Xetra","LSE","Euronext Paris","SIX"], tickers:["ATGL","AGLC","ATWD","AGLX"], quality:99, provider:"Atlas Data Feed", freshness:1, replication:"Physical", distribution:"Accumulating", domicile:"IE" },
  { isin:"IE1000001249", name:"Northstar US Equity Core UCITS ETF", issuer:"Northstar Asset Management", assetClass:"Equity", category:"US Equity", benchmark:"US Large Cap 500", aum:9850, currency:"USD", ter:.09, age:11.8, exchanges:["LSE","Xetra","SIX"], tickers:["NSUS","NUSC","NUSA"], quality:98, provider:"Northstar Public Data", freshness:1, replication:"Physical", distribution:"Distributing", domicile:"IE" },
  { isin:"IE1000002072", name:"Helix Global Aggregate Bond ETF", issuer:"Helix Funds", assetClass:"Fixed Income", category:"Global Aggregate Bond", benchmark:"Global Aggregate Bond", aum:7210, currency:"EUR", ter:.14, age:9.6, exchanges:["Xetra","Euronext Paris","Borsa Italiana"], tickers:["HGAB","HXGA","HLXB"], quality:97, provider:"Helix Market Files", freshness:2, replication:"Sampling", distribution:"Accumulating", domicile:"LU" },
  { isin:"IE1000003487", name:"Meridian Europe 600 Index ETF", issuer:"Meridian ETFs", assetClass:"Equity", category:"European Equity", benchmark:"Europe 600", aum:6380, currency:"EUR", ter:.16, age:8.2, exchanges:["Xetra","Euronext Paris","Borsa Italiana","Euronext Amsterdam"], tickers:["MEU6","M600","MDEU","MEQA"], quality:96, provider:"Meridian Data Service", freshness:2, replication:"Physical", distribution:"Distributing", domicile:"LU" },
  { isin:"IE1000004210", name:"Aperture Climate Transition ETF", issuer:"Aperture Index", assetClass:"Equity", category:"Climate Transition", benchmark:"Global Climate Transition", aum:2940, currency:"EUR", ter:.28, age:4.1, exchanges:["LSE","Xetra","Euronext Paris"], tickers:["ACTR","APCT","CLIM"], quality:95, provider:"Aperture Public Feed", freshness:1, replication:"Sampling", distribution:"Accumulating", domicile:"IE" },
  { isin:"IE1000005792", name:"Cedar Euro Government 7–10Y ETF", issuer:"Cedar Capital", assetClass:"Fixed Income", category:"Euro Government Bond", benchmark:"Euro Sovereign 7-10Y", aum:1860, currency:"EUR", ter:.18, age:6.7, exchanges:["Xetra","Borsa Italiana"], tickers:["CEG7","CEUR"], quality:94, provider:"Cedar Fund Data", freshness:3, replication:"Physical", distribution:"Distributing", domicile:"LU" },
  { isin:"IE1000006535", name:"Quarry Emerging Markets Broad ETF", issuer:"Quarry Investments", assetClass:"Equity", category:"Emerging Markets", benchmark:"Emerging Markets Broad", aum:1540, currency:"USD", ter:.22, age:5.9, exchanges:["LSE","Xetra","SIX"], tickers:["QEMB","QEMK","QEMR"], quality:93, provider:"Quarry Product Feed", freshness:2, replication:"Physical", distribution:"Accumulating", domicile:"IE" },
  { isin:"IE1000007112", name:"Vela Global Technology Leaders ETF", issuer:"Vela Asset Management", assetClass:"Equity", category:"Technology", benchmark:"Global Technology Leaders", aum:990, currency:"USD", ter:.35, age:3.2, exchanges:["LSE","Xetra"], tickers:["VTEC","VGLT"], quality:92, provider:"Vela Fund Files", freshness:4, replication:"Physical", distribution:"Accumulating", domicile:"IE" },
  { isin:"IE1000008068", name:"Atlas Diversified Commodity ETF", issuer:"Atlas Index", assetClass:"Commodity", category:"Broad Commodities", benchmark:"Diversified Commodity", aum:740, currency:"USD", ter:.39, age:7.4, exchanges:["LSE","SIX"], tickers:["ADCO","ATCM"], quality:96, provider:"Atlas Data Feed", freshness:1, replication:"Synthetic", distribution:"Accumulating", domicile:"IE" },
  { isin:"IE1000009271", name:"Northstar EUR Corporate 1–3Y ETF", issuer:"Northstar Asset Management", assetClass:"Fixed Income", category:"Short Duration", benchmark:"EUR Corporate 1-3Y", aum:510, currency:"EUR", ter:.15, age:2.8, exchanges:["Xetra","Euronext Paris"], tickers:["NE13","NSCD"], quality:91, provider:"Northstar Public Data", freshness:7, replication:"Sampling", distribution:"Distributing", domicile:"LU" },
  { isin:"IE1000010146", name:"Helix Global Balanced 60/40 ETF", issuer:"Helix Funds", assetClass:"Multi-Asset", category:"Balanced", benchmark:"Global 60/40", aum:185, currency:"EUR", ter:.42, age:1.6, exchanges:["Xetra"], tickers:["H604"], quality:84, provider:"Helix Market Files", freshness:18, replication:"Sampling", distribution:"Accumulating", domicile:"IE" },
  { isin:"IE1000011327", name:"Meridian Physical Gold Reference ETF", issuer:"Meridian ETFs", assetClass:"Commodity", category:"Gold", benchmark:"Physical Gold Reference", aum:0, currency:"USD", ter:.24, age:.8, exchanges:["LSE","SIX"], tickers:["MPGL","MGLD"], quality:68, provider:"Meridian Data Service", freshness:34, replication:"Physical", distribution:"Accumulating", domicile:"IE" },
];

export const providers: Provider[] = [
  {name:"Atlas Data Feed",score:98,completeness:99.4,freshness:100,consistency:98.8,anomalies:1,records:68},
  {name:"Northstar Public Data",score:96,completeness:98.8,freshness:98,consistency:97.2,anomalies:2,records:57},
  {name:"Helix Market Files",score:94,completeness:97.1,freshness:93,consistency:96.5,anomalies:3,records:44},
  {name:"Aperture Public Feed",score:92,completeness:96.4,freshness:96,consistency:91.8,anomalies:2,records:35},
  {name:"Cedar Fund Data",score:89,completeness:94.2,freshness:88,consistency:92.1,anomalies:4,records:31},
  {name:"Meridian Data Service",score:78,completeness:89.6,freshness:72,consistency:87.4,anomalies:7,records:39},
];

export const anomalies: Anomaly[] = [
  {id:"a-001",isin:"IE1000011327",severity:"High",type:"Zero AUM",title:"Suspicious zero AUM",explanation:"A live, multi-listing ETF reports exactly zero AUM. This often indicates a source placeholder rather than an economic value.",observed:"USD 0M",expected:"Positive AUM or unavailable"},
  {id:"a-002",isin:"IE1000010146",severity:"Medium",type:"Stale source",title:"Fund facts are stale",explanation:"The latest provider observation is older than the 14-day freshness objective.",observed:"18 days old",expected:"≤ 14 days"},
  {id:"a-003",isin:"IE1000003487",severity:"Low",type:"Broad coverage",title:"Unusually broad exchange coverage",explanation:"The listing count is above the 95th percentile for this demo universe.",observed:"4 listings",expected:"1–3 listings"},
  {id:"a-004",isin:"IE1000007112",severity:"Low",type:"Unusual profile",title:"Unusual multivariate profile",explanation:"Isolation Forest marked this record unusual; TER is the largest standardized distance from the median.",observed:"TER 0.35%",expected:"Median 0.18%"},
];

export const snapshots = [
  {date:"2026-08-14",etfs:225,listings:506,coverage:94.8,health:92},
  {date:"2026-08-21",etfs:232,listings:526,coverage:96.1,health:94},
  {date:"2026-08-28",etfs:239,listings:545,coverage:98.7,health:96},
];

export const issuerAum = [
  {name:"Atlas",value:13580},{name:"Northstar",value:10360},{name:"Helix",value:7395},{name:"Meridian",value:6380},{name:"Aperture",value:2940},{name:"Cedar",value:1860},{name:"Quarry",value:1540},{name:"Vela",value:990},
];

export function formatAum(value: number | null, currency = "EUR") {
  if (value === null) return "Not available";
  const symbol = currency === "EUR" ? "€" : currency === "GBP" ? "£" : currency === "USD" ? "$" : `${currency} `;
  return value >= 1000 ? `${symbol}${(value / 1000).toFixed(value >= 10000 ? 1 : 2)}B` : `${symbol}${value.toFixed(0)}M`;
}

export function similarity(source: ETF, target: ETF) {
  const parts = [
    {label:"Semantic characteristics",weight:25,value:source.category===target.category?1:source.assetClass===target.assetClass?.7:.15},
    {label:"Asset-class match",weight:20,value:source.assetClass===target.assetClass?1:0},
    {label:"Index similarity",weight:15,value:source.benchmark===target.benchmark?1:source.category===target.category?.7:.1},
    {label:"Currency match",weight:12,value:source.currency===target.currency?1:0},
    {label:"AUM similarity",weight:11,value:source.aum&&target.aum?Math.max(0,1-Math.abs(Math.log1p(source.aum)-Math.log1p(target.aum))/5):0},
    {label:"Exchange overlap",weight:10,value:source.exchanges.filter(x=>target.exchanges.includes(x)).length/new Set([...source.exchanges,...target.exchanges]).size},
    {label:"Fund-age proximity",weight:7,value:Math.max(0,1-Math.abs(source.age-target.age)/15)},
  ];
  const contributions=parts.map(p=>({...p,points:+(p.weight*p.value).toFixed(1)}));
  return {score:+contributions.reduce((a,b)=>a+b.points,0).toFixed(1),contributions:contributions.sort((a,b)=>b.points-a.points)};
}
