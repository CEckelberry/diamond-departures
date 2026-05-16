const SOUND_ENABLED_KEY = 'diamond-sound-enabled';
const SOUND_VOLUME_KEY = 'diamond-sound-volume';

function parseEnabled(raw) {
	return raw === 'true';
}

function parseVolume(raw) {
	if (raw == null || raw.trim() === '') return 0.3;
	const parsed = Number(raw);
	if (!Number.isFinite(parsed)) return 0.3;
	return Math.max(0, Math.min(1, parsed));
}

export function createSoundPrefs(storage) {
	let state = {
		enabled: storage ? parseEnabled(storage.getItem(SOUND_ENABLED_KEY)) : false,
		volume: storage ? parseVolume(storage.getItem(SOUND_VOLUME_KEY)) : 0.3
	};

	function persist() {
		if (!storage) return;
		storage.setItem(SOUND_ENABLED_KEY, String(state.enabled));
		storage.setItem(SOUND_VOLUME_KEY, String(state.volume));
	}

	persist();

	return {
		get() {
			return { ...state };
		},
		setEnabled(enabled) {
			state = { ...state, enabled: Boolean(enabled) };
			persist();
			return { ...state };
		},
		setVolume(volume) {
			state = { ...state, volume: Math.max(0, Math.min(1, Number(volume) || 0.3)) };
			persist();
			return { ...state };
		}
	};
}
