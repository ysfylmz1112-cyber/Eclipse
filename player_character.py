"""Detailed procedural male player for Eclipse.
Uses Panda3D's guaranteed box model so the character is visible without external assets.
"""

from panda3d.core import Vec4


class EclipseCharacter:
    def __init__(self, game, parent):
        self.game = game
        self.parent = parent
        self.parts = []
        self.build()

    def part(self, name, pos, scale, color, lightoff=False):
        m = self.game.loader.loadModel('models/box')
        m.setName('Player_' + name)
        m.reparentTo(self.parent)
        m.setPos(*pos)
        m.setScale(*scale)
        m.setColor(*color)
        m.setTwoSided(True)
        if lightoff:
            m.setLightOff()
        self.parts.append(m)
        return m

    def build(self):
        # Colors: realistic dark expedition clothing with small cyan instrument lights.
        skin = (.55, .34, .24, 1)
        skin_light = (.68, .44, .31, 1)
        skin_shadow = (.31, .16, .12, 1)
        hair = (.012, .010, .009, 1)
        hair2 = (.028, .024, .020, 1)
        jacket = (.028, .060, .078, 1)
        jacket_light = (.055, .125, .155, 1)
        jacket_edge = (.095, .205, .235, 1)
        pants = (.022, .027, .034, 1)
        pants_light = (.045, .052, .062, 1)
        boot = (.010, .012, .015, 1)
        metal = (.18, .21, .23, 1)
        glass = (.08, .48, .64, 1)
        white = (.72, .76, .78, 1)

        P = self.part

        # Boots and lower legs
        P('boot_l', (-.29, -.13, .18), (.27, .47, .19), boot)
        P('boot_r', (.29, -.13, .18), (.27, .47, .19), boot)
        P('sole_l', (-.29, -.15, .075), (.29, .50, .055), metal, True)
        P('sole_r', (.29, -.15, .075), (.29, .50, .055), metal, True)
        P('ankle_l', (-.29, 0, .43), (.20, .20, .18), pants_light)
        P('ankle_r', (.29, 0, .43), (.20, .20, .18), pants_light)
        P('shin_l', (-.29, 0, .68), (.20, .21, .34), pants)
        P('shin_r', (.29, 0, .68), (.20, .21, .34), pants)
        P('knee_l', (-.29, -.015, .96), (.22, .23, .15), pants_light)
        P('knee_r', (.29, -.015, .96), (.22, .23, .15), pants_light)
        P('thigh_l', (-.29, 0, 1.19), (.27, .25, .31), pants)
        P('thigh_r', (.29, 0, 1.19), (.27, .25, .31), pants)

        # Belt / hips
        P('pelvis', (0, 0, 1.40), (.48, .30, .24), pants)
        P('belt', (0, -.01, 1.55), (.52, .33, .075), metal)
        P('belt_light', (0, -.35, 1.55), (.10, .025, .065), glass, True)
        P('belt_left', (-.43, -.01, 1.56), (.09, .25, .12), jacket_light)
        P('belt_right', (.43, -.01, 1.56), (.09, .25, .12), jacket_light)

        # Torso, fitted expedition jacket
        P('abdomen', (0, 0, 1.73), (.45, .29, .30), jacket)
        P('chest', (0, 0, 2.02), (.60, .35, .34), jacket)
        P('chest_panel', (0, -.355, 2.02), (.37, .025, .27), jacket_light)
        P('zipper', (0, -.385, 1.80), (.018, .018, .31), metal, True)
        P('zip_top', (0, -.38, 2.25), (.08, .02, .035), metal, True)
        P('badge', (-.25, -.39, 2.10), (.075, .018, .07), glass, True)
        P('strap_l', (-.35, -.36, 1.98), (.045, .025, .28), jacket_edge)
        P('strap_r', (.35, -.36, 1.98), (.045, .025, .28), jacket_edge)
        P('collar_l', (-.18, -.30, 2.27), (.16, .09, .13), jacket_edge)
        P('collar_r', (.18, -.30, 2.27), (.16, .09, .13), jacket_edge)

        # Shoulders / arms
        P('shoulder_l', (-.66, 0, 2.13), (.28, .30, .24), jacket_light)
        P('shoulder_r', (.66, 0, 2.13), (.28, .30, .24), jacket_light)
        P('arm_l', (-.82, 0, 1.82), (.20, .22, .31), jacket)
        P('arm_r', (.82, 0, 1.82), (.20, .22, .31), jacket)
        P('elbow_l', (-.82, -.01, 1.53), (.21, .23, .14), jacket_light)
        P('elbow_r', (.82, -.01, 1.53), (.21, .23, .14), jacket_light)
        P('forearm_l', (-.82, 0, 1.28), (.18, .20, .26), jacket)
        P('forearm_r', (.82, 0, 1.28), (.18, .20, .26), jacket)
        P('wrist_l', (-.82, 0, 1.08), (.16, .18, .10), metal)
        P('wrist_r', (.82, 0, 1.08), (.16, .18, .10), metal)
        P('glove_l', (-.82, -.015, .96), (.17, .18, .13), boot)
        P('glove_r', (.82, -.015, .96), (.17, .18, .13), boot)
        P('shoulder_light_l', (-.66, -.31, 2.17), (.065, .025, .065), glass, True)
        P('shoulder_light_r', (.66, -.31, 2.17), (.065, .025, .065), glass, True)

        # Neck
        P('neck', (0, 0, 2.37), (.21, .20, .16), skin)
        P('neck_guard', (0, -.02, 2.31), (.29, .23, .08), jacket_light)

        # Head: layered boxes give a more defined male face than one cube.
        P('head', (0, 0, 2.70), (.39, .34, .39), skin_light)
        P('jaw', (0, -.015, 2.55), (.32, .30, .22), skin)
        P('cheek_l', (-.18, -.27, 2.60), (.13, .08, .13), skin_light)
        P('cheek_r', (.18, -.27, 2.60), (.13, .08, .13), skin_light)
        P('ear_l', (-.38, 0, 2.68), (.065, .10, .12), skin)
        P('ear_r', (.38, 0, 2.68), (.065, .10, .12), skin)
        P('brow_l', (-.14, -.32, 2.82), (.12, .025, .035), hair)
        P('brow_r', (.14, -.32, 2.82), (.12, .025, .035), hair)
        P('eye_l', (-.14, -.335, 2.72), (.062, .025, .055), white, True)
        P('eye_r', (.14, -.335, 2.72), (.062, .025, .055), white, True)
        P('pupil_l', (-.14, -.355, 2.72), (.026, .012, .030), hair, True)
        P('pupil_r', (.14, -.355, 2.72), (.026, .012, .030), hair, True)
        P('nose_bridge', (0, -.34, 2.64), (.055, .065, .12), skin)
        P('nose_tip', (0, -.385, 2.60), (.065, .055, .045), skin_light)
        P('mouth', (0, -.315, 2.49), (.13, .022, .028), skin_shadow)
        P('chin', (0, -.27, 2.48), (.15, .06, .075), skin)

        # Hairline + top hair for a recognizable male silhouette.
        P('hair_back', (0, .10, 2.91), (.40, .28, .22), hair)
        P('hair_top', (0, -.01, 3.00), (.42, .33, .18), hair)
        P('hair_front', (0, -.25, 2.95), (.34, .10, .15), hair2)
        for i, x in enumerate((-.28, -.18, -.06, .06, .18, .28)):
            P('hair_lock_%02d' % i, (x, -.27, 2.94), (.095, .07, .16), hair)

        # Small sci-fi equipment details.
        P('back_pack', (0, .28, 1.95), (.34, .16, .40), jacket_light)
        P('back_pack_top', (0, .31, 2.22), (.25, .12, .10), metal)
        P('radio_l', (-.49, -.02, 1.82), (.10, .13, .18), metal)
        P('radio_light', (-.49, -.145, 1.88), (.025, .018, .025), glass, True)
        P('wrist_screen', (.82, -.20, 1.16), (.11, .035, .07), glass, True)

        # Never allow lighting/culling to hide the model.
        self.parent.setTwoSided(True)
        self.parent.show()
        for p in self.parts:
            p.show()

    def show(self):
        self.parent.show()

    def hide(self):
        self.parent.hide()
