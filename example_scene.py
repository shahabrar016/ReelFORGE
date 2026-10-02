"""
Example vertical (9:16) Manim scene that syncs itself to the voiceover.

Each self.next_section("name") is a beat. After `python reelforge.py voice project.yaml`,
reel_work/timings.json holds how long each section's narration needs, and `fill()` waits
exactly the remaining time, so no frames ever need to be frozen.
Without timings.json it still renders; ReelForge then holds frames where needed.
"""
import json
from pathlib import Path

from manim import *

config.frame_height = 16
config.frame_width = 9
config.background_color = "#0E1020"

_T = Path(__file__).with_name("reel_work") / "timings.json"
TIMINGS = json.loads(_T.read_text()) if _T.exists() else {}


class SyncedScene(Scene):
    def section(self, name):
        self.next_section(name)
        self._sec_name, self._sec_t0 = name, self.renderer.time

    def fill(self, fallback=0.8):
        need = TIMINGS.get(self._sec_name)
        spent = self.renderer.time - self._sec_t0
        self.wait(max(0.1, need - spent) if need else fallback)


class PythagorasReel(SyncedScene):
    def construct(self):
        A, B, C = np.array([0, 0, 0]), np.array([3, 0, 0]), np.array([0, 4, 0])
        n = np.array([4, 3, 0])  # outward normal of the hypotenuse, length 5
        tri = Polygon(A, B, C, color=WHITE, stroke_width=6)
        sq_a = Polygon(A, B, B + DOWN * 3, A + DOWN * 3, color=BLUE, fill_opacity=0.55)
        sq_b = Polygon(A, C, C + LEFT * 4, A + LEFT * 4, color=GREEN, fill_opacity=0.55)
        sq_c = Polygon(B, C, C + n, B + n, color=ORANGE, fill_opacity=0.55)
        fig = VGroup(sq_a, sq_b, sq_c, tri).scale(0.72).move_to(DOWN * 0.6)
        figure_only = [sq_a, sq_b, sq_c]

        # 1 — hook
        self.section("hook")
        title = Text("a² + b² = c²", font_size=150, weight=BOLD).move_to(UP * 1)
        q = Text("but WHY?", font_size=110, color=YELLOW).next_to(title, DOWN, buff=0.8)
        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(q, shift=UP * 0.4), run_time=0.6)
        self.fill()

        # 2 — triangle
        self.section("triangle")
        self.play(FadeOut(q), title.animate.scale(0.6).to_edge(UP, buff=1.2), run_time=0.8)
        self.play(Create(tri), run_time=1.2)
        la = Text("a", font_size=96, color=BLUE).next_to(tri, DOWN, buff=0.25)
        lb = Text("b", font_size=96, color=GREEN).next_to(tri, LEFT, buff=0.25)
        lc = Text("c", font_size=96, color=ORANGE).move_to(tri.get_center() + RIGHT * 0.9 + UP * 0.6)
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in (la, lb, lc)], lag_ratio=0.3))
        self.fill()

        # 3 — squares on every side
        self.section("squares")
        self.play(FadeOut(la, lb, lc), run_time=0.3)
        self.play(LaggedStart(*[DrawBorderThenFill(s) for s in figure_only], lag_ratio=0.4), run_time=2)
        self.bring_to_front(tri)
        areas = VGroup(*[Text(t, font_size=110, weight=BOLD).move_to(s) for t, s in
                         zip(("9", "16", "25"), figure_only)])
        self.play(LaggedStart(*[Write(a) for a in areas], lag_ratio=0.35))
        self.fill()

        # 4 — the punchline
        self.section("proof")
        eq = Text("9 + 16 = 25", font_size=130, weight=BOLD).to_edge(DOWN, buff=1.6)
        self.play(TransformFromCopy(areas[0], eq[0]), TransformFromCopy(areas[1], eq[2:4]),
                  FadeIn(eq[1]), run_time=1.2)
        self.play(FadeIn(eq[4]), TransformFromCopy(areas[2], eq[5:]), run_time=1)
        self.play(Circumscribe(eq, color=YELLOW, buff=0.25), run_time=1.2)
        self.fill()

        # 5 — outro
        self.section("outro")
        self.play(FadeOut(fig, areas, eq, title), run_time=0.6)
        cta = VGroup(Text("Math in 60s", font_size=120, weight=BOLD),
                     Text("follow for more", font_size=80, color=YELLOW)).arrange(DOWN, buff=0.6)
        self.play(GrowFromCenter(cta[0]), FadeIn(cta[1], shift=UP * 0.3))
        self.fill(1.5)
