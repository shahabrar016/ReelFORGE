# ReelForge

Manim animation + Gemini / ElevenLabs voiceover → a ready-to-post 1080×1920 reel, with the voice automatically placed on the right animation beats.

## Setup

```bash
pip install -r requirements.txt          # plus ffmpeg on your PATH (with libass for captions)
export ELEVENLABS_API_KEY=...            # if using ElevenLabs
export GEMINI_API_KEY=...                # if using Gemini TTS
```

## Workflow A — audio-first (perfect sync, recommended)

```bash
python reelforge.py voice project.yaml   # generates voice, writes reel_work/timings.json
python reelforge.py build project.yaml   # renders Manim (sections now match the voice) + composes reel
```

In your scene, subclass `SyncedScene` from `example_scene.py`, start each beat with `self.section("name")` and end it with `self.fill()`. The scene waits exactly as long as the narration needs.

## Workflow B — animation-first (fully automatic)

Point `video.path` at any rendered video (Manim or not, any aspect ratio) and list narration blocks with no `section`. ReelForge finds the animation beats itself (where each `self.wait()` ends), then an optimiser decides which block goes on which beat, minimising frozen frames and dead air while keeping each block on its cue. Where the voice needs more time than the visuals, the last frame of that beat is held.

You can also give one long recording with `audio_file:`; it is split into blocks at natural pauses.

## Commands

| Command | What it does |
|---|---|
| `voice` | TTS only, writes `timings.json` |
| `analyze` | Prints the placement plan without encoding |
| `build` | Full pipeline → `output` mp4 |

TTS results are cached by text and voice, so re-running never spends credits twice.

## Output

H.264 High / yuv420p / 30 fps / AAC 48 kHz, `+faststart`, loudness normalised to −14 LUFS, optional music with automatic ducking, and word-by-word highlighted captions placed above the platform UI. `reel_work/timeline.json` records exactly where every block landed.

## Tuning (`reel:` in project.yaml)

`lead`, `gap`, `tail` control pacing. `sync_weight` (higher = stricter one-block-per-beat), `overflow_weight` (higher = avoid frozen frames) and `silence_weight` (higher = avoid quiet animation) steer the auto-placer. For freeze detection on noisy or non-Manim footage, raise `analysis.freeze_noise` (e.g. `-50dB`).
