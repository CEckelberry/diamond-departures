import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, parent }) => {
    const { user } = await parent();
    if (!user?.is_premium) return { boards: [] };

    const resp = await fetch('/api/watch-boards');
    if (!resp.ok) return { boards: [] };
    return { boards: await resp.json() };
};
