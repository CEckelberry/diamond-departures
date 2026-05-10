import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Use API_URL if set, fallback to docker service name
const API_URL = (typeof process !== 'undefined' && process.env.API_URL) || 'http://api:18000';

export const fallback: RequestHandler = async ({ request, url, fetch }) => {
	// url.pathname already includes /api
	const targetUrl = new URL(url.pathname + url.search, API_URL);

	try {
		const response = await fetch(targetUrl.toString(), {
			method: request.method,
			headers: request.headers,
			// @ts-ignore
			duplex: 'half'
		});

		// For SSE, we need to return the response as is
		return response;
	} catch (err) {
		console.error('Proxy error:', err);
		throw error(502, 'Bad Gateway: Could not reach backend API');
	}
};
