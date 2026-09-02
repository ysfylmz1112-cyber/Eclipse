"""Eclipse graphics and atmosphere system."""
from panda3d.core import AmbientLight, DirectionalLight, Fog, PointLight, Vec4
import math


class GraphicsSystem:
    def __init__(self, game):
        self.game = game
        self.render = game.render
        self.fog = None
        self.ambient_node = None
        self.moon_node = None
        self.setup()

    def setup(self):
        ambient = AmbientLight("eclipse_ambient")
        ambient.setColor(Vec4(0.075, 0.085, 0.11, 1))
        self.ambient_node = self.render.attachNewNode(ambient)
        self.render.setLight(self.ambient_node)

        moon = DirectionalLight("eclipse_moon")
        moon.setColor(Vec4(0.42, 0.49, 0.64, 1))
        self.moon_node = self.render.attachNewNode(moon)
        self.moon_node.setHpr(-35, -58, 0)
        self.render.setLight(self.moon_node)

        self.fog = Fog("eclipse_atmosphere")
        self.fog.setColor(0.006, 0.009, 0.018)
        self.fog.setExpDensity(0.0068)
        self.render.setFog(self.fog)
        self.render.setShaderAuto()

    def set_fog_density(self, density):
        if self.fog:
            self.fog.setExpDensity(max(0.0, float(density)))

    def set_moon_intensity(self, intensity):
        intensity = max(0.0, min(2.0, float(intensity)))
        if self.moon_node:
            self.moon_node.node().setColor(
                Vec4(0.42 * intensity, 0.49 * intensity, 0.64 * intensity, 1)
            )

    def create_fill_light(self, name, pos, color, attenuation=(1, .16, .04)):
        light = PointLight(name)
        light.setColor(Vec4(*color))
        light.setAttenuation(attenuation)
        node = self.render.attachNewNode(light)
        node.setPos(*pos)
        self.render.setLight(node)
        return node

    def update(self, dt):
        if self.moon_node:
            phase = math.sin(self.game.globalClock.getFrameTime() * 0.18)
            self.set_moon_intensity(0.96 + phase * 0.025)
