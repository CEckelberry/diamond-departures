import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const API_URL = (typeof process !== 'undefined' && process.env.API_URL) || 'http://api:18000';

export const fallback: RequestHandler = async ({ request, url, fetch, locals }) => {
	const targetUrl = new URL(url.pathname + url.search, API_URL);

	const headers = new Headers(request.headers);
	if (locals.session?.access_token) {
		headers.set('Authorization', `Bearer ${locals.session.access_token}`);
	}

	try {
		const response = await fetch(targetUrl.toString(), {
			method: request.method,
			headers,
			body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
			// @ts-ignore
			duplex: 'half',
		});
		return response;
	} catch (err) {
		console.error('Proxy error:', err);
		throw error(502, 'Bad Gateway: Could not reach backend API');
	}
};
