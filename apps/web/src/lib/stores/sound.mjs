export const SOUND_ENABLED_KEY = 'diamond-sound-enabled';
export const SOUND_VOLUME_KEY = 'diamond-sound-volume';

/**
 * @param {string | null} raw
 */
function parseEnabled(raw) {
	return raw === 'true';
}

/**
 * @param {string | null} raw
 */
function parseVolume(raw) {
	if (raw == null || raw.trim() === '') return 0.3;
	const parsed = Number(raw);
	if (!Number.isFinite(parsed)) return 0.3;
	return Math.max(0, Math.min(1, parsed));
}

/**
 * @param {{getItem:(key:string)=>string|null,setItem:(key:string,value:string)=>void}|undefined} storage
 */
export function createSoundPrefs(storage) {
	const source = storage;
	let state = {
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
		/** @param {boolean} enabled */
		setEnabled(enabled) {
			state = { ...state, enabled: Boolean(enabled) };
			persist();
			return { ...state };
		},
		/** @param {number} volume */
		setVolume(volume) {
			state = {
				...state,
				volume: Math.max(0, Math.min(1, Number(volume) || 0.3))
			};
			persist();
			return { ...state };
		}
	};
}
