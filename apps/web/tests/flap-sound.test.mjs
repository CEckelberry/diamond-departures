import test from 'node:test';
import assert from 'node:assert/strict';

import { createSoundPrefs } from '../src/lib/stores/sound.node.mjs';
import { createFlapSoundManager } from '../src/lib/audio/flap.node.mjs';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function createMemoryStorage() {
	const bucket = new Map();
	return {
		getItem(key) {
			return bucket.has(key) ? bucket.get(key) : null;
		},
		setItem(key, value) {
			bucket.set(key, String(value));
		}
	};
}

test('sound prefs default: off and volume 0.3', () => {
	const prefs = createSoundPrefs(createMemoryStorage());
	assert.deepEqual(prefs.get(), { enabled: false, volume: 0.3 });
});

test('sound prefs persist updates to storage', () => {
	const storage = createMemoryStorage();
	const prefs = createSoundPrefs(storage);
	prefs.setEnabled(true);
	prefs.setVolume(0.6);

	const restored = createSoundPrefs(storage);
	assert.deepEqual(restored.get(), { enabled: true, volume: 0.6 });
});

test('sound manager emits single clip for one flip', async () => {
	const played = [];
	const manager = createFlapSoundManager({
		isEnabled: () => true,
		getVolume: () => 0.3,
		play: (clip, volume) => played.push({ clip, volume })
	});

	manager.noteFlip();
	await sleep(130);
	assert.deepEqual(played, [{ clip: 'single', volume: 0.3 }]);
});

test('sound manager debounces burst into many clip', async () => {
	const played = [];
	const manager = createFlapSoundManager({
		isEnabled: () => true,
		getVolume: () => 0.3,
		play: (clip, volume) => played.push({ clip, volume })
	});

	manager.noteFlip();
	manager.noteFlip();
	manager.noteFlip();
	await sleep(130);
	assert.deepEqual(played, [{ clip: 'many', volume: 0.3 }]);
});
