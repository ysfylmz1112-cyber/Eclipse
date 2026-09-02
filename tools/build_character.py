from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'main.py'
text = MAIN.read_text(encoding='utf-8')
backup = MAIN.with_suffix('.py.backup_character')
backup.write_text(text, encoding='utf-8')

new_player = '''    def sphere(self, name, x, y, z, sx, sy, sz, c, parent=None, lightoff=False):
        m = self.loader.loadModel('models/misc/sphere')
        m.setName(name)
        m.reparentTo(parent if parent is not None else self.render)
        m.setPos(x, y, z)
        m.setScale(sx, sy, sz)
        m.setColor(*c)
        if lightoff:
            m.setLightOff()
        return m

    def player(self):
        self.p = self.render.attachNewNode('Player')
        self.p.setPos(0, -2, 1)
        self.character = self.p.attachNewNode('EclipseCharacter')

        # Detailed procedural male character.  No character geometry is added
        # to world collision; the player root handles movement/collision.
        skin = (.56, .37, .28, 1)
        skin2 = (.68, .46, .35, 1)
        skin_dark = (.40, .25, .19, 1)
        hair = (.018, .014, .012, 1)
        eye = (.012, .016, .020, 1)
        white = (.82, .86, .88, 1)
        jacket = (.035, .075, .095, 1)
        jacket2 = (.055, .14, .18, 1)
        jacket3 = (.09, .20, .24, 1)
        pants = (.025, .032, .040, 1)
        pants2 = (.045, .055, .065, 1)
        shoe = (.012, .014, .017, 1)
        metal = (.18, .22, .24, 1)
        accent = (.12, .55, .72, 1)

        # Feet, lower legs and thighs.
        self.sphere('shoe_l', -.27, -.10, .12, .30, .52, .14, shoe, self.character)
        self.sphere('shoe_r', .27, -.10, .12, .30, .52, .14, shoe, self.character)
        self.sphere('sole_l', -.27, -.10, .045, .31, .54, .055, metal, self.character)
        self.sphere('sole_r', .27, -.10, .045, .31, .54, .055, metal, self.character)
        self.sphere('shin_l', -.27, 0, .52, .22, .22, .52, pants, self.character)
        self.sphere('shin_r', .27, 0, .52, .22, .22, .52, pants, self.character)
        self.sphere('knee_l', -.27, -.015, .91, .235, .235, .19, pants2, self.character)
        self.sphere('knee_r', .27, -.015, .91, .235, .235, .19, pants2, self.character)
        self.sphere('thigh_l', -.27, 0, 1.16, .29, .27, .40, pants, self.character)
        self.sphere('thigh_r', .27, 0, 1.16, .29, .27, .40, pants, self.character)

        # Belt and pelvis.
        self.sphere('pelvis', 0, 0, 1.05, .48, .30, .31, pants, self.character)
        self.sphere('belt', 0, -.01, 1.30, .51, .32, .10, metal, self.character)
        self.sphere('belt_front', 0, -.31, 1.30, .12, .035, .09, accent, self.character)

        # Layered torso for a less blocky silhouette.
        self.sphere('abdomen', 0, 0, 1.58, .49, .30, .42, jacket, self.character)
        self.sphere('chest', 0, -.005, 1.88, .62, .35, .42, jacket, self.character)
        self.sphere('chest_plate', 0, -.325, 1.88, .38, .035, .30, jacket2, self.character)
        self.sphere('chest_badge', 0, -.365, 2.00, .075, .025, .055, accent, self.character, True)
        self.sphere('zipper', 0, -.365, 1.67, .018, .018, .28, metal, self.character, True)
        self.sphere('collar_l', -.20, -.32, 2.12, .18, .08, .13, jacket3, self.character)
        self.sphere('collar_r', .20, -.32, 2.12, .18, .08, .13, jacket3, self.character)

        # Shoulders, upper/lower arms, gloves.
        self.sphere('shoulder_l', -.64, 0, 2.02, .27, .32, .25, jacket2, self.character)
        self.sphere('shoulder_r', .64, 0, 2.02, .27, .32, .25, jacket2, self.character)
        self.sphere('upper_arm_l', -.78, 0, 1.70, .20, .22, .38, jacket, self.character)
        self.sphere('upper_arm_r', .78, 0, 1.70, .20, .22, .38, jacket, self.character)
        self.sphere('elbow_l', -.78, 0, 1.34, .21, .22, .16, jacket2, self.character)
        self.sphere('elbow_r', .78, 0, 1.34, .21, .22, .16, jacket2, self.character)
        self.sphere('forearm_l', -.78, 0, 1.10, .18, .20, .30, jacket, self.character)
        self.sphere('forearm_r', .78, 0, 1.10, .18, .20, .30, jacket, self.character)
        self.sphere('glove_l', -.78, -.01, .83, .17, .18, .17, shoe, self.character)
        self.sphere('glove_r', .78, -.01, .83, .17, .18, .17, shoe, self.character)
        self.sphere('glove_knuckle_l', -.78, -.17, .85, .11, .035, .06, metal, self.character, True)
        self.sphere('glove_knuckle_r', .78, -.17, .85, .11, .035, .06, metal, self.character, True)

        # Neck and head.
        self.sphere('neck', 0, 0, 2.25, .22, .21, .20, skin, self.character)
        self.sphere('head', 0, 0, 2.62, .39, .35, .46, skin2, self.character)
        self.sphere('jaw', 0, -.015, 2.48, .34, .32, .25, skin, self.character)
        self.sphere('ear_l', -.385, 0, 2.62, .075, .10, .13, skin, self.character)
        self.sphere('ear_r', .385, 0, 2.62, .075, .10, .13, skin, self.character)
        self.sphere('ear_inner_l', -.405, -.025, 2.62, .028, .055, .07, skin_dark, self.character)
        self.sphere('ear_inner_r', .405, -.025, 2.62, .028, .055, .07, skin_dark, self.character)

        # Face: eyes, eyebrows, nose, cheek/jaw definition and mouth.
        self.sphere('eye_l', -.145, -.325, 2.68, .065, .028, .065, eye, self.character, True)
        self.sphere('eye_r', .145, -.325, 2.68, .065, .028, .065, eye, self.character, True)
        self.sphere('iris_l', -.145, -.350, 2.68, .028, .012, .032, accent, self.character, True)
        self.sphere('iris_r', .145, -.350, 2.68, .028, .012, .032, accent, self.character, True)
        self.sphere('brow_l', -.145, -.315, 2.80, .12, .025, .035, hair, self.character)
        self.sphere('brow_r', .145, -.315, 2.80, .12, .025, .035, hair, self.character)
        self.sphere('nose', 0, -.355, 2.58, .075, .095, .12, skin, self.character)
        self.sphere('nose_tip', 0, -.425, 2.56, .055, .045, .045, skin2, self.character)
        self.sphere('cheek_l', -.22, -.305, 2.53, .10, .045, .08, skin2, self.character)
        self.sphere('cheek_r', .22, -.305, 2.53, .10, .045, .08, skin2, self.character)
        self.sphere('mouth', 0, -.342, 2.43, .13, .025, .035, skin_dark, self.character)

        # Hair cap plus several locks for a recognisable silhouette.
        self.sphere('hair_cap', 0, .005, 2.93, .42, .37, .25, hair, self.character)
        self.sphere('hair_front', 0, -.30, 2.89, .34, .10, .16, hair, self.character)
        for i, (x, y, z, sx, sy, sz) in enumerate([
            (-.30, -.20, 2.87, .12, .12, .20), (-.20, -.29, 2.95, .13, .11, .19),
            (-.08, -.32, 2.99, .12, .10, .17), (.08, -.32, 2.99, .12, .10, .17),
            (.20, -.29, 2.95, .13, .11, .19), (.30, -.20, 2.87, .12, .12, .20),
            (-.38, -.02, 2.80, .08, .18, .24), (.38, -.02, 2.80, .08, .18, .24),
        ]):
            self.sphere(f'hair_lock_{i}', x, y, z, sx, sy, sz, hair, self.character)

        # Neck/shoulder seams and small equipment details.
        self.sphere('neck_guard', 0, -.02, 2.20, .28, .23, .08, jacket2, self.character)
        self.sphere('strap_l', -.34, -.32, 1.82, .055, .035, .33, jacket3, self.character)
        self.sphere('strap_r', .34, -.32, 1.82, .055, .035, .33, jacket3, self.character)
        self.sphere('shoulder_pad_l', -.68, -.02, 2.09, .23, .29, .08, jacket3, self.character)
        self.sphere('shoulder_pad_r', .68, -.02, 2.09, .23, .29, .08, jacket3, self.character)
        self.sphere('arm_badge_l', -.79, -.22, 1.73, .07, .025, .10, accent, self.character, True)
        self.sphere('arm_badge_r', .79, -.22, 1.73, .07, .025, .10, accent, self.character, True)

        self.character.setScale(1.0)
        self.character.show()
'''

pattern = re.compile(r"    def player\(self\):.*?\n    def lights\(self\):", re.S)
if not pattern.search(text):
    raise SystemExit('player() section not found')
text = pattern.sub(new_player + '\n    def lights(self):', text, count=1)
MAIN.write_text(text, encoding='utf-8')
print('Detailed male character installed.')
print('Backup:', backup.name)
