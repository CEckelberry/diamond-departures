// src/lib/stores/user.ts
import { writable } from 'svelte/store';

export type User = {
	id: string;
	email: string;
	name: string | null;
	avatar_url: string | null;
	is_premium: boolean;
};

export const userStore = writable<User | null>(null);
