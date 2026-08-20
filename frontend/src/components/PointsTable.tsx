import type { PointOut } from "../types";

const PLAYER_LABEL: Record<string, string> = { player1: "Player 1", player2: "Player 2" };
const PLAYER_COLOR: Record<string, string> = { player1: "var(--player1)", player2: "var(--player2)" };

function PlayerTag({ player }: { player: string }) {
  return (
    <span className="player-tag">
      <span className="swatch" style={{ background: PLAYER_COLOR[player] }} />
      {PLAYER_LABEL[player] ?? player}
    </span>
  );
}

interface Props {
  points: PointOut[];
}

export default function PointsTable({ points }: Props) {
  return (
    <div className="card">
      <h2>Points ({points.length})</h2>
      {points.length === 0 ? (
        <div className="empty-state">No points match the current filters.</div>
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Server</th>
                <th>Winner</th>
                <th>Outcome</th>
                <th>Shots</th>
              </tr>
            </thead>
            <tbody>
              {points.map((p) => (
                <tr key={p.index}>
                  <td>{p.index}</td>
                  <td>
                    <PlayerTag player={p.server} />
                  </td>
                  <td>
                    <PlayerTag player={p.winner} />
                  </td>
                  <td>{p.outcome}</td>
                  <td>{p.shots.length}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
