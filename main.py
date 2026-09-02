from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import DirectLabel
from panda3d.core import AmbientLight, DirectionalLight, Fog, PointLight, TextNode, Vec3, Vec4, WindowProperties
from systems.graphics_system import GraphicsSystem
import math
import random


class EclipseGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.set_background_color(.012, .017, .026, 1)
        self.keys = {k: False for k in ('w', 'a', 's', 'd', 'shift')}
        self.speed = 5.5
        self.sprint_speed = 9.0
        self.gravity = 23
        self.jump_speed = 8.5
        self.vz = 0
        self.on_ground = True
        self.health = 100
        self.stamina = 100
        self.radius = .62
        self.yaw = 0.0
        self.target_yaw = 0.0
        self.pitch = -6.0
        self.target_pitch = -6.0
        self.mouse_captured = True
        self.sensitivity = .025
        self.paused = False
        self.flashlight = True
        self.camera_mode = 'third'
        self.camera_distance = 7.2
        self.camera_height = 1.6
        self.bob = 0.0
        self.obstacles = []
        self.terminals = []
        self.found = set()
        self.message_timer = 0.0
        random.seed(42)
        self.graphics_system = GraphicsSystem(self)
        self.world()
        self.player()
        self.lights()
        self.hud()
        self.input()
        self.capture()
        self.taskMgr.add(self.update, 'eclipse_update')

    def box(self, name, x, y, z, sx, sy, sz, c, solid=False, lightoff=False, parent=None):
        m = self.loader.loadModel('models/box')
        m.setName(name)
        m.reparentTo(parent if parent is not None else self.render)
        m.setPos(x, y, z)
        m.setScale(sx, sy, sz)
        m.setColor(*c)
        if lightoff:
            m.setLightOff()
        if solid and parent is None:
            self.obstacles.append((x, y, sx, sy, z + sz))
        return m

    def sphere(self, name, x, y, z, sx, sy, sz, c, parent=None, lightoff=False):
        m = self.loader.loadModel('models/misc/sphere')
        m.setName(name)
        m.reparentTo(parent if parent is not None else self.render)
        m.setPos(x, y, z)
        m.setScale(sx, sy, sz)
        m.setColor(*c)
        m.setTwoSided(True)
        if lightoff:
            m.setLightOff()
        return m

    def building(self, x, y, sx, sy, h, wall_color, windows=3):
        self.box('building', x, y, h, sx, sy, h, wall_color, True)
        self.box('roof', x, y, h * 2.03, sx * 1.04, sy * 1.04, .10, (.025, .03, .04, 1))
        for side in (-1, 1):
            for i in range(windows):
                yy = -sy * .72 + (2 * sy * .72) * (i / max(1, windows - 1))
                self.box('window', x + side * (sx + .035), y + yy, h * .72, .035, .34, .40, (.22, .52, .68, 1), False, True)
                self.box('window2', x + side * (sx + .035), y + yy, h * 1.38, .035, .34, .40, (.16, .34, .48, 1), False, True)
        for side in (-1, 1):
            for i in range(2):
                xx = -sx * .55 + i * sx * .55
                self.box('side_window', x + xx, y + side * (sy + .035), h * .78, .30, .035, .38, (.20, .48, .62, 1), False, True)
        self.box('door', x, y - sy - .045, .85, .52, .06, .85, (.045, .055, .065, 1))
        self.box('door_light', x, y - sy - .065, 1.35, .09, .025, .09, (1.0, .66, .30, 1), False, True)
        self.box('awning', x, y - sy - .16, 1.72, .85, .32, .08, (.08, .09, .11, 1))
        self.box('ac_unit', x + sx * .45, y + sy * .25, h * 2.18, .35, .28, .22, (.10, .11, .12, 1))
        self.box('roof_box', x - sx * .35, y - sy * .25, h * 2.17, .42, .30, .25, (.06, .07, .08, 1))

    def lamp(self, x, y):
        self.box('lamp_pole', x, y, 2.7, .075, .075, 2.7, (.055, .06, .07, 1), True)
        self.box('lamp_head', x, y, 5.35, .20, .20, .10, (1.0, .62, .24, 1), False, True)
        p = PointLight('street_light')
        p.setColor(Vec4(1.0, .52, .18, 1))
        p.setAttenuation((1, .14, .035))
        n = self.render.attachNewNode(p)
        n.setPos(x, y, 5.15)
        self.render.setLight(n)

    def tree(self, x, y, s=1.0):
        self.box('trunk', x, y, 1.0 * s, .22 * s, .22 * s, 1.0 * s, (.16, .075, .035, 1))
        self.box('crown_a', x, y, 2.05 * s, .95 * s, .95 * s, .65 * s, (.025, .11, .055, 1))
        self.box('crown_b', x, y, 2.65 * s, .72 * s, .72 * s, .55 * s, (.02, .085, .045, 1))
        self.box('crown_c', x, y, 3.10 * s, .48 * s, .48 * s, .42 * s, (.035, .13, .065, 1))

    def world(self):
        self.box('ground', 0, 0, -.35, 32, 32, .35, (.055, .065, .062, 1))
        road = (.032, .036, .041, 1)
        self.box('road_ns', 0, 0, .02, 4.2, 32, .025, road)
        self.box('road_ew', 0, 0, .025, 32, 4.2, .025, road)
        sidewalk = (.12, .125, .12, 1)
        for x in (-7.0, 7.0): self.box('sidewalk_v', x, 0, .075, 1.0, 31, .075, sidewalk, True)
        for y in (-7.0, 7.0): self.box('sidewalk_h', 0, y, .075, 31, 1.0, .075, sidewalk, True)
        mark = (.72, .67, .45, 1)
        for q in range(-28, 29, 4):
            self.box('lane_mark', 0, q, .065, .08, 1.05, .015, mark, False, True)
            self.box('lane_mark', q, 0, .067, 1.05, .08, .015, mark, False, True)
        buildings = [(-14.0, 13.5, 3.6, 3.7, 3.4, (.18, .20, .23, 1), 3),(-22.5, 14.0, 3.2, 3.4, 2.9, (.24, .22, .19, 1), 2),(14.0, 13.5, 3.8, 3.5, 3.8, (.20, .22, .25, 1), 3),(22.5, 14.0, 3.0, 3.4, 2.8, (.26, .23, .20, 1), 2),(-14.0, -13.5, 3.6, 3.6, 3.1, (.19, .22, .20, 1), 3),(-22.0, -14.0, 3.0, 3.2, 2.7, (.22, .21, .23, 1), 2),(14.0, -13.5, 3.7, 3.5, 3.5, (.23, .20, .19, 1), 3),(22.0, -14.0, 3.1, 3.1, 2.9, (.21, .23, .22, 1), 2)]
        for b in buildings: self.building(*b)
        for x, y, s in [(-28, 9, 1.0),(-25, 23, .9),(-18, 24, 1.1),(-9, 26, .8),(9, 26, .9),(19, 24, 1.0),(27, 22, .9),(28, 9, 1.0),(-28, -9, .9),(-26, -23, 1.0),(-18, -24, .8),(-9, -26, 1.0),(9, -26, .9),(19, -24, 1.0),(27, -22, .9),(28, -9, 1.0)]: self.tree(x, y, s)
        for x, y in [(-6, -16),(6, -16),(-6, -8),(6, -8),(-6, 8),(6, 8),(-6, 16),(6, 16),(-16, -6),(-16, 6),(16, -6),(16, 6)]: self.lamp(x, y)
        for i, (x, y) in enumerate([(-9, -4), (6, 14), (17, -3)]):
            t = self.box('terminal', x, y, 1.0, .58, .40, 1.0, (.025, .22, .28, 1), True)
            self.box('screen', x, y - .43, 1.16, .34, .025, .22, (.10, .75, .95, 1), False, True)
            self.terminals.append((t, f'Terminal {i + 1}'))
        wall = (.025, .032, .042, 1)
        self.box('north', 0, 31.5, 2.0, 32, .5, 2.0, wall, True)
        self.box('south', 0, -31.5, 2.0, 32, .5, 2.0, wall, True)
        self.box('east', 31.5, 0, 2.0, .5, 32, 2.0, wall, True)
        self.box('west', -31.5, 0, 2.0, .5, 32, 2.0, wall, True)

    def player(self):
        self.p = self.render.attachNewNode('Player')
        self.p.setPos(0, -2, 0.70)
        self.character = self.p.attachNewNode('EclipseCharacter')
        self.character.setPos(0, 0, 0)
        self.character.setScale(1.0)
        self.character.setTwoSided(True)

        skin = (.56, .37, .28, 1); skin2 = (.68, .46, .35, 1); skin_dark = (.30, .18, .14, 1)
        hair = (.018, .014, .012, 1); eye = (.01, .012, .015, 1); white = (.85, .87, .88, 1)
        jacket = (.035, .075, .095, 1); jacket2 = (.055, .14, .18, 1); jacket3 = (.10, .23, .27, 1)
        pants = (.025, .032, .040, 1); pants2 = (.05, .06, .07, 1); shoe = (.012, .014, .017, 1)
        metal = (.18, .22, .24, 1); accent = (.10, .55, .75, 1)

        S = self.sphere
        # Legs and boots
        S('boot_l', -.28, -.10, .18, .28, .48, .18, shoe, self.character)
        S('boot_r', .28, -.10, .18, .28, .48, .18, shoe, self.character)
        S('sole_l', -.28, -.10, .08, .30, .50, .055, metal, self.character, True)
        S('sole_r', .28, -.10, .08, .30, .50, .055, metal, self.character, True)
        S('shin_l', -.28, 0, .57, .20, .20, .48, pants, self.character)
        S('shin_r', .28, 0, .57, .20, .20, .48, pants, self.character)
        S('knee_l', -.28, -.02, .96, .22, .22, .17, pants2, self.character)
        S('knee_r', .28, -.02, .96, .22, .22, .17, pants2, self.character)
        S('thigh_l', -.28, 0, 1.20, .28, .26, .40, pants, self.character)
        S('thigh_r', .28, 0, 1.20, .28, .26, .40, pants, self.character)
        # Waist and torso
        S('pelvis', 0, 0, 1.10, .48, .30, .30, pants, self.character)
        S('belt', 0, 0, 1.35, .52, .32, .09, metal, self.character)
        S('belt_light', 0, -.32, 1.35, .11, .025, .08, accent, self.character, True)
        S('abdomen', 0, 0, 1.62, .48, .30, .42, jacket, self.character)
        S('chest', 0, 0, 1.91, .62, .35, .42, jacket, self.character)
        S('chest_panel', 0, -.34, 1.91, .37, .035, .30, jacket2, self.character)
        S('zipper', 0, -.378, 1.72, .018, .018, .30, metal, self.character, True)
        S('badge', 0, -.382, 2.02, .07, .02, .06, accent, self.character, True)
        S('collar_l', -.19, -.31, 2.13, .17, .08, .13, jacket3, self.character)
        S('collar_r', .19, -.31, 2.13, .17, .08, .13, jacket3, self.character)
        # Arms
        S('shoulder_l', -.64, 0, 2.04, .27, .31, .25, jacket2, self.character)
        S('shoulder_r', .64, 0, 2.04, .27, .31, .25, jacket2, self.character)
        S('upper_arm_l', -.79, 0, 1.72, .20, .22, .38, jacket, self.character)
        S('upper_arm_r', .79, 0, 1.72, .20, .22, .38, jacket, self.character)
        S('elbow_l', -.79, 0, 1.38, .21, .22, .15, jacket2, self.character)
        S('elbow_r', .79, 0, 1.38, .21, .22, .15, jacket2, self.character)
        S('forearm_l', -.79, 0, 1.13, .18, .20, .30, jacket, self.character)
        S('forearm_r', .79, 0, 1.13, .18, .20, .30, jacket, self.character)
        S('glove_l', -.79, -.01, .88, .17, .18, .17, shoe, self.character)
        S('glove_r', .79, -.01, .88, .17, .18, .17, shoe, self.character)
        # Neck and face
        S('neck', 0, 0, 2.28, .22, .21, .19, skin, self.character)
        S('neck_guard', 0, -.02, 2.20, .28, .23, .08, jacket2, self.character)
        S('head', 0, 0, 2.66, .40, .35, .46, skin2, self.character)
        S('jaw', 0, -.01, 2.51, .34, .32, .25, skin, self.character)
        S('ear_l', -.39, 0, 2.66, .075, .10, .13, skin, self.character)
        S('ear_r', .39, 0, 2.66, .075, .10, .13, skin, self.character)
        S('eye_l', -.145, -.345, 2.72, .065, .028, .065, eye, self.character, True)
        S('eye_r', .145, -.345, 2.72, .065, .028, .065, eye, self.character, True)
        S('iris_l', -.145, -.37, 2.72, .028, .012, .032, accent, self.character, True)
        S('iris_r', .145, -.37, 2.72, .028, .012, .032, accent, self.character, True)
        S('brow_l', -.145, -.33, 2.83, .12, .025, .035, hair, self.character)
        S('brow_r', .145, -.33, 2.83, .12, .025, .035, hair, self.character)
        S('nose', 0, -.36, 2.61, .07, .09, .12, skin, self.character)
        S('nose_tip', 0, -.425, 2.59, .05, .045, .045, skin2, self.character)
        S('mouth', 0, -.35, 2.48, .13, .025, .035, skin_dark, self.character)
        # Hair
        S('hair_cap', 0, .005, 2.98, .43, .37, .25, hair, self.character)
        S('hair_front', 0, -.30, 2.94, .35, .10, .15, hair, self.character)
        for i, x in enumerate((-.30, -.20, -.08, .08, .20, .30)):
            S(f'hair_{i}', x, -.25, 2.94, .12, .11, .18, hair, self.character)
        # Clothing seams and shoulder lights
        S('strap_l', -.34, -.33, 1.84, .05, .03, .34, jacket3, self.character)
        S('strap_r', .34, -.33, 1.84, .05, .03, .34, jacket3, self.character)
        S('shoulder_light_l', -.65, -.28, 2.10, .07, .025, .07, accent, self.character, True)
        S('shoulder_light_r', .65, -.28, 2.10, .07, .025, .07, accent, self.character, True)
        self.character.show()
        self.character.flattenLight()

    def lights(self):
        self.player_light = PointLight('player_light')
        self.player_light.setColor(Vec4(.45, .60, .78, 1))
        self.player_light.setAttenuation((1, .10, .025))
        self.player_light_node = self.p.attachNewNode(self.player_light)
        self.player_light_node.setPos(0, -1.0, 2.0)
        self.render.setLight(self.player_light_node)

    def input(self):
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(key + '-up', self.set_key, [key, False])
        self.accept('escape', self.toggle_mouse)
        self.accept('r', self.toggle_camera)
        self.accept('f', self.toggle_flashlight)
        self.accept('p', self.toggle_pause)
        self.accept('e', self.interact)
        self.accept('space', self.jump)

    def set_key(self, key, value): self.keys[key] = value
    def toggle_mouse(self): self.mouse_captured = not self.mouse_captured; self.center()
    def capture(self): self.mouse_captured = True; self.center()
    def center(self):
        if self.win:
            self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)

    def mouse(self):
        if not self.mouse_captured or self.paused: return
        cx = self.win.getXSize() // 2; cy = self.win.getYSize() // 2; q = self.win.getPointer(0)
        dx = q.getX() - cx; dy = q.getY() - cy
        if dx or dy:
            self.target_yaw -= dx * self.sensitivity
            self.target_pitch = max(-55, min(38, self.target_pitch - dy * self.sensitivity))
            self.center()

    def toggle_camera(self):
        self.camera_mode = 'first' if self.camera_mode == 'third' else 'third'
        if self.camera_mode == 'first': self.character.hide(); self.message('BİRİNCİ ŞAHIS')
        else: self.character.show(); self.message('ÜÇÜNCÜ ŞAHIS')

    def update_camera(self, dt):
        self.pitch += (self.target_pitch - self.pitch) * min(1.0, dt * 9.0)
        self.yaw += (self.target_yaw - self.yaw) * min(1.0, dt * 12.0)
        self.p.setH(self.yaw)
        if self.camera_mode == 'first':
            moving = any(self.keys[k] for k in ('w','a','s','d'))
            bob = math.sin(self.bob) * (.025 if moving else 0.0)
            self.camera.setPos(self.p.getPos() + Vec3(0,0,2.08+bob))
            self.camera.setHpr(self.yaw, self.pitch, 0)
        else:
            y = math.radians(self.yaw); p = math.radians(self.pitch)
            target = self.p.getPos() + Vec3(0,0,1.42)
            horizontal = self.camera_distance * math.cos(p)
            desired = Vec3(target.x - math.sin(y)*horizontal, target.y - math.cos(y)*horizontal, target.z + self.camera_height + self.camera_distance*math.sin(p))
            current = self.camera.getPos(); smooth = min(1.0, dt*8.5)
            self.camera.setPos(current + (desired-current)*smooth)
            self.camera.lookAt(target)

    def update(self, task):
        dt = min(.05, globalClock.getDt())
        if hasattr(self, 'mouse'): self.mouse()
        if not self.paused:
            move = Vec3(0,0,0)
            if self.keys['w']: move.y += 1
            if self.keys['s']: move.y -= 1
            if self.keys['a']: move.x -= 1
            if self.keys['d']: move.x += 1
            if move.lengthSquared() > 0:
                move.normalize()
                move = Vec3(move.x*math.cos(math.radians(self.yaw)) + move.y*math.sin(math.radians(self.yaw)), -move.x*math.sin(math.radians(self.yaw)) + move.y*math.cos(math.radians(self.yaw)), 0)
                speed = self.sprint_speed if self.keys['shift'] and self.stamina > 0 else self.speed
                self.p.setPos(self.p.getPos() + move * speed * dt)
                self.bob += dt * (12 if speed > self.speed else 8)
                if self.keys['shift']: self.stamina = max(0, self.stamina - 24*dt)
            else: self.stamina = min(100, self.stamina + 15*dt)
            self.vz -= self.gravity * dt
            self.p.setZ(max(.70, self.p.getZ() + self.vz*dt))
            if self.p.getZ() <= .70: self.p.setZ(.70); self.vz=0; self.on_ground=True
            else: self.on_ground=False
        self.update_camera(dt)
        self.graphics_system.update(dt)
        return Task.cont

    def jump(self):
        if self.on_ground and not self.paused: self.vz = self.jump_speed; self.on_ground=False
    def toggle_flashlight(self): self.flashlight = not self.flashlight; self.message('FENER: ' + ('AÇIK' if self.flashlight else 'KAPALI'))
    def toggle_pause(self): self.paused = not self.paused; self.message('OYUN DURAKLATILDI' if self.paused else 'OYUN DEVAM')
    def interact(self): self.message('ETKİLEŞİM')
    def message(self, text): self.message_timer=2.0; self.status_text.setText(text) if hasattr(self,'status_text') else None

    def hud(self):
        self.status_text = DirectLabel(text='ECLIPSE  •  HAYAT 100  •  STAMINA 100', scale=.045, pos=(-1.25,0, .88), text_align=TextNode.ALeft, frameColor=(0,0,0,0))
        self.status_text.reparentTo(self.a2dTopLeft)


if __name__ == '__main__':
    game = EclipseGame()
    game.run()
