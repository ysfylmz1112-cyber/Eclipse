from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import DirectLabel
from panda3d.core import AmbientLight, DirectionalLight, Fog, PointLight, Vec4, TextNode, CardMaker, Vec3


class Eclipse(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.setBackgroundColor(0.015, 0.02, 0.035, 1)
        self.accept('escape', self.userExit)
        self.keys = {k: False for k in ('w', 'a', 's', 'd')}
        for k in self.keys:
            self.accept(k, self.set_key, [k, True])
            self.accept(k + '-up', self.set_key, [k, False])
        self.phase = 0
        self.phase_time = 0.0
        self.player_pos = Vec3(0, -8, 0.9)
        self.build_scene()
        self.build_player()
        self.build_hud()
        self.taskMgr.add(self.update, 'eclipse_update')

    def set_key(self, key, value):
        self.keys[key] = value

    def model(self, path, pos, scale, color, parent=None):
        node = self.loader.loadModel(path)
        node.reparentTo(parent or self.render)
        node.setPos(*pos)
        node.setScale(*scale)
        node.setColor(*color)
        return node

    def build_scene(self):
        cm = CardMaker('ground')
        cm.setFrame(-70, 70, -70, 70)
        self.ground = self.render.attachNewNode(cm.generate())
        self.ground.setP(-90)
        self.ground.setColor(0.12, 0.16, 0.13, 1)
        self.ground.setTwoSided(True)

        self.sun = self.model('models/misc/sphere', (18, 32, 30), (7, 7, 7), (1, 0.55, 0.18, 1))
        self.moon = self.model('models/misc/sphere', (18, 31, 30), (3, 3, 3), (0.08, 0.09, 0.12, 1))

        light = PointLight('sun_light')
        light.setColor(Vec4(1, 0.55, 0.22, 1))
        light.setAttenuation((1, 0.01, 0.001))
        ln = self.render.attachNewNode(light)
        ln.setPos(18, 20, 20)
        self.render.setLight(ln)

        ambient = AmbientLight('ambient')
        ambient.setColor(Vec4(0.32, 0.36, 0.42, 1))
        self.ambient_node = self.render.attachNewNode(ambient)
        self.render.setLight(self.ambient_node)

        moon_light = DirectionalLight('moon_light')
        moon_light.setColor(Vec4(0.22, 0.28, 0.40, 1))
        mn = self.render.attachNewNode(moon_light)
        mn.setHpr(-35, -55, 0)
        self.render.setLight(mn)

        fog = Fog('atmosphere')
        fog.setColor(0.03, 0.045, 0.07)
        fog.setExpDensity(0.0018)
        self.render.setFog(fog)

        for x, y, s in [(-18, 8, 2.5), (-8, 20, 3.2), (12, 14, 2.8), (25, 5, 2.2), (-25, -8, 3), (18, -18, 3.5)]:
            self.model('models/misc/sphere', (x, y, s * 0.8), (s * 2, s * 2, s), (0.07, 0.09, 0.10, 1))

    def build_player(self):
        self.player = self.render.attachNewNode('Player')
        self.model('models/misc/sphere', (0, 0, 1.1), (0.55, 0.38, 1.05), (0.16, 0.22, 0.30, 1), self.player)
        self.model('models/misc/sphere', (0, 0, 2.15), (0.38, 0.38, 0.38), (0.55, 0.38, 0.28, 1), self.player)
        self.player.setPos(self.player_pos)

    def build_hud(self):
        DirectLabel(text='E C L I P S E', scale=0.075, pos=(0, 0, 0.90), text_fg=(0.85, 0.92, 1, 1))
        self.status = DirectLabel(text='', scale=0.045, pos=(-1.28, 0, 0.82), text_align=TextNode.ALeft, text_fg=(0.8, 0.86, 0.92, 1))
        self.objective = DirectLabel(text='', scale=0.05, pos=(-1.28, 0, -0.86), text_align=TextNode.ALeft, text_fg=(1, 0.78, 0.42, 1))
        self.status['text'] = 'Güneş tutulması başlıyor...'

    def advance_story(self, dt):
        self.phase_time += dt
        if self.phase == 0 and self.phase_time >= 8:
            self.phase = 1; self.phase_time = 0
            self.status['text'] = 'Tutulma sona erdi. Güneş verileri bekleniyor...'
        elif self.phase == 1 and self.phase_time >= 8:
            self.phase = 2; self.phase_time = 0
            self.status['text'] = 'GÜNEŞ ANOMALİSİ: olağandışı enerji tespit edildi.'
            self.sun.setColor(1.0, 0.18, 0.04, 1)
            self.sun.setScale(8.5)
        elif self.phase == 2 and self.phase_time >= 7:
            self.phase = 3; self.phase_time = 0
            self.status['text'] = 'İLK VERİ ALINDI: Dünya gözlem ağı olayı doğruladı.'
            self.objective['text'] = 'GÖREV 01  •  Gözlem merkezine git ve ilk veriyi incele.'
        elif self.phase == 3 and self.phase_time >= 15:
            self.phase = 4; self.phase_time = 0
            self.status['text'] = 'ECLIPSE PROTOKOLÜ AKTİF — insanlığın geleceği değişiyor.'
            self.objective['text'] = 'HİKÂYE DEVAM EDECEK  •  Dünya → Ay → Mars → Uzay'

    def update(self, task):
        dt = min(globalClock.getDt(), 0.05)
        self.advance_story(dt)
        move = Vec3(0, 0, 0)
        if self.keys['w']: move.y += 1
        if self.keys['s']: move.y -= 1
        if self.keys['a']: move.x -= 1
        if self.keys['d']: move.x += 1
        if move.lengthSquared() > 0:
            move.normalize()
            self.player_pos += move * (6.0 * dt)
            self.player_pos.z = 0.9
            self.player.setPos(self.player_pos)
        self.camera.setPos(self.player_pos.x, self.player_pos.y - 11, self.player_pos.z + 5.2)
        self.camera.lookAt(self.player_pos + Vec3(0, 0, 1.2))
        return Task.cont


Eclipse().run()
