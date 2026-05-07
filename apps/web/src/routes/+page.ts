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

type ViewResolution = {
	apiView: string;
	selectedPosition: string;
};

function resolveView(params: URLSearchParams): ViewResolution {
	const view = params.get("view") ?? "hitters";
	if (view === "pitchers") {
		return { apiView: "pitchers", selectedPosition: "all" };
	}
	if (view !== "positions") {
		return { apiView: "hitters", selectedPosition: "all" };
	}

	const selectedPosition = (params.get("position") ?? "all").toUpperCase();
	if (selectedPosition === "SS") return { apiView: 'hitters_ss', selectedPosition: 'SS' };
	if (selectedPosition === "OF") return { apiView: "hitters_of", selectedPosition: "OF" };
	if (selectedPosition === "SP") return { apiView: "pitchers_sp", selectedPosition: "SP" };
	if (selectedPosition === "RP") return { apiView: "pitchers_rp", selectedPosition: "RP" };

	if (selectedPosition === "ALL") {
		return { apiView: "hitters", selectedPosition: "all" };
	}

	return { apiView: "hitters", selectedPosition };
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
	const resolvedView = resolveView(url.searchParams);
	params.set("view", resolvedView.apiView);
	params.set("sort", resolveSort(url.searchParams, resolvedView.apiView));

	const response = await fetch("/api/board?" + params.toString());
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
		selectedPosition: resolvedView.selectedPosition,
	};
};
