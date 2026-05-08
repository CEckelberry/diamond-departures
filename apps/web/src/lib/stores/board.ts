import { derived, writable } from "svelte/store";
import type { BoardRow } from "$lib/components/board/types";

export type BoardEntry = {
	rank: number;
	player: {
		id: number;
		name: string;
		team_abbr: string;
		headshot_url: string;
		position: string;
	};
	stat_value: number;
	freshness: {
		timestamp: string;
		age_category: "live" | "recent" | "stale" | "old";
	};
	newly_qualified?: boolean;
	qualified_at?: string | null;
};

type DeltaPayload = {
	view: string;
	sort: string;
	changes: Array<{
		player_id: number;
		old_rank: number | null;
		new_rank: number | null;
		newly_qualified?: boolean;
		qualified_at?: string | null;
		changed_stats: Array<{ name: string; old: unknown; new: unknown }>;
	}>;
};

type SnapshotPayload = {
	view: string;
	sort: string;
	entries: BoardEntry[];
};

type BoardState = {
	view: string;
	sort: string;
	entries: BoardEntry[];
};

const state = writable<BoardState>({
	view: "hitters",
	sort: "wRC+",
	entries: [],
});

export const boardRows = derived(state, ($state) =>
	toBoardRows($state.entries),
);

export function seedBoard(view: string, sort: string, entries: BoardEntry[]) {
	state.set({ view, sort, entries: [...entries] });
}

export function applySnapshot(payload: SnapshotPayload) {
	state.set({
		view: payload.view,
		sort: payload.sort,
		entries: [...payload.entries],
	});
}

export function applyDelta(payload: DeltaPayload) {
	state.update((current) => {
		if (payload.view !== current.view || payload.sort !== current.sort)
			return current;
		const nextEntries = current.entries.map((entry) => ({
			...entry,
			player: { ...entry.player },
			freshness: { ...entry.freshness },
		}));

		for (const change of payload.changes) {
			const entry = nextEntries.find(
				(item) => item.player.id === change.player_id,
			);
			if (!entry) continue;
			if (typeof change.new_rank === "number") entry.rank = change.new_rank;
			if (change.newly_qualified) {
				entry.newly_qualified = true;
				entry.qualified_at = change.qualified_at ?? new Date().toISOString();
			} else if (change.qualified_at) {
				entry.qualified_at = change.qualified_at;
			}

			for (const stat of change.changed_stats) {
				if (stat.name !== "stat_value") continue;
				entry.stat_value = Number(stat.new);
			}
		}

		nextEntries.sort((left, right) => left.rank - right.rank);
		return {
			...current,
			entries: nextEntries,
		};
	});
}

function isWithin24Hours(timestamp: string | null | undefined): boolean {
	if (!timestamp) return false;
	const t = Date.parse(timestamp);
	if (Number.isNaN(t)) return false;
	return Date.now() - t <= 24 * 60 * 60 * 1000;
}

export function toBoardRows(entries: BoardEntry[]): BoardRow[] {
	return entries.map((entry) => ({
		playerId: entry.player.id,
		rank: String(entry.rank).padStart(3, " "),
		player: entry.player.name,
		team: entry.player.team_abbr,
		position: entry.player.position,
		stat: Number(entry.stat_value).toFixed(1),
		justQualified:
			Boolean(entry.newly_qualified) && isWithin24Hours(entry.qualified_at ?? null),
		qualifiedAt: entry.qualified_at ?? null,
	}));
}
