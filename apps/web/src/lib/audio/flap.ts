import { browser } from '$app/environment';
import { createFlapSoundManager } from './flap.mjs';
import { getSoundVolume, isSoundEnabled } from '$lib/stores/sound';

type ClipName = 'single' | 'many' | 'row-shift';

const clipUrls: Record<ClipName, string> = {
	single: '/audio/flap-single.mp3',
	many: '/audio/flap-many.mp3',
	'row-shift': '/audio/flap-row-shift.mp3'
};

const players: Partial<Record<ClipName, HTMLAudioElement>> = {};

function playClip(clip: ClipName, volume: number) {
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
