"""Eclipse visual foundation.

Keeps the visual layer separate from gameplay so graphics can be improved
without rewriting movement, missions, saving, or interaction code.
"""
from panda3d.core import AmbientLight, DirectionalLight, Fog, Vec4


class GraphicsSystem:
    def __init__(self, game):
        self.game = game
        self.render = game.render
        self.fog = None
        self.setup()

    def setup(self):
        # Dark cinematic base lighting.
        ambient = AmbientLight("eclipse_ambient")
        ambient.setColor(Vec4(0.055, 0.065, 0.085, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        moon = DirectionalLight("eclipse_moon")
        moon.setColor(Vec4(0.32, 0.39, 0.52, 1))
        moon_node = self.render.attachNewNode(moon)
        moon_node.setHpr(-35, -58, 0)
        self.render.setLight(moon_node)

        # Layered distance fog gives the small prototype world more depth.
        self.fog = Fog("eclipse_atmosphere")
        self.fog.setColor(0.006, 0.009, 0.018)
        self.fog.setExpDensity(0.0075)
        self.render.setFog(self.fog)

        # Slightly stronger material response for the scene as a whole.
        self.render.setShaderAuto()

    def set_fog_density(self, density):
        if self.fog:
            self.fog.setExpDensity(max(0.0, float(density)))

    def update(self, dt):
        # Reserved for dynamic day/night, weather and post-processing hooks.
        pass
