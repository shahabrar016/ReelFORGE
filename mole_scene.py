"""
Mole concept fundamentals - ReelForge scene.

Vertical frame 9 x 16, no LaTeX, no images. Uses the existing SyncedScene
from example_scene.py (section(name) / fill()).
Section names MUST match the `section:` keys in mole_concept.yaml.
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


def NA(size=80, color=AMBER):
    """N with a small subscript A (no LaTeX)."""
    n = Text("N", font_size=size, color=color, weight=BOLD)
    a = Text("A", font_size=int(size * 0.5), color=color, weight=BOLD)
    a.next_to(n, RIGHT, buff=0.03, aligned_edge=DOWN).shift(DOWN * 0.08)
    return VGroup(n, a)


def frac(num, den, size=72, color=WHITE):
    n = num if isinstance(num, Mobject) else Text(num, font_size=size, color=color)
    d = den if isinstance(den, Mobject) else Text(den, font_size=size, color=color)
    w = max(n.width, d.width) + 0.3
    bar = Line(LEFT * w / 2, RIGHT * w / 2, color=color, stroke_width=6)
    return VGroup(n, bar, d).arrange(DOWN, buff=0.15)


def eq_row(label, num, den, color, cond=None):
    n_eq = Text("n =", font_size=72, color=color, weight=BOLD)
    f = frac(num, den, 72, color)
    lab = Text(label, font_size=46, color=DIM)
    if cond:
        lab = VGroup(lab, Text(cond, font_size=38, color=DIM)).arrange(
            DOWN, buff=0.12, aligned_edge=LEFT)
    return VGroup(n_eq, f, lab).arrange(RIGHT, buff=0.45)


def dots_in(box, n, seed, radius=0.06, color=WHITE):
    rng = np.random.default_rng(seed)
    cx, cy = box.get_center()[:2]
    w, h = box.width, box.height
    return VGroup(*[
        Dot(point=[cx + rng.uniform(-w / 2 + 0.2, w / 2 - 0.2),
                   cy + rng.uniform(-h / 2 + 0.2, h / 2 - 0.2), 0],
            radius=radius, color=color)
        for _ in range(n)
    ])


# ------------------------------------------------------------------ scene
class MoleConcept(SyncedScene):
    def construct(self):
        self.camera.background_color = BG
        self.s_hook()
        self.s_avogadro()
        self.s_molar_mass()
        self.s_formula_mass()
        self.s_formula_particles()
        self.s_formula_volume()
        self.s_water_moles()
        self.s_water_atoms()
        self.s_gas_volume()
        self.s_gas_mass()
        self.s_equation()
        self.s_masses()

    def _wipe(self):
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.4)

    # 1 ------------------------------------------------------------ hook
    def s_hook(self):
        self.section("hook")
        dozen = T("1 dozen = 12", 96, AMBER, True).move_to([0, 5.6, 0])
        grid = VGroup(*[Dot(radius=0.2, color=AMBER) for _ in range(12)])
        grid.arrange_in_grid(2, 6, buff=0.4).move_to([0, 3.9, 0])
        mole = T("1 mole", 110, TEAL, True).move_to([0, 2.2, 0])
        big = T("6.022 × 10²³", 110, TEAL, True).next_to(mole, DOWN, buff=0.35)

        rng = np.random.default_rng(7)
        swarm = VGroup(*[
            Dot(point=[rng.uniform(-4.1, 4.1), rng.uniform(-2.7, -0.7), 0],
                radius=0.035, color=TEAL)
            for _ in range(260)
        ])

        self.play(Write(dozen), run_time=0.8)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in grid],
                              lag_ratio=0.1), run_time=1.2)
        self.play(Write(mole), run_time=0.7)
        self.play(Write(big), run_time=1.0)
        self.play(LaggedStartMap(FadeIn, swarm, lag_ratio=0.01), run_time=1.5)
        self.fill()

    # 2 ------------------------------------------------------ avogadro
    def s_avogadro(self):
        self.section("avogadro")
        self._wipe()
        title = T("Avogadro constant", 72, AMBER, True).move_to([0, 6.0, 0])
        value = VGroup(NA(104, TEAL),
                       T("= 6.022 × 10²³", 104, TEAL, True)
                       ).arrange(RIGHT, buff=0.3)
        fit(value).move_to([0, 4.5, 0])

        atom = Circle(radius=0.55, color=BLUE, fill_opacity=0.9, stroke_width=0)
        o = Circle(radius=0.45, color=CORAL, fill_opacity=0.9, stroke_width=0)
        h1 = Circle(radius=0.28, color=WHITE, fill_opacity=1, stroke_width=0)
        h2 = Circle(radius=0.28, color=WHITE, fill_opacity=1, stroke_width=0)
        h1.move_to(o.get_center() + np.array([-0.6, -0.45, 0]))
        h2.move_to(o.get_center() + np.array([0.6, -0.45, 0]))
        molecule = VGroup(o, h1, h2)
        ion = VGroup(Circle(radius=0.55, color=TEAL, fill_opacity=0.9,
                            stroke_width=0),
                     Text("+", font_size=80, color=BG, weight=BOLD))

        xs = [-2.9, 0, 2.9]
        icons = [atom, molecule, ion]
        for m, x in zip(icons, xs):
            m.move_to([x, 2.8, 0])

        def lab(word, x):
            g = VGroup(T("1 mol", 60, TEAL, True), T(word, 52, DIM))
            return g.arrange(DOWN, buff=0.12).move_to([x, 1.0, 0])

        labels = [lab("atoms", xs[0]), lab("molecules", xs[1]), lab("ions", xs[2])]

        self.play(Write(title), run_time=0.7)
        self.play(Write(value), run_time=1.0)
        self.play(LaggedStart(*[GrowFromCenter(m) for m in icons],
                              lag_ratio=0.3), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in labels],
                              lag_ratio=0.3), run_time=1.0)
        self.play(Indicate(value, color=AMBER), run_time=0.8)
        self.fill()

    # 3 ---------------------------------------------------- molar mass
    def s_molar_mass(self):
        self.section("molar_mass")
        self._wipe()
        head = T("Molar mass", 80, AMBER, True).move_to([0, 6.0, 0])

        def card(formula, calc, result, color):
            return VGroup(T(formula, 96, WHITE, True),
                          T(calc, 54, DIM),
                          T(result, 80, color, True)).arrange(DOWN, buff=0.25)

        c1 = card("H₂O", "2 × 1 + 16", "18 g/mol", TEAL)
        c2 = card("CO₂", "12 + 2 × 16", "44 g/mol", CORAL)
        VGroup(c1, c2).arrange(DOWN, buff=0.8).next_to(head, DOWN, buff=0.7)

        self.play(Write(head), run_time=0.6)
        for c in (c1, c2):
            self.play(Write(c[0]), run_time=0.7)
            self.play(FadeIn(c[1], shift=UP * 0.2), run_time=0.6)
            self.play(Write(c[2]), run_time=0.7)
        self.fill()

    # 4a ------------------------------------------------ formula: mass
    def s_formula_mass(self):
        self.section("formula_mass")
        self._wipe()
        r1 = eq_row("mass", "m", "M", TEAL)
        r2 = eq_row("particles", "N", NA(72, AMBER), AMBER)
        r3 = eq_row("gas volume", "V", "22.4 L", CORAL, cond="273 K, 1 atm")
        rows = VGroup(r1, r2, r3).arrange(DOWN, buff=0.8, aligned_edge=LEFT)
        fit(rows).move_to([0, 2.2, 0])
        self._rows = (r1, r2, r3)
        self.play(FadeIn(r1, shift=RIGHT * 0.4), run_time=0.9)
        self.play(Indicate(r1[1], color=WHITE), run_time=0.8)
        self.fill()

    # 4b ------------------------------------------- formula: particles
    def s_formula_particles(self):
        self.section("formula_particles")
        r2 = self._rows[1]
        self.play(FadeIn(r2, shift=RIGHT * 0.4), run_time=0.9)
        self.play(Indicate(r2[1], color=WHITE), run_time=0.8)
        self.fill()

    # 4c --------------------------------------------- formula: volume
    def s_formula_volume(self):
        self.section("formula_volume")
        r3 = self._rows[2]
        self.play(FadeIn(r3, shift=RIGHT * 0.4), run_time=0.9)
        self.play(Indicate(r3[1], color=WHITE), run_time=0.8)
        self.fill()

    # 5 ------------------------------------------------- water: moles
    def s_water_moles(self):
        self.section("water_moles")
        self._wipe()
        self._w_head = T("36 g H₂O", 100, WHITE, True).move_to([0, 5.6, 0])
        self._w_n = T("n = 36 / 18 = 2 mol", 80, TEAL, True).move_to([0, 4.0, 0])
        self._w_mol = VGroup(
            T("molecules", 52, DIM),
            T("2 × 6.022 × 10²³", 80, AMBER),
            T("= 1.204 × 10²⁴", 96, AMBER, True),
        ).arrange(DOWN, buff=0.3).move_to([0, 1.4, 0])

        self.play(Write(self._w_head), run_time=0.8)
        self.play(Write(self._w_n), run_time=1.0)
        self.play(FadeIn(self._w_mol[0]), run_time=0.4)
        self.play(Write(self._w_mol[1]), run_time=1.0)
        self.play(Write(self._w_mol[2]), run_time=1.0)
        self.fill()

    # 6 ------------------------------------------------- water: atoms
    def s_water_atoms(self):
        self.section("water_atoms")
        self.play(FadeOut(self._w_mol), run_time=0.4)

        o = Circle(radius=0.4, color=CORAL, fill_opacity=0.9, stroke_width=0)
        h1 = Circle(radius=0.24, color=WHITE, fill_opacity=1, stroke_width=0)
        h2 = Circle(radius=0.24, color=WHITE, fill_opacity=1, stroke_width=0)
        h1.move_to(o.get_center() + np.array([-0.52, -0.4, 0]))
        h2.move_to(o.get_center() + np.array([0.52, -0.4, 0]))
        mol = VGroup(o, h1, h2).move_to([0, 2.5, 0])

        atoms = VGroup(
            T("atoms", 52, DIM),
            T("3 × 1.204 × 10²⁴", 80, CORAL),
            T("≈ 3.6 × 10²⁴", 96, CORAL, True),
        ).arrange(DOWN, buff=0.3).move_to([0, -0.2, 0])

        self.play(GrowFromCenter(mol), run_time=0.7)
        self.play(Indicate(mol, color=AMBER), run_time=0.8)
        self.play(FadeIn(atoms[0]), run_time=0.4)
        self.play(Write(atoms[1]), run_time=1.0)
        self.play(Write(atoms[2]), run_time=1.0)
        self.fill()

    # 7 ------------------------------------------------ gas: volume
    def s_gas_volume(self):
        self.section("gas_volume")
        self._wipe()
        cond = T("273 K, 1 atm", 56, DIM).move_to([0, 6.1, 0])
        b1 = Rectangle(width=3.4, height=3.4, color=CORAL, stroke_width=8)
        b1.move_to([-2.2, 3.7, 0])                      # y: 2.0 .. 5.4
        b2 = Rectangle(width=3.4, height=1.7, color=BLUE, stroke_width=8)
        b2.move_to([2.2, 2.85, 0])                      # y: 2.0 .. 3.7
        d1 = dots_in(b1, 28, 1)
        d2 = dots_in(b2, 14, 2)

        l1 = VGroup(T("22.4 L", 64, CORAL, True), T("1 mol", 56, WHITE))
        l1.arrange(DOWN, buff=0.15).next_to(b1, DOWN, buff=0.4)
        l2 = VGroup(T("11.2 L", 64, BLUE, True), T("0.5 mol", 56, WHITE))
        l2.arrange(DOWN, buff=0.15).next_to(b1, DOWN, buff=0.4)
        l2.set_x(2.2)

        self._g_boxes = VGroup(b2, d2, l2)
        self._g_label_pos = l2

        self.play(FadeIn(cond), run_time=0.4)
        self.play(Create(b1), run_time=0.8)
        self.play(LaggedStartMap(FadeIn, d1, lag_ratio=0.03), run_time=0.8)
        self.play(Write(l1), run_time=0.8)
        self.play(Create(b2), run_time=0.7)
        self.play(LaggedStartMap(FadeIn, d2, lag_ratio=0.05), run_time=0.6)
        self.play(Write(l2), run_time=0.8)
        self.fill()

    # 8 --------------------------------------------------- gas: mass
    def s_gas_mass(self):
        self.section("gas_mass")
        note = T("O₂, 32 g/mol", 56, DIM).move_to([0, -0.7, 0])
        calc = T("0.5 × 32 = 16 g", 90, TEAL, True).move_to([0, -1.9, 0])
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.6)
        self.play(Write(calc), run_time=1.0)
        self.play(Indicate(calc, color=AMBER), run_time=0.8)
        self.fill()

    # 9 ------------------------------------------------- equation
    def s_equation(self):
        self.section("equation")
        self._wipe()
        terms = [
            T("2H₂", 96, BLUE, True),
            T("+", 96, WHITE),
            T("O₂", 96, CORAL, True),
            T("→", 96, WHITE),
            T("2H₂O", 96, TEAL, True),
        ]
        eq = VGroup(*terms).arrange(RIGHT, buff=0.35)
        fit(eq).move_to([0, 5.0, 0])

        self._moles = []
        for term, txt, col in ((terms[0], "2 mol", BLUE),
                               (terms[2], "1 mol", CORAL),
                               (terms[4], "2 mol", TEAL)):
            lab = T(txt, 52, col, True).next_to(term, DOWN, buff=0.5)
            self._moles.append(lab)
        self._terms = terms

        self.play(Write(eq), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in self._moles],
                              lag_ratio=0.4), run_time=1.6)
        self.fill()

    # 10 ------------------------------------------------------ masses
    def s_masses(self):
        self.section("masses")
        grams = []
        for lab, txt in zip(self._moles, ("4 g", "32 g", "36 g")):
            grams.append(T(txt, 56, DIM).next_to(lab, DOWN, buff=0.35))
        self.play(LaggedStart(*[Write(g) for g in grams], lag_ratio=0.4),
                  run_time=1.6)
        self.play(*[Indicate(g, color=AMBER) for g in grams], run_time=0.9)
        self.fill()
