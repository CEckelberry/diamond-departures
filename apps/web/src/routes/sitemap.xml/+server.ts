import type { RequestHandler } from "@sveltejs/kit";

export const prerender = true;

export const GET: RequestHandler = async ({ url }) => {
	const origin = `${url.protocol}//${url.host}`;
	const updated = new Date().toISOString();
	const routes = ["/", "/methodology", "/player/aaron-judge"];
	const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${routes
		.map(
			(path) =>
				`  <url><loc>${origin}${path}</loc><lastmod>${updated}</lastmod><changefreq>daily</changefreq></url>`,
		)
		.join("\n")}\n</urlset>`;

	return new Response(body, {
		headers: {
			"content-type": "application/xml; charset=utf-8",
			"cache-control": "public, max-age=3600",
		},
	});
};
