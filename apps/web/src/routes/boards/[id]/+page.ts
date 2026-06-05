import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params, parent }) => {
    const { user } = await parent();
    if (!user?.is_premium) throw error(403, 'Premium required');

    const resp = await fetch(`/api/watch-boards/${params.id}`);
    if (!resp.ok) throw error(404, 'Board not found');

    return { board: await resp.json() };
};
