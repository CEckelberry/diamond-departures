import { browser } from '$app/environment';
import { get, writable } from 'svelte/store';
import { createSoundPrefs } from './sound.mjs';

const prefs = createSoundPrefs(browser ? window.localStorage : undefined);
const initial = prefs.get();

export const soundEnabled = writable<boolean>(initial.enabled);
export const soundVolume = writable<number>(initial.volume);

if (browser) {
	soundEnabled.subscribe((enabled) => {
		prefs.setEnabled(enabled);
	});
	soundVolume.subscribe((volume) => {
		prefs.setVolume(volume);
	});
}

export function setSoundEnabled(enabled: boolean) {
	soundEnabled.set(enabled);
}

export function setSoundVolume(volume: number) {
	soundVolume.set(Math.max(0, Math.min(1, volume)));
}

export function isSoundEnabled(): boolean {
	return get(soundEnabled);
}

export function getSoundVolume(): number {
	return get(soundVolume);
}
