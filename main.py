from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import AmbientLight, DirectionalLight, Fog, Vec3, Vec4, CardMaker, TextNode


class Eclipse(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()
        self.setBackgroundColor(0.025, 0.035, 0.055)
        self.first_person = False
        self.speed = 9.0
        self.keys = {"w": False, "a": False, "s": False, "d": False, "shift": False}
        self.setup_lighting()
        self.setup_fog()
        self.create_world()
        self.create_player()
        self.create_hud()
        self.setup_input()
        self.setup_camera()
        self.taskMgr.add(self.update, "game_update")

    def setup_lighting(self):
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.38, 0.42, 0.50, 1))
        self.render.setLight(self.render.attachNewNode(ambient))
        sun = DirectionalLight("sun")
        sun.setColor(Vec4(0.95, 0.90, 0.78, 1))
        sun_node = self.render.attachNewNode(sun)
        sun_node.setHpr(-25, -48, 0)
        self.render.setLight(sun_node)

    def setup_fog(self):
        fog = Fog("eclipse_fog")
        fog.setColor(0.025, 0.035, 0.055)
        fog.setExpDensity(0.006)
        self.render.setFog(fog)

    def make_card(self, name, x1, x2, y1, y2, z, color):
        cm = CardMaker(name)
        cm.setFrame(x1, x2, y1, y2)
        node = self.render.attachNewNode(cm.generate())
        node.setP(-90)
        node.setZ(z)
        node.setColor(*color)
        return node

    def create_world(self):
        # Continuous terrain: no floating objects and no black void.
        self.make_card("terrain", -100, 100, -100, 100, 0, (0.10, 0.12, 0.11, 1))

        # A real street layout with sidewalks and intersections.
        self.make_card("main_road_v", -4.5, 4.5, -100, 100, 0.015, (0.045, 0.048, 0.052, 1))
        self.make_card("main_road_h", -100, 100, -4.5, 4.5, 0.016, (0.045, 0.048, 0.052, 1))
        self.make_card("side_road_l", -28, -22, -100, 100, 0.017, (0.055, 0.058, 0.062, 1))
        self.make_card("side_road_r", 22, 28, -100, 100, 0.018, (0.055, 0.058, 0.062, 1))
        for x in (-6.2, 6.2, -29.7, 29.7):
            self.make_card(f"sidewalk_{x}", x - 0.65, x + 0.65, -100, 100, 0.03, (0.20, 0.20, 0.19, 1))
        for y in (-6.2, 6.2):
            self.make_card(f"sidewalk_y_{y}", -100, 100, y - 0.65, y + 0.65, 0.031, (0.20, 0.20, 0.19, 1))

        for y in range(-94, 95, 8):
            self.make_card(f"roadline_y_{y}", -0.09, 0.09, y - 1.7, y + 1.7, 0.035, (0.78, 0.67, 0.34, 1))
        for x in range(-94, 95, 8):
            self.make_card(f"roadline_x_{x}", x - 1.7, x + 1.7, -0.09, 0.09, 0.036, (0.78, 0.67, 0.34, 1))

        # Buildings are grounded on street lots and have windows.
        lots = [
            (-15, -15, 9, 8), (-36, -15, 11, 9), (14, -16, 10, 9), (37, -15, 11, 10),
            (-15, 15, 9, 10), (-36, 15, 11, 8), (14, 16, 10, 9), (37, 15, 11, 9),
            (-55, -16, 12, 10), (55, -16, 12, 10), (-55, 16, 12, 10), (55, 16, 12, 10),
            (-75, -20, 13, 12), (75, -20, 13, 12), (-75, 20, 13, 12), (75, 20, 13, 12),
        ]
        for i, (x, y, w, d) in enumerate(lots):
            self.create_house(i, x, y, w, d)

        # Trees and lamps give the streets life.
        for i, (x, y) in enumerate([(-9,-13),(9,-13),(-9,13),(9,13),(-41,-7),(-41,7),(41,-7),(41,7),(-62,-7),(-62,7),(62,-7),(62,7)]):
            self.create_tree(i, x, y)
        i = 0
        for y in range(-88, 89, 16):
            for x in (-7.6, 7.6):
                self.create_lamp(i, x, y)
                i += 1

        self.sun = self.loader.loadModel("models/misc/sphere")
        self.sun.reparentTo(self.render)
        self.sun.setScale(5)
        self.sun.setPos(-35, 55, 34)
        self.sun.setColor(1.0, 0.55, 0.20, 1)
        self.sun.setLightOff()

        self.moon = self.loader.loadModel("models/misc/sphere")
        self.moon.reparentTo(self.render)
        self.moon.setScale(3.2)
        self.moon.setPos(-34, 51.5, 34)
        self.moon.setColor(0.07, 0.08, 0.11, 1)
        self.moon.setLightOff()

    def cube(self, scale, pos, color):
        node = self.loader.loadModel("models/misc/rgbCube")
        node.reparentTo(self.render)
        node.setScale(*scale)
        node.setPos(*pos)
        node.setColor(*color)
        return node

    def create_house(self, i, x, y, w, d):
        h = 4.0 + (i % 3) * 1.2
        self.cube((w/2, d/2, h/2), (x, y, h/2), (0.24 + (i % 2)*0.04, 0.25, 0.28, 1))
        # Low roof cap, aligned to the building instead of floating randomly.
        self.cube((w/2 + 0.2, d/2 + 0.2, 0.18), (x, y, h + 0.18), (0.09, 0.10, 0.12, 1))
        count = max(2, int(w // 3))
        for n in range(count):
            wx = x - w/2 + 1.4 + n * ((w - 2.8) / max(1, count-1))
            win = self.cube((0.42, 0.055, 0.62), (wx, y - d/2 - 0.06, 2.0), (0.62, 0.50, 0.28, 1))
            win.setLightOff()
            if h > 5:
                win2 = self.cube((0.42, 0.055, 0.62), (wx, y - d/2 - 0.06, 4.2), (0.62, 0.50, 0.28, 1))
                win2.setLightOff()

    def create_tree(self, i, x, y):
        self.cube((0.22, 0.22, 1.35), (x, y, 1.35), (0.20, 0.13, 0.08, 1))
        crown = self.loader.loadModel("models/misc/sphere")
        crown.reparentTo(self.render)
        crown.setScale(1.55, 1.55, 1.8)
        crown.setPos(x, y, 3.15)
        crown.setColor(0.07, 0.15, 0.09, 1)

    def create_lamp(self, i, x, y):
        self.cube((0.06, 0.06, 2.0), (x, y, 2.0), (0.07, 0.075, 0.08, 1))
        light = self.loader.loadModel("models/misc/sphere")
        light.reparentTo(self.render)
        light.setScale(0.20)
        light.setPos(x, y, 4.05)
        light.setColor(1.0, 0.72, 0.32, 1)
        light.setLightOff()

    def create_player(self):
        self.player = self.render.attachNewNode("Player")
        self.player.setPos(0, -16, 0)
        body = self.loader.loadModel("models/misc/rgbCube")
        body.reparentTo(self.player)
        body.setScale(0.42, 0.28, 0.72)
        body.setPos(0, 0, 0.82)
        body.setColor(0.055, 0.065, 0.08, 1)
        head = self.loader.loadModel("models/misc/sphere")
        head.reparentTo(self.player)
        head.setScale(0.30)
        head.setPos(0, 0, 1.82)
        head.setColor(0.46, 0.32, 0.23, 1)

    def create_hud(self):
        text = TextNode("hud")
        text.setText("ECLIPSE   |   W A S D: HAREKET   |   SHIFT: KOS   |   V: 1. / 3. SAHIS")
        text.setTextColor(0.86, 0.88, 0.92, 1)
        text.setAlign(TextNode.ALeft)
        hud = self.aspect2d.attachNewNode(text)
        hud.setScale(0.043)
        hud.setPos(-1.28, 0, -0.88)

    def setup_input(self):
        for key in ("w", "a", "s", "d", "shift"):
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        self.accept("v", self.toggle_camera)

    def set_key(self, key, value):
        self.keys[key] = value

    def toggle_camera(self):
        self.first_person = not self.first_person

    def setup_camera(self):
        self.camera.setPos(0, -26, 7)
        self.camera.lookAt(self.player.getPos() + Vec3(0, 0, 1.2))

    def update(self, task):
        dt = min(globalClock.getDt(), 0.05)
        direction = Vec3(0, 0, 0)
        if self.keys["w"]: direction.y += 1
        if self.keys["s"]: direction.y -= 1
        if self.keys["a"]: direction.x -= 1
        if self.keys["d"]: direction.x += 1
        if direction.lengthSquared() > 0:
            direction.normalize()
            speed = self.speed * (1.8 if self.keys["shift"] else 1.0)
            self.player.setPos(self.player.getPos() + direction * speed * dt)
        p = self.player.getPos()
        if self.first_person:
            self.camera.setPos(p.x, p.y, p.z + 1.65)
            self.camera.lookAt(p.x, p.y + 5, p.z + 1.65)
        else:
            self.camera.setPos(p.x, p.y - 11, p.z + 5.5)
            self.camera.lookAt(p.x, p.y + 1.5, p.z + 1.0)
        return Task.cont


if __name__ == "__main__":
    Eclipse().run()
