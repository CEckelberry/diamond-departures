type SnapshotPayload = {
	view: string;
	sort: string;
	entries: Array<{
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
	}>;
};

type DeltaPayload = {
	view: string;
	sort: string;
	changes: Array<{
		player_id: number;
		old_rank: number | null;
		new_rank: number | null;
		changed_stats: Array<{ name: string; old: unknown; new: unknown }>;
	}>;
};

type StreamHandlers = {
	onSnapshot: (payload: SnapshotPayload) => void;
	onDelta: (payload: DeltaPayload) => void;
	onError?: (error: Event) => void;
};

type StreamOptions = {
	endpoint?: string;
};

export function openBoardStream(
	view: string,
	sort: string,
	handlers: StreamHandlers,
	options?: StreamOptions,
): () => void {
	if (typeof window === "undefined") {
		return () => {};
	}

	let stopped = false;
	let attempts = 0;
	let retryTimer: number | null = null;
	let source: EventSource | null = null;

	const connect = () => {
		if (stopped) return;
		const params = new URLSearchParams();
		params.set("view", view);
		params.set("sort", sort);
		if (!options?.endpoint) {
			source = new EventSource("/api/board/sse?" + params.toString());
		} else {
			source = new EventSource(options.endpoint + "?" + params.toString());
		}

		source.addEventListener("snapshot", (event) => {
			attempts = 0;
			handlers.onSnapshot(
				JSON.parse((event as MessageEvent).data) as SnapshotPayload,
			);
		});

		source.addEventListener("delta", (event) => {
			handlers.onDelta(
				JSON.parse((event as MessageEvent).data) as DeltaPayload,
			);
		});

		source.onerror = (event) => {
			handlers.onError?.(event);
			source?.close();
			if (stopped) return;
			const delay = Math.min(8000, 500 * 2 ** attempts);
			attempts += 1;
			retryTimer = window.setTimeout(connect, delay);
		};
	};

	connect();

	return () => {
		stopped = true;
		if (retryTimer !== null) window.clearTimeout(retryTimer);
		source?.close();
	};
}
