export function createFlapSoundManager(deps) {
	let pending = 0;
	let timer;
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
