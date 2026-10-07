"""ReelForge: Rutherford's nuclear atom. 1080x1920, 30 fps, no LaTeX.
Use prepare_rutherford.py to inherit your working voice configuration.
"""
from manim import *
import numpy as np

try:
    from example_scene import SyncedScene
except ModuleNotFoundError as exc:
    if exc.name != "example_scene":
        raise
    class SyncedScene(Scene):
        """Standalone silent preview; real ReelForge uses its own timing class."""
        def section(self, name):
            self.next_section(name)
            self._beat_start = self.time
        def fill(self):
            self.wait(max(0.1, 8.0 - (self.time - self._beat_start)))

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30
config.background_color = "#0B1220"

INK = "#F3F6FC"
MUTED = "#B1BED3"
GOLD = "#FFD166"
CYAN = "#57D9E8"
RED = "#FF7F87"

NARRATION = [
    ("hook", "An atom is mostly empty space. Rutherford's nuclear model explained a surprising result: a few alpha particles turned back."),
    ("experiment", "Geiger and Marsden fired positively charged alpha particles at thin gold foil. A fluorescent screen detected where the particles went."),
    ("observations", "Most passed almost straight through. Some were deflected. A very small fraction scattered backward, through angles greater than ninety degrees."),
    ("empty_space", "Most particles passed through because an atom's mass and positive charge are concentrated in a tiny region, leaving mostly empty space."),
    ("repulsion", "An alpha particle and the nucleus are both positive. Electrical repulsion bends its path. A closer approach can produce a larger deflection."),
    ("nucleus", "Rutherford proposed a tiny, dense, positive nucleus containing almost all the atom's mass, with negative electrons outside it."),
    ("scale", "In modern measurements, atomic radii are roughly ten thousand to a hundred thousand times nuclear radii. Our nucleus is greatly enlarged."),
    ("limits", "This historical model did not explain atomic stability or discrete spectral lines. Modern quantum theory describes electrons with orbitals, not fixed planetary paths."),
    ("recap", "Remember: mostly empty space, a tiny positive nucleus, and electrons outside. Rare backward scattering was the crucial clue to the nucleus."),
]


def label(words, y, size=48, color=INK, width=7.7):
    obj = Text(words, font="DejaVu Sans", font_size=size, color=color,
               line_spacing=1.15)
    if obj.width > width:
        obj.scale_to_fit_width(width)
    return obj.move_to([0, y, 0])


def coulomb_points(impact):
    """RK4 repulsive inverse-square scattering in dimensionless units.
    Heavy, stationary point nucleus; no hard-sphere collision. Rendering only.
    Every case uses the same incoming velocity and force constant.
    """
    state = np.array([-3.6, impact, 1.8, 0.0], dtype=float)
    dt, strength = 0.008, 1.1
    points = []
    def deriv(s):
        r = s[:2]
        return np.r_[s[2:], strength * r / np.linalg.norm(r)**3]
    for _ in range(1800):
        x, y = state[:2]
        if points and (abs(x) > 3.65 or abs(y) > 2.05):
            break
        points.append([x, y + 1.65, 0])
        a = deriv(state)
        b = deriv(state + dt*a/2)
        c = deriv(state + dt*b/2)
        d = deriv(state + dt*c)
        state += dt*(a+2*b+2*c+d)/6
    return points


