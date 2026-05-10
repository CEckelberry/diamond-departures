import { browser } from '$app/environment';
import { get, writable } from 'svelte/store';

export const SOUND_ENABLED_KEY = 'diamond-sound-enabled';
export const SOUND_VOLUME_KEY = 'diamond-sound-volume';

function parseEnabled(raw: string | null): boolean {
	return raw === 'true';
}

function parseVolume(raw: string | null): number {
	if (raw == null || raw.trim() === '') return 0.3;
	const parsed = Number(raw);
	if (!Number.isFinite(parsed)) return 0.3;
	return Math.max(0, Math.min(1, parsed));
}

interface SoundPrefs {
	enabled: boolean;
	volume: number;
}

interface Storage {
	getItem(key: string): string | null;
	setItem(key: string, value: string): void;
}

export function createSoundPrefs(storage?: Storage) {
	const source = storage;
	let state: SoundPrefs = {
		enabled: source ? parseEnabled(source.getItem(SOUND_ENABLED_KEY)) : false,
		volume: source ? parseVolume(source.getItem(SOUND_VOLUME_KEY)) : 0.3
	};

	function persist() {
		if (!source) return;
		source.setItem(SOUND_ENABLED_KEY, String(state.enabled));
		source.setItem(SOUND_VOLUME_KEY, String(state.volume));
	}

	persist();

	return {
		get() {
			return { ...state };
		},
		setEnabled(enabled: boolean) {
			state = { ...state, enabled: Boolean(enabled) };
			persist();
			return { ...state };
		},
		setVolume(volume: number) {
			state = {
				...state,
				volume: Math.max(0, Math.min(1, Number(volume) || 0.3))
			};
			persist();
			return { ...state };
		}
	};
}

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
