import { useState } from "react";
import type { PlayerStats } from "../types";

const COURT_WIDTH_M = 8.23;
const COURT_LENGTH_M = 23.77;
const SCALE = 100; // meters -> SVG user units
const VB_W = COURT_WIDTH_M * SCALE;
const VB_H = COURT_LENGTH_M * SCALE;
const NET_Y = VB_H / 2;
const SERVICE_OFFSET = 6.4 * SCALE;
const MARKER_R = 26;

type LocationKind = "contact" | "bounce";

interface Props {
  player1: PlayerStats;
  player2: PlayerStats;
}

interface TooltipState {
  x: number;
  y: number;
  label: string;
  courtX: number;
  courtY: number;
}

export default function CourtScatter({ player1, player2 }: Props) {
  const [kind, setKind] = useState<LocationKind>("contact");
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  const series: { label: string; color: string; points: [number, number][] }[] = [
    {
      label: "Player 1",
      color: "var(--player1)",
      points: kind === "contact" ? player1.contact_locations : player1.bounce_locations,
    },
    {
      label: "Player 2",
      color: "var(--player2)",
      points: kind === "contact" ? player2.contact_locations : player2.bounce_locations,
    },
  ];

  const hasData = series.some((s) => s.points.length > 0);

  return (
    <div className="card">
      <h2>{kind === "contact" ? "Contact locations" : "Bounce locations"}</h2>
      <div className="scatter-toggle">
        <button className={kind === "contact" ? "active" : ""} onClick={() => setKind("contact")}>
          Contact
        </button>
        <button className={kind === "bounce" ? "active" : ""} onClick={() => setKind("bounce")}>
          Bounce
        </button>
      </div>
      <div className="legend">
        {series.map((s) => (
          <span className="legend-item" key={s.label}>
            <span className="swatch" style={{ background: s.color }} />
            {s.label}
          </span>
        ))}
      </div>
      {hasData ? (
        <div className="court-wrap" style={{ width: 240 }}>
          <svg
            viewBox={`0 0 ${VB_W} ${VB_H}`}
            width={240}
            height={(240 * VB_H) / VB_W}
            role="img"
            aria-label={`Court diagram of ${kind} locations`}
          >
            <rect x={0} y={0} width={VB_W} height={VB_H} fill="var(--surface)" stroke="var(--baseline)" strokeWidth={4} />
            <line x1={0} y1={NET_Y} x2={VB_W} y2={NET_Y} stroke="var(--baseline)" strokeWidth={4} />
            <line x1={0} y1={NET_Y - SERVICE_OFFSET} x2={VB_W} y2={NET_Y - SERVICE_OFFSET} stroke="var(--gridline)" strokeWidth={3} />
            <line x1={0} y1={NET_Y + SERVICE_OFFSET} x2={VB_W} y2={NET_Y + SERVICE_OFFSET} stroke="var(--gridline)" strokeWidth={3} />
            <line
              x1={VB_W / 2}
              y1={NET_Y - SERVICE_OFFSET}
              x2={VB_W / 2}
              y2={NET_Y + SERVICE_OFFSET}
              stroke="var(--gridline)"
              strokeWidth={3}
            />
            {series.map((s) =>
              s.points.map(([x, y], i) => (
                <circle
                  key={`${s.label}-${i}`}
                  cx={x * SCALE}
                  cy={y * SCALE}
                  r={MARKER_R}
                  fill={s.color}
                  fillOpacity={0.75}
                  stroke="var(--surface)"
                  strokeWidth={4}
                  onMouseEnter={(e) => {
                    const rect = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect();
                    const px = (x * SCALE * rect.width) / VB_W;
                    const py = (y * SCALE * rect.height) / VB_H;
                    setTooltip({ x: px, y: py, label: s.label, courtX: x, courtY: y });
                  }}
                  onMouseLeave={() => setTooltip(null)}
                />
              )),
            )}
          </svg>
          {tooltip && (
            <div className="court-tooltip" style={{ left: tooltip.x, top: tooltip.y }}>
              {tooltip.label} · ({tooltip.courtX.toFixed(1)}m, {tooltip.courtY.toFixed(1)}m)
            </div>
          )}
        </div>
      ) : (
        <div className="empty-state">No {kind} data for the current filters.</div>
      )}
    </div>
  );
}
