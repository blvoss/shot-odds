export type MatchStatus =
  | "pending"
  | "downloading"
  | "ready_for_calibration"
  | "calibrated"
  | "processing"
  | "done"
  | "error";

export type Player = "player1" | "player2";
export type PointOutcome = "winner" | "error";
export type ShotType = "serve" | "groundstroke" | "other";

export interface MatchOut {
  id: number;
  source_type: string;
  source_reference: string;
  status: MatchStatus;
  error_message: string | null;
}

export interface ShotOut {
  shot_index: number;
  hitter: Player;
  shot_type: ShotType;
  contact_x: number;
  contact_y: number;
  contact_time: number;
  bounce_x: number;
  bounce_y: number;
  bounce_time: number;
  speed: number;
}

export interface PointOut {
  index: number;
  server: Player;
  winner: Player;
  outcome: PointOutcome;
  shots: ShotOut[];
}

export interface PlayerStats {
  points_won: number;
  winners: number;
  errors: number;
  avg_serve_speed: number | null;
  avg_groundstroke_speed: number | null;
  contact_locations: [number, number][];
  bounce_locations: [number, number][];
}

export interface StatsOut {
  player1: PlayerStats;
  player2: PlayerStats;
  total_points: number;
}

export interface PointFilters {
  server?: Player;
  winner?: Player;
  start?: number;
  end?: number;
}
