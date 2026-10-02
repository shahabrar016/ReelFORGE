"""
"4 Determinant Rules" — a ~35 s vertical reel.

Layout is designed for 1080x1920 with platform safe zones:
  top    y > 6.8  : avoided (status bar / account name)
  bottom y < -3.0 : avoided (captions + like/comment buttons)
No LaTeX needed: matrices are built from Text + lines.
"""
import json
from pathlib import Path

from manim import *

# ---- explicit vertical frame (the -r flag alone does NOT change Manim's frame) ----
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_height = 16
config.frame_width = 9
config.background_color = "#0B0F1A"

_T = Path(__file__).with_name("reel_work") / "timings.json"
TIMINGS = json.loads(_T.read_text()) if _T.exists() else {}

ACCENT, POS, NEG, MUTED = YELLOW, "#4ADE80", "#F87171", GRAY_B
CALC_Y = -1.9


def fit(m, max_w=8.2):
    if m.width > max_w:
        m.scale_to_fit_width(max_w)
    return m


def T(s, size=72, color=WHITE, bold=False):
    return fit(Text(s, font_size=size, color=color, weight=BOLD if bold else NORMAL))


class SyncedScene(Scene):
    def section(self, name):
        self.next_section(name)
        self._sec_name, self._sec_t0 = name, self.renderer.time

    def fill(self, fallback=0.8):
        need = TIMINGS.get(self._sec_name)
        spent = self.renderer.time - self._sec_t0
        self.wait(max(0.1, need - spent) if need else fallback)


