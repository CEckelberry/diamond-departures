import { browser } from '$app/environment';
import { writable } from 'svelte/store';

export type EinkMode = 'off' | 'aesthetic' | 'faithful';

export const STORAGE_KEY = 'eink-mode';

function detectEink(): boolean {
	if (!browser) return false;
	const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	const lowColorDepth = window.screen.colorDepth <= 8;
	return reducedMotion && lowColorDepth;
}

function applyClass(mode: EinkMode) {
	if (!browser) return;
	document.body.classList.remove('eink-aesthetic', 'eink-faithful');
	if (mode === 'aesthetic') document.body.classList.add('eink-aesthetic');
	if (mode === 'faithful') document.body.classList.add('eink-faithful');
}

function createEinkStore() {
	const { subscribe, set, update } = writable<EinkMode>('off');

	function init() {
		if (!browser) return;
		const saved = localStorage.getItem(STORAGE_KEY) as EinkMode | null;
		if (saved === 'aesthetic' || saved === 'faithful') {
			set(saved);
			applyClass(saved);
		} else if (detectEink()) {
			// auto-detected: don't persist so user's explicit choice always wins
			set('faithful');
			applyClass('faithful');
		}
	}

	function cycle() {
		update(current => {
			const next: EinkMode =
				current === 'off' ? 'aesthetic' :
				current === 'aesthetic' ? 'faithful' : 'off';
			if (browser) {
				localStorage.setItem(STORAGE_KEY, next);
				applyClass(next);
			}
			return next;
		});
	}

	return { subscribe, init, cycle };
}

export const einkStore = createEinkStore();
