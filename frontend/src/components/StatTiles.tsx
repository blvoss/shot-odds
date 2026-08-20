import type { PlayerStats } from "../types";

function fmtSpeed(v: number | null): string {
  return v === null ? "—" : `${v.toFixed(1)} m/s`;
}

interface Props {
  label: string;
  color: string;
  stats: PlayerStats;
}

export default function StatTiles({ label, color, stats }: Props) {
  const tiles = [
    { label: "Points won", value: String(stats.points_won) },
    { label: "Winners", value: String(stats.winners) },
    { label: "Errors", value: String(stats.errors) },
    { label: "Avg serve speed", value: fmtSpeed(stats.avg_serve_speed) },
    { label: "Avg groundstroke speed", value: fmtSpeed(stats.avg_groundstroke_speed) },
  ];

  return (
    <div className="card player-card" style={{ ["--player-color" as string]: color }}>
      <div className="player-card-title">
        <span className="swatch" style={{ background: color }} />
        {label}
      </div>
      <div className="stat-tiles">
        {tiles.map((tile) => (
          <div className="stat-tile" key={tile.label}>
            <div className="value">{tile.value}</div>
            <div className="label">{tile.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
