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
};

export type BoardRow = {
	playerId: number;
	rank: string;
	player: string;
	team: string;
	position: string;
	stat: string;
};
