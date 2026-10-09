"""Narration-paced Rutherford lesson. Run through reelforge.py build rutherford.yaml.
Text is Pango-rendered (no LaTeX). No external image/video assets.
"""
import os
import numpy as np
from manim import *
from synced_scene import SyncedScene

# Preview dimensions are an explicit opt-in; production is full HD vertical.
config.pixel_width = int(os.environ.get('RF_PREVIEW_WIDTH', '1080'))
config.pixel_height = int(os.environ.get('RF_PREVIEW_HEIGHT', '1920'))
config.frame_width = 9
config.frame_height = 16
config.background_color = '#080F1D'
BG='#080F1D'; WHITE_INK='#F1F5FC'; DIM='#AABBD1'
TEAL='#55E1DF'; GOLD='#FFD16B'; CORAL='#FF7C89'; BLUE='#648CFF'


def text(value, y=0, size=46, color=WHITE_INK, width=7.6):
    result=Text(value,font='DejaVu Sans',font_size=size,color=color,line_spacing=1.15)
    if result.width > width: result.scale_to_fit_width(width)
    return result.move_to([0,y,0])


def nucleus(center, radius=.22):
    return VGroup(Circle(radius=radius*1.8,stroke_opacity=0,fill_color=GOLD,fill_opacity=.08),
                  Dot(radius=radius,color=GOLD),Text('+',font_size=29,color=BG)).move_to(center)


def coulomb_path(impact, center=np.array([0,1.5,0])):
    """Heavy fixed nucleus, repulsive inverse-square force, identical incident speed.
    No hard collision. Diagram uses dimensionless units and an enlarged nucleus.
    """
    state=np.array([-3.65,impact,1.8,0.])
    points=[]
    def f(s):
        r=s[:2]
        return np.r_[s[2:],1.1*r/np.linalg.norm(r)**3]
    for _ in range(2000):
        x,y=state[:2]
        if points and (abs(x)>3.7 or abs(y)>2.4): break
        points.append(center+np.array([x,y,0]))
        dt=.008
        a=f(state);b=f(state+dt*a/2);c=f(state+dt*b/2);d=f(state+dt*c)
        state+=dt*(a+2*b+2*c+d)/6
    path=VMobject().set_points_as_corners(points)
    path.physics_points=np.array(points)
    path.physics_duration=(len(points)-1)*.008
    return path


class NumberText(Text):
    def __init__(self, value, **kwargs):
        super().__init__(value, font='DejaVu Sans', **kwargs)


