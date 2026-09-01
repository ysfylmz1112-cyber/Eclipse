from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, Vec4


class EclipseGame(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # Arka plan
        self.set_background_color(0.03, 0.04, 0.06, 1)

        # Mouse kamera kontrolünü kapat
        self.disableMouse()

        # Kamera
        self.camera.setPos(0, -20, 8)
        self.camera.lookAt(0, 0, 0)

        # 3D zemin
        self.ground = self.loader.loadModel("models/box")
        self.ground.reparentTo(self.render)
        self.ground.setScale(15, 15, 0.2)
        self.ground.setPos(0, 0, -0.2)
        self.ground.setColor(0.25, 0.28, 0.32, 1)

        # Ortam ışığı
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.4, 0.4, 0.4, 1))

        ambient_node = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_node)

        # Ana ışık
        sun = DirectionalLight("sun")
        sun.setColor(Vec4(1, 1, 1, 1))

        sun_node = self.render.attachNewNode(sun)
        sun_node.setHpr(-45, -45, 0)

        self.render.setLight(sun_node)


game = EclipseGame()
game.run()