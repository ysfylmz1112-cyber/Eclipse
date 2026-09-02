"""Eclipse lighting and atmosphere system."""
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
        # Keep enough ambient light for building surfaces to remain visible.
        ambient = AmbientLight("eclipse_ambient")
        ambient.setColor(Vec4(0.16, 0.18, 0.22, 1))
        self.ambient_node = self.render.attachNewNode(ambient)
        self.render.setLight(self.ambient_node)

        moon = DirectionalLight("eclipse_moon")
        moon.setColor(Vec4(0.48, 0.55, 0.68, 1))
        self.moon_node = self.render.attachNewNode(moon)
        self.moon_node.setHpr(-35, -58, 0)
        self.render.setLight(self.moon_node)

        self.fog = Fog("eclipse_atmosphere")
        self.fog.setColor(0.018, 0.025, 0.04)
        self.fog.setExpDensity(0.0038)
        self.render.setFog(self.fog)

        # Do not force Panda3D's automatic shader pipeline here. The current
        # box-based assets use the fixed-function lighting reliably.

    def set_fog_density(self, density):
        if self.fog:
            self.fog.setExpDensity(max(0.0, float(density)))

    def set_moon_intensity(self, intensity):
        intensity = max(0.0, min(2.0, float(intensity)))
        if self.moon_node:
            self.moon_node.node().setColor(
                Vec4(0.48 * intensity, 0.55 * intensity, 0.68 * intensity, 1)
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
            self.set_moon_intensity(0.98 + phase * 0.02)
