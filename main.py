from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import DirectLabel
from panda3d.core import AmbientLight, DirectionalLight, Vec4, CardMaker


class Eclipse(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()
        self.setBackgroundColor(0.008, 0.012, 0.025)

        self.story_time = 0.0
        self.story_stage = 0

        self.setup_lighting()
        self.create_world()
        self.create_sun_and_moon()
        self.create_player()
        self.create_hud()

        self.taskMgr.add(self.update, "eclipse_update")

    def setup_lighting(self):
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.32, 0.34, 0.40, 1))
        ambient_node = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_node)

        daylight = DirectionalLight("daylight")
        daylight.setColor(Vec4(1.0, 0.82, 0.58, 1))
        daylight_node = self.render.attachNewNode(daylight)
        daylight_node.setHpr(-25, -45, 0)
        self.render.setLight(daylight_node)

    def create_world(self):
        ground = CardMaker("ground")
        ground.setFrame(-60, 60, -60, 60)
        self.ground = self.render.attachNewNode(ground.generate())
        self.ground.setP(-90)
        self.ground.setZ(0)
        self.ground.setColor(0.08, 0.10, 0.11, 1)

        # Simple road layout for the first playable prototype.
        road = CardMaker("road")
        road.setFrame(-4, 4, -60, 60)
        self.road = self.render.attachNewNode(road.generate())
        self.road.setP(-90)
        self.road.setZ(0.01)
        self.road.setColor(0.025, 0.028, 0.032, 1)

        side_road = CardMaker("side_road")
        side_road.setFrame(-35, 35, -3, 3)
        self.side_road = self.render.attachNewNode(side_road.generate())
        self.side_road.setP(-90)
        self.side_road.setZ(0.02)
        self.side_road.setColor(0.025, 0.028, 0.032, 1)

    def create_sun_and_moon(self):
        self.sun = self.loader.loadModel("models/misc/sphere")
        self.sun.reparentTo(self.render)
        self.sun.setScale(3.0)
        self.sun.setPos(0, 28, 20)
        self.sun.setColor(1.0, 0.68, 0.18, 1)
        self.sun.setLightOff()

        self.moon = self.loader.loadModel("models/misc/sphere")
        self.moon.reparentTo(self.render)
        self.moon.setScale(2.0)
        self.moon.setPos(-10, 27.7, 20)
        self.moon.setColor(0.05, 0.06, 0.08, 1)
        self.moon.setLightOff()

    def create_player(self):
        self.player = self.render.attachNewNode("Player")
        self.player.setPos(0, -8, 0)

        body = self.loader.loadModel("models/misc/sphere")
        body.reparentTo(self.player)
        body.setScale(0.55, 0.38, 0.85)
        body.setPos(0, 0, 0.95)
        body.setColor(0.16, 0.18, 0.21, 1)

        head = self.loader.loadModel("models/misc/sphere")
        head.reparentTo(self.player)
        head.setScale(0.34)
        head.setPos(0, 0, 1.95)
        head.setColor(0.45, 0.32, 0.24, 1)

    def create_hud(self):
        self.title = DirectLabel(
            text="E C L I P S E",
            scale=0.065,
            pos=(0, 0, 0.88),
            text_fg=(0.92, 0.92, 0.96, 1),
        )

        self.story_text = DirectLabel(
            text="",
            scale=0.045,
            pos=(-1.25, 0, -0.82),
            text_fg=(0.82, 0.86, 0.92, 1),
            text_align=0,
        )
        self.story_text["text"] = "Güneş tutulması başlamak üzere..."

    def update_story(self, dt):
        self.story_time += dt

        if self.story_stage == 0 and self.story_time >= 5:
            self.story_stage = 1
            self.story_time = 0
            self.story_text["text"] = "Tutulma sona erdi."

        elif self.story_stage == 1 and self.story_time >= 7:
            self.story_stage = 2
            self.story_time = 0
            self.story_text["text"] = "Güneşten anormal bir veri geliyor..."

        elif self.story_stage == 2 and self.story_time >= 6:
            self.story_stage = 3
            self.story_time = 0
            self.story_text["text"] = "UYARI: Güneş aktivitesi hızla yükseliyor."
            self.sun.setColor(1.0, 0.18, 0.04, 1)
            self.sun.setScale(3.4)

        elif self.story_stage == 3 and self.story_time >= 5:
            self.story_stage = 4
            self.story_time = 0
            self.story_text["text"] = "GÖREV: Anomalinin kaynağını araştır."

    def update_camera(self):
        target = self.player.getPos()
        self.camera.setPos(target.x, target.y - 14, target.z + 5)
        self.camera.lookAt(target.x, target.y, target.z + 1.0)

    def update(self, task):
        dt = globalClock.getDt()
        self.update_story(dt)
        self.update_camera()
        return Task.cont


if __name__ == "__main__":
    game = Eclipse()
    game.run()
