import { error } from "@sveltejs/kit";

export type BoardEntryPayload = {
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

const VALID_SORTS = new Set(["wRC+", "OPS", "ERA", "FIP", "K-BB%"]);

function resolveView(params: URLSearchParams): string {
	const view = params.get("view") ?? "hitters";
	if (view === "pitchers") return "pitchers";
	if (view !== "positions") return "hitters";

	const position = (params.get("position") ?? "all").toUpperCase();
	if (position === "SS") return "hitters_ss";
	if (position === "OF") return "hitters_of";
	if (position === "SP") return "pitchers_sp";
	if (position === "RP") return "pitchers_rp";
	return "hitters";
}

function resolveSort(params: URLSearchParams, apiView: string): string {
	const fromUrl = params.get("sort") ?? "";
	if (VALID_SORTS.has(fromUrl)) return fromUrl;
	return apiView.startsWith("pitchers") ? "ERA" : "wRC+";
}

export const load = async ({
	fetch,
	url,
}: {
	fetch: typeof globalThis.fetch;
	url: URL;
}) => {
	const params = new URLSearchParams();
	params.set('view', resolveView(url.searchParams));
	params.set('sort', resolveSort(url.searchParams, params.get('view') ?? 'hitters'));

	const response = await fetch('/api/board?' + params.toString());
	if (!response.ok) {
		throw error(response.status, "Failed to load board");
	}

	const payload = (await response.json()) as {
		view: string;
		sort: string;
		entries: BoardEntryPayload[];
	};

	return {
		boardView: payload.view,
		boardSort: payload.sort,
		entries: payload.entries,
	};
};
