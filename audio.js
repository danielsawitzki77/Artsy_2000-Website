// ============================================================================
// BUCK FIFTY INNOVATION LABS - RETRO AUDIO ENGINE (Web Audio API)
// Synthesizes authentic 90s FM corporate synth music & sound effects
// ============================================================================

let audioCtx = null;
let bgMusicInterval = null;
let isMusicPlaying = false;

function getAudioContext() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) {
      audioCtx = new AudioContextClass();
    }
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

// Retro FM Synth Note
function playSynthNote(freq, duration, type = 'sine', decay = 0.8) {
  const ctx = getAudioContext();
  if (!ctx) return;

  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  const filter = ctx.createBiquadFilter();

  osc.type = type;
  osc.frequency.setValueAtTime(freq, ctx.currentTime);

  // 90s lowpass warmth
  filter.type = 'lowpass';
  filter.frequency.setValueAtTime(freq * 3, ctx.currentTime);
  filter.frequency.exponentialRampToValueAtTime(Math.max(freq, 200), ctx.currentTime + duration);

  gain.gain.setValueAtTime(0.15, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration * decay);

  osc.connect(filter);
  filter.connect(gain);
  gain.connect(ctx.destination);

  osc.start(ctx.currentTime);
  osc.stop(ctx.currentTime + duration);
}

// 90s UI Click Sound
function playClickSound() {
  const ctx = getAudioContext();
  if (!ctx) return;
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = 'triangle';
  osc.frequency.setValueAtTime(800, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(300, ctx.currentTime + 0.05);
  gain.gain.setValueAtTime(0.12, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start();
  osc.stop(ctx.currentTime + 0.05);
}

// Modem Dialup Sound Effect
function playModemSound() {
  const ctx = getAudioContext();
  if (!ctx) return;

  const now = ctx.currentTime;
  // Dial tone
  const osc1 = ctx.createOscillator();
  const osc2 = ctx.createOscillator();
  const gain = ctx.createGain();

  osc1.type = 'sine';
  osc2.type = 'sine';
  osc1.frequency.setValueAtTime(350, now);
  osc2.frequency.setValueAtTime(440, now);

  gain.gain.setValueAtTime(0.1, now);
  gain.gain.setValueAtTime(0.1, now + 0.4);
  gain.gain.setValueAtTime(0.0, now + 0.5);

  osc1.connect(gain);
  osc2.connect(gain);
  gain.connect(ctx.destination);

  osc1.start(now);
  osc2.start(now);
  osc1.stop(now + 0.5);
  osc2.stop(now + 0.5);

  // Digital screech burst
  const noiseBuffer = ctx.createBuffer(1, ctx.sampleRate * 0.8, ctx.sampleRate);
  const output = noiseBuffer.getChannelData(0);
  for (let i = 0; i < noiseBuffer.length; i++) {
    output[i] = (Math.random() * 2 - 1) * Math.sin(i * 0.05);
  }
  const whiteNoise = ctx.createBufferSource();
  whiteNoise.buffer = noiseBuffer;
  const noiseFilter = ctx.createBiquadFilter();
  noiseFilter.type = 'bandpass';
  noiseFilter.frequency.setValueAtTime(1800, now + 0.5);

  const noiseGain = ctx.createGain();
  noiseGain.gain.setValueAtTime(0.08, now + 0.5);
  noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 1.3);

  whiteNoise.connect(noiseFilter);
  noiseFilter.connect(noiseGain);
  noiseGain.connect(ctx.destination);

  whiteNoise.start(now + 0.5);
  whiteNoise.stop(now + 1.3);
}

// Visceral Guts Sound
function playGutsSound() {
  const ctx = getAudioContext();
  if (!ctx) return;
  const now = ctx.currentTime;
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = 'sawtooth';
  osc.frequency.setValueAtTime(120, now);
  osc.frequency.linearRampToValueAtTime(40, now + 0.4);
  gain.gain.setValueAtTime(0.25, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start(now);
  osc.stop(now + 0.4);
}

// 90s Cheesy Corporate MIDI / FM Synth Loop
// Notes for corporate hope & sinister undertones (C, E, G, B, A, F#, G)
const retroNotes = [
  261.63, 329.63, 392.00, 493.88, 523.25, 493.88, 392.00, 329.63,
  220.00, 277.18, 329.63, 440.00, 392.00, 329.63, 277.18, 220.00
];
let currentNoteIdx = 0;

function toggleRetroMusic() {
  const ctx = getAudioContext();
  if (!ctx) return;

  const btn = document.getElementById('musicToggleBtn');
  if (isMusicPlaying) {
    clearInterval(bgMusicInterval);
    isMusicPlaying = false;
    if (btn) btn.innerText = '▶ PLAY 90s MIDI SOUNDTRACK';
  } else {
    isMusicPlaying = true;
    if (btn) btn.innerText = '⏸ PAUSE MIDI SOUNDTRACK';
    bgMusicInterval = setInterval(() => {
      const freq = retroNotes[currentNoteIdx % retroNotes.length];
      playSynthNote(freq, 0.22, 'sawtooth', 0.85);
      if (currentNoteIdx % 4 === 0) {
        // Bass root
        playSynthNote(freq / 2, 0.4, 'triangle', 0.9);
      }
      currentNoteIdx++;
    }, 180);
  }
}

window.playClickSound = playClickSound;
window.playModemSound = playModemSound;
window.playGutsSound = playGutsSound;
window.toggleRetroMusic = toggleRetroMusic;
