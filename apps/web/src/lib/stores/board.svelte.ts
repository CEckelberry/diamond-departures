import type { BoardRow } from '$lib/components/board/types';

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
		stat: String(entry.stat_value ?? 0),
		stats: entry.additional_stats ?? {},
		justQualified: Boolean(entry.newly_qualified),
		qualifiedAt: entry.qualified_at ?? null
	}));
}
