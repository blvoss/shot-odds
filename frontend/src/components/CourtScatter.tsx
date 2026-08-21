import { useMemo, useState } from "react";
import type { PlayerStats } from "../types";

const COURT_WIDTH_M = 8.23;
const COURT_LENGTH_M = 23.77;
const SCALE = 100; // meters -> SVG user units
const VB_W = COURT_WIDTH_M * SCALE;
const VB_H = COURT_LENGTH_M * SCALE;
const NET_Y = VB_H / 2;
const SERVICE_OFFSET = 6.4 * SCALE;

const RENDER_WIDTH_PX = 240;
const MARKER_RADIUS_PX = 7.5;
const MARKER_STROKE_PX = 1.2;
const BOUNDARY_WIDTH_PX = 1.2;
const SERVICE_LINE_WIDTH_PX = 0.9;

type LocationKind = "contact" | "bounce";

interface Props {
  player1: PlayerStats;
  player2: PlayerStats;
}

interface Series {
  label: string;
  color: string;
  points: [number, number][];
}

interface TooltipState {
  x: number;
  y: number;
  label: string;
  courtX: number;
  courtY: number;
}

/**
 * Sizes the viewBox to the smallest box, centered on the court, that still
 * contains every point (plus enough padding for a marker's own radius so
 * it isn't clipped at the edge). Points from real data can land anywhere,
 * so this can't be a fixed margin -- it has to fit whatever the match
 * actually produced.
 */
function computeViewBox(series: Series[]) {
  const xs = series.flatMap((s) => s.points.map(([x]) => x));
  const ys = series.flatMap((s) => s.points.map(([, y]) => y));

  const rawMarginX = Math.max(0, -Math.min(0, ...xs), Math.max(COURT_WIDTH_M, ...xs) - COURT_WIDTH_M);
  const rawMarginY = Math.max(0, -Math.min(0, ...ys), Math.max(COURT_LENGTH_M, ...ys) - COURT_LENGTH_M);

  // One correction pass for the marker's own radius: estimate the scale
  // from the raw margin, convert the target on-screen radius into meters
  // at that scale, then pad the margin by it. The radius is tiny relative
  // to court size, so a second pass isn't needed.
  const rawTotalW = (COURT_WIDTH_M + 2 * rawMarginX) * SCALE;
  const initialScale = RENDER_WIDTH_PX / rawTotalW;
  const markerRadiusMeters = MARKER_RADIUS_PX / initialScale / SCALE;

  const marginX = rawMarginX + markerRadiusMeters;
  const marginY = rawMarginY + markerRadiusMeters;

  const totalW = (COURT_WIDTH_M + 2 * marginX) * SCALE;
  const totalH = (COURT_LENGTH_M + 2 * marginY) * SCALE;

  return {
    originX: -marginX * SCALE,
    originY: -marginY * SCALE,
    totalW,
    totalH,
    scale: RENDER_WIDTH_PX / totalW,
  };
}

export default function CourtScatter({ player1, player2 }: Props) {
  const [kind, setKind] = useState<LocationKind>("contact");
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  const series: Series[] = [
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
  const { originX, originY, totalW, totalH, scale } = useMemo(() => computeViewBox(series), [series]);
  const renderHeight = (RENDER_WIDTH_PX * totalH) / totalW;

  const markerR = MARKER_RADIUS_PX / scale;
  const markerStroke = MARKER_STROKE_PX / scale;
  const boundaryWidth = BOUNDARY_WIDTH_PX / scale;
  const serviceLineWidth = SERVICE_LINE_WIDTH_PX / scale;

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
        <div className="court-wrap" style={{ width: RENDER_WIDTH_PX }}>
          <svg
            viewBox={`${originX} ${originY} ${totalW} ${totalH}`}
            width={RENDER_WIDTH_PX}
            height={renderHeight}
            role="img"
            aria-label={`Court diagram of ${kind} locations`}
          >
            <rect
              x={0}
              y={0}
              width={VB_W}
              height={VB_H}
              fill="var(--surface)"
              stroke="var(--baseline)"
              strokeWidth={boundaryWidth}
            />
            <line x1={0} y1={NET_Y} x2={VB_W} y2={NET_Y} stroke="var(--baseline)" strokeWidth={boundaryWidth} />
            <line
              x1={0}
              y1={NET_Y - SERVICE_OFFSET}
              x2={VB_W}
              y2={NET_Y - SERVICE_OFFSET}
              stroke="var(--gridline)"
              strokeWidth={serviceLineWidth}
            />
            <line
              x1={0}
              y1={NET_Y + SERVICE_OFFSET}
              x2={VB_W}
              y2={NET_Y + SERVICE_OFFSET}
              stroke="var(--gridline)"
              strokeWidth={serviceLineWidth}
            />
            <line
              x1={VB_W / 2}
              y1={NET_Y - SERVICE_OFFSET}
              x2={VB_W / 2}
              y2={NET_Y + SERVICE_OFFSET}
              stroke="var(--gridline)"
              strokeWidth={serviceLineWidth}
            />
            {series.map((s) =>
              s.points.map(([x, y], i) => (
                <circle
                  key={`${s.label}-${i}`}
                  cx={x * SCALE}
                  cy={y * SCALE}
                  r={markerR}
                  fill={s.color}
                  fillOpacity={0.75}
                  stroke="var(--surface)"
                  strokeWidth={markerStroke}
                  onMouseEnter={(e) => {
                    const rect = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect();
                    const px = ((x * SCALE - originX) * rect.width) / totalW;
                    const py = ((y * SCALE - originY) * rect.height) / totalH;
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
