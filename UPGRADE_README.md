# ReelForge animation and timing update

## GitHub browser steps

1. Extract this ZIP. Upload the files in its root to your repository root, replacing matching files. Keep your existing `project.yaml`, `determinants.yaml`, secrets, and existing workflow.
2. Run your existing **Build reel** workflow with project **rutherford.yaml**. No terminal, setup script, voice ID editing, or separate voice-generation step is needed. The old workflow may still run `voice` before `build`; that remains supported and cached.
3. Download `out/rutherford.mp4` from the completed artifact.

`rutherford.yaml` uses the first available `tts:` block from `determinants.yaml`, then `project.yaml`. That file must have working provider/model/voice settings; the update does not validate account access or invent a voice ID. To use different settings, remove `tts_from` and supply a normal `tts:` block.

An optional workflow is included at `.github/workflows/build-rutherford.yml`. To add it using the browser, choose **Add file → Create new file**, use that exact path, and paste the included contents. It adds **Build Rutherford (updated)** and uploads extra diagnostics. Your existing workflow is sufficient to render; adding this one is optional.

## What changed

- `build` writes current `timings.json` and `cues.json` BEFORE rendering. A stale file or skipped `voice` step no longer controls section duration.
- The reusable `synced_scene.py` loads the actual configured work directory through environment variables. It exposes `section`, `section_duration`, `cue`, `at`, `until`, and `fill` for other topics.
- `at("spoken phrase", fallback_fraction)` synchronizes a reveal to the section-local word timestamp. ElevenLabs timestamps are used when available. Gemini and personal audio without timestamps use approximate word timing, not forced alignment.
- Waits explicitly allow updaters to run. Rutherford has moving alpha-particle streams, fading trails, progressive path reveals, detector pulses, close-up scattering, a scale comparison, and a classical-collapse/quantum-envelope comparison. Electrons in the nuclear schematic are not drawn on Bohr shells.
- The Rutherford profile reduces scheduled section padding from 0.60 s to 0.16 s, plus small render-frame rounding differences. Internal speech pauses remain untouched. Head/tail padding protects speech, provider word timestamps guard quiet word boundaries, and 5 ms edge fades reduce join clicks.
- Cache metadata now resolves audio inside the current runner's cache directory rather than trusting a stale absolute path.
- Missing/duplicate named sections fail clearly rather than silently shifting narration. Empty initial Manim sections are supported.
- `quality_report.json` reports inter-block scheduled gaps and extra frame holds. It does not claim to detect audible stuttering or all static visuals automatically.
- Manim is pinned to 0.21.0 and PyAV to 16.0.1 for reproducible behavior. Manim partial-movie caching is disabled so a stale or incomplete intermediate cannot be reused; TTS caching remains enabled. Full render output is recorded in `reel_work/manim.log`. Production output remains 1080×1920 at 30 fps.

## If the voice itself still stutters

The engine can remove added scheduling gaps; it cannot repair a glitch already spoken into a cached TTS clip. Add `tts_cache_tag: fresh-voice-1` at the top level of `rutherford.yaml` and rerun the workflow to request new audio. Leave that tag unchanged to reuse the new clips on later builds; change it only when another regeneration is wanted. The default keeps existing usable audio cached.

## Reusing the timing helper for new scenes

```python
from synced_scene import SyncedScene

class MyScene(SyncedScene):
    def construct(self):
        self.section("experiment")
        # Add a diagram and appropriate particle updaters here.
        self.at("gold foil", fallback_fraction=0.35)
        # Animate the foil when the narration reaches that phrase.
        self.fill()  # only the remaining time; does not stop updaters
```

The animation content still needs to be authored for each lesson. Changing the engine cannot automatically make any static Manim scene highly animated. A `fill()` call only keeps motion alive when the scene has active updaters.

## Physics and visual scope

Scattering curves numerically integrate repulsive inverse-square forces for an alpha particle and a fixed heavy nucleus. Sizes, stream density, and playback speed are illustrative; this is not a calibrated simulation of the gold foil experiment. Atom boundary and electrons are schematic, not the electron configuration of gold. The quantum envelope is symbolic, not a calculated orbital density. Modern radius values are approximate. No neutrons or quantized shells are attributed to Rutherford's 1911 model.

References: https://www.aps.org/apsnews/2006/05/rutherford-discovery-atomic-nucleus ; https://history.aip.org/exhibits/rutherford/sections/alpha-particles-atom.html ; https://docs.manim.community/en/stable/reference/manim.animation.animation.Wait.html

## Checks

Run `python -m unittest discover -s tests -v` for timing, cache portability, configuration inheritance, section validation, and audio-trim checks. See `VALIDATION.md` for what was actually exercised for this release and the remaining limits.
