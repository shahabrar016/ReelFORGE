"""
Principle of Atom Conservation (POAC) - ReelForge scene.

Vertical frame 9 x 16, no LaTeX, no images. Uses the existing SyncedScene
from example_scene.py (section(name) / fill()).
Section names MUST match the `section:` keys in poac.yaml.
"""
import numpy as np
from manim import *
from example_scene import SyncedScene

# --- vertical frame (must come after imports) ---
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_height = 16
config.frame_width = 9

BG = "#0D1117"
TEAL = "#4ECDC4"
AMBER = "#FFC857"
CORAL = "#FF6B6B"
BLUE = "#6CB4FF"
DIM = "#8B949E"


# ---------------------------------------------------------------- helpers
def fit(m, w=8.2):
    """Shrink anything wider than the safe width."""
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


def T(s, size=80, color=WHITE, bold=False):
    return fit(Text(s, font_size=size, color=color,
                    weight=BOLD if bold else NORMAL))


def elem_row(sym, color, n_before, n_after):
    """[symbol] [dots before] = [dots after], columns aligned across rows."""
    letter = Text(sym, font_size=90, color=color, weight=BOLD)

    def cell(n):
        rect = Rectangle(width=2.4, height=0.6, stroke_width=0, fill_opacity=0)
        dots = VGroup(*[Dot(radius=0.2, color=color) for _ in range(n)])
        dots.arrange(RIGHT, buff=0.25).move_to(rect.get_center())
        return VGroup(rect, dots)

    return VGroup(letter, cell(n_before), T("=", 80, WHITE, True),
                  cell(n_after)).arrange(RIGHT, buff=0.5)


