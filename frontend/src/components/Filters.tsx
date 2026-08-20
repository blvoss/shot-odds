import type { PointFilters } from "../types";

interface Props {
  filters: PointFilters;
  onChange: (filters: PointFilters) => void;
}

function emptyToUndefined(v: string): string | undefined {
  return v === "" ? undefined : v;
}

export default function Filters({ filters, onChange }: Props) {
  return (
    <div className="card filters">
      <div className="filter-field">
        <label htmlFor="server">Server</label>
        <select
          id="server"
          value={filters.server ?? ""}
          onChange={(e) =>
            onChange({ ...filters, server: emptyToUndefined(e.target.value) as PointFilters["server"] })
          }
        >
          <option value="">Any</option>
          <option value="player1">Player 1</option>
          <option value="player2">Player 2</option>
        </select>
      </div>
      <div className="filter-field">
        <label htmlFor="winner">Winner</label>
        <select
          id="winner"
          value={filters.winner ?? ""}
          onChange={(e) =>
            onChange({ ...filters, winner: emptyToUndefined(e.target.value) as PointFilters["winner"] })
          }
        >
          <option value="">Any</option>
          <option value="player1">Player 1</option>
          <option value="player2">Player 2</option>
        </select>
      </div>
      <div className="filter-field">
        <label htmlFor="start">From point #</label>
        <input
          id="start"
          type="number"
          min={1}
          value={filters.start ?? ""}
          onChange={(e) => onChange({ ...filters, start: e.target.value === "" ? undefined : Number(e.target.value) })}
        />
      </div>
      <div className="filter-field">
        <label htmlFor="end">To point #</label>
        <input
          id="end"
          type="number"
          min={1}
          value={filters.end ?? ""}
          onChange={(e) => onChange({ ...filters, end: e.target.value === "" ? undefined : Number(e.target.value) })}
        />
      </div>
    </div>
  );
}
