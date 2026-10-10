"""
Stoichiometry - ReelForge scene.

Vertical frame 9 x 16, no LaTeX, no images. Uses the existing SyncedScene
from example_scene.py (section(name) / fill()).
Section names MUST match the `section:` keys in stoichiometry.yaml.
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

N_COL = BLUE     # nitrogen
H_COL = CORAL    # hydrogen
P_COL = AMBER    # ammonia / products


# ---------------------------------------------------------------- helpers
def fit(m, w=8.2):
    """Shrink anything wider than the safe width."""
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


def T(s, size=80, color=WHITE, bold=False):
    return fit(Text(s, font_size=size, color=color,
                    weight=BOLD if bold else NORMAL))


def _atom(r, color, pos=(0, 0)):
    return Circle(radius=r, color=color, fill_opacity=1,
                  stroke_width=0).move_to([pos[0], pos[1], 0])


def mol_N2():
    return VGroup(_atom(0.32, N_COL, (-0.3, 0)), _atom(0.32, N_COL, (0.3, 0)))


def mol_H2():
    return VGroup(_atom(0.22, H_COL, (-0.17, 0)), _atom(0.22, H_COL, (0.17, 0)))


def mol_NH3():
    return VGroup(_atom(0.3, N_COL, (0, 0)),
                  _atom(0.2, H_COL, (0, 0.5)),
                  _atom(0.2, H_COL, (-0.43, -0.25)),
                  _atom(0.2, H_COL, (0.43, -0.25)))


def equation(size, buff=0.3):
    eq = VGroup(T("N₂", size, N_COL, True), T("+", size),
                T("3H₂", size, H_COL, True), T("→", size),
                T("2NH₃", size, P_COL, True)).arrange(RIGHT, buff=buff)
    return fit(eq)


# ------------------------------------------------------------------ scene
class Stoichiometry(SyncedScene):
    def construct(self):
        self.camera.background_color = BG
        self.s_recipe()
        self.s_ratio()
        self.s_roadmap()
        self.s_ex_setup()
        self.s_ex_step1()
        self.s_ex_step2()
        self.s_ex_step3()
        self.s_lim_setup()
        self.s_lim_divide()
        self.s_lim_react()
        self.s_cta()

    def _wipe(self):
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.4)

    def _swap(self, old, new, rt=0.7):
        self.play(ReplacementTransform(old, new), run_time=rt)
        return new

    # 1 -------------------------------------------------------- recipe
    def s_recipe(self):
        self.section("recipe")
        eq = equation(88).move_to([0, 5.8, 0])

        items = [mol_N2(), T("+", 72), mol_H2(), mol_H2(), mol_H2(),
                 T("→", 72), mol_NH3(), mol_NH3()]
        row = VGroup(*items).arrange(RIGHT, buff=0.3)
        fit(row).move_to([0, 3.2, 0])
        count = T("N: 2 = 2      H: 6 = 6", 60, DIM).move_to([0, 1.3, 0])

        self.play(Write(eq), run_time=1.2)
        self.play(GrowFromCenter(items[0]), FadeIn(items[1]), run_time=0.6)
        self.play(LaggedStart(*[GrowFromCenter(h) for h in items[2:5]],
                              lag_ratio=0.3), run_time=1.0)
        self.play(Write(items[5]), run_time=0.4)
        self.play(Flash(items[5].get_center(), color=AMBER, flash_radius=0.8),
                  LaggedStart(*[FadeIn(p, shift=RIGHT * 0.8, scale=0.3)
                                for p in items[6:]], lag_ratio=0.3),
                  run_time=1.2)
        self.play(FadeIn(count, shift=UP * 0.2), run_time=0.6)
        self.play(Indicate(count, color=WHITE), run_time=0.7)
        self.fill()

    # 2 --------------------------------------------------------- ratio
    def s_ratio(self):
        self.section("ratio")
        self._wipe()
        terms = [T("N₂", 88, N_COL, True), T("+", 88),
                 T("3H₂", 88, H_COL, True), T("→", 88),
                 T("2NH₃", 88, P_COL, True)]
        eq = VGroup(*terms).arrange(RIGHT, buff=0.35)
        fit(eq).move_to([0, 5.4, 0])

        def counts(a, b, c):
            labs = []
            for term, v, col in ((terms[0], a, N_COL), (terms[2], b, H_COL),
                                 (terms[4], c, P_COL)):
                labs.append(T(f"{v} mol", 56, col, True)
                            .next_to(term, DOWN, buff=0.5))
            return VGroup(*labs)

        c1, c2, c3 = counts(1, 3, 2), counts(2, 6, 4), counts(10, 30, 20)
        t1 = T("× 1", 96, WHITE, True).move_to([0, 2.5, 0])
        t2 = T("× 2", 96, WHITE, True).move_to([0, 2.5, 0])
        t3 = T("× 10", 96, WHITE, True).move_to([0, 2.5, 0])
        ratio = T("1 : 3 : 2", 110, TEAL, True).move_to([0, 0.6, 0])

        self.play(Write(eq), run_time=1.0)
        self.play(FadeIn(c1, shift=UP * 0.2), run_time=1.0)
        self.play(FadeIn(t1), Write(ratio), run_time=0.8)
        self.play(ReplacementTransform(c1, c2), ReplacementTransform(t1, t2),
                  run_time=0.9)
        self.play(Indicate(ratio, color=WHITE), run_time=0.6)
        self.play(ReplacementTransform(c2, c3), ReplacementTransform(t2, t3),
                  run_time=0.9)
        self.play(Indicate(ratio, color=WHITE), run_time=0.6)
        self.fill()

    # 3 ------------------------------------------------------- roadmap
    def s_roadmap(self):
        self.section("roadmap")
        self._wipe()
        ys = [4.6, 2.8, 1.0, -0.8]
        spec = [("mass of A", BLUE), ("moles of A", BLUE),
                ("moles of B", AMBER), ("mass of B", AMBER)]
        self._rects, self._labels = [], []
        for y, (nm, col) in zip(ys, spec):
            rect = RoundedRectangle(width=3.6, height=1.2, corner_radius=0.25,
                                    color=col, stroke_width=8).move_to([0, y, 0])
            lab = T(nm, 52, col, True).move_to(rect.get_center())
            self._rects.append(rect)
            self._labels.append(lab)

        self._arrows, self._alabs = [], []
        for i, (txt, col) in enumerate([("÷ M", BLUE), ("mole ratio", TEAL),
                                        ("× M", AMBER)]):
            a = Arrow(self._rects[i].get_bottom(), self._rects[i + 1].get_top(),
                      buff=0.05, color=DIM, stroke_width=8, tip_length=0.25,
                      max_tip_length_to_length_ratio=0.5)
            al = T(txt, 46, col, True).next_to(a, RIGHT, buff=0.3)
            self._arrows.append(a)
            self._alabs.append(al)

        for i in range(4):
            self.play(GrowFromCenter(self._rects[i]),
                      FadeIn(self._labels[i]), run_time=0.5)
            if i < 3:
                self.play(Create(self._arrows[i]),
                          FadeIn(self._alabs[i], shift=RIGHT * 0.2),
                          run_time=0.5)

        dot = Dot(radius=0.18, color=WHITE).move_to(self._rects[0].get_center())
        self.play(FadeIn(dot), run_time=0.2)
        for i in range(1, 4):
            self.play(dot.animate.move_to(self._rects[i].get_center()),
                      Indicate(self._rects[i], color=WHITE, scale_factor=1.08),
                      run_time=0.6)
        self.play(FadeOut(dot), run_time=0.2)
        self.fill()

    # 4 ------------------------------------------------------ ex: setup
    def s_ex_setup(self):
        self.section("ex_setup")
        eq = equation(64).move_to([0, 6.3, 0])
        exc = T("H₂ in excess", 40, DIM).move_to([0, 5.6, 0])
        new1 = T("28 g N₂", 56, N_COL, True).move_to(self._rects[0].get_center())
        new4 = T("? g NH₃", 56, P_COL, True).move_to(self._rects[3].get_center())

        self.play(FadeIn(eq, shift=DOWN * 0.3), run_time=0.7)
        self.play(FadeIn(exc), run_time=0.4)
        self._labels[0] = self._swap(self._labels[0], new1)
        self._labels[3] = self._swap(self._labels[3], new4)
        self.play(Indicate(self._rects[0], color=N_COL),
                  Indicate(self._rects[3], color=P_COL), run_time=0.8)
        self.fill()

    # 5 ------------------------------------------------------ ex: step 1
    def s_ex_step1(self):
        self.section("ex_step1")
        al = T("÷ 28", 46, N_COL, True).next_to(self._arrows[0], RIGHT, buff=0.3)
        b2 = T("1 mol N₂", 52, N_COL, True).move_to(self._rects[1].get_center())
        self._alabs[0] = self._swap(self._alabs[0], al)
        self.play(Indicate(self._arrows[0], color=WHITE), run_time=0.5)
        self._labels[1] = self._swap(self._labels[1], b2)
        self.play(Indicate(self._rects[1], color=N_COL, scale_factor=1.1),
                  run_time=0.7)
        self.fill()

    # 6 ------------------------------------------------------ ex: step 2
    def s_ex_step2(self):
        self.section("ex_step2")
        al = T("× 2 / 1", 46, TEAL, True).next_to(self._arrows[1], RIGHT, buff=0.3)
        b3 = T("2 mol NH₃", 52, P_COL, True).move_to(self._rects[2].get_center())
        self._alabs[1] = self._swap(self._alabs[1], al)
        self.play(Indicate(self._arrows[1], color=WHITE), run_time=0.5)
        self._labels[2] = self._swap(self._labels[2], b3)
        self.play(Indicate(self._rects[2], color=P_COL, scale_factor=1.1),
                  run_time=0.7)
        self.fill()

    # 7 ------------------------------------------------------ ex: step 3
    def s_ex_step3(self):
        self.section("ex_step3")
        al = T("× 17", 46, P_COL, True).next_to(self._arrows[2], RIGHT, buff=0.3)
        b4 = T("34 g NH₃", 56, P_COL, True).move_to(self._rects[3].get_center())
        self._alabs[2] = self._swap(self._alabs[2], al)
        self.play(Indicate(self._arrows[2], color=WHITE), run_time=0.5)
        self._labels[3] = self._swap(self._labels[3], b4)
        self.play(Circumscribe(self._rects[3], color=P_COL), run_time=1.0)
        self.fill()

    # 8 ----------------------------------------------------- lim: setup
    def s_lim_setup(self):
        self.section("lim_setup")
        self._wipe()
        y = 4.4
        self._n2 = [mol_N2().move_to([x, y, 0]) for x in (-3.0, -1.4)]
        self._h2 = [mol_H2().move_to([x, y, 0]) for x in (0.9, 2.2, 3.5)]
        self._lab_n = T("2 mol N₂", 60, N_COL, True).move_to([-2.2, 3.1, 0])
        self._lab_h = T("3 mol H₂", 60, H_COL, True).move_to([2.2, 3.1, 0])
        self._q = T("who runs out first?", 64, AMBER, True).move_to([0, 1.8, 0])

        self.play(LaggedStart(*[GrowFromCenter(m) for m in self._n2],
                              lag_ratio=0.3), run_time=0.9)
        self.play(FadeIn(self._lab_n, shift=UP * 0.2), run_time=0.5)
        self.play(LaggedStart(*[GrowFromCenter(m) for m in self._h2],
                              lag_ratio=0.3), run_time=1.0)
        self.play(FadeIn(self._lab_h, shift=UP * 0.2), run_time=0.5)
        self.play(Write(self._q), run_time=0.9)
        self.fill()

    # 9 ----------------------------------------------------- lim: divide
    def s_lim_divide(self):
        self.section("lim_divide")
        self.play(FadeOut(self._q), run_time=0.3)
        r1 = T("N₂: 2 ÷ 1 = 2", 72, N_COL, True).move_to([0, 1.9, 0])
        r2 = T("H₂: 3 ÷ 3 = 1", 72, H_COL, True).move_to([0, 0.7, 0])
        tag = T("limiting", 68, AMBER, True).move_to([0, -0.8, 0])

        self.play(Write(r1), run_time=0.9)
        self.play(Write(r2), run_time=0.9)
        self.play(r1.animate.set_opacity(0.35), run_time=0.4)
        box = SurroundingRectangle(r2, color=AMBER, buff=0.25, stroke_width=8)
        self.play(Create(box), run_time=0.6)
        self.play(Write(tag), run_time=0.6)
        self.play(Indicate(self._h2[0], color=AMBER),
                  Indicate(self._h2[1], color=AMBER),
                  Indicate(self._h2[2], color=AMBER), run_time=0.8)
        self._lim_items = [r1, r2, box, tag]
        self.fill()

    # 10 ----------------------------------------------------- lim: react
    def s_lim_react(self):
        self.section("lim_react")
        self.play(FadeOut(*self._lim_items, self._lab_n, self._lab_h),
                  run_time=0.4)
        y = 4.4
        reactants = [self._n2[1]] + self._h2
        products = [mol_NH3().move_to([1.1, y, 0]),
                    mol_NH3().move_to([2.8, y, 0])]
        hit = [1.9, y, 0]

        self.play(*[m.animate.move_to(hit) for m in reactants], run_time=1.0)
        self.play(Flash(np.array(hit), color=AMBER, flash_radius=1.0),
                  FadeOut(*reactants),
                  *[FadeIn(p, scale=0.3) for p in products],
                  run_time=0.9)
        formed = T("2 mol NH₃ formed", 68, P_COL, True).move_to([0, 2.2, 0])
        left = T("1 mol N₂ left", 68, N_COL, True).move_to([0, 1.0, 0])
        self.play(Write(formed), run_time=0.9)
        self.play(Write(left), Indicate(self._n2[0], color=WHITE),
                  run_time=0.9)
        self.fill()

    # 11 ------------------------------------------------------------ CTA
    def s_cta(self):
        self.section("cta")
        self._wipe()
        btn_box = RoundedRectangle(width=4.6, height=1.4, corner_radius=0.7,
                                   color=TEAL, fill_color=TEAL, fill_opacity=1,
                                   stroke_width=0)
        btn_txt = Text("Follow", font_size=84, color=BG, weight=BOLD)
        btn_txt.move_to(btn_box.get_center())
        btn = VGroup(btn_box, btn_txt).move_to([0, 4.6, 0])
        brand = T("IITians PACE", 116, AMBER, True).move_to([0, 2.5, 0])
        sub = T("for more videos like this", 54, DIM).move_to([0, 1.2, 0])

        self.play(GrowFromCenter(btn), run_time=0.7)
        self.play(Write(brand), run_time=1.0)
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.6)
        self.play(Indicate(btn, color=TEAL, scale_factor=1.12), run_time=0.8)
        self.fill()
