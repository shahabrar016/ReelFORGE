# Validation and limitations

- Ten regression tests passed, including a real FFmpeg composition test that decodes the resulting audio and verifies both spoken-block substitutes remain audible at their expected frequencies.
- Tests cover refresh-before-render ordering, frame-aligned timing metadata, section validation, portable voice caches, intentional TTS regeneration, configuration inheritance, and preservation of internal audio pauses.
- The updated scene has been rendered locally at 1080 × 1920, 30 fps with Manim Community 0.21.0. The final physics-time particle interpolation was subsequently checked directly against the RK4 samples for all three paths; the demonstration render uses the preceding schematic playback timing. The supplied demonstration reuses narration extracted from your uploaded MP4. No external TTS API or GitHub runner was used during local validation.
- The nine section names match the YAML. The source contains no LaTeX-dependent objects or external visual assets.
- Word cues for the demonstration are estimated because the uploaded MP4 contains no provider timestamps. Your normal ElevenLabs builds use returned provider timestamps when available. Gemini timings remain estimates.
- Speech glitches already embedded in a source recording or cached TTS clip are not removed by the timing engine. Use the documented `tts_cache_tag` option to request new TTS audio when needed.
- Diagrams remain schematic: nuclear size is exaggerated; stream density is not a measurement of scattering probabilities; the orbital envelope is symbolic. Coulomb particle motion uses equal-time integration samples and the same numerical incident velocity for all scattering paths.
- An initial run using PyAV 19 and partial-movie caching produced an incomplete intermediate clip. This release pins PyAV 16.0.1 and disables Manim partial-movie caching. TTS caching remains enabled. This is a reproducibility precaution, not a proven diagnosis of PyAV 19.

See `validation_summary.json` for the final render dimensions, durations, test result, and measured scheduled voice gaps. Natural silence inside the voice clips is additional to those scheduled gaps.
