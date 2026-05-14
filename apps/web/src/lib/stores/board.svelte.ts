import type { BoardRow } from "$lib/components/board/types";

export type BoardEntry = {
	rank: number;
	player: { id: number; name: string; team_abbr: string; headshot_url: string; position: string; };
	stat_value: number;
	additional_stats: Record<string, number>;
	freshness: { timestamp: string; age_category: "live" | "recent" | "stale" | "old"; };
	newly_qualified?: boolean;
};

class BoardStore {
	entries = $state<BoardEntry[]>([]);

	set(entries: BoardEntry[]) {
		this.entries = [...entries];
	}

	applyDelta(payload: any) {
		const next = [...this.entries];
		for (const change of payload.changes) {
			const entry = next.find((item) => item.player.id === change.player_id);
			if (!entry) continue;
			if (typeof change.new_rank === "number") entry.rank = change.new_rank;
			if (change.newly_qualified) entry.newly_qualified = true;
			for (const stat of change.changed_stats) {
				if (stat.name === "stat_value") entry.stat_value = Number(stat.new);
			}
		}
		next.sort((a, b) => a.rank - b.rank);
		this.entries = next;
	}
}

export const boardStore = new BoardStore();

export function toBoardRows(entries: BoardEntry[]): BoardRow[] {
	return entries.map((entry, index) => ({
		playerId: entry.player?.id ?? 0,
		rank: String(entry.rank || index + 1).padStart(3, " "),
		player: (entry.player?.name ?? "UNKNOWN").toUpperCase(),
		team: (entry.player?.team_abbr ?? "---").toUpperCase(),
		position: (entry.player?.position ?? "--").toUpperCase(),
		stat: String(entry.stat_value ?? 0),
		stats: entry.additional_stats ?? {},
		justQualified: Boolean(entry.newly_qualified)
	}));
}