class RutherfordAtom(SyncedScene):
    def start(self,name,number,title,kicker):
        self.section(name)
        # Remove old updater objects as well as old labels at the section boundary.
        old=list(self.mobjects)
        if old:
            for mob in old: mob.clear_updaters(recursive=True)
            self.play(*[FadeOut(mob) for mob in old],run_time=.18)
        self.add(text('THE ATOM  /  RUTHERFORD',6.4,29,TEAL))
        self.add(text(title,5.5,64))
        self.add(text(kicker,4.63,33,DIM))
        self.add(text(f'{number:02d} / 09',-2.85,24,DIM))

    def stream(self,path,color=TEAL,count=5,period=3.0):
        """Repeated particles with fading tails; motion continues during narration."""
        # Precompute arc-length lookup once; avoid traversing hundreds of
        # Coulomb curve segments for every tail dot on every rendered frame.
        if 'physics_points' in path.__dict__:
            # RK4 samples have equal time steps: preserve slowing near the
            # nucleus and equal incident speeds across the three trajectories.
            anchors=path.physics_points
            fractions=np.linspace(0,1,len(anchors))
            period=path.physics_duration
        else:
            anchors=np.array(path.get_anchors())
            lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(anchors,axis=0),axis=1))]
            fractions=lengths/lengths[-1]
        def point(alpha):
            return np.array([np.interp(alpha,fractions,anchors[:,axis]) for axis in range(3)])
        packets=VGroup()
        for index in range(count):
            packet=VGroup(*[Dot(radius=.052 if j else .085,color=color)
                            .set_opacity(1-j/6) for j in range(5)])
            packet.phase=index/count
            def update(m,dt,cycle=period):
                m.phase=(m.phase+dt/cycle)%1
                for j,dot in enumerate(m):
                    dot.move_to(point((m.phase-j*.008)%1))
            packet.add_updater(update)
            update(packet,0)
            packets.add(packet)
        self.add(packets)
        return packets

    def atom(self):
        center=np.array([0,1.25,0])
        boundary=DashedVMobject(Circle(radius=2.65,color=DIM,stroke_width=2),num_dashes=64).move_to(center)
        core=nucleus(center)
        electrons=VGroup()
        for angle,r in [(35,2.05),(163,2.25),(276,1.95)]:
            p=center+r*np.array([np.cos(angle*DEGREES),np.sin(angle*DEGREES),0])
            electrons.add(VGroup(Dot(p,radius=.14,color=TEAL),
                                 Text('−',font_size=27,color=BG).move_to(p)))
        return VGroup(boundary,core,electrons)

    def note(self,value,y=-2.1,color=DIM):
        mob=text(value,y,30,color)
        self.play(FadeIn(mob,shift=UP*.08),run_time=.25)
        return mob

    def construct(self):
        self.start('hook',1,'Mostly empty space','A tiny nucleus changed everything')
        atom=self.atom()
        self.play(Create(atom[0]),FadeIn(atom[1:]),run_time=.7)
        self.note('Atom schematic • nucleus enlarged')
        for y in [-.6,3.1]:
            self.stream(Line([-3.7,y,0],[3.7,y,0]),TEAL,count=3,period=3)
        self.at('a few',.64)
        curve=coulomb_path(.10,np.array([0,1.25,0])).set_stroke(CORAL,4)
        self.play(Create(curve),run_time=.7)
        self.stream(curve,CORAL,count=1,period=2.5)
        self.fill()

        self.start('experiment',2,'Gold foil experiment','Geiger & Marsden • Rutherford’s laboratory')
        foil=Rectangle(width=.13,height=3.65,stroke_color=GOLD,fill_color=GOLD,fill_opacity=.85).move_to([0,1.35,0])
        emitter=RoundedRectangle(width=.85,height=.85,corner_radius=.12,color=TEAL,fill_opacity=.12).move_to([-3.15,1.35,0])
        detector=Arc(radius=2.3,start_angle=-PI/2,angle=PI,color=BLUE,stroke_width=5).move_arc_center_to([0,1.35,0])
        self.play(FadeIn(emitter),Create(foil),Create(detector),run_time=.65)
        self.add(text('α source (+)',3.7,31,TEAL).shift(LEFT*2.3),text('Thin gold foil',-.95,37,GOLD))
        incoming=Line([-2.7,1.35,0],[2.3,1.35,0])
        self.stream(incoming,TEAL,count=4,period=2.6)
        self.at('fluorescent screen',.7)
        self.play(Indicate(detector,color=TEAL),run_time=.6)
        self.note('Screen flashes when a particle arrives',-1.72)
        spot=Dot([2.3,1.35,0],radius=.15,color=GOLD)
        spot.phase=0
        def pulse(m,dt):
            m.phase+=dt
            phase=m.phase % (2.6/4)
            distance=min(phase,2.6/4-phase)
            m.set_opacity(.15+.85*np.exp(-(distance/.055)**2))
        spot.add_updater(pulse);self.add(spot)
        self.note('Apparatus schematic • not to scale',-2.28)
        self.fill()

        self.start('observations',3,'Three paths. One clue.','Example paths • not measured percentages')
        rows=[(3.35,'MOST · almost straight',TEAL,Line([-3.4,2.75,0],[3.4,2.75,0])),
              (1.15,'SOME · deflected',GOLD,VMobject().set_points_as_corners([[-3.4,.45,0],[0,.45,0],[3.4,1.0,0]])),
              (-.95,'VERY FEW · backward',CORAL,VMobject().set_points_as_corners([[-3.4,-1.55,0],[.5,-1.55,0],[-2,-2.28,0]]))]
        for (y,words,col,path),phrase,fraction in zip(rows,['Most','Some','A very small'],[0,.32,.56]):
            self.at(phrase,fraction)
            self.play(FadeIn(text(words,y,43,col)),Create(path.set_stroke(col,3)),run_time=.45)
            self.stream(path,col,count=4 if col==TEAL else 1,period=2.6)
        self.fill()

        self.start('empty_space',4,'Why most pass through','The nucleus fills very little of the atom')
        atom=self.atom()
        self.play(FadeIn(atom),run_time=.65)
        # Widely offset paths: no contact with the tiny nucleus.
        for y in [-.7,.1,2.45,3.2]:
            self.stream(Line([-3.7,y,0],[3.7,y,0]),TEAL,count=2,period=3.2)
        self.at('tiny region',.65)
        self.play(Circumscribe(atom[1],color=GOLD,buff=.16),run_time=.7)
        self.note('Near-straight paths • nucleus enlarged')
        self.fill()

        self.start('repulsion',5,'A force, not a collision','Positive alpha particle ↔ positive nucleus')
        self.add(nucleus([0,1.35,0],.17))
        paths=[coulomb_path(b,np.array([0,1.35,0])).set_stroke(col,3)
               for b,col in [(1.15,TEAL),(.43,GOLD),(.07,CORAL)]]
        self.play(Create(paths[0]),run_time=.5);self.stream(paths[0],TEAL,2,3.1)
        self.at('bends its path',.5)
        self.play(Create(paths[1]),run_time=.5);self.stream(paths[1],GOLD,1,3.1)
        self.at('closer approach',.68)
        self.play(Create(paths[2]),run_time=.6);self.stream(paths[2],CORAL,1,3.1)
        self.note('Closer approach → stronger deflection',-1.7,WHITE_INK)
        self.note('Same incoming speed • nucleus enlarged',-2.3)
        self.fill()

        self.start('nucleus',6,'The nuclear atom','Rutherford’s historical model')
        atom=self.atom(); self.play(FadeIn(atom),run_time=.6)
        self.at('positive nucleus',.24)
        self.play(atom[1].animate.scale(1.7),run_time=.7)
        self.note('+ Nucleus: almost all the mass',-1.65,GOLD)
        self.at('negative electrons',.72)
        self.play(LaggedStart(*[Indicate(e,color=TEAL,scale_factor=1.35) for e in atom[2]],lag_ratio=.15),run_time=1)
        self.note('− Electrons outside; no fixed shells shown',-2.3,TEAL)
        self.fill()

        self.start('scale',7,'Far smaller than this dot','Modern radius estimates • vary by atom')
        disk=Circle(radius=2.35,color=TEAL,stroke_width=3).move_to([0,1.45,0])
        tiny=Dot([0,1.45,0],radius=.15,color=GOLD)
        self.play(Create(disk),FadeIn(tiny),run_time=.65)
        self.note('Atom radius ≈ 10⁻¹⁰ m',-1.25,TEAL)
        self.at('ten thousand',.27)
        ratio=ValueTracker(1)
        number=DecimalNumber(1,mob_class=NumberText,num_decimal_places=0,font_size=55,color=GOLD,group_with_commas=True,edge_to_fix=ORIGIN).move_to([0,1.45,0])
        number.add_updater(lambda m:m.set_value(ratio.get_value()))
        self.play(FadeOut(tiny),FadeIn(number),run_time=.25)
        self.play(ratio.animate.set_value(100000),run_time=max(.5,self.section_duration()*.30),rate_func=smooth)
        number.clear_updaters()
        self.play(Transform(number,text('10,000–100,000',1.45,48,GOLD,width=4.3)),run_time=.3)
        self.add(text('times smaller',.6,35,GOLD))
        self.note('Nucleus radius ≈ 10⁻¹⁵–10⁻¹⁴ m',-1.98,GOLD)
        self.note('A true-scale nucleus is invisible here',-2.48)
        self.fill()

        self.start('limits',8,'Where the model stops','The next step required quantum theory')
        center=np.array([0,2,0]);core=nucleus(center,.16)
        self.add(core)
        spiral=ParametricFunction(lambda t:center+np.array([2.1*(1-.88*t)*np.cos(5*PI*t),2.1*(1-.88*t)*np.sin(5*PI*t),0]),t_range=[0,1],color=CORAL)
        electron=Dot(spiral.get_start(),color=TEAL,radius=.12)
        explanation=text('Classical orbit → radiation → collapse',-.6,34,CORAL)
        self.add(electron,explanation)
        self.play(Create(spiral),MoveAlongPath(electron,spiral),run_time=max(1,self.section_duration()*.3),rate_func=linear)
        self.at('discrete spectral lines',.37)
        bars=VGroup(*[Line([x,-1.45,0],[x,-.98,0],color=c,stroke_width=7)
                       for x,c in [(-2.8,CORAL),(-.8,TEAL),(.6,BLUE),(2.4,PURPLE)]])
        self.play(Create(bars),Transform(explanation,text('Discrete spectral lines',-.6,38,GOLD)),run_time=.6)
        self.at('Modern quantum',.55)
        self.play(FadeOut(spiral,electron),Transform(explanation,text('Quantum orbitals, not fixed paths',-.6,34,TEAL)),run_time=.3)
        # A labelled symbolic orbital envelope, not a simulated probability density.
        envelope=VGroup(*[Circle(radius=r,color=BLUE,stroke_width=12,stroke_opacity=.09).move_to(center)
                           for r in np.linspace(.4,2.0,15)])
        self.play(FadeIn(envelope),run_time=.8)
        self.note('Quantum orbitals • envelope is schematic',-2.15,TEAL)
        self.fill()

        self.start('recap',9,'The evidence changed the atom','Rare backward scattering was the key clue')
        atom=self.atom().scale(.72).move_to([0,2.2,0])
        self.play(FadeIn(atom),run_time=.55)
        path=Line([-3.6,3.3,0],[3.6,3.3,0]); self.stream(path,TEAL,3,2.8)
        for phrase,fraction,value,y,color in [('mostly empty',.15,'01  Mostly empty space',-.25,TEAL),
                                            ('tiny positive',.3,'02  Tiny positive nucleus',-1.05,GOLD),
                                            ('electrons outside',.45,'03  Electrons outside',-1.85,TEAL)]:
            self.at(phrase,fraction)
            self.play(FadeIn(text(value,y,42,color),shift=UP*.12),run_time=.35)
        self.fill()
