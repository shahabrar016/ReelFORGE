"""
Quantum numbers - ReelForge scene.

Vertical frame 9 x 16, no LaTeX, no images. Uses the existing SyncedScene
from example_scene.py (section(name) / fill()).
Section names MUST match the `section:` keys in quantum_numbers.yaml.
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


def sym(base, sub=None, size=80, color=WHITE):
    """Italic variable with optional small subscript (no LaTeX)."""
    b = Text(base, font_size=size, color=color, weight=BOLD, slant=ITALIC)
    if sub is None:
        return b
    s = Text(sub, font_size=int(size * 0.55), color=color, weight=BOLD,
             slant=ITALIC)
    s.next_to(b, RIGHT, buff=0.03, aligned_edge=DOWN).shift(DOWN * size / 80 * 0.1)
    return VGroup(b, s)


def fmt_m(m):
    if m == 0:
        return "0"
    return ("+" if m > 0 else "−") + str(abs(m))


def lobe(w, h, color, angle_deg, dist):
    """Ellipse lobe whose long axis points along angle_deg."""
    e = Ellipse(width=w, height=h, color=color, fill_opacity=0.65,
                stroke_width=3)
    e.rotate((angle_deg - 90) * DEGREES)
    a = angle_deg * DEGREES
    e.move_to([dist * np.cos(a), dist * np.sin(a), 0])
    return e


def shape_s():
    return VGroup(Circle(radius=0.7, color=BLUE, fill_opacity=0.65,
                         stroke_width=3))


def shape_p():
    return VGroup(lobe(0.9, 1.5, TEAL, 90, 0.75),
                  lobe(0.9, 1.5, CORAL, 270, 0.75))


def shape_d():
    cols = [AMBER, BLUE, AMBER, BLUE]
    return VGroup(*[lobe(0.55, 1.1, c, a, 0.55)
                    for c, a in zip(cols, (45, 135, 225, 315))])


def shape_f():
    ring = DashedVMobject(Circle(radius=0.75, color=DIM, stroke_width=5))
    return VGroup(ring, T("complex", 34, DIM))


def tick(color=TEAL):
    return VMobject(color=color, stroke_width=10).set_points_as_corners(
        [[-0.3, 0, 0], [-0.1, -0.25, 0], [0.3, 0.3, 0]])


def cross(color=CORAL):
    return VGroup(
        Line([-0.28, -0.28, 0], [0.28, 0.28, 0], color=color, stroke_width=10),
        Line([-0.28, 0.28, 0], [0.28, -0.28, 0], color=color, stroke_width=10))


# ------------------------------------------------------------------ scene
class QuantumNumbers(SyncedScene):
    def construct(self):
        self.camera.background_color = BG
        self.s_intro()
        self.s_n()
        self.s_l()
        self.s_ml()
        self.s_ms()
        self.s_pauli()
        self.s_cap_sub()
        self.s_example()
        self.s_check1()
        self.s_check2()
        self.s_check3()
        self.s_cta()

    def _wipe(self):
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.4)

    # 1 ------------------------------------------------------------ intro
    def s_intro(self):
        self.section("intro")
        spec = [(sym("n", None, 120, BLUE), "shell", BLUE, (-2.0, 4.6)),
                (sym("l", None, 120, TEAL), "subshell", TEAL, (2.0, 4.6)),
                (sym("m", "l", 120, AMBER), "orbital", AMBER, (-2.0, 1.5)),
                (sym("m", "s", 120, CORAL), "spin", CORAL, (2.0, 1.5))]
        for symbol, role, col, (x, y) in spec:
            rect = RoundedRectangle(width=3.8, height=2.8, corner_radius=0.3,
                                    color=col, stroke_width=8).move_to([x, y, 0])
            symbol.move_to([x, y + 0.4, 0])
            r = T(role, 52, DIM).move_to([x, y - 0.8, 0])
            self.play(GrowFromCenter(rect), Write(symbol), FadeIn(r),
                      run_time=0.8)
        self.fill()

    # 2 ---------------------------------------------------------------- n
    def s_n(self):
        self.section("n")
        self._wipe()
        c = np.array([0, 3.0, 0])
        nucleus = Dot(c, radius=0.12, color=WHITE)
        cols = [BLUE, TEAL, AMBER]
        self.play(FadeIn(nucleus), run_time=0.3)
        for n, col, dy in zip((1, 2, 3), cols, (0.75, 1.95, 3.1)):
            ring = Circle(radius=0.3 * n * n, color=col, stroke_width=7)
            ring.move_to(c)
            lab = VGroup(sym("n", None, 48, col), T("= " + str(n), 48, col, True))
            lab.arrange(RIGHT, buff=0.12).move_to(c + np.array([0, dy, 0]))
            self.play(Create(ring), FadeIn(lab, shift=UP * 0.15), run_time=0.9)
        note = T("energy and size grow", 52, DIM).move_to([0, -0.7, 0])
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.6)
        self.fill()

    # 3 ---------------------------------------------------------------- l
    def s_l(self):
        self.section("l")
        self._wipe()
        xs = [-3.3, -1.1, 1.1, 3.3]
        shapes = [shape_s(), shape_p(), shape_d(), shape_f()]
        letters = [("s", BLUE), ("p", TEAL), ("d", AMBER), ("f", CORAL)]
        anims = []
        for k, (x, shp, (ch, col)) in enumerate(zip(xs, shapes, letters)):
            shp.move_to([x, 4.8, 0])
            letter = T(ch, 90, col, True).move_to([x, 3.2, 0])
            lval = VGroup(sym("l", None, 52, DIM), T("= " + str(k), 52, DIM))
            lval.arrange(RIGHT, buff=0.1).move_to([x, 2.2, 0])
            anims.append(AnimationGroup(GrowFromCenter(shp), Write(letter),
                                        FadeIn(lval)))
        self.play(LaggedStart(*anims, lag_ratio=0.5), run_time=3.2)
        rule = VGroup(sym("l", None, 80, AMBER),
                      T("= 0 to n − 1", 80, AMBER, True))
        rule.arrange(RIGHT, buff=0.15)
        fit(rule).move_to([0, 0.6, 0])
        self.play(Write(rule), run_time=1.0)
        self.play(Indicate(rule, color=WHITE), run_time=0.7)
        self.fill()

    # 4 --------------------------------------------------------------- ml
    def s_ml(self):
        self.section("ml")
        self._wipe()

        def orbital_row(letter, color, l):
            boxes = VGroup(*[Square(side_length=1.0, color=color, stroke_width=6)
                             for _ in range(2 * l + 1)]).arrange(RIGHT, buff=0.12)
            labs = VGroup(*[T(fmt_m(m), 44, DIM).next_to(b, DOWN, buff=0.15)
                            for m, b in zip(range(-l, l + 1), boxes)])
            let = T(letter, 80, color, True).next_to(boxes, LEFT, buff=0.4)
            return VGroup(let, boxes, labs)

        rows = VGroup(orbital_row("s", BLUE, 0),
                      orbital_row("p", TEAL, 1),
                      orbital_row("d", AMBER, 2))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit(rows).move_to([0, 3.0, 0])

        formula = VGroup(T("orbitals = 2", 72, AMBER, True),
                         sym("l", None, 72, AMBER),
                         T("+ 1", 72, AMBER, True)).arrange(RIGHT, buff=0.15)
        fit(formula).move_to([0, -1.4, 0])

        for r in rows:
            self.play(Write(r[0]), run_time=0.4)
            self.play(LaggedStart(*[Create(b) for b in r[1]], lag_ratio=0.2),
                      run_time=0.8)
            self.play(FadeIn(r[2]), run_time=0.4)
        self.play(Write(formula), run_time=1.0)
        self.play(Indicate(formula, color=WHITE), run_time=0.7)
        self.fill()

    # 5 --------------------------------------------------------------- ms
    def s_ms(self):
        self.section("ms")
        self._wipe()
        head = sym("m", "s", 110, CORAL).move_to([0, 6.0, 0])
        box = Square(side_length=2.4, color=TEAL, stroke_width=8)
        box.move_to([0, 3.6, 0])
        up = Arrow([-0.45, 2.9, 0], [-0.45, 4.3, 0], buff=0, color=BLUE,
                   stroke_width=10, max_tip_length_to_length_ratio=0.35)
        down = Arrow([0.45, 4.3, 0], [0.45, 2.9, 0], buff=0, color=CORAL,
                     stroke_width=10, max_tip_length_to_length_ratio=0.35)
        lab_up = T("+½", 72, BLUE, True).move_to([-0.9, 1.5, 0])
        lab_dn = T("−½", 72, CORAL, True).move_to([0.9, 1.5, 0])
        up_w = T("up", 44, DIM).move_to([-0.9, 0.7, 0])
        dn_w = T("down", 44, DIM).move_to([0.9, 0.7, 0])
        cap = T("max 2 per orbital", 56, DIM).move_to([0, -0.6, 0])

        self.play(Write(head), run_time=0.7)
        self.play(Create(box), run_time=0.7)
        self.play(GrowArrow(up), FadeIn(lab_up, shift=UP * 0.2), FadeIn(up_w),
                  run_time=0.9)
        self.play(GrowArrow(down), FadeIn(lab_dn, shift=UP * 0.2), FadeIn(dn_w),
                  run_time=0.9)
        self.play(Indicate(box, color=AMBER, scale_factor=1.08), run_time=0.8)
        self.play(FadeIn(cap, shift=UP * 0.2), run_time=0.6)
        self.fill()

    # 6 ------------------------------------------------------------ pauli
    def s_pauli(self):
        self.section("pauli")
        self._wipe()
        head = T("Pauli exclusion", 76, AMBER, True).move_to([0, 6.1, 0])
        xs = [-2.7, -0.9, 0.9, 2.7]
        heads = [sym("n", None, 76, BLUE), sym("l", None, 76, TEAL),
                 sym("m", "l", 76, AMBER), sym("m", "s", 76, CORAL)]
        cols = [BLUE, TEAL, AMBER, CORAL]
        for h, x in zip(heads, xs):
            h.move_to([x, 4.7, 0])
        row1 = ["1", "0", "0", "+½"]
        row2 = ["1", "0", "0", "−½"]
        cells1 = [T(t, 100, c, True).move_to([x, 3.2, 0])
                  for t, c, x in zip(row1, cols, xs)]
        cells2 = [T(t, 100, c, True).move_to([x, 1.8, 0])
                  for t, c, x in zip(row2, cols, xs)]
        note = T("both in 1s", 52, DIM).move_to([0, 0.4, 0])

        self.play(Write(head), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(h, shift=DOWN * 0.2) for h in heads],
                              lag_ratio=0.2), run_time=0.9)
        self.play(LaggedStart(*[Write(c) for c in cells1], lag_ratio=0.2),
                  run_time=1.0)
        self.play(LaggedStart(*[Write(c) for c in cells2], lag_ratio=0.2),
                  run_time=1.0)
        self.play(FadeIn(note), run_time=0.4)
        spin_box = SurroundingRectangle(VGroup(cells1[3], cells2[3]),
                                        color=AMBER, buff=0.2, stroke_width=8)
        self.play(Create(spin_box), run_time=0.6)
        self.play(Indicate(cells1[3], color=WHITE),
                  Indicate(cells2[3], color=WHITE), run_time=0.8)
        self.fill()

    # 7 ----------------------------------------------------------- cap_sub
    def s_cap_sub(self):
        self.section("cap_sub")
        self._wipe()
        head = VGroup(T("2 × (2", 88, AMBER, True), sym("l", None, 88, AMBER),
                      T("+ 1)", 88, AMBER, True)).arrange(RIGHT, buff=0.12)
        fit(head).move_to([0, 6.3, 0])

        spec = [("s", 1, BLUE), ("p", 3, TEAL), ("d", 5, AMBER), ("f", 7, CORAL)]
        rows = []
        for letter, k, col in spec:
            pairs = VGroup(*[VGroup(Dot(radius=0.17, color=col),
                                    Dot(radius=0.17, color=col)
                                    ).arrange(RIGHT, buff=0.06)
                             for _ in range(k)]).arrange(RIGHT, buff=0.25)
            rows.append(VGroup(T(letter, 80, col, True), pairs,
                               T(str(2 * k), 80, col, True)
                               ).arrange(RIGHT, buff=0.4))
        grid = VGroup(*rows).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        fit(grid).move_to([0, 2.9, 0])

        self.play(Write(head), run_time=0.9)
        for r in rows:
            self.play(Write(r[0]), run_time=0.3)
            dots = [d for pair in r[1] for d in pair]
            self.play(LaggedStart(*[GrowFromCenter(d) for d in dots],
                                  lag_ratio=0.08), run_time=0.9)
            self.play(Write(r[2]), run_time=0.3)
        self.fill()

    # 8 ----------------------------------------------------------- example
    def s_example(self):
        self.section("example")
        self._wipe()
        head = VGroup(sym("n", None, 96, AMBER),
                      T("= 3", 96, AMBER, True)).arrange(RIGHT, buff=0.2)
        head.move_to([0, 6.1, 0])

        spec = [("3s", 1, BLUE), ("3p", 3, TEAL), ("3d", 5, AMBER)]
        rows = []
        for label, k, col in spec:
            boxes = VGroup(*[Square(side_length=0.9, color=col, stroke_width=6)
                             for _ in range(k)]).arrange(RIGHT, buff=0.12)
            rows.append(VGroup(T(label, 72, col, True), boxes
                               ).arrange(RIGHT, buff=0.4))
        grid = VGroup(*rows).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit(grid).move_to([0, 3.6, 0])

        total = VGroup(T("1 + 3 + 5 = 9 = ", 72, TEAL, True),
                       sym("n", None, 72, TEAL),
                       T("²", 72, TEAL, True)).arrange(RIGHT, buff=0.05)
        fit(total).move_to([0, 0.4, 0])
        elec = VGroup(T("2 × 9 = 18 = 2", 72, CORAL, True),
                      sym("n", None, 72, CORAL),
                      T("²", 72, CORAL, True)).arrange(RIGHT, buff=0.05)
        fit(elec).move_to([0, -0.9, 0])

        self.play(Write(head), run_time=0.8)
        for r in rows:
            self.play(Write(r[0]), run_time=0.4)
            self.play(LaggedStart(*[Create(b) for b in r[1]], lag_ratio=0.2),
                      run_time=0.7)
        self.play(Write(total), run_time=1.0)
        self.play(Write(elec), run_time=1.0)
        self.play(Indicate(total, color=WHITE), Indicate(elec, color=WHITE),
                  run_time=0.8)
        self.fill()

    # 9-11 ------------------------------------------------------- checks
    def _tuple(self, text, y):
        return T(text, 84, WHITE, True).move_to([0, y, 0])

    def s_check1(self):
        self.section("check1")
        self._wipe()
        tup = self._tuple("(2, 1, −1, +½)", 4.8)
        mark = tick()
        why = T("valid", 56, TEAL, True)
        res = VGroup(mark, why).arrange(RIGHT, buff=0.35).next_to(tup, DOWN, buff=0.35)
        self.play(Write(tup), run_time=1.2)
        self.play(Create(mark), FadeIn(why, shift=RIGHT * 0.2), run_time=0.7)
        self.fill()

    def s_check2(self):
        self.section("check2")
        tup = self._tuple("(2, 2, 0, +½)", 2.5)
        mark = cross()
        why = VGroup(sym("l", None, 56, CORAL), T("≤ n − 1", 56, CORAL, True))
        why.arrange(RIGHT, buff=0.15)
        res = VGroup(mark, why).arrange(RIGHT, buff=0.35).next_to(tup, DOWN, buff=0.35)
        self.play(Write(tup), run_time=1.2)
        self.play(Create(mark), FadeIn(why, shift=RIGHT * 0.2), run_time=0.7)
        self.fill()

    def s_check3(self):
        self.section("check3")
        tup = self._tuple("(3, 1, 2, −½)", 0.2)
        mark = cross()
        why = VGroup(T("−l ≤", 52, CORAL, True), sym("m", "l", 52, CORAL),
                     T("≤ +l", 52, CORAL, True)).arrange(RIGHT, buff=0.12)
        fit(why, 6.0)
        res = VGroup(mark, why).arrange(RIGHT, buff=0.35).next_to(tup, DOWN, buff=0.35)
        self.play(Write(tup), run_time=1.2)
        self.play(Create(mark), FadeIn(why, shift=RIGHT * 0.2), run_time=0.7)
        self.fill()

    # 12 ----------------------------------------------------------- CTA
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
