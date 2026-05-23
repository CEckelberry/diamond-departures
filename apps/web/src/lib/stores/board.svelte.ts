import type { BoardRow } from '$lib/components/board/types';

class AnimControl {
	// Set true before a bulk data swap so cells that stay mounted skip simultaneous animation.
	snap = $state(false);
	// Set true after the first-ever page load completes. Cells mounting after that snap
	// directly instead of running the cascade intro (avoids chaos on view switches).
	firstLoadDone = false;

	// Fraction of live-update cells that get the theatrical flip (vs snap directly).
	// Recomputed by Board whenever the board's visible height changes so the number of
	// simultaneous animated compositor layers never blows past the ~364-cell GPU budget.
	density = $state(1.0);

	adjustForViewport(boardBodyHeight: number, rowHeight: number, cellsPerRow: number) {
		const BUDGET = 364; // empirical: max simultaneous animated cells at ~60 fps (M3/M4 validated)
		const visibleRows = Math.max(1, Math.floor(boardBodyHeight / rowHeight));
		this.density = Math.min(1.0, Math.max(0.05, BUDGET / (visibleRows * cellsPerRow)));
	}
}
export const anim = new AnimControl();

export type BoardEntry = {
	rank: number;
	player: { id: number; name: string; team_abbr: string; headshot_url: string; position: string };
	stat_value: number;
	additional_stats: Record<string, number>;
	freshness: { timestamp: string; age_category: 'live' | 'recent' | 'stale' | 'old' };
	newly_qualified?: boolean;
	qualified_at?: string | null;
};

type DeltaChange = {
	player_id: number;
	old_rank?: number | null;
	new_rank?: number | null;
	newly_qualified?: boolean;
	qualified_at?: string | null;
	changed_stats: Array<{ name: string; old: unknown; new: unknown }>;
};

export function applySnapshot(payload: { entries: BoardEntry[] }): BoardEntry[] {
	return [...payload.entries];
}

export function applyDelta(entries: BoardEntry[], payload: { changes: DeltaChange[] }): BoardEntry[] {
	const next = [...entries];
	for (const change of payload.changes) {
		const entry = next.find((item) => item.player.id === change.player_id);
		if (!entry) continue;
		if (typeof change.new_rank === 'number') entry.rank = change.new_rank;
		if (change.newly_qualified) {
			entry.newly_qualified = true;
			entry.qualified_at = change.qualified_at ?? new Date().toISOString();
		}
		for (const stat of change.changed_stats) {
			if (stat.name === 'stat_value') entry.stat_value = Number(stat.new);
		}
	}
	next.sort((a, b) => a.rank - b.rank);
	return next;
}

export function toBoardRows(entries: BoardEntry[]): BoardRow[] {
	return entries.map((entry, index) => ({
		playerId: entry.player?.id ?? 0,
		rank: String(entry.rank || index + 1).padStart(3, ' '),
		player: (entry.player?.name ?? 'UNKNOWN').toUpperCase(),
		team: (entry.player?.team_abbr ?? '---').toUpperCase(),
		position: (entry.player?.position ?? '--').toUpperCase(),
		stat: (() => {
			const v = entry.stat_value ?? 0;
			if (!Number.isInteger(v) && v < 10) return v.toFixed(3);
			return String(Math.round(v));
		})(),
		stats: (() => {
			const s = { ...(entry.additional_stats ?? {}) };
			// OBP isn't seeded directly; derive it (OPS = OBP + SLG is exact by definition)
			if (!('OBP' in s) && 'OPS' in s && 'SLG' in s) {
				s['OBP'] = Math.round((s['OPS'] - s['SLG']) * 1000) / 1000;
			}
			return s;
		})(),
		justQualified: Boolean(entry.newly_qualified),
		qualifiedAt: entry.qualified_at ?? null
	}));
}