class RutherfordAtom(SyncedScene):
    def begin(self, name, title, subtitle):
        self.section(name)
        self.clear()
        self.add(label("RUTHERFORD  /  1911", 6.45, 30, CYAN))
        self.add(label(title, 5.45, 62))
        self.add(label(subtitle, 4.48, 32, MUTED))
        index = [x[0] for x in NARRATION].index(name)
        self.add(VGroup(*[
            Line([-.96+i*.24, -2.8, 0], [-.80+i*.24, -2.8, 0],
                 color=CYAN if i <= index else "#344055", stroke_width=5)
            for i in range(9)]))

    def atom(self):
        center = np.array([0, 1.55, 0])
        edge = DashedVMobject(Circle(radius=2.15, color=MUTED), num_dashes=44).move_to(center)
        core = Dot(center, radius=.20, color=GOLD)
        plus = Text("+", font_size=26, color="#0B1220").move_to(center)
        electrons = VGroup()
        for angle, radius in [(25, 1.55), (150, 1.85), (265, 1.65)]:
            p = center + radius*np.array([np.cos(angle*DEGREES), np.sin(angle*DEGREES), 0])
            electrons.add(Dot(p, radius=.12, color=CYAN), Text("−", font_size=20, color="#0B1220").move_to(p))
        return VGroup(edge, core, plus, electrons)

    def construct(self):
        self.begin("hook", "Mostly empty space", "What did the gold foil experiment reveal?")
        atom = self.atom()
        self.play(FadeIn(atom), run_time=1.2)
        self.play(FadeIn(label("A tiny centre. A surprising clue.", -1.35, 39)), run_time=.6)
        self.add(label("Schematic • nucleus enlarged", -2.15, 27, MUTED))
        self.fill()

        self.begin("experiment", "The experiment", "Geiger & Marsden • Rutherford's laboratory")
        foil = Rectangle(width=.13, height=3.0, color=GOLD, fill_opacity=.8).move_to([0,1.3,0])
        source = RoundedRectangle(width=1.15, height=.8, corner_radius=.12, color=CYAN).move_to([-2.95,1.3,0])
        screen = Arc(radius=2.25, start_angle=-PI/2, angle=PI, color=MUTED).move_arc_center_to([0,1.3,0])
        self.play(Create(foil), Create(source), Create(screen), run_time=.8)
        self.add(label("Alpha source (+)", 3.5, 31).shift(LEFT*2.2))
        self.add(label("Gold foil", -.7, 31, GOLD))
        self.add(label("Fluorescent screen", -1.4, 32, MUTED))
        beam = Arrow([-2.3,1.3,0],[-.18,1.3,0], color=CYAN, buff=0)
        self.play(GrowArrow(beam), run_time=.6)
        self.play(MoveAlongPath(Dot([-2.25,1.3,0], color=CYAN), Line([-2.25,1.3,0],[2.25,1.3,0])), run_time=1.0)
        self.play(Flash([2.25,1.3,0], color=GOLD, flash_radius=.2), run_time=.5)
        self.add(label("Apparatus schematic • not to scale", -2.15, 26, MUTED))
        self.fill()

        self.begin("observations", "Three observations", "Directions shown schematically, not percentages")
        for y, words, color, endpoint in [
            (3.0,"MOST: nearly straight",CYAN,[3.0,2.55,0]),
            (1.15,"SOME: deflected",GOLD,[2.7,1.1,0]),
            (-.70,"VERY FEW: backward",RED,[-1.8,-1.9,0])]:
            self.add(label(words,y,36,color))
            origin = np.array([0,y-.45,0])
            self.play(Create(Line([-3,y-.45,0], origin, color=color)),
                      GrowArrow(Arrow(origin, endpoint, color=color, buff=0)), run_time=.65)
        self.fill()

        self.begin("empty_space", "Mostly empty space", "The nucleus occupies very little of the atom")
        atom = self.atom()
        self.play(FadeIn(atom), run_time=.7)
        paths = VGroup(*[Arrow([-3.5,y,0],[3.5,y,0],color=CYAN,buff=0,stroke_width=3)
                         for y in [.30,2.90]])
        self.play(LaggedStart(*[GrowArrow(p) for p in paths], lag_ratio=.3),run_time=1.2)
        self.add(label("Most alpha particles miss the tiny nucleus", -1.25, 35))
        self.add(label("Near-straight paths • nucleus enlarged", -2.1, 26, MUTED))
        self.fill()

        self.begin("repulsion", "Repulsion bends paths", "Positive alpha particle ↔ positive nucleus")
        core = VGroup(Dot([0,1.65,0],radius=.16,color=GOLD), Text("+",font_size=23,color=BLACK).move_to([0,1.65,0]))
        self.add(core)
        for impact,color in [(1.1,CYAN),(.42,GOLD),(.07,RED)]:
            path=VMobject(color=color,stroke_width=4).set_points_as_corners(coulomb_points(impact))
            particle=Dot(path.get_start(),radius=.085,color=color)
            self.add(particle)
            self.play(Create(path),MoveAlongPath(particle,path),run_time=1.3,rate_func=linear)
        self.add(label("Smaller offset → larger deflection", -1.05, 36))
        self.add(label("Curves: repulsive Coulomb force", -1.72, 29, MUTED))
        self.add(label("Same incoming speed • nucleus enlarged", -2.22, 26, MUTED))
        self.fill()

        self.begin("nucleus", "The nuclear atom", "Rutherford's historical model")
        self.play(FadeIn(self.atom()),run_time=.8)
        self.add(label("+ nucleus: almost all the mass", -.95, 36, GOLD))
        self.add(label("− electrons: outside the nucleus", -1.62, 36, CYAN))
        self.add(label("Illustrative electrons • no fixed shells implied", -2.23, 25, MUTED))
        self.fill()

        self.begin("scale", "How tiny is tiny?", "Modern approximate sizes • vary by atom")
        self.play(FadeIn(label("Atomic radius",3.05,42,CYAN)),
                  FadeIn(label("~10⁻¹⁰ m",2.25,66,CYAN)),run_time=.7)
        self.play(FadeIn(label("Nuclear radius",.98,42,GOLD)),
                  FadeIn(label("~10⁻¹⁵ to 10⁻¹⁴ m",.15,58,GOLD)),run_time=.7)
        self.add(label("Radius ratio: ~10,000–100,000", -1.15, 37))
        self.add(label("A true-scale nucleus would be invisible here", -2.03, 27, MUTED))
        self.fill()

        self.begin("limits", "What it could not explain", "An essential step, not the final theory")
        for y,heading,detail in [
            (3.0,"Atomic stability","Classical orbiting charges radiate energy"),
            (1.1,"Discrete spectral lines","Only particular wavelengths are observed"),
            (-.8,"Modern picture","Quantum orbitals, not fixed planetary paths")]:
            self.play(FadeIn(label(heading,y,43,GOLD)),
                      FadeIn(label(detail,y-.65,30,MUTED)),run_time=.7)
        self.fill()

        self.begin("recap", "Remember three things", "The evidence changed our picture of matter")
        for y,words,color in [(3.1,"01  Mostly empty space",CYAN),
                              (1.6,"02  Tiny positive nucleus",GOLD),
                              (.1,"03  Electrons outside",CYAN)]:
            self.play(FadeIn(label(words,y,46,color)),run_time=.65)
        self.add(label("Key clue: rare backward scattering", -1.4, 37))
        self.add(label("Historical model • diagrams not to scale", -2.2, 26, MUTED))
        self.fill()
