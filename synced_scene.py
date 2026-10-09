"""Shared audio-first timing for Manim. Existing section()/fill() API retained."""
import json
import os
import re
from pathlib import Path
from manim import Scene, config

class SyncedScene(Scene):
    def setup(self):
        super().setup()
        root = Path(__file__).parent / 'reel_work'
        def read(env, filename):
            path = Path(os.environ.get(env, str(root / filename)))
            return json.loads(path.read_text()) if path.exists() else {}
        self.timings = read('REELFORGE_TIMINGS', 'timings.json')
        self.cues = read('REELFORGE_CUES', 'cues.json')

    def section(self, name):
        self.next_section(name)
        self._sec_name, self._sec_t0 = name, self.renderer.time

    @property
    def elapsed(self):
        return self.renderer.time - self._sec_t0

    def section_duration(self, fallback=8.0):
        return float(self.timings.get(self._sec_name, fallback))

    def cue(self, phrase, fallback_fraction=0.0):
        """First matching phrase, relative to the current section's start.
        Exact for provider timestamps; approximate for estimated word timings.
        """
        clean = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
        wanted = [clean(w) for w in phrase.split()]
        words = self.cues.get(self._sec_name, {}).get('words', [])
        actual = [clean(w['text']) for w in words]
        for i in range(len(actual)-len(wanted)+1):
            if actual[i:i+len(wanted)] == wanted:
                return words[i]['start']
        return self.section_duration()*fallback_fraction

    def until(self, moment):
        frames = int(round((moment-self.elapsed)*config.frame_rate))
        if frames > 0:
            # Manim samples with arange; a tiny epsilon avoids an extra frame
            # from floating-point residue at an exact frame boundary.
            self.wait((frames-1e-6)/config.frame_rate, frozen_frame=False)

    def at(self, phrase, fallback_fraction=0.0):
        self.until(self.cue(phrase, fallback_fraction))

    def fill(self, fallback=0.8):
        if self._sec_name in self.timings:
            self.until(self.section_duration())
        else:
            self.wait(fallback, frozen_frame=False)
