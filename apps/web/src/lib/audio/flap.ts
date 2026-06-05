import { browser } from '$app/environment';
import { getSoundVolume, isSoundEnabled } from '$lib/stores/sound';

// ── Keep references so Audio elements aren't GC'd mid-play ─────────────────
const _playing = new Set<HTMLAudioElement>();

function playUrl(url: string, volume: number) {
	const audio = new Audio(url);
	audio.volume = Math.max(0, Math.min(1, volume));
	_playing.add(audio);
	audio.addEventListener('ended', () => { _playing.delete(audio); }, { once: true });
	void audio.play().catch(() => { _playing.delete(audio); });
}

// ── WAV encoder ─────────────────────────────────────────────────────────────
function encodeWav(buf: AudioBuffer): string {
	const sr = buf.sampleRate;
	const len = buf.length;
	const ab = new ArrayBuffer(44 + len * 2);
	const v = new DataView(ab);
	const w = (o: number, s: string) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
	w(0, 'RIFF'); v.setUint32(4, 36 + len * 2, true);
	w(8, 'WAVE'); w(12, 'fmt '); v.setUint32(16, 16, true);
	v.setUint16(20, 1, true); v.setUint16(22, 1, true);
	v.setUint32(24, sr, true); v.setUint32(28, sr * 2, true);
	v.setUint16(32, 2, true); v.setUint16(34, 16, true);
	w(36, 'data'); v.setUint32(40, len * 2, true);
	const d = buf.getChannelData(0);
	for (let i = 0; i < len; i++) {
		v.setInt16(44 + i * 2, Math.max(-1, Math.min(1, d[i])) * 0x7FFF, true);
	}
	return URL.createObjectURL(new Blob([ab], { type: 'audio/wav' }));
}

// ── Offline rendering helper ────────────────────────────────────────────────
async function render(duration: number, fn: (ctx: OfflineAudioContext) => void): Promise<string> {
	const ctx = new OfflineAudioContext(1, Math.ceil(44100 * duration), 44100);
	fn(ctx);
	return encodeWav(await ctx.startRendering());
}

// ── Sound definitions ───────────────────────────────────────────────────────
function buildFlapClick(ctx: OfflineAudioContext, t: number, vol: number) {
	const len = Math.ceil(ctx.sampleRate * 0.1);
	const noiseBuf = ctx.createBuffer(1, len, ctx.sampleRate);
	const d = noiseBuf.getChannelData(0);
	for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;

	const src = ctx.createBufferSource();
	src.buffer = noiseBuf;

	const bp = ctx.createBiquadFilter();
	bp.type = 'bandpass';
	bp.frequency.value = 3800 + Math.random() * 800;
	bp.Q.value = 1.2;

	const gain = ctx.createGain();
	gain.gain.setValueAtTime(0, t);
	gain.gain.linearRampToValueAtTime(vol * 0.35, t + 0.002);
	gain.gain.exponentialRampToValueAtTime(0.001, t + 0.055);

	src.connect(bp); bp.connect(gain); gain.connect(ctx.destination);
	src.start(t); src.stop(t + 0.06);
}

function buildChimeNote(ctx: OfflineAudioContext, freq: number, vol: number, t: number) {
	const osc = ctx.createOscillator();
	osc.type = 'sine';
	osc.frequency.value = freq;

	const osc2 = ctx.createOscillator();
	osc2.type = 'sine';
	osc2.frequency.value = freq * 2.756;

	const g1 = ctx.createGain();
	g1.gain.setValueAtTime(0, t);
	g1.gain.linearRampToValueAtTime(vol * 0.38, t + 0.008);
	g1.gain.exponentialRampToValueAtTime(0.001, t + 0.55);

	const g2 = ctx.createGain();
	g2.gain.setValueAtTime(0, t);
	g2.gain.linearRampToValueAtTime(vol * 0.09, t + 0.008);
	g2.gain.exponentialRampToValueAtTime(0.001, t + 0.28);

	osc.connect(g1);  g1.connect(ctx.destination);
	osc2.connect(g2); g2.connect(ctx.destination);
	osc.start(t);  osc.stop(t + 0.6);
	osc2.start(t); osc2.stop(t + 0.32);
}

// ── Pre-rendered sound cache ────────────────────────────────────────────────
type SoundCache = {
	single: string | null;
	many:   string | null;
	// chime[dir][noteCount] — noteCount 2/3/4 → index 0/1/2
	chime: { up: [string|null, string|null, string|null]; down: [string|null, string|null, string|null] };
};

const cache: SoundCache = {
	single: null,
	many: null,
	chime: { up: [null, null, null], down: [null, null, null] },
};

const UP_NOTES   = [523.25, 659.25, 783.99, 1046.50];
const DOWN_NOTES = [783.99, 659.25, 523.25,  392.00];

async function prerender() {
	cache.single = await render(0.1, (ctx) => buildFlapClick(ctx, 0, 1));
	cache.many   = await render(0.15, (ctx) => {
		buildFlapClick(ctx, 0,     1);
		buildFlapClick(ctx, 0.018, 0.75);
		buildFlapClick(ctx, 0.038, 0.55);
	});

	for (const dir of ['up', 'down'] as const) {
		const notes = dir === 'up' ? UP_NOTES : DOWN_NOTES;
		for (let ni = 0; ni < 3; ni++) {
			const count   = ni + 2;           // 2, 3, 4 notes
			const loudness = 0.65 + ni * 0.08; // scales 0.65 → 0.81
			const spacing  = 0.11;
			const duration = spacing * (count - 1) + 0.65;
			cache.chime[dir][ni] = await render(duration, (ctx) => {
				for (let i = 0; i < count; i++) {
					buildChimeNote(ctx, notes[i], loudness, i * spacing);
				}
			});
		}
	}
}

// ── AudioContext unlock + pre-render trigger ────────────────────────────────
let _prerendered = false;

function unlock() {
	if (_prerendered) return;
	_prerendered = true;
	prerender().catch(() => { _prerendered = false; });
}

if (browser) {
	for (const evt of ['pointerdown', 'keydown', 'touchstart'] as const) {
		document.addEventListener(evt, unlock, { once: true, capture: true, passive: true });
	}
}

// ── Public API ──────────────────────────────────────────────────────────────
export type FlapClip = 'single' | 'many' | 'row-shift';

export function noteFlapFlip() {
	if (!isSoundEnabled()) return;
	// Debounce: coalesce rapid flips into single or many
	_pending++;
	if (_flapTimer) clearTimeout(_flapTimer);
	_flapTimer = setTimeout(_flushFlap, 100);
}

let _pending = 0;
let _flapTimer: ReturnType<typeof setTimeout> | undefined;

function _flushFlap() {
	_flapTimer = undefined;
	if (_pending === 0 || !isSoundEnabled()) { _pending = 0; return; }
	const url = _pending > 1 ? cache.many : cache.single;
	_pending = 0;
	if (url) playUrl(url, getSoundVolume());
}

export function playRowShift() { /* folded into playRankChange */ }

export function playRankChange(direction: 'up' | 'down', magnitude: number) {
	if (!isSoundEnabled()) return;
	const ni    = magnitude <= 2 ? 0 : magnitude <= 5 ? 1 : 2;
	const vol   = getSoundVolume() * Math.min(1, 0.7 + magnitude * 0.04);
	const url   = cache.chime[direction][ni];
	if (url) playUrl(url, vol);
}

