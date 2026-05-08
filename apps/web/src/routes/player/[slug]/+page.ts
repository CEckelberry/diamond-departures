import { error } from "@sveltejs/kit";

type BoardEntryPayload = {
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

function slugify(value: string): string {
	return value
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, "-")
		.replace(/^-+|-+$/g, "");
}

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
	params,
}: {
	fetch: typeof globalThis.fetch;
	url: URL;
	params: { slug: string };
}) => {
	const q = new URLSearchParams();
	q.set("view", resolveView(url.searchParams));
	q.set("sort", resolveSort(url.searchParams, q.get("view") ?? "hitters"));

	const response = await fetch("/api/board?" + q.toString());
	if (!response.ok) throw error(response.status, "Failed to load board");

	const payload = (await response.json()) as {
		view: string;
		sort: string;
		entries: BoardEntryPayload[];
	};

	const selected = payload.entries.find(
		(entry) => slugify(entry.player.name) === params.slug,
	);

	return {
		boardView: payload.view,
		boardSort: payload.sort,
		entries: payload.entries,
		selectedPlayerId: selected?.player.id ?? null,
		selectedSlug: params.slug,
	};
};
