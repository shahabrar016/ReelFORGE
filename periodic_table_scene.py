"""
Modern periodic table - ReelForge scenes (three reels, one file).

  PeriodicTableStructure  -> periodic_table_1_structure.yaml
  PeriodicTableTrends     -> periodic_table_2_trends.yaml
  PeriodicTableTricks     -> periodic_table_3_tricks.yaml

Vertical frame 9 x 16, no LaTeX, no images. Uses the existing SyncedScene
from example_scene.py (section(name) / fill()).
Section names MUST match the `section:` keys in each yaml.
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
VIOLET = "#C792EA"
GREEN = "#7EE787"
DIM = "#8B949E"

BLOCK_COL = {"s": BLUE, "p": TEAL, "d": AMBER, "f": CORAL}

# ------------------------------------------------------- table geometry
CELL = 0.41
PITCH = 0.44
TOP_Y = 5.9


def gx(g):
    return (g - 9.5) * PITCH


def py(p):
    return TOP_Y - (p - 1) * PITCH


F_Y = [py(7) - 0.75, py(7) - 0.75 - PITCH]


def present(p):
    if p == 1:
        return [1, 18]
    if p in (2, 3):
        return [1, 2] + list(range(13, 19))
    return list(range(1, 19))


def block_of(p, g):
    if g in (1, 2):
        return "s"
    if g >= 13:
        return "p"
    return "d"


NONMETAL = {(1, 1), (1, 18), (2, 14), (2, 15), (2, 16), (2, 17), (2, 18),
            (3, 15), (3, 16), (3, 17), (3, 18), (4, 16), (4, 17), (4, 18),
            (5, 17), (5, 18), (6, 17), (6, 18), (7, 18)}
METALLOID = {(2, 13), (3, 14), (4, 14), (4, 15), (5, 15), (5, 16)}
GASES = {(1, 1), (1, 18), (2, 15), (2, 16), (2, 17), (2, 18), (3, 17),
         (3, 18), (4, 18), (5, 18), (6, 18)}
LIQUIDS = {(4, 17), (6, 12)}


# ---------------------------------------------------------------- helpers
def fit(m, w=8.2):
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


def T(s, size=80, color=WHITE, bold=False):
    return fit(Text(s, font_size=size, color=color,
                    weight=BOLD if bold else NORMAL))


def chip(s, color):
    rect = RoundedRectangle(width=0.68, height=0.68, corner_radius=0.1,
                            color=color, stroke_width=4)
    txt = Text(s, font_size=34, color=color, weight=BOLD).move_to(rect.get_center())
    return VGroup(rect, txt)


def tick(color=TEAL):
    return VMobject(color=color, stroke_width=10).set_points_as_corners(
        [[-0.3, 0, 0], [-0.1, -0.25, 0], [0.3, 0.3, 0]])


# ------------------------------------------------------------ shared base
class Common(SyncedScene):
    _lab = None
    _sub = None

    def _wipe(self):
        if self.mobjects:
            self.play(FadeOut(*self.mobjects), run_time=0.4)
        self._lab = None
        self._sub = None

    # ---- grid ----
    def _make_grid(self):
        self.cells = {}
        for p in range(1, 8):
            for g in present(p):
                self.cells[(p, g)] = Square(
                    side_length=CELL, stroke_width=2, color=DIM,
                    fill_opacity=0).move_to([gx(g), py(p), 0])
        self.fcells = []
        for r in range(2):
            for i in range(14):
                self.fcells.append(Square(
                    side_length=CELL, stroke_width=2, color=DIM,
                    fill_opacity=0).move_to([gx(3 + i), F_Y[r], 0]))
        self.glabs = [Text(str(g), font_size=26, color=DIM)
                      .move_to([gx(g), TOP_Y + 0.42, 0]) for g in range(1, 19)]
        self.plabs = [Text(str(p), font_size=26, color=DIM)
                      .move_to([gx(1) - 0.45, py(p), 0]) for p in range(1, 8)]

    def _all_cells(self):
        return list(self.cells.values()) + list(self.fcells)

    def _dim_instant(self):
        for c in self._all_cells():
            c.set_fill(DIM, 0.25).set_stroke(DIM)

    def _dim_all(self, rt=0.5):
        self.play(*[c.animate.set_fill(DIM, 0.25).set_stroke(DIM)
                    for c in self._all_cells()], run_time=rt)

    def _paint(self, cells, color, op=0.85, rt=0.8):
        self.play(*[c.animate.set_fill(color, op).set_stroke(color)
                    for c in cells], run_time=rt)

    def _say(self, text, color, sub=None, size=72):
        outs = [m for m in (self._lab, self._sub) if m is not None]
        if outs:
            self.play(FadeOut(*outs), run_time=0.2)
        self._lab = T(text, size, color, True).move_to([0, 0.9, 0])
        ins = [FadeIn(self._lab, shift=UP * 0.2)]
        self._sub = None
        if sub:
            self._sub = T(sub, 48, DIM).move_to([0, -0.1, 0])
            ins.append(FadeIn(self._sub, shift=UP * 0.2))
        self.play(*ins, run_time=0.4)

    # ---- mnemonic block ----
    def _mn_block(self, title, sentence, symbols, color, y_center, size=50):
        words = sentence.split()
        wobs = []
        for w, s in zip(words, symbols):
            k = 0
            for a, b in zip(w.lower(), s.lower()):
                if a == b:
                    k += 1
                else:
                    break
            k = max(1, k)
            wobs.append(Text(w, font_size=size, color=WHITE,
                             t2c={f"[0:{k}]": color}))
        rows = [VGroup(*wobs[i:i + 3]).arrange(RIGHT, buff=0.3)
                for i in range(0, len(wobs), 3)]
        sent = VGroup(*rows).arrange(DOWN, buff=0.2)
        fit(sent, 8.0)
        ttl = T(title, 40, DIM)
        chips = VGroup(*[chip(s, color) for s in symbols]).arrange(RIGHT, buff=0.08)
        fit(chips, 8.2)
        VGroup(ttl, sent, chips).arrange(DOWN, buff=0.3).move_to([0, y_center, 0])
        self.play(FadeIn(ttl), Write(sent), run_time=1.2)
        for w, c in zip(wobs, chips):
            self.play(Indicate(w, color=color, scale_factor=1.15),
                      GrowFromCenter(c), run_time=0.45)

    # ---- CTA ----
    def _cta(self):
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


# =====================================================================
#  REEL 1 - STRUCTURE
# =====================================================================
class PeriodicTableStructure(Common):
    def construct(self):
        self.camera.background_color = BG
        self.s_history()
        self.s_law()
        self.s_layout()
        self.s_blocks()
        self.s_periods()
        self.s_fam_s()
        self.s_fam_d()
        self.s_fam_p()
        self.s_classes()
        self.s_states()
        self._cta()

    # 1 -------------------------------------------------------- history
    def s_history(self):
        self.section("history")
        ys = [5.2, 3.2, 1.2]
        spec = [("Döbereiner", "triads", BLUE),
                ("Newlands", "octaves", TEAL),
                ("Mendeleev", "atomic mass, with gaps", AMBER)]
        line = Line([-3.6, ys[0], 0], [-3.6, ys[-1], 0], color=DIM, stroke_width=5)
        self.play(Create(line), run_time=0.5)
        for y, (name, sub, col) in zip(ys, spec):
            dot = Dot([-3.6, y, 0], radius=0.2, color=col)
            txt = VGroup(T(name, 68, col, True), T(sub, 46, DIM))
            txt.arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            txt.next_to(dot, RIGHT, buff=0.4)
            self.play(GrowFromCenter(dot), FadeIn(txt, shift=RIGHT * 0.3),
                      run_time=0.9)
        pred = T("predicted Ga and Ge", 56, AMBER).move_to([0, -0.6, 0])
        self.play(Write(pred), run_time=1.0)
        self.fill()

    # 2 ------------------------------------------------------------ law
    def s_law(self):
        self.section("law")
        self._wipe()
        m1 = T("Mendeleev", 56, DIM).move_to([0, 6.0, 0])
        mass = T("atomic mass", 84, CORAL, True).move_to([0, 4.9, 0])
        strike = Line(mass.get_left() + LEFT * 0.2, mass.get_right() + RIGHT * 0.2,
                      color=CORAL, stroke_width=10)
        m2 = T("Moseley", 56, DIM).move_to([0, 3.5, 0])
        num = T("atomic number, Z", 84, TEAL, True).move_to([0, 2.4, 0])
        wave = ParametricFunction(lambda t: np.array([t, 0.7 * np.sin(2.2 * t) + 0.1, 0]),
                                  t_range=[-3.9, 3.9], color=AMBER, stroke_width=8)
        axis = Arrow([-4.1, -0.6, 0], [4.1, -0.6, 0], buff=0, color=DIM,
                     stroke_width=5, max_tip_length_to_length_ratio=0.1)
        zlab = T("Z", 48, DIM).move_to([3.9, -1.1, 0])
        prop = T("property", 44, DIM).move_to([-3.2, 1.0, 0])
        wave.shift(UP * 0.0)

        self.play(FadeIn(m1), Write(mass), run_time=0.8)
        self.play(Create(strike), run_time=0.5)
        self.play(FadeIn(m2), Write(num), run_time=1.0)
        tk = tick().next_to(m2, RIGHT, buff=0.4)
        self.play(Create(tk), run_time=0.4)
        self.play(Create(axis), FadeIn(zlab), FadeIn(prop), run_time=0.6)
        self.play(Create(wave), run_time=1.6)
        self.fill()

    # 3 ---------------------------------------------------------- layout
    def s_layout(self):
        self.section("layout")
        self._wipe()
        self._make_grid()
        self.play(LaggedStartMap(FadeIn, VGroup(*self.glabs), lag_ratio=0.05),
                  run_time=0.9)
        for p in range(1, 8):
            row = VGroup(*[self.cells[(p, g)] for g in present(p)])
            self.play(LaggedStartMap(FadeIn, row, lag_ratio=0.04),
                      FadeIn(self.plabs[p - 1]), run_time=0.45)
        self.play(LaggedStartMap(FadeIn, VGroup(*self.fcells), lag_ratio=0.02),
                  run_time=0.9)
        total = T("118 elements", 76, TEAL, True).move_to([0, 0.8, 0])
        self.play(Write(total), run_time=0.9)
        self.play(Indicate(total, color=WHITE), run_time=0.7)
        self._total = total
        self.fill()

    # 4 ----------------------------------------------------------- blocks
    def s_blocks(self):
        self.section("blocks")
        self.play(FadeOut(self._total), run_time=0.3)
        s_cells = [c for (p, g), c in self.cells.items() if block_of(p, g) == "s"]
        p_cells = [c for (p, g), c in self.cells.items() if block_of(p, g) == "p"]
        d_cells = [c for (p, g), c in self.cells.items() if block_of(p, g) == "d"]
        self._paint(s_cells, BLUE)
        self._say("s block", BLUE, "groups 1, 2")
        self._paint(p_cells, TEAL)
        self._say("p block", TEAL, "groups 13 to 18")
        self._paint(d_cells, AMBER)
        self._say("d block", AMBER, "groups 3 to 12")
        self._paint(self.fcells, CORAL)
        self._say("f block", CORAL, "below the table")
        self.play(Indicate(self.cells[(1, 18)], color=WHITE, scale_factor=1.8),
                  run_time=0.9)
        self.fill()

    # 5 ----------------------------------------------------------- periods
    def s_periods(self):
        self.section("periods")
        self._wipe()
        counts = [2, 8, 8, 18, 18, 32, 32]
        fills = ["1s", "2s 2p", "3s 3p", "4s 3d 4p", "5s 4d 5p",
                 "6s 4f 5d 6p", "7s 5f 6d 7p"]
        cols = [BLUE, TEAL, TEAL, AMBER, AMBER, CORAL, CORAL]
        x0 = -2.7
        for i, (n, f, col) in enumerate(zip(counts, fills, cols)):
            y = 5.4 - 0.9 * i
            plab = T(str(i + 1), 36, DIM).move_to([-4.15, y, 0])
            cnt = T(str(n), 60, col, True).move_to([-3.4, y, 0])
            w = 0.12 * n
            bar = Rectangle(width=w, height=0.5, color=col, fill_opacity=0.85,
                            stroke_width=0).move_to([x0 + w / 2, y, 0])
            fl = T(f, 34, DIM).next_to(bar, RIGHT, buff=0.2)
            self.play(FadeIn(plab), Write(cnt), GrowFromEdge(bar, LEFT),
                      FadeIn(fl), run_time=0.6)
        self.fill()

    # 6 ------------------------------------------------------------ fam_s
    def s_fam_s(self):
        self.section("fam_s")
        self._wipe()
        self._make_grid()
        self._dim_instant()
        allg = VGroup(*self._all_cells(), *self.glabs, *self.plabs)
        self.play(FadeIn(allg), run_time=0.8)
        g1 = [self.cells[(p, 1)] for p in range(2, 8)]
        g2 = [self.cells[(p, 2)] for p in range(2, 8)]
        self._paint(g1, BLUE)
        self._say("alkali metals", BLUE, "not hydrogen")
        self._paint(g2, TEAL)
        self._say("alkaline earth metals", TEAL, "group 2")
        self.fill()

    # 7 ------------------------------------------------------------ fam_d
    def s_fam_d(self):
        self.section("fam_d")
        self._dim_all(0.4)
        d_cells = [c for (p, g), c in self.cells.items() if block_of(p, g) == "d"]
        self._paint(d_cells, AMBER)
        self._say("transition elements", AMBER, "groups 3 to 12")
        self._paint(self.fcells, CORAL)
        self._say("inner transition", CORAL, "lanthanoids, actinoids")
        self.fill()

    # 8 ------------------------------------------------------------ fam_p
    def s_fam_p(self):
        self.section("fam_p")
        self._dim_all(0.4)
        spec = [(13, "boron family", TEAL), (14, "carbon family", BLUE),
                (15, "nitrogen family", AMBER), (16, "oxygen family", CORAL),
                (17, "halogens", VIOLET), (18, "noble gases", GREEN)]
        subs = {15: "pnictogens", 16: "chalcogens"}
        for g, name, col in spec:
            cs = [c for (p, gg), c in self.cells.items() if gg == g]
            self._paint(cs, col, rt=0.5)
            self._say(name, col, subs.get(g))
        self.fill()

    # 9 ---------------------------------------------------------- classes
    def s_classes(self):
        self.section("classes")
        outs = [m for m in (self._lab, self._sub) if m is not None]
        if outs:
            self.play(FadeOut(*outs), run_time=0.3)
        self._lab = self._sub = None
        self._dim_all(0.4)
        metals = [c for k, c in self.cells.items()
                  if k not in NONMETAL and k not in METALLOID] + list(self.fcells)
        nonm = [self.cells[k] for k in NONMETAL]
        meta = [self.cells[k] for k in METALLOID]
        l1 = T("metals", 44, BLUE, True).move_to([-3.0, 0.9, 0])
        l2 = T("non-metals", 44, TEAL, True).move_to([0, 0.9, 0])
        l3 = T("metalloids", 44, AMBER, True).move_to([3.0, 0.9, 0])
        self._paint(metals, BLUE)
        self.play(FadeIn(l1, shift=UP * 0.2), run_time=0.4)
        self._paint(nonm, TEAL)
        self.play(FadeIn(l2, shift=UP * 0.2), run_time=0.4)
        self._paint(meta, AMBER)
        self.play(FadeIn(l3, shift=UP * 0.2), run_time=0.4)
        self._legend = [l1, l2, l3]
        self.fill()

    # 10 ------------------------------------------------------------ states
    def s_states(self):
        self.section("states")
        self.play(FadeOut(*self._legend), run_time=0.3)
        self._dim_all(0.4)
        gas = [self.cells[k] for k in GASES]
        liq = [self.cells[k] for k in LIQUIDS]
        l1 = T("11 gases", 56, TEAL, True).move_to([-2.2, 0.9, 0])
        l2 = T("2 liquids", 56, AMBER, True).move_to([2.2, 0.9, 0])
        self._paint(gas, TEAL)
        self.play(FadeIn(l1, shift=UP * 0.2), run_time=0.4)
        self._paint(liq, AMBER)
        self.play(FadeIn(l2, shift=UP * 0.2), run_time=0.4)
        self.play(*[Indicate(c, color=WHITE, scale_factor=1.8) for c in liq],
                  run_time=0.9)
        self.fill()


# =====================================================================
#  REEL 2 - TRENDS
# =====================================================================
class PeriodicTableTrends(Common):
    def construct(self):
        self.camera.background_color = BG
        self.s_radius_period()
        self.s_radius_group()
        self.s_trends()
        self.s_ie_exc()
        self.s_eg_exc()
        self.s_diagonal()
        self._cta()

    # 1 ------------------------------------------------- radius: period
    def s_radius_period(self):
        self.section("radius_period")
        data = [("Li", 152), ("Be", 111), ("B", 88), ("C", 77),
                ("N", 74), ("O", 66), ("F", 64)]
        head = T("atomic radius (pm)", 56, DIM).move_to([0, 6.2, 0])
        self.play(FadeIn(head), run_time=0.4)
        circles, vals = [], []
        for i, (s, v) in enumerate(data):
            x = -3.3 + 1.1 * i
            r = v * 0.0033
            c = Circle(radius=r, color=BLUE, fill_opacity=0.35, stroke_width=5)
            c.move_to([x, 4.6, 0])
            t = Text(s, font_size=30, color=WHITE, weight=BOLD).move_to(c.get_center())
            val = T(str(v), 36, BLUE, True).move_to([x, 3.6, 0])
            circles.append(VGroup(c, t))
            vals.append(val)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in circles],
                              lag_ratio=0.25), run_time=2.2)
        self.play(LaggedStart(*[FadeIn(v) for v in vals], lag_ratio=0.1),
                  run_time=0.8)
        arr = Arrow([-3.6, 2.4, 0], [3.6, 2.4, 0], buff=0, color=AMBER,
                    stroke_width=8)
        why = T("nuclear charge increases", 52, AMBER).move_to([0, 1.5, 0])
        res = T("radius decreases", 72, TEAL, True).move_to([0, 0.2, 0])
        self.play(Create(arr), FadeIn(why), run_time=0.8)
        self.play(Write(res), run_time=0.9)
        self.fill()

    # 2 --------------------------------------------------- radius: group
    def s_radius_group(self):
        self.section("radius_group")
        self._wipe()
        data = [("Li", 152), ("Na", 186), ("K", 231), ("Rb", 244), ("Cs", 262)]
        head = T("atomic radius (pm)", 56, DIM).move_to([0, 6.5, 0])
        self.play(FadeIn(head), run_time=0.4)
        y = 6.0
        for s, v in data:
            r = v * 0.0027
            cy = y - r
            c = Circle(radius=r, color=BLUE, fill_opacity=0.35, stroke_width=5)
            c.move_to([-1.5, cy, 0])
            t = Text(s, font_size=38, color=WHITE, weight=BOLD).move_to(c.get_center())
            val = T(str(v), 48, BLUE, True).move_to([1.3, cy, 0])
            self.play(GrowFromCenter(c), FadeIn(t), FadeIn(val), run_time=0.7)
            y = cy - r - 0.2
        arr = Arrow([3.6, 5.8, 0], [3.6, -0.2, 0], buff=0, color=AMBER,
                    stroke_width=8)
        why = T("new shell each period", 50, AMBER).move_to([0, -1.2, 0])
        res = T("radius increases", 68, TEAL, True).move_to([0, -2.3, 0])
        self.play(Create(arr), FadeIn(why), run_time=0.8)
        self.play(Write(res), run_time=0.9)
        self.fill()

    # 3 --------------------------------------------------------- trends
    def s_trends(self):
        self.section("trends")
        self._wipe()
        h1 = T("across", 46, AMBER, True).move_to([1.2, 5.9, 0])
        h2 = T("down", 46, AMBER, True).move_to([3.4, 5.9, 0])
        self.play(FadeIn(h1), FadeIn(h2), run_time=0.5)

        def arrow(up):
            col = TEAL if up else CORAL
            a = Arrow([0, -0.35, 0], [0, 0.35, 0] if up else [0, 0.35, 0],
                      buff=0, color=col, stroke_width=10,
                      max_tip_length_to_length_ratio=0.5)
            if not up:
                a = Arrow([0, 0.35, 0], [0, -0.35, 0], buff=0, color=col,
                          stroke_width=10, max_tip_length_to_length_ratio=0.5)
            return a

        rows = [("radius", False, True),
                ("ionization enthalpy", True, False),
                ("electronegativity", True, False),
                ("metallic character", False, True),
                ("electron gain", None, None)]
        for i, (lab, a_up, d_up) in enumerate(rows):
            y = 4.6 - 1.15 * i
            tl = T(lab, 40, WHITE)
            tl.move_to([-4.2 + tl.width / 2, y, 0])
            if a_up is None:
                c1 = T("more −ve", 32, TEAL, True).move_to([1.2, y, 0])
                c2 = T("less −ve", 32, CORAL, True).move_to([3.4, y, 0])
                self.play(FadeIn(tl), FadeIn(c1), FadeIn(c2), run_time=0.6)
            else:
                c1 = arrow(a_up).move_to([1.2, y, 0])
                c2 = arrow(d_up).move_to([3.4, y, 0])
                self.play(FadeIn(tl), GrowArrow(c1), GrowArrow(c2), run_time=0.6)
        self.fill()

    # 4 ------------------------------------------------------- IE exceptions
    def s_ie_exc(self):
        self.section("ie_exc")
        self._wipe()
        data = [("Li", 520), ("Be", 899), ("B", 801), ("C", 1086),
                ("N", 1402), ("O", 1314), ("F", 1681), ("Ne", 2081)]
        head = T("ionization enthalpy (kJ/mol)", 48, DIM).move_to([0, 6.0, 0])
        self.play(FadeIn(head), run_time=0.4)
        base = 1.0
        bars, labels = [], []
        for i, (s, v) in enumerate(data):
            x = (i - 3.5) * 0.95
            h = v * 0.0019
            col = CORAL if s in ("B", "O") else (AMBER if s in ("Be", "N") else TEAL)
            bar = Rectangle(width=0.72, height=h, color=col, fill_opacity=0.85,
                            stroke_width=0).move_to([x, base + h / 2, 0])
            sl = T(s, 40, col, True).move_to([x, base - 0.45, 0])
            vl = T(str(v), 28, DIM).move_to([x, base + h + 0.3, 0])
            bars.append(bar)
            labels.append((sl, vl))
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars],
                              lag_ratio=0.15),
                  LaggedStart(*[FadeIn(l[0]) for l in labels], lag_ratio=0.15),
                  run_time=2.2)
        self.play(LaggedStart(*[FadeIn(l[1]) for l in labels], lag_ratio=0.08),
                  run_time=0.8)
        self.play(Indicate(bars[2], color=WHITE), Indicate(bars[5], color=WHITE),
                  run_time=0.9)
        self.play(Indicate(bars[1], color=WHITE), Indicate(bars[4], color=WHITE),
                  run_time=0.9)
        self.fill()

    # 5 ----------------------------------------------------- EG exception
    def s_eg_exc(self):
        self.section("eg_exc")
        self._wipe()
        head = T("electron gain enthalpy (kJ/mol)", 46, DIM).move_to([0, 6.0, 0])
        cf = Circle(radius=0.58, color=CORAL, fill_opacity=0.35, stroke_width=6)
        cf.move_to([-2.0, 4.2, 0])
        tf = Text("F", font_size=56, color=WHITE, weight=BOLD).move_to(cf.get_center())
        cc = Circle(radius=0.9, color=TEAL, fill_opacity=0.35, stroke_width=6)
        cc.move_to([2.0, 4.2, 0])
        tc = Text("Cl", font_size=56, color=WHITE, weight=BOLD).move_to(cc.get_center())
        vf = T("−328", 76, CORAL, True).move_to([-2.0, 2.5, 0])
        vc = T("−349", 76, TEAL, True).move_to([2.0, 2.5, 0])
        tag = T("most negative", 54, AMBER, True).move_to([2.0, 1.3, 0])

        self.play(FadeIn(head), run_time=0.4)
        self.play(GrowFromCenter(cf), FadeIn(tf), GrowFromCenter(cc), FadeIn(tc),
                  run_time=1.0)
        self.play(Write(vf), Write(vc), run_time=1.0)
        self.play(FadeIn(tag, shift=UP * 0.2), run_time=0.6)
        self.play(Indicate(vc, color=WHITE), run_time=0.8)
        self.fill()

    # 6 ------------------------------------------------------- diagonal
    def s_diagonal(self):
        self.section("diagonal")
        self._wipe()
        syms = [["Li", "Be", "B", "C"], ["Na", "Mg", "Al", "Si"]]
        tiles = {}
        for r, row in enumerate(syms):
            for c, s in enumerate(row):
                x = (c - 1.5) * 1.8
                y = 4.6 - 1.8 * r
                rect = RoundedRectangle(width=1.5, height=1.5, corner_radius=0.2,
                                        color=DIM, stroke_width=5)
                t = Text(s, font_size=56, color=WHITE, weight=BOLD)
                g = VGroup(rect, t).move_to([x, y, 0])
                tiles[(r, c)] = g
        self.play(LaggedStart(*[FadeIn(tiles[(0, c)]) for c in range(4)],
                              lag_ratio=0.15), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(tiles[(1, c)]) for c in range(4)],
                              lag_ratio=0.15), run_time=1.0)
        pairs = [((0, 0), (1, 1), BLUE), ((0, 1), (1, 2), TEAL),
                 ((0, 2), (1, 3), AMBER)]
        for a, b, col in pairs:
            ln = Line(tiles[a].get_center(), tiles[b].get_center(), buff=0.85,
                      color=col, stroke_width=10)
            self.play(Create(ln),
                      tiles[a][0].animate.set_color(col),
                      tiles[b][0].animate.set_color(col), run_time=0.9)
        self.fill()


# =====================================================================
#  REEL 3 - TRICKS
# =====================================================================
class PeriodicTableTricks(Common):
    def construct(self):
        self.camera.background_color = BG
        self.s_trick_arrow()
        self.s_trick_len()
        self.s_trick_valence()
        self.s_mn_20a()
        self.s_mn_20b()
        self.s_mn_g1()
        self.s_mn_g2()
        self.s_mn_g3()
        self.s_mn_d()
        self.s_mn_ie()
        self._cta()

    # 1 ----------------------------------------------------- trick arrow
    def s_trick_arrow(self):
        self.section("trick_arrow")
        c = np.array([0, 3.0, 0])
        frame = Rectangle(width=5, height=5, color=DIM, stroke_width=6).move_to(c)
        a = Arrow(c + np.array([-1.0, -1.8, 0]), c + np.array([1.8, 1.0, 0]),
                  buff=0, color=TEAL, stroke_width=12)
        b = Arrow(c + np.array([1.0, 1.8, 0]), c + np.array([-1.8, -1.0, 0]),
                  buff=0, color=CORAL, stroke_width=12)
        f = T("F", 90, TEAL, True).move_to([3.3, 5.7, 0])
        fr = T("Fr", 90, CORAL, True).move_to([-3.2, 0.3, 0])
        up_t = VGroup(T("IE", 48, TEAL, True), T("EN", 48, TEAL, True))
        up_t.arrange(DOWN, buff=0.15).move_to([3.4, 4.3, 0])
        dn_t = VGroup(T("radius", 44, CORAL, True), T("metallic", 44, CORAL, True))
        dn_t.arrange(DOWN, buff=0.15).move_to([-3.2, 1.6, 0])

        self.play(Create(frame), run_time=0.6)
        self.play(GrowArrow(a), Write(f), run_time=1.0)
        self.play(FadeIn(up_t, shift=UP * 0.2), run_time=0.7)
        self.play(GrowArrow(b), Write(fr), run_time=1.0)
        self.play(FadeIn(dn_t, shift=UP * 0.2), run_time=0.7)
        self.fill()

    # 2 -------------------------------------------------------- trick len
    def s_trick_len(self):
        self.section("trick_len")
        self._wipe()
        head = T("n: 1, 2, 2, 3, 3, 4, 4", 64, AMBER, True).move_to([0, 6.2, 0])
        self.play(Write(head), run_time=0.9)
        ns = [1, 2, 2, 3, 3, 4, 4]
        cols = [BLUE, TEAL, TEAL, AMBER, AMBER, CORAL, CORAL]
        for p, (n, col) in enumerate(zip(ns, cols), start=1):
            y = 5.0 - 0.8 * (p - 1)
            lab = T(f"period {p}", 40, DIM).move_to([-2.9, y, 0])
            expr = T(f"2 × {n}² = {2 * n * n}", 64, col, True).move_to([1.4, y, 0])
            self.play(FadeIn(lab), Write(expr), run_time=0.6)
        self.fill()

    # 3 ---------------------------------------------------- trick valence
    def s_trick_valence(self):
        self.section("trick_valence")
        self._wipe()
        top = T("period = number of shells", 60, AMBER, True).move_to([0, 5.8, 0])
        self.play(Write(top), run_time=1.0)
        groups = [1, 2, 13, 14, 15, 16, 17, 18]
        vals = [1, 2, 3, 4, 5, 6, 7, 8]
        gl = T("group", 40, DIM).move_to([0, 4.4, 0])
        self.play(FadeIn(gl), run_time=0.3)
        gs, cs = [], []
        for i, (g, v) in enumerate(zip(groups, vals)):
            x = (i - 3.5) * 1.0
            gs.append(T(str(g), 40, DIM, True).move_to([x, 3.7, 0]))
            col = BLUE if g in (1, 2) else TEAL
            cs.append(chip(str(v), col).move_to([x, 2.7, 0]))
        self.play(LaggedStart(*[FadeIn(g) for g in gs], lag_ratio=0.1),
                  run_time=0.9)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in cs], lag_ratio=0.2),
                  run_time=1.6)
        vl = T("valence electrons", 56, TEAL, True).move_to([0, 1.3, 0])
        self.play(Write(vl), run_time=0.9)
        self.fill()

    # 4 --------------------------------------------------------- mn 20a
    def s_mn_20a(self):
        self.section("mn_20a")
        self._wipe()
        self._mn_block("H to Ne", "Happy Hens Like Beans But Cats Never Offer Fresh Needles",
                       ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne"],
                       AMBER, 3.6)
        self.fill()

    # 5 --------------------------------------------------------- mn 20b
    def s_mn_20b(self):
        self.section("mn_20b")
        self._wipe()
        self._mn_block("Na to Ca",
                       "Nana Magically Allows Silly Pigs Sing Clapping Arrogantly Kicking Cats",
                       ["Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca"],
                       TEAL, 3.6)
        self.fill()

    # 6 ----------------------------------------------------------- mn g1
    def s_mn_g1(self):
        self.section("mn_g1")
        self._wipe()
        self._mn_block("group 1", "Little Nasty Kids Rob Cute Frogs",
                       ["Li", "Na", "K", "Rb", "Cs", "Fr"], BLUE, 4.8)
        self._mn_block("group 2", "Beautiful Magic Carpets Sail By Rainbows",
                       ["Be", "Mg", "Ca", "Sr", "Ba", "Ra"], TEAL, 1.3)
        self.fill()

    # 7 ----------------------------------------------------------- mn g2
    def s_mn_g2(self):
        self.section("mn_g2")
        self._wipe()
        self._mn_block("group 15", "New Parents Are Super Busy",
                       ["N", "P", "As", "Sb", "Bi"], AMBER, 4.8)
        self._mn_block("group 16", "Ocean Shells Seem To Pop",
                       ["O", "S", "Se", "Te", "Po"], CORAL, 1.3)
        self.fill()

    # 8 ----------------------------------------------------------- mn g3
    def s_mn_g3(self):
        self.section("mn_g3")
        self._wipe()
        self._mn_block("group 17", "Fat Clowns Bring Ice Always",
                       ["F", "Cl", "Br", "I", "At"], VIOLET, 4.8)
        self._mn_block("group 18", "Hey Nerds Are Kids Xtra Rowdy",
                       ["He", "Ne", "Ar", "Kr", "Xe", "Rn"], GREEN, 1.3)
        self.fill()

    # 9 ------------------------------------------------------------ mn d
    def s_mn_d(self):
        self.section("mn_d")
        self._wipe()
        self._mn_block("first transition series",
                       "Scientists Tickled Vampires Crazy Men Fought Cops Nicely Cut Zeros",
                       ["Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"],
                       AMBER, 3.6)
        self.fill()

    # 10 ----------------------------------------------------------- mn IE
    def s_mn_ie(self):
        self.section("mn_ie")
        self._wipe()
        self._mn_block("ionization enthalpy, period 2",
                       "Little Boys Bring Cats Only Need Food Nectar",
                       ["Li", "B", "Be", "C", "O", "N", "F", "Ne"], CORAL, 4.0)
        arr = Arrow([-3.3, 1.2, 0], [3.3, 1.2, 0], buff=0, color=AMBER,
                    stroke_width=8)
        txt = T("increasing", 52, AMBER, True).move_to([0, 0.3, 0])
        self.play(Create(arr), FadeIn(txt), run_time=0.8)
        self.fill()
