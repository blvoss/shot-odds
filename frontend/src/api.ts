import type { MatchOut, PointFilters, PointOut, StatsOut } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json() as Promise<T>;
}

function filterQuery(filters: PointFilters): string {
  const params = new URLSearchParams();
  if (filters.server) params.set("server", filters.server);
  if (filters.winner) params.set("winner", filters.winner);
  if (filters.start !== undefined) params.set("start", String(filters.start));
  if (filters.end !== undefined) params.set("end", String(filters.end));
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export function getMatch(matchId: number): Promise<MatchOut> {
  return request(`/matches/${matchId}`);
}

export function getStats(matchId: number, filters: PointFilters): Promise<StatsOut> {
  return request(`/matches/${matchId}/stats${filterQuery(filters)}`);
}

export function getPoints(matchId: number, filters: PointFilters): Promise<PointOut[]> {
  return request(`/matches/${matchId}/points${filterQuery(filters)}`);
}
