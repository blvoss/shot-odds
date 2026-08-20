import { useEffect, useState } from "react";
import { getMatch, getPoints, getStats } from "./api";
import Filters from "./components/Filters";
import StatTiles from "./components/StatTiles";
import CourtScatter from "./components/CourtScatter";
import PointsTable from "./components/PointsTable";
import type { MatchOut, PointFilters, PointOut, StatsOut } from "./types";

export default function App() {
  const [matchIdInput, setMatchIdInput] = useState("1");
  const [matchId, setMatchId] = useState<number | null>(1);
  const [match, setMatch] = useState<MatchOut | null>(null);
  const [stats, setStats] = useState<StatsOut | null>(null);
  const [points, setPoints] = useState<PointOut[]>([]);
  const [filters, setFilters] = useState<PointFilters>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (matchId === null) return;
    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([getMatch(matchId), getStats(matchId, filters), getPoints(matchId, filters)])
      .then(([matchRes, statsRes, pointsRes]) => {
        if (cancelled) return;
        setMatch(matchRes);
        setStats(statsRes);
        setPoints(pointsRes);
      })
      .catch((err: Error) => {
        if (cancelled) return;
        setMatch(null);
        setStats(null);
        setPoints([]);
        setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [matchId, filters]);

  return (
    <>
      <h1>Shot Odds</h1>
      <p className="subtitle">Match stats dashboard</p>

      <div className="match-picker">
        <input
          type="number"
          min={1}
          value={matchIdInput}
          onChange={(e) => setMatchIdInput(e.target.value)}
          aria-label="Match ID"
        />
        <button
          disabled={matchIdInput === ""}
          onClick={() => setMatchId(Number(matchIdInput))}
        >
          Load match
        </button>
        {match && <span className="status-pill">{match.status}</span>}
        {loading && <span className="status-pill">Loading…</span>}
      </div>

      {error && <div className="error-banner">{error}</div>}

      {stats && (
        <>
          <Filters filters={filters} onChange={setFilters} />

          <div className="kpi-row">
            <StatTiles label="Player 1" color="var(--player1)" stats={stats.player1} />
            <StatTiles label="Player 2" color="var(--player2)" stats={stats.player2} />
          </div>

          <CourtScatter player1={stats.player1} player2={stats.player2} />

          <PointsTable points={points} />
        </>
      )}
    </>
  );
}