# ------------------------------------------------------------------ scene
class POAC(SyncedScene):
    def construct(self):
        self.camera.background_color = BG
        self.s_idea()
        self.s_mole_atoms()
        self.s_mole_rule()
        self.s_method()
        self.s_ex_setup()
        self.s_ex_mole()
        self.s_ex_poac()
        self.s_ex_answer()
        self.s_cta()

    def _wipe(self):
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.4)

    # 1 ----------------------------------------------------------- idea
    def s_idea(self):
        self.section("idea")
        head = T("POAC", 96, AMBER, True).move_to([0, 6.1, 0])
        eq = VGroup(
            T("CH₄", 72, WHITE, True), T("+", 72), T("2O₂", 72, WHITE, True),
            T("→", 72), T("CO₂", 72, WHITE, True), T("+", 72),
            T("2H₂O", 72, WHITE, True),
        ).arrange(RIGHT, buff=0.25)
        fit(eq).move_to([0, 4.8, 0])

        rows = VGroup(
            elem_row("C", AMBER, 1, 1),
            elem_row("H", BLUE, 4, 4),
            elem_row("O", CORAL, 4, 4),
        ).arrange(DOWN, buff=0.7).move_to([0, 1.4, 0])
        fit(rows)

        before = T("before", 44, DIM).move_to([rows[0][1].get_center()[0], 4.1, 0])
        after = T("after", 44, DIM).move_to([rows[0][3].get_center()[0], 4.1, 0])

        self.play(Write(head), run_time=0.7)
        self.play(Write(eq), run_time=1.2)
        self.play(FadeIn(before), FadeIn(after), run_time=0.5)
        for r in rows:
            self.play(Write(r[0]), run_time=0.4)
            self.play(LaggedStart(*[GrowFromCenter(d) for d in r[1][1]],
                                  lag_ratio=0.15), run_time=0.7)
            self.play(Write(r[2]), run_time=0.3)
            self.play(LaggedStart(*[GrowFromCenter(d) for d in r[3][1]],
                                  lag_ratio=0.15), run_time=0.7)
        self.fill()

    # 2 ---------------------------------------------------- mole atoms
    def s_mole_atoms(self):
        self.section("mole_atoms")
        self._wipe()
        head = T("1 mol Al₂(SO₄)₃", 84, WHITE, True).move_to([0, 5.9, 0])
        self._ma_rows = VGroup(
            T("2 mol Al", 80, BLUE, True),
            T("3 mol S", 80, AMBER, True),
            T("12 mol O", 80, CORAL, True),
        ).arrange(DOWN, buff=0.45).move_to([0, 3.0, 0])

        self.play(Write(head), run_time=0.9)
        for r in self._ma_rows:
            self.play(FadeIn(r, shift=RIGHT * 0.4), run_time=0.7)
        self.fill()

    # 3 ------------------------------------------------------ mole rule
    def s_mole_rule(self):
        self.section("mole_rule")
        lab = T("moles of atoms", 52, DIM).move_to([0, -0.2, 0])
        rule = T("= n × atoms per formula", 72, AMBER, True).move_to([0, -1.4, 0])
        self.play(FadeIn(lab, shift=UP * 0.2), run_time=0.5)
        self.play(Write(rule), run_time=1.2)
        self.play(Indicate(rule, color=WHITE), run_time=0.8)
        self.fill()

    # 4 --------------------------------------------------------- method
    def s_method(self):
        self.section("method")
        self._wipe()
        head = T("moles of atoms of X", 64, AMBER, True).move_to([0, 5.2, 0])

        def box(word, color, x):
            rect = RoundedRectangle(width=3.4, height=2.0, corner_radius=0.3,
                                    color=color, stroke_width=8)
            txt = VGroup(T(word, 64, color, True),
                         T("all species", 40, DIM)).arrange(DOWN, buff=0.15)
            g = VGroup(rect, txt)
            txt.move_to(rect.get_center())
            return g.move_to([x, 2.8, 0])

        b_before = box("before", BLUE, -2.4)
        b_after = box("after", TEAL, 2.4)
        eq = T("=", 120, WHITE, True).move_to([0, 2.8, 0])

        self.play(Write(head), run_time=0.8)
        self.play(Create(b_before), run_time=0.8)
        self.play(Create(b_after), run_time=0.8)
        self.play(Write(eq), run_time=0.5)
        self.play(Indicate(eq, color=AMBER), run_time=0.8)
        self.fill()

    # 5 ------------------------------------------------------ ex: setup
    def s_ex_setup(self):
        self.section("ex_setup")
        self._wipe()
        self._head = T("122.5 g KClO₃", 96, WHITE, True).move_to([0, 5.6, 0])
        self._rxn = VGroup(
            T("KClO₃", 80, BLUE, True), T("→", 80),
            T("KCl", 80, TEAL, True), T("+", 80), T("O₂", 80, CORAL, True),
        ).arrange(RIGHT, buff=0.3)
        fit(self._rxn).move_to([0, 4.0, 0])
        self._q = T("O₂ = ?", 90, AMBER, True).move_to([0, 2.7, 0])

        self.play(Write(self._head), run_time=0.9)
        self.play(Write(self._rxn), run_time=1.2)
        self.play(FadeIn(self._q, shift=UP * 0.2), run_time=0.6)
        self.fill()

    # 6 -------------------------------------------------------- ex: mole
    def s_ex_mole(self):
        self.section("ex_mole")
        self._m = T("M = 122.5 g/mol", 56, DIM).move_to([0, 1.6, 0])
        self._n = T("n = 122.5 / 122.5 = 1 mol", 72, TEAL, True).move_to([0, 0.4, 0])
        self.play(FadeIn(self._m, shift=UP * 0.2), run_time=0.6)
        self.play(Write(self._n), run_time=1.2)
        self.fill()

    # 7 -------------------------------------------------------- ex: POAC
    def s_ex_poac(self):
        self.section("ex_poac")
        self.play(FadeOut(self._m, self._n, self._q), run_time=0.4)

        left = T("3 × 1", 96, BLUE, True)
        mid = T("=", 96, WHITE, True)
        right = T("2 × n(O₂)", 96, CORAL, True)
        eq = VGroup(left, mid, right).arrange(RIGHT, buff=0.4)
        fit(eq).move_to([0, 2.7, 0])
        l_lab = T("O in KClO₃", 44, DIM).next_to(left, DOWN, buff=0.4)
        r_lab = T("O in O₂", 44, DIM).next_to(right, DOWN, buff=0.4)
        self._res = T("n(O₂) = 3 / 2 = 1.5 mol", 76, TEAL, True).move_to([0, 0.4, 0])

        self.play(Write(left), run_time=0.8)
        self.play(FadeIn(l_lab), run_time=0.4)
        self.play(Write(mid), run_time=0.3)
        self.play(Write(right), run_time=0.9)
        self.play(FadeIn(r_lab), run_time=0.4)
        self.play(Write(self._res), run_time=1.2)
        self.fill()

    # 8 ------------------------------------------------------ ex: answer
    def s_ex_answer(self):
        self.section("ex_answer")
        grams = T("1.5 × 32 = 48 g", 76, CORAL, True).move_to([0, -0.8, 0])
        litres = T("1.5 × 22.4 = 33.6 L", 76, BLUE, True).move_to([0, -1.9, 0])
        cond = T("273 K, 1 atm", 40, DIM).move_to([0, -2.7, 0])
        self.play(Write(grams), run_time=1.0)
        self.play(Write(litres), run_time=1.0)
        self.play(FadeIn(cond), run_time=0.4)
        self.play(Indicate(grams, color=AMBER), Indicate(litres, color=AMBER),
                  run_time=0.8)
        self.fill()

    # 9 ------------------------------------------------------------ CTA
    def s_cta(self):
        self.section("cta")
        self._wipe()
        btn_box = RoundedRectangle(width=4.6, height=1.4, corner_radius=0.7,
                                   color=TEAL, fill_color=TEAL, fill_opacity=1,
                                   stroke_width=0)
        btn_txt = Text("Follow", font_size=84, color=BG, weight=BOLD)
        btn = VGroup(btn_box, btn_txt)
        btn_txt.move_to(btn_box.get_center())
        btn.move_to([0, 4.6, 0])
        brand = T("IITians PACE", 116, AMBER, True).move_to([0, 2.5, 0])
        sub = T("for more videos like this", 54, DIM).move_to([0, 1.2, 0])

        self.play(GrowFromCenter(btn), run_time=0.7)
        self.play(Write(brand), run_time=1.0)
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.6)
        self.play(Indicate(btn, color=TEAL, scale_factor=1.12), run_time=0.8)
        self.fill()
