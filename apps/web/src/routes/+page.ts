import { error } from "@sveltejs/kit";
import { browser } from "$app/environment";

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
	additional_stats: Record<string, number>;
	freshness: {
		timestamp: string;
		age_category: "live" | "recent" | "stale" | "old";
	};
};

type CachedBoard = { entries: BoardEntryPayload[]; view: string; sort: string; season: number };
const boardCache = new Map<string, CachedBoard>();

const VALID_SORTS = new Set([
	"wRC+", "OPS", "OPS+", "HR", "SB", "WAR", "AVG", "RBI", "SLG", "H",
	"DRS", "xwOBA", "ERA", "FIP", "K%", "K/9", "WHIP", "W", "SV", "K",
	"K-BB%", "BB/9", "xFIP", "OAA", "UZR", "Fielding %", "Def", "E",
	"wOBA", "ISO", "BABIP", "BB%", "OBP",
	// Statcast
	"xBA", "barrel_pct", "hard_hit_pct", "exit_velocity",
]);

type ViewResolution = {
	apiView: string;
	selectedPosition: string;
};

function resolveView(params: URLSearchParams): ViewResolution {
	const view = params.get("view") ?? "hitters";
	if (view === "defense") return { apiView: "defense", selectedPosition: "all" };
	if (view === "defense") return { apiView: "defense", selectedPosition: "all" };
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

	const style = params.get("style") ?? "sabermetric";
	if (apiView === "defense") return style === "sabermetric" ? "OAA" : "Fielding %";
	if (apiView.startsWith("pitchers")) {
		return style === "sabermetric" ? "FIP" : "W";
	}
	if (style === "statcast") return "xwOBA";
	if (style === "traditional") return "AVG";
	return "OPS";
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

	const season = url.searchParams.get('season');
	if (season) params.set('season', season);

	const cacheKey = params.toString();
	const boardStyle = url.searchParams.get('style') ?? 'sabermetric';

	if (browser) {
		const cached = boardCache.get(cacheKey);
		if (cached) {
			// Return cached data immediately, revalidate silently in background.
			fetch("/api/board?" + cacheKey)
				.then((r) => r.json())
				.then((p) => { boardCache.set(cacheKey, { entries: p.entries, view: p.view, sort: p.sort, season: (p as any).season ?? new Date().getFullYear() }); })
				.catch(() => {});
			return {
				boardView: cached.view,
				boardSort: cached.sort,
				boardStyle,
				boardSeason: cached.season ?? new Date().getFullYear(),
				entries: cached.entries,
				selectedPosition: resolvedView.selectedPosition,
			};
		}
	}

	const response = await fetch("/api/board?" + cacheKey);
	if (!response.ok) {
		throw error(response.status, "Failed to load board");
	}

	const payload = (await response.json()) as {
		view: string;
		sort: string;
		entries: BoardEntryPayload[];
	};

	if (browser) {
		boardCache.set(cacheKey, { entries: payload.entries, view: payload.view, sort: payload.sort, season: (payload as any).season ?? new Date().getFullYear() });
	}

	return {
		boardView: payload.view,
		boardSort: payload.sort,
		boardStyle,
		boardSeason: (payload as any).season ?? new Date().getFullYear(),
		entries: payload.entries,
		selectedPosition: resolvedView.selectedPosition,
	};
};
