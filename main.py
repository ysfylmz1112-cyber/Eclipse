from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import DirectLabel
from panda3d.core import AmbientLight, DirectionalLight, Fog, TextNode, Vec3, Vec4, WindowProperties, TransparencyAttrib
import math
import random


class EclipseGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.set_background_color(0.008, 0.012, 0.022, 1)

        self.keys = {k: False for k in ('w', 'a', 's', 'd', 'shift')}
        self.speed = 5.5
        self.sprint_speed = 8.5
        self.gravity = 22.0
        self.jump_speed = 8.2
        self.vz = 0.0
        self.on_ground = True
        self.radius = 0.62

        self.health = 100
        self.stamina = 100.0
        self.flashlight = True
        self.mouse_captured = True
        self.sensitivity = 0.035
        self.yaw = 0.0
        self.pitch = -9.0
        self.target_pitch = -9.0
        self.camera_distance = 7.5
        self.camera_height = 2.8
        self.obstacles = []
        self.interactables = []
        self.discovered = set()
        self.message_timer = 0.0

        random.seed(12)

        self.build_world()
        self.build_player()
        self.build_lighting()
        self.build_hud()
        self.bind_input()
        self.capture_mouse()
        self.taskMgr.add(self.update, 'eclipse_update')

    def box(self, name, x, y, z, sx, sy, sz, color, solid=False, emissive=False):
        m = self.loader.loadModel('models/box')
        m.setName(name)
        m.reparentTo(self.render)
        m.setPos(x, y, z)
        m.setScale(sx, sy, sz)
        m.setColor(*color)
        if emissive:
            m.setLightOff()
        if solid:
            self.obstacles.append((x, y, sx, sy, z + sz))
        return m

    def make_tree(self, x, y, scale=1.0):
        self.box('TreeTrunk', x, y, 1.4 * scale, .32 * scale, .32 * scale, 1.4 * scale,
                 (0.18, 0.09, 0.035, 1), True)
        for z, s in ((2.8, 1.25), (3.5, 1.0), (4.15, .72)):
            self.box('TreeFoliage', x, y, z * scale, s * scale, s * scale, .65 * scale,
                     (0.035, 0.16, 0.075, 1), False)

    def make_building(self, x, y, sx, sy, h):
        self.box('Building', x, y, h, sx, sy, h, (0.09, 0.105, 0.125, 1), True)
        self.box('Roof', x, y, h * 2.08, sx * 1.04, sy * 1.04, .10,
                 (0.025, 0.03, 0.04, 1))
        for yy in (-sy * .62, 0, sy * .62):
            self.box('Window', x + sx * 1.01, y + yy, h * 1.15,
                     .035, .42, .48, (0.20, 0.43, 0.55, 1), False, True)

    def build_world(self):
        self.box('Ground', 0, 0, -0.35, 32, 32, .35, (0.055, 0.075, 0.07, 1))
        tile_colors = [
            (0.065, 0.085, 0.078, 1), (0.052, 0.070, 0.064, 1),
            (0.075, 0.092, 0.082, 1), (0.048, 0.065, 0.060, 1)
        ]
        for ix in range(-5, 6):
            for iy in range(-5, 6):
                if (ix + iy) % 3 == 0:
                    self.box('GroundPatch', ix * 5.5, iy * 5.5, .012,
                             2.7, 2.7, .015, random.choice(tile_colors))

        self.box('Road', 0, 0, .025, 5.0, 31, .025, (0.045, 0.048, 0.052, 1))
        for y in range(-28, 29, 4):
            self.box('RoadMark', 0, y, .06, .12, 1.0, .025, (0.72, 0.66, 0.40, 1))

        self.make_building(-12, 10, 3.5, 4.0, 3.5)
        self.make_building(12, 12, 4.0, 3.0, 4.2)
        self.make_building(-13, -12, 3.0, 3.5, 3.0)
        self.make_building(13, -10, 4.0, 3.0, 3.6)

        for x, y, s in [
            (-22, -20, 1.0), (-19, -15, .8), (-23, 8, 1.1),
            (-18, 19, .9), (20, 18, 1.0), (23, 8, .8),
            (21, -20, 1.1), (-20, -2, .8), (20, 1, .9)
        ]:
            self.make_tree(x, y, s)

        for x, y in [(-4, -15), (4, -7), (-4, 1), (4, 9), (-4, 17)]:
            self.box('LampPole', x, y, 2.7, .10, .10, 2.7, (0.08, 0.09, 0.10, 1), True)
            self.box('Lamp', x, y, 5.45, .28, .28, .12, (0.85, 0.65, 0.25, 1), False, True)

        self.box('CrateA', 7, 7, .9, 1.3, 1.3, .9, (0.34, 0.22, 0.10, 1), True)
        self.box('CrateB', 8.8, 7.2, .9, 1.0, 1.0, .9, (0.30, 0.19, 0.09, 1), True)
        self.box('Barrier', -7, 6, .7, 3.0, .45, .7, (0.18, 0.20, 0.22, 1), True)
        self.box('Container', 8, -9, 1.5, 2.5, 4.0, 1.5, (0.08, 0.23, 0.28, 1), True)

        wall = (0.025, 0.032, 0.045, 1)
        self.box('WallN', 0, 31.5, 2.5, 32, .5, 2.5, wall, True)
        self.box('WallS', 0, -31.5, 2.5, 32, .5, 2.5, wall, True)
        self.box('WallE', 31.5, 0, 2.5, .5, 32, 2.5, wall, True)
        self.box('WallW', -31.5, 0, 2.5, .5, 32, 2.5, wall, True)

        for i, (x, y) in enumerate([(-8, -5), (6, 14), (16, -3)]):
            terminal = self.box(f'Terminal{i}', x, y, 1.2, .7, .45, 1.2,
                                (0.06, 0.30, 0.36, 1), True)
            self.interactables.append((terminal, f'Terminal {i + 1}'))

        for _ in range(80):
            x = random.uniform(-28, 28)
            y = random.uniform(-28, 28)
            z = random.uniform(.2, 5.5)
            self.box('Dust', x, y, z, .025, .025, .025,
                     (0.55, 0.62, 0.65, .22), False, True)

    def build_player(self):
        self.player = self.render.attachNewNode('Player')
        self.player.setPos(0, 0, 1.0)

        body = self.loader.loadModel('models/box')
        body.reparentTo(self.player)
        body.setScale(.62, .42, 1.0)
        body.setColor(.12, .27, .34, 1)

        head = self.loader.loadModel('models/box')
        head.reparentTo(self.player)
        head.setScale(.43, .40, .43)
        head.setPos(0, 0, 1.43)
        head.setColor(.40, .50, .52, 1)

        shoulder = self.box('PlayerLight', 0, .45, 1.15, .06, .06, .06,
                            (1.0, .82, .52, 1), False, True)
        shoulder.reparentTo(self.player)

    def build_lighting(self):
        self.ambient = AmbientLight('ambient')
        self.ambient.setColor(Vec4(.24, .27, .32, 1))
        self.render.setLight(self.render.attachNewNode(self.ambient))

        self.sun = DirectionalLight('moon_sun')
        self.sun.setColor(Vec4(.75, .80, .92, 1))
        self.sun_node = self.render.attachNewNode(self.sun)
        self.sun_node.setHpr(-38, -58, 0)
        self.render.setLight(self.sun_node)

        self.flash = self.box('FlashlightGlow', 0, 1.3, 1.35, .35, 1.2, .22,
                              (0.75, 0.88, 1.0, .55), False, True)
        self.flash.reparentTo(self.player)
        self.flash.setTransparency(TransparencyAttrib.MAlpha)

        fog = Fog('atmosphere')
        fog.setColor(.008, .012, .022)
        fog.setExpDensity(.010)
        self.render.setFog(fog)

    def build_hud(self):
        self.title = DirectLabel(text='ECLIPSE', scale=.055, pos=(-1.28, 0, .90),
                                 text_align=TextNode.ALeft, text_fg=(.45, .82, 1, 1),
                                 frameColor=(0, 0, 0, 0))
        self.objective = DirectLabel(text='GÖREV: Bölgeyi keşfet', scale=.035,
                                     pos=(-1.28, 0, .81), text_align=TextNode.ALeft,
                                     text_fg=(.85, .90, .96, 1), frameColor=(0, 0, 0, 0))
        self.stats = DirectLabel(text='', scale=.032, pos=(-1.28, 0, .73),
                                 text_align=TextNode.ALeft, text_fg=(.72, .80, .86, 1),
                                 frameColor=(0, 0, 0, 0))
        self.controls = DirectLabel(
            text='WASD hareket | SHIFT koş | SPACE zıpla | F fener | E etkileşim | ESC mouse',
            scale=.032, pos=(0, 0, -.92), text_align=TextNode.ACenter,
            text_fg=(.68, .74, .82, 1), frameColor=(0, 0, 0, 0)
        )
        self.message = DirectLabel(text='', scale=.040, pos=(0, 0, -.76),
                                   text_align=TextNode.ACenter, text_fg=(1, .86, .50, 1),
                                   frameColor=(0, 0, 0, 0))
        self.fps = DirectLabel(text='FPS: --', scale=.032, pos=(1.28, 0, .90),
                               text_align=TextNode.ARight, text_fg=(.70, .76, .84, 1),
                               frameColor=(0, 0, 0, 0))
        self.ft = 0.0
        self.frames = 0
        self.fps_value = 0

    def bind_input(self):
        for k in ('w', 'a', 's', 'd'):
            self.accept(k, self.set_key, [k, True])
            self.accept(k + '-up', self.set_key, [k, False])
        self.accept('shift', self.set_key, ['shift', True])
        self.accept('shift-up', self.set_key, ['shift', False])
        self.accept('space', self.jump)
        self.accept('escape', self.toggle_mouse)
        self.accept('f', self.toggle_flashlight)
        self.accept('e', self.interact)

    def set_key(self, key, value):
        self.keys[key] = value

    def jump(self):
        if self.on_ground:
            self.vz = self.jump_speed
            self.on_ground = False

    def toggle_flashlight(self):
        self.flashlight = not self.flashlight
        if self.flashlight:
            self.flash.show()
        else:
            self.flash.hide()
        self.show_message('Fener açıldı' if self.flashlight else 'Fener kapatıldı')

    def interact(self):
        nearest = None
        best = 999.0
        for node, label in self.interactables:
            d = (node.getPos(self.render) - self.player.getPos(self.render)).length()
            if d < best:
                best = d
                nearest = label
        if nearest and best < 3.2:
            self.discovered.add(nearest)
            self.objective['text'] = f'GÖREV: {len(self.discovered)}/3 terminal bulundu'
            self.show_message(f'{nearest} incelendi')
            if len(self.discovered) == 3:
                self.show_message('Bölge keşfi tamamlandı!')

    def show_message(self, text):
        self.message['text'] = text
        self.message_timer = 2.2

    def capture_mouse(self):
        p = WindowProperties()
        p.setCursorHidden(True)
        self.win.requestProperties(p)
        self.center_mouse()

    def center_mouse(self):
        if self.win:
            self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)

    def toggle_mouse(self):
        self.mouse_captured = not self.mouse_captured
        p = WindowProperties()
        p.setCursorHidden(self.mouse_captured)
        self.win.requestProperties(p)
        if self.mouse_captured:
            self.center_mouse()

    def mouse_look(self):
        if not self.mouse_captured:
            return
        cx, cy = self.win.getXSize() // 2, self.win.getYSize() // 2
        pointer = self.win.getPointer(0)
        dx, dy = pointer.getX() - cx, pointer.getY() - cy
        if dx or dy:
            self.yaw -= dx * self.sensitivity
            self.target_pitch -= dy * self.sensitivity
            self.target_pitch = max(-55, min(32, self.target_pitch))
            self.center_mouse()

    def blocked(self, x, y):
        for ox, oy, hx, hy, top in self.obstacles:
            if self.player.getZ() - 0.9 < top:
                qx = max(ox - hx, min(x, ox + hx))
                qy = max(oy - hy, min(y, oy + hy))
                if (x - qx) ** 2 + (y - qy) ** 2 < self.radius ** 2:
                    return True
        return False

    def move(self, dx, dy):
        x, y = self.player.getX(), self.player.getY()
        if not self.blocked(x + dx, y):
            self.player.setX(x + dx)
        x, y = self.player.getX(), self.player.getY()
        if not self.blocked(x, y + dy):
            self.player.setY(y + dy)

    def update_camera(self):
        self.pitch += (self.target_pitch - self.pitch) * .12
        self.player.setH(self.yaw)
        yaw = math.radians(self.yaw)
        pitch = math.radians(self.pitch)
        hdist = self.camera_distance * math.cos(pitch)
        target = self.player.getPos() + Vec3(0, 0, 1.15)
        self.camera.setPos(
            target.x - math.sin(yaw) * hdist,
            target.y - math.cos(yaw) * hdist,
            target.z + self.camera_height + self.camera_distance * math.sin(pitch)
        )
        self.camera.lookAt(target)

    def update(self, task):
        dt = min(globalClock.getDt(), .05)
        self.mouse_look()

        mx = (-1 if self.keys['a'] else 0) + (1 if self.keys['d'] else 0)
        my = (1 if self.keys['w'] else 0) + (-1 if self.keys['s'] else 0)
        length = math.hypot(mx, my)

        sprinting = self.keys['shift'] and my > 0 and self.stamina > 0 and length > 0
        if sprinting:
            self.stamina = max(0, self.stamina - 28 * dt)
        else:
            self.stamina = min(100, self.stamina + 18 * dt)

        if length:
            mx, my = mx / length, my / length
            yaw = math.radians(self.yaw)
            fx, fy = math.sin(yaw), math.cos(yaw)
            rx, ry = math.cos(yaw), -math.sin(yaw)
            speed = self.sprint_speed if sprinting else self.speed
            self.move((fx * my + rx * mx) * speed * dt,
                      (fy * my + ry * mx) * speed * dt)

        self.vz -= self.gravity * dt
        z = self.player.getZ() + self.vz * dt
        if z <= 1.0:
            z, self.vz, self.on_ground = 1.0, 0.0, True
        else:
            self.on_ground = False
        self.player.setZ(z)

        self.player.setX(max(-30, min(30, self.player.getX())))
        self.player.setY(max(-30, min(30, self.player.getY())))
        self.update_camera()

        self.ft += dt
        self.frames += 1
        if self.ft >= .5:
            self.fps_value = int(self.frames / self.ft)
            self.ft, self.frames = 0, 0

        state = 'YERDE' if self.on_ground else 'HAVADA'
        self.stats['text'] = (
            f'CAN  {self.health}    STAMINA  {self.stamina:03.0f}\n'
            f'Konum  {self.player.getX():.1f}, {self.player.getY():.1f}    {state}'
        )
        self.fps['text'] = f'FPS: {self.fps_value}'

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message['text'] = ''

        return Task.cont


if __name__ == '__main__':
    EclipseGame().run()
