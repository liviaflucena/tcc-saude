const BASE = "";

export async function apiGet<T = any>(path: string, params?: Record<string, any>): Promise<T> {
  const url = new URL(`${BASE}${path}`, window.location.origin);
  if (params) Object.entries(params).forEach(([k,v]) => v!==undefined && url.searchParams.append(k, String(v)));
  const r = await fetch(url.toString(), { headers: { "Accept": "application/json" } });
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
  return r.json() as Promise<T>;
}
