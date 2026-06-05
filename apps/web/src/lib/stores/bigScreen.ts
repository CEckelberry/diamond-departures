import { writable } from 'svelte/store';

export const bigScreen = writable(false);

export function toggleBigScreen() {
	bigScreen.update((v) => !v);
}
