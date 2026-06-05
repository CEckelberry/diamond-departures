// src/routes/+layout.server.ts
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, locals }) => {
	if (!locals.session) {
		return { user: null };
	}

	try {
		const response = await fetch('/api/auth/me');
		if (response.ok) {
			return { user: await response.json() };
		}
	} catch {
		// API unreachable — degrade gracefully
	}

	return { user: null };
};
