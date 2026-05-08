import type { RequestHandler } from "@sveltejs/kit";

export const prerender = false;

export const GET: RequestHandler = async ({ fetch }) => {
	let names = ["Aaron Judge", "Shohei Ohtani", "Bobby Witt Jr."];

	try {
		const response = await fetch("/api/board?view=hitters&sort=wrc_plus");
		if (response.ok) {
			const payload = (await response.json()) as {
				entries?: Array<{ player?: { name?: string } }>;
			};
			const topThree = payload.entries
				?.slice(0, 3)
				.map((entry) => entry.player?.name)
				.filter(Boolean);
			if (topThree && topThree.length === 3) {
				names = topThree as string[];
			}
		}
	} catch {
		// fallback names above
	}

	const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#140b2f"/><stop offset="1" stop-color="#2a1c68"/></linearGradient></defs><rect width="1200" height="630" fill="url(#g)"/><text x="72" y="140" fill="#fac775" font-size="58" font-family="Inter, sans-serif">Diamond Departures</text><text x="72" y="204" fill="#f8f5ff" font-size="34" font-family="Inter, sans-serif">Today’s top 3 hitters</text><text x="72" y="300" fill="#ffffff" font-size="44" font-family="Inter, sans-serif">1. ${names[0]}</text><text x="72" y="372" fill="#ffffff" font-size="44" font-family="Inter, sans-serif">2. ${names[1]}</text><text x="72" y="444" fill="#ffffff" font-size="44" font-family="Inter, sans-serif">3. ${names[2]}</text></svg>`;

	return new Response(svg, {
		headers: {
			"content-type": "image/svg+xml; charset=utf-8",
			"cache-control": "public, max-age=3600",
		},
	});
};