class DeterminantRules(SyncedScene):
    DX, DY = 1.6, 1.4
    CENTER = np.array([-1.0, 0.9, 0.0])

    # ---------- helpers ----------
    def pos(self, i, j):
        return self.CENTER + np.array([(j - 0.5) * self.DX, (0.5 - i) * self.DY, 0.0])

    def num(self, v, i, j, color=WHITE):
        return Text(str(v), font_size=110, weight=BOLD, color=color).move_to(self.pos(i, j))

    def value(self, v, color=WHITE):
        return Text(f"= {v}", font_size=110, weight=BOLD, color=color).next_to(self.bars[1], RIGHT, buff=0.45)

    def calc_text(self, s, color=WHITE):
        return T(s, 84, color).move_to(UP * CALC_Y)

    def show_rule(self, n, name, old=None):
        lab = VGroup(T(f"RULE {n}", 56, MUTED, bold=True),
                     T(name, 76, ACCENT, bold=True)).arrange(DOWN, buff=0.25).move_to(UP * 3.9)
        anims = [FadeIn(lab, shift=UP * 0.3)]
        if old is not None:
            anims.append(FadeOut(old, shift=UP * 0.3))
        self.play(*anims, run_time=0.5)
        return lab

    def swap_rows(self, run_time=1.0):
        top, bot = self.E
        self.play(*[m.animate(path_arc=-PI / 2).move_to(self.pos(1, j)) for j, m in enumerate(top)],
                  *[m.animate(path_arc=-PI / 2).move_to(self.pos(0, j)) for j, m in enumerate(bot)],
                  run_time=run_time)
        self.E = [bot, top]

    # ---------- the reel ----------
    def construct(self):
        title = T("DETERMINANTS", 120, bold=True).move_to(UP * 6.1)
        sub = T("4 rules in 30 seconds", 64, ACCENT).next_to(title, DOWN, buff=0.35)

        self.E = [[self.num(3, 0, 0), self.num(1, 0, 1)],
                  [self.num(2, 1, 0), self.num(4, 1, 1)]]
        h = self.DY * 2
        xl = self.CENTER[0] - self.DX / 2 - 0.95
        xr = self.CENTER[0] + self.DX / 2 + 0.95
        self.bars = VGroup(
            Line(UP * h / 2, DOWN * h / 2, stroke_width=8).move_to([xl, self.CENTER[1], 0]),
            Line(UP * h / 2, DOWN * h / 2, stroke_width=8).move_to([xr, self.CENTER[1], 0]))
        val = self.value("10")
        calc = self.calc_text("3·4 − 1·2")

        # HOOK — compute the determinant once
        self.section("hook")
        self.play(Write(title), FadeIn(sub, shift=UP * 0.3), run_time=1.0)
        cells = [m for row in self.E for m in row]
        self.play(Create(self.bars),
                  LaggedStart(*[FadeIn(c, scale=1.3) for c in cells], lag_ratio=0.15), run_time=1.0)
        d1 = Line(self.E[0][0].get_center(), self.E[1][1].get_center(), buff=0.45, color=POS, stroke_width=10)
        d2 = Line(self.E[0][1].get_center(), self.E[1][0].get_center(), buff=0.45, color=NEG, stroke_width=10)
        self.play(Create(d1), run_time=0.5)
        self.play(Create(d2), run_time=0.5)
        self.play(FadeIn(calc, shift=UP * 0.2), run_time=0.5)
        self.play(Write(val), run_time=0.6)
        self.fill()

        # RULE 1 — swap rows
        self.section("swap")
        self.play(FadeOut(sub), FadeOut(d1), FadeOut(d2), run_time=0.4)
        lab = self.show_rule(1, "Swap rows → sign flips")
        self.swap_rows()
        self.play(Transform(calc, self.calc_text("2·1 − 4·3")),
                  Transform(val, self.value("−10", NEG)), run_time=0.6)
        self.fill()

        # RULE 2 — scale a row
        self.section("scale")
        self.swap_rows(run_time=0.6)
        self.play(Transform(calc, self.calc_text("3·4 − 1·2")), Transform(val, self.value("10")), run_time=0.4)
        lab = self.show_rule(2, "Row × k → det × k", lab)
        k = Text("×2", font_size=76, weight=BOLD, color=ACCENT)
        k.next_to(self.bars[0], LEFT, buff=0.25).set_y(self.pos(0, 0)[1])
        self.play(FadeIn(k, shift=RIGHT * 0.3), run_time=0.4)
        self.play(Transform(self.E[0][0], self.num(6, 0, 0, ACCENT)),
                  Transform(self.E[0][1], self.num(2, 0, 1, ACCENT)), run_time=0.7)
        self.play(Transform(calc, self.calc_text("6·4 − 2·2")),
                  Transform(val, self.value("20", POS)), run_time=0.6)
        self.fill()

        # RULE 3 — equal rows
        self.section("zero")
        self.play(FadeOut(k),
                  Transform(self.E[0][0], self.num(3, 0, 0)), Transform(self.E[0][1], self.num(1, 0, 1)),
                  Transform(calc, self.calc_text("3·4 − 1·2")), Transform(val, self.value("10")),
                  run_time=0.5)
        lab = self.show_rule(3, "Equal rows → det = 0", lab)
        copies = [self.num(3, 1, 0, NEG), self.num(1, 1, 1, NEG)]
        self.play(FadeOut(self.E[1][0]), FadeOut(self.E[1][1]),
                  TransformFromCopy(self.E[0][0], copies[0]),
                  TransformFromCopy(self.E[0][1], copies[1]), run_time=0.8)
        self.E[1] = copies
        self.play(Transform(calc, self.calc_text("3·1 − 1·3")),
                  Transform(val, self.value("0", NEG)), run_time=0.6)
        self.fill()

        # RULE 4 — transpose
        self.section("transpose")
        self.play(Transform(self.E[1][0], self.num(2, 1, 0)), Transform(self.E[1][1], self.num(4, 1, 1)),
                  Transform(calc, self.calc_text("3·4 − 1·2")), Transform(val, self.value("10")),
                  run_time=0.5)
        lab = self.show_rule(4, "Transpose → no change", lab)
        b, c = self.E[0][1], self.E[1][0]
        self.play(b.animate(path_arc=PI * 0.8).move_to(self.pos(1, 0)),
                  c.animate(path_arc=PI * 0.8).move_to(self.pos(0, 1)), run_time=1.0)
        self.E[0][1], self.E[1][0] = c, b
        self.play(Transform(calc, self.calc_text("3·4 − 2·1")), run_time=0.5)
        self.play(Indicate(val, color=POS, scale_factor=1.2), run_time=0.7)
        self.fill()

        # OUTRO — recap
        self.section("outro")
        grid = VGroup(*[m for row in self.E for m in row], self.bars)
        self.play(FadeOut(grid), FadeOut(val), FadeOut(calc), FadeOut(lab), run_time=0.5)
        recap = VGroup(*[T(s, 68) for s in ("Swap rows → −det",
                                             "Row × k → k · det",
                                             "Equal rows → 0",
                                             "Transpose → same det")])
        recap.arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to(UP * 1.3)
        cta = T("Save this for your exam", 70, ACCENT, bold=True).next_to(recap, DOWN, buff=0.9)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in recap], lag_ratio=0.25), run_time=1.6)
        self.play(FadeIn(cta, scale=1.1), run_time=0.5)
        self.fill(1.5)
