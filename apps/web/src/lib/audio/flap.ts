import { browser } from '$app/environment';
import { getSoundVolume, isSoundEnabled } from '$lib/stores/sound';

export type FlapClip = 'single' | 'many' | 'row-shift';

interface FlapSoundManagerDeps {
	isEnabled: () => boolean;
	getVolume: () => number;
	play: (clip: FlapClip, volume: number) => void;
	debounceMs?: number;
}

export function createFlapSoundManager(deps: FlapSoundManagerDeps) {
	let pending = 0;
	let timer: ReturnType<typeof setTimeout> | undefined;
	const debounceMs = deps.debounceMs ?? 100;

	function flush() {
		timer = undefined;
		if (pending === 0 || !deps.isEnabled()) {
			pending = 0;
			return;
		}
		const clip = pending > 1 ? 'many' : 'single';
		pending = 0;
		deps.play(clip, deps.getVolume());
	}

	return {
		noteFlip() {
			if (!deps.isEnabled()) return;
			pending += 1;
			if (timer) clearTimeout(timer);
			timer = setTimeout(flush, debounceMs);
		},
		playRowShift() {
			if (!deps.isEnabled()) return;
			deps.play('row-shift', deps.getVolume());
		},
		dispose() {
			if (timer) clearTimeout(timer);
			timer = undefined;
			pending = 0;
		}
	};
}

const clipUrls: Record<FlapClip, string> = {
	single: '/audio/flap-single.mp3',
	many: '/audio/flap-many.mp3',
	'row-shift': '/audio/flap-row-shift.mp3'
};

const players: Partial<Record<FlapClip, HTMLAudioElement>> = {};

function playClip(clip: FlapClip, volume: number) {
	if (!browser) return;
	if (!players[clip]) {
		players[clip] = new Audio(clipUrls[clip]);
		players[clip]!.preload = 'auto';
	}
	const player = players[clip]!;
	player.volume = Math.max(0, Math.min(1, volume));
	player.currentTime = 0;
	void player.play().catch(() => {
		/* ignore autoplay block */
	});
}

const manager = createFlapSoundManager({
	isEnabled: () => isSoundEnabled(),
	getVolume: () => getSoundVolume(),
	play: playClip
});

export function noteFlapFlip() {
	manager.noteFlip();
}

export function playRowShift() {
	manager.playRowShift();
}
