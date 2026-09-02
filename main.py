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
        if solid:
            self.obstacles.append((x, y, sx, sy, z + sz))
        return m

    def building(self, x, y, sx, sy, h, wall_color, windows=3):
        # h is half-height: the building rests exactly on the ground.
        self.box('building', x, y, h, sx, sy, h, wall_color, True)
        self.box('roof', x, y, h * 2.03, sx * 1.04, sy * 1.04, .10, (.025, .03, .04, 1))

        # Front/back windows.
        for side in (-1, 1):
            for i in range(windows):
                yy = -sy * .72 + (2 * sy * .72) * (i / max(1, windows - 1))
                self.box('window', x + side * (sx + .035), y + yy, h * .72,
                         .035, .34, .40, (.22, .52, .68, 1), False, True)
                self.box('window2', x + side * (sx + .035), y + yy, h * 1.38,
                         .035, .34, .40, (.16, .34, .48, 1), False, True)

        # Side windows.
        for side in (-1, 1):
            for i in range(2):
                xx = -sx * .55 + i * sx * .55
                self.box('side_window', x + xx, y + side * (sy + .035), h * .78,
                         .30, .035, .38, (.20, .48, .62, 1), False, True)

        # Entrance, awning and rooftop equipment.
        self.box('door', x, y - sy - .045, .85, .52, .06, .85, (.045, .055, .065, 1), False)
        self.box('door_light', x, y - sy - .065, 1.35, .09, .025, .09, (1.0, .66, .30, 1), False, True)
        self.box('awning', x, y - sy - .16, 1.72, .85, .32, .08, (.08, .09, .11, 1), False)
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
        # Trees are deliberately placed only on grass/sidewalk zones.
        self.box('trunk', x, y, 1.0 * s, .22 * s, .22 * s, 1.0 * s, (.16, .075, .035, 1), True)
        self.box('crown_a', x, y, 2.05 * s, .95 * s, .95 * s, .65 * s, (.025, .11, .055, 1))
        self.box('crown_b', x, y, 2.65 * s, .72 * s, .72 * s, .55 * s, (.02, .085, .045, 1))
        self.box('crown_c', x, y, 3.10 * s, .48 * s, .48 * s, .42 * s, (.035, .13, .065, 1))

    def world(self):
        # Clean city layout: roads, sidewalks, grass blocks and buildings never overlap.
        self.box('ground', 0, 0, -.35, 32, 32, .35, (.055, .065, .062, 1))

        road = (.032, .036, .041, 1)
        self.box('road_ns', 0, 0, .02, 4.2, 32, .025, road)
        self.box('road_ew', 0, 0, .025, 32, 4.2, .025, road)

        # Raised sidewalks define the four city blocks.
        sidewalk = (.12, .125, .12, 1)
        for x in (-7.0, 7.0):
            self.box('sidewalk_v', x, 0, .075, 1.0, 31, .075, sidewalk, True)
        for y in (-7.0, 7.0):
            self.box('sidewalk_h', 0, y, .075, 31, 1.0, .075, sidewalk, True)

        # Road markings are centered and never run through buildings.
        mark = (.72, .67, .45, 1)
        for q in range(-28, 29, 4):
            self.box('lane_mark', 0, q, .065, .08, 1.05, .015, mark, False, True)
            self.box('lane_mark', q, 0, .067, 1.05, .08, .015, mark, False, True)

        # Four clean blocks with buildings placed away from road corridors.
        buildings = [
            (-14.0, 13.5, 3.6, 3.7, 3.4, (.18, .20, .23, 1), 3),
            (-22.5, 14.0, 3.2, 3.4, 2.9, (.24, .22, .19, 1), 2),
            (14.0, 13.5, 3.8, 3.5, 3.8, (.20, .22, .25, 1), 3),
            (22.5, 14.0, 3.0, 3.4, 2.8, (.26, .23, .20, 1), 2),
            (-14.0, -13.5, 3.6, 3.6, 3.1, (.19, .22, .20, 1), 3),
            (-22.0, -14.0, 3.0, 3.2, 2.7, (.22, .21, .23, 1), 2),
            (14.0, -13.5, 3.7, 3.5, 3.5, (.23, .20, .19, 1), 3),
            (22.0, -14.0, 3.1, 3.1, 2.9, (.21, .23, .22, 1), 2),
        ]
        for b in buildings:
            self.building(*b)

        # Trees stay in grass corners, not on the road.
        tree_positions = [
            (-28, 9, 1.0), (-25, 23, .9), (-18, 24, 1.1), (-9, 26, .8),
            (9, 26, .9), (19, 24, 1.0), (27, 22, .9), (28, 9, 1.0),
            (-28, -9, .9), (-26, -23, 1.0), (-18, -24, .8), (-9, -26, 1.0),
            (9, -26, .9), (19, -24, 1.0), (27, -22, .9), (28, -9, 1.0),
        ]
        for x, y, s in tree_positions:
            self.tree(x, y, s)

        # Street lamps line the sidewalks, never the driving lanes.
        for x, y in [
            (-6, -16), (6, -16), (-6, -8), (6, -8), (-6, 8), (6, 8), (-6, 16), (6, 16),
            (-16, -6), (-16, 6), (16, -6), (16, 6)
        ]:
            self.lamp(x, y)

        # Small believable street props.
        self.box('crate_a', 9.5, 9.0, .65, .75, .75, .65, (.30, .19, .08, 1), True)
        self.box('crate_b', 10.9, 9.2, .48, .55, .55, .48, (.24, .15, .06, 1), True)
        self.box('container', 10.5, -10.0, 1.25, 2.0, 3.2, 1.25, (.055, .16, .19, 1), True)
        self.box('barrier', -9.2, 6.0, .48, 2.2, .32, .48, (.16, .17, .18, 1), True)
        self.box('barrier_stripe', -9.2, 5.65, .50, 1.8, .03, .15, (.72, .52, .18, 1), False, True)

        # Terminals remain accessible from the sidewalks.
        for i, (x, y) in enumerate([(-9, -4), (6, 14), (17, -3)]):
            t = self.box('terminal', x, y, 1.0, .58, .40, 1.0, (.025, .22, .28, 1), True)
            self.box('screen', x, y - .43, 1.16, .34, .025, .22, (.10, .75, .95, 1), False, True)
            self.terminals.append((t, f'Terminal {i + 1}'))

        # Solid boundary walls are grounded and aligned.
        wall = (.025, .032, .042, 1)
        self.box('north', 0, 31.5, 2.0, 32, .5, 2.0, wall, True)
        self.box('south', 0, -31.5, 2.0, 32, .5, 2.0, wall, True)
        self.box('east', 31.5, 0, 2.0, .5, 32, 2.0, wall, True)
        self.box('west', -31.5, 0, 2.0, .5, 32, 2.0, wall, True)

    def player(self):
        self.p = self.render.attachNewNode('Player')
        self.p.setPos(0, -2, 1)
        self.character = self.render.attachNewNode('EclipseCharacter')
        self.character.reparentTo(self.p)

        # Detailed male character assembled from clean low-poly parts.
        skin = (.52, .34, .25, 1)
        skin_light = (.66, .44, .33, 1)
        jacket = (.045, .11, .15, 1)
        jacket_light = (.075, .17, .21, 1)
        pants = (.035, .045, .055, 1)
        shoes = (.018, .020, .024, 1)
        hair = (.025, .018, .015, 1)

        self.box('pelvis', 0, 0, .72, .48, .30, .32, pants, True, parent=self.character)
        self.box('torso', 0, 0, 1.48, .58, .34, .72, jacket, False, parent=self.character)
        self.box('chest_panel', 0, -.355, 1.55, .34, .025, .42, jacket_light, False, parent=self.character)
        self.box('neck', 0, 0, 2.18, .20, .20, .16, skin, False, parent=self.character)
        self.box('head', 0, 0, 2.62, .38, .34, .40, skin_light, False, parent=self.character)
        self.box('hair_top', 0, 0, 3.00, .39, .35, .16, hair, False, parent=self.character)
        self.box('hair_side_l', -.38, 0, 2.79, .06, .32, .20, hair, False, parent=self.character)
        self.box('hair_side_r', .38, 0, 2.79, .06, .32, .20, hair, False, parent=self.character)
        self.box('eye_l', -.14, -.345, 2.67, .055, .025, .055, (.015, .02, .025, 1), False, True, parent=self.character)
        self.box('eye_r', .14, -.345, 2.67, .055, .025, .055, (.015, .02, .025, 1), False, True, parent=self.character)
        self.box('arm_l', -.70, 0, 1.50, .18, .25, .62, jacket, False, parent=self.character)
        self.box('arm_r', .70, 0, 1.50, .18, .25, .62, jacket, False, parent=self.character)
        self.box('hand_l', -.70, 0, .82, .18, .20, .20, skin, False, parent=self.character)
        self.box('hand_r', .70, 0, .82, .18, .20, .20, skin, False, parent=self.character)
        self.box('leg_l', -.29, 0, .02, .22, .25, .70, pants, True, parent=self.character)
        self.box('leg_r', .29, 0, .02, .22, .25, .70, pants, True, parent=self.character)
        self.box('shoe_l', -.29, -.12, -.68, .28, .42, .18, shoes, True, parent=self.character)
        self.box('shoe_r', .29, -.12, -.68, .28, .42, .18, shoes, True, parent=self.character)
        self.box('shoulder_l', -.60, 0, 1.92, .28, .35, .22, jacket_light, False, parent=self.character)
        self.box('shoulder_r', .60, 0, 1.92, .28, .35, .22, jacket_light, False, parent=self.character)

        self.character.show()

    def lights(self):
        # Player flashlight/light is separate from the global atmosphere system.
        self.pl = PointLight('player_light')
        self.pl.setColor(Vec4(.72, .86, 1.0, 1))
        self.pl.setAttenuation((1, .11, .028))
        self.pln = self.render.attachNewNode(self.pl)
        self.pln.reparentTo(self.p)
        self.pln.setPos(0, .55, 1.65)
        self.render.setLight(self.pln)

        # Local cool fill lights make facades readable without making the scene flat.
        for i, pos in enumerate([(-10, 11, 4), (10, 11, 4), (-10, -11, 4), (10, -11, 4)]):
            self.graphics_system.create_fill_light(
                f'building_fill_{i}', pos, (.28, .34, .44, 1), (1, .20, .055)
            )

    def hud(self):
        self.title = DirectLabel(text='ECLIPSE', scale=.055, pos=(-1.28, 0, .91),
                                 text_align=TextNode.ALeft, text_fg=(.42, .8, 1, 1),
                                 frameColor=(0, 0, 0, 0))
        self.obj = DirectLabel(text='GÖREV: 3 terminali keşfet', scale=.034, pos=(-1.28, 0, .82),
                               text_align=TextNode.ALeft, text_fg=(.86, .9, .96, 1),
                               frameColor=(0, 0, 0, 0))
        self.stats = DirectLabel(text='', scale=.031, pos=(-1.28, 0, .72),
                                 text_align=TextNode.ALeft, text_fg=(.68, .77, .85, 1),
                                 frameColor=(0, 0, 0, 0))
        self.msg = DirectLabel(text='', scale=.04, pos=(0, 0, -.76),
                               text_align=TextNode.ACenter, text_fg=(1, .82, .42, 1),
                               frameColor=(0, 0, 0, 0))
        DirectLabel(text='WASD | SHIFT koş | SPACE zıpla | F fener | E etkileşim | R kamera | P duraklat | ESC mouse',
                    scale=.029, pos=(0, 0, -.92), text_align=TextNode.ACenter,
                    text_fg=(.66, .72, .8, 1), frameColor=(0, 0, 0, 0))
        self.fps = DirectLabel(text='FPS: --', scale=.031, pos=(1.28, 0, .91),
                               text_align=TextNode.ARight, text_fg=(.68, .75, .84, 1),
                               frameColor=(0, 0, 0, 0))
        self.ft = 0
        self.frames = 0
        self.fpsv = 0

    def input(self):
        for k in ('w', 'a', 's', 'd'):
            self.accept(k, self.key, [k, True])
            self.accept(k + '-up', self.key, [k, False])
        self.accept('shift', self.key, ['shift', True])
        self.accept('shift-up', self.key, ['shift', False])
        self.accept('space', self.jump)
        self.accept('f', self.toggle_flash)
        self.accept('e', self.interact)
        self.accept('r', self.toggle_camera)
        self.accept('p', self.pause)
        self.accept('escape', self.toggle_mouse)

    def key(self, k, v):
        self.keys[k] = v

    def jump(self):
        if not self.paused and self.on_ground:
            self.vz = self.jump_speed
            self.on_ground = False

    def pause(self):
        self.paused = not self.paused
        self.message('Oyun duraklatıldı' if self.paused else 'Oyun devam ediyor')

    def toggle_flash(self):
        self.flashlight = not self.flashlight
        if self.flashlight:
            self.render.setLight(self.pln)
        else:
            self.render.clearLight(self.pln)
        self.message('Fener açıldı' if self.flashlight else 'Fener kapatıldı')

    def toggle_camera(self):
        self.camera_mode = 'first' if self.camera_mode == 'third' else 'third'
        if self.camera_mode == 'first':
            self.character.hide()
            self.message('BİRİNCİ ŞAHIS')
        else:
            self.character.show()
            self.message('ÜÇÜNCÜ ŞAHIS')

    def message(self, text):
        self.msg['text'] = text
        self.message_timer = 2.0

    def capture(self):
        p = WindowProperties()
        p.setCursorHidden(True)
        self.win.requestProperties(p)
        self.center()

    def center(self):
        self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)

    def toggle_mouse(self):
        self.mouse_captured = not self.mouse_captured
        p = WindowProperties()
        p.setCursorHidden(self.mouse_captured)
        self.win.requestProperties(p)
        if self.mouse_captured:
            self.center()

    def mouse(self):
        if not self.mouse_captured or self.paused:
            return
        cx = self.win.getXSize() // 2
        cy = self.win.getYSize() // 2
        q = self.win.getPointer(0)
        dx = q.getX() - cx
        dy = q.getY() - cy
        if dx or dy:
            # Mouse yaw directly turns the character. Third-person camera follows it.
            self.yaw -= dx * self.sensitivity
            self.target_pitch = max(-55, min(38, self.target_pitch - dy * self.sensitivity))
            self.center()

    def blocked(self, x, y):
        for ox, oy, hx, hy, top in self.obstacles:
            if self.p.getZ() - .82 < top:
                qx = max(ox - hx, min(x, ox + hx))
                qy = max(oy - hy, min(y, oy + hy))
                if (x - qx) ** 2 + (y - qy) ** 2 < self.radius ** 2:
                    return True
        return False

    def move(self, dx, dy):
        x, y = self.p.getX(), self.p.getY()
        if not self.blocked(x + dx, y):
            self.p.setX(x + dx)
        x, y = self.p.getX(), self.p.getY()
        if not self.blocked(x, y + dy):
            self.p.setY(y + dy)

    def interact(self):
        if self.paused:
            return
        best = 999
        near = None
        for node, label in self.terminals:
            d = (node.getPos(self.render) - self.p.getPos(self.render)).length()
            if d < best:
                best = d
                near = label
        if near and best < 3.3:
            self.found.add(near)
            self.obj['text'] = f'GÖREV: {len(self.found)}/3 terminal bulundu'
            self.message(near + ' incelendi')
            if len(self.found) == 3:
                self.message('BÖLGE KEŞFİ TAMAMLANDI!')

    def update_camera(self, dt):
        self.pitch += (self.target_pitch - self.pitch) * min(1.0, dt * 9.0)
        self.p.setH(self.yaw)

        if self.camera_mode == 'first':
            # Eye-level camera, with subtle walking bob.
            moving = any(self.keys[k] for k in ('w', 'a', 's', 'd'))
            bob = math.sin(self.bob) * (.025 if moving else 0.0)
            eye = self.p.getPos() + Vec3(0, 0, 2.05 + bob)
            self.camera.setPos(eye)
            self.camera.setHpr(self.yaw, self.pitch, 0)
        else:
            # Smooth over-the-shoulder third person camera.
            y = math.radians(self.yaw)
            p = math.radians(self.pitch)
            target = self.p.getPos() + Vec3(0, 0, 1.55)
            horizontal = self.camera_distance * math.cos(p)
            desired = Vec3(
                target.x - math.sin(y) * horizontal,
                target.y - math.cos(y) * horizontal,
                target.z + self.camera_height + self.camera_distance * math.sin(p),
            )
            current = self.camera.getPos()
            smooth = min(1.0, dt * 8.5)
            self.camera.setPos(current + (desired - current) * smooth)
            self.camera.lookAt(target)

    def update(self, task):
        dt = min(globalClock.getDt(), .05)
        self.mouse()

        if not self.paused:
            mx = (-1 if self.keys['a'] else 0) + (1 if self.keys['d'] else 0)
            my = (1 if self.keys['w'] else 0) + (-1 if self.keys['s'] else 0)
            moving = math.hypot(mx, my) > 0

            if moving:
                length = math.hypot(mx, my)
                mx /= length
                my /= length
                y = math.radians(self.yaw)
                fx, fy = math.sin(y), math.cos(y)
                rx, ry = math.cos(y), -math.sin(y)
                sprint = self.keys['shift'] and self.stamina > 1
                sp = self.sprint_speed if sprint else self.speed
                self.move((fx * my + rx * mx) * sp * dt,
                          (fy * my + ry * mx) * sp * dt)
                self.stamina = max(0, self.stamina - 28 * dt) if sprint else min(100, self.stamina + 16 * dt)
                self.bob += dt * (13 if sprint else 9)
            else:
                self.stamina = min(100, self.stamina + 22 * dt)

            self.vz -= self.gravity * dt
            z = self.p.getZ() + self.vz * dt
            if z <= 1:
                z = 1
                self.vz = 0
                self.on_ground = True
            else:
                self.on_ground = False
            self.p.setZ(z)
            self.p.setX(max(-29, min(29, self.p.getX())))
            self.p.setY(max(-29, min(29, self.p.getY())))

        self.update_camera(dt)
        self.graphics_system.update(dt)

        self.message_timer -= dt
        if self.message_timer <= 0:
            self.msg['text'] = ''

        self.ft += dt
        self.frames += 1
        if self.ft >= .5:
            self.fpsv = int(self.frames / self.ft)
            self.ft = 0
            self.frames = 0

        state = 'YERDE' if self.on_ground else 'HAVADA'
        mouse = 'AKTİF' if self.mouse_captured else 'SERBEST'
        mode = '1. ŞAHIS' if self.camera_mode == 'first' else '3. ŞAHIS'
        self.stats['text'] = (
            f'CAN: {self.health}%  STAMINA: {int(self.stamina)}%\n'
            f'KONUM: {self.p.getX():.1f}, {self.p.getY():.1f}\n'
            f'KAMERA: {mode} | DURUM: {state} | FENER: {"AÇIK" if self.flashlight else "KAPALI"} | MOUSE: {mouse}'
        )
        self.fps['text'] = f'FPS: {self.fpsv}'
        return Task.cont


if __name__ == '__main__':
    EclipseGame().run()
