from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import AmbientLight, DirectionalLight, Vec4, CardMaker


class Eclipse(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()
        self.setBackgroundColor(0.02, 0.025, 0.04)
        self.setup_lighting()
        self.create_world()
        self.create_player()
        self.setup_camera()
        self.taskMgr.add(self.update, "game_update")

    def setup_lighting(self):
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.55, 0.58, 0.65, 1))
        ambient_node = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_node)

        sun = DirectionalLight("sun")
        sun.setColor(Vec4(1.0, 0.92, 0.78, 1))
        sun_node = self.render.attachNewNode(sun)
        sun_node.setHpr(-35, -55, 0)
        self.render.setLight(sun_node)

    def create_world(self):
        ground_card = CardMaker("ground")
        ground_card.setFrame(-40, 40, -40, 40)
        ground = self.render.attachNewNode(ground_card.generate())
        ground.setP(-90)
        ground.setColor(0.16, 0.17, 0.19, 1)

        road_card = CardMaker("road")
        road_card.setFrame(-3.0, 3.0, -40, 40)
        road = self.render.attachNewNode(road_card.generate())
        road.setP(-90)
        road.setZ(0.01)
        road.setColor(0.055, 0.06, 0.065, 1)

        for y in range(-38, 39, 5):
            mark_card = CardMaker(f"mark_{y}")
            mark_card.setFrame(-0.08, 0.08, -1.2, 1.2)
            mark = self.render.attachNewNode(mark_card.generate())
            mark.setP(-90)
            mark.setPos(0, y, 0.02)
            mark.setColor(0.8, 0.72, 0.35, 1)

        sky_card = CardMaker("sky")
        sky_card.setFrame(-80, 80, -45, 45)
        sky = self.render.attachNewNode(sky_card.generate())
        sky.setPos(0, 25, 20)
        sky.setColor(0.035, 0.06, 0.12, 1)

        self.sun = self.loader.loadModel("models/misc/sphere")
        self.sun.reparentTo(self.render)
        self.sun.setScale(2.5)
        self.sun.setPos(0, 25, 15)
        self.sun.setColor(1.0, 0.72, 0.25, 1)
        self.sun.setLightOff()

        self.moon = self.loader.loadModel("models/misc/sphere")
        self.moon.reparentTo(self.render)
        self.moon.setScale(2.0)
        self.moon.setPos(-5, 24.5, 15)
        self.moon.setColor(0.12, 0.13, 0.16, 1)
        self.moon.setLightOff()

    def create_player(self):
        self.player = self.render.attachNewNode("player")
        self.player.setPos(0, -8, 0)

        body = self.loader.loadModel("models/misc/sphere")
        body.reparentTo(self.player)
        body.setScale(0.55, 0.38, 0.9)
        body.setPos(0, 0, 0.9)
        body.setColor(0.08, 0.10, 0.13, 1)

        head = self.loader.loadModel("models/misc/sphere")
        head.reparentTo(self.player)
        head.setScale(0.34)
        head.setPos(0, 0, 1.95)
        head.setColor(0.55, 0.40, 0.30, 1)

    def setup_camera(self):
        self.camera.setPos(0, -14, 5)
        self.camera.lookAt(0, -5, 1.0)

    def update(self, task):
        target = self.player.getPos()
        self.camera.setPos(target.x, target.y - 14, target.z + 5)
        self.camera.lookAt(target.x, target.y, target.z + 1.0)
        return Task.cont


if __name__ == "__main__":
    game = Eclipse()
    game.run()
