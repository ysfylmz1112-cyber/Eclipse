from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import AmbientLight, DirectionalLight, Fog, TextNode, Vec3, Vec4, WindowProperties
import math


class EclipseGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.set_background_color(0.015, 0.02, 0.035, 1)

        self.keys = {k: False for k in ('w', 'a', 's', 'd', 'shift')}
        self.speed = 6.0
        self.sprint_speed = 9.0
        self.gravity = 22.0
        self.jump_speed = 8.0
        self.vz = 0.0
        self.on_ground = True
        self.height = 2.0
        self.radius = 0.65

        self.mouse_captured = True
        self.sensitivity = 0.055
        self.yaw = 0.0
        self.pitch = -10.0
        self.target_pitch = -10.0
        self.camera_distance = 8.0
        self.camera_height = 3.0
        self.obstacles = []

        self.build_world()
        self.build_player()
        self.build_lighting()
        self.build_hud()
        self.bind_input()
        self.capture_mouse()
        self.taskMgr.add(self.update, 'eclipse_update')

    def box(self, name, x, y, z, sx, sy, sz, color, solid=False):
        m = self.loader.loadModel('models/box')
        m.setName(name)
        m.reparentTo(self.render)
        m.setPos(x, y, z)
        m.setScale(sx, sy, sz)
        m.setColor(*color)
        if solid:
            self.obstacles.append((x, y, sx, sy, z + sz))
        return m

    def build_world(self):
        # Top surface of this platform is Z=0; player starts on it.
        self.box('StartingPlatform', 0, 0, -0.25, 20, 20, 0.25, (0.08, 0.22, 0.30, 1))

        self.box('RedBlock', 7, 8, 1, 2, 2, 1, (0.65, 0.16, 0.12, 1), True)
        self.box('GreenBlock', -8, 7, 1.5, 2, 3, 1.5, (0.12, 0.55, 0.25, 1), True)
        self.box('GoldBlock', 8, -6, 0.75, 3, 1.5, 0.75, (0.70, 0.48, 0.10, 1), True)
        self.box('PurpleBlock', -7, -7, 1, 2.5, 2.5, 1, (0.34, 0.18, 0.65, 1), True)
        self.box('NorthBlock', 0, 10, 0.6, 4, 1, 0.6, (0.30, 0.55, 0.75, 1), True)
        self.box('EastBlock', 11, 0, 1.2, 1, 4, 1.2, (0.12, 0.42, 0.70, 1), True)
        self.box('WestBlock', -11, 0, 0.8, 1, 3, 0.8, (0.70, 0.18, 0.35, 1), True)

        wall = (0.045, 0.06, 0.09, 1)
        self.box('WallN', 0, 20.5, 2, 21, .5, 2, wall, True)
        self.box('WallS', 0, -20.5, 2, 21, .5, 2, wall, True)
        self.box('WallE', 20.5, 0, 2, .5, 21, 2, wall, True)
        self.box('WallW', -20.5, 0, 2, .5, 21, 2, wall, True)

        for x, y in [(-15, -15), (15, -15), (-15, 15), (15, 15)]:
            self.box('Marker', x, y, 1.5, .35, .35, 1.5, (0.2, 0.65, 0.9, 1))

    def build_player(self):
        self.player = self.render.attachNewNode('Player')
        self.player.setPos(0, 0, 1.0)
        body = self.loader.loadModel('models/box')
        body.reparentTo(self.player)
        body.setScale(.65, .65, 1.0)
        body.setColor(.10, .55, .95, 1)
        head = self.loader.loadModel('models/box')
        head.reparentTo(self.player)
        head.setScale(.48, .48, .45)
        head.setPos(0, 0, 1.45)
        head.setColor(.25, .75, 1, 1)

    def build_lighting(self):
        ambient = AmbientLight('ambient')
        ambient.setColor(Vec4(.35, .38, .46, 1))
        self.render.setLight(self.render.attachNewNode(ambient))
        sun = DirectionalLight('sun')
        sun.setColor(Vec4(.9, .92, 1, 1))
        node = self.render.attachNewNode(sun)
        node.setHpr(-35, -55, 0)
        self.render.setLight(node)
        fog = Fog('fog')
        fog.setColor(.015, .02, .035)
        fog.setExpDensity(.012)
        self.render.setFog(fog)

    def build_hud(self):
        self.title = OnscreenText(text='ECLIPSE', pos=(-1.28, .90), scale=.06,
                                  fg=(.35, .78, 1, 1), align=TextNode.ALeft)
        self.status = OnscreenText(text='', pos=(-1.28, .81), scale=.035,
                                   fg=(.85, .9, .96, 1), align=TextNode.ALeft)
        self.controls = OnscreenText(text='WASD hareket | SHIFT koş | SPACE zıpla | ESC mouse',
                                     pos=(0, -.92), scale=.035,
                                     fg=(.75, .8, .88, 1), align=TextNode.ACenter)
        self.fps = OnscreenText(text='FPS: --', pos=(1.28, .90), scale=.035,
                                fg=(.75, .8, .88, 1), align=TextNode.ARight)
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

    def set_key(self, key, value):
        self.keys[key] = value

    def jump(self):
        if self.on_ground:
            self.vz = self.jump_speed
            self.on_ground = False

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
            self.target_pitch = max(-55, min(35, self.target_pitch))
            self.center_mouse()

    def blocked(self, x, y):
        for ox, oy, hx, hy, top in self.obstacles:
            # Only blocks that are currently around the player's vertical level.
            if self.player.getZ() - 1 < top:
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
        self.pitch += (self.target_pitch - self.pitch) * .15
        self.player.setH(self.yaw)
        yaw = math.radians(self.yaw)
        pitch = math.radians(self.pitch)
        hdist = self.camera_distance * math.cos(pitch)
        target = self.player.getPos() + Vec3(0, 0, 1.05)
        self.camera.setPos(target.x - math.sin(yaw) * hdist,
                           target.y - math.cos(yaw) * hdist,
                           target.z + self.camera_height + self.camera_distance * math.sin(pitch))
        self.camera.lookAt(target)

    def update(self, task):
        dt = min(globalClock.getDt(), .05)
        self.mouse_look()

        mx = (-1 if self.keys['a'] else 0) + (1 if self.keys['d'] else 0)
        my = (1 if self.keys['w'] else 0) + (-1 if self.keys['s'] else 0)
        length = math.hypot(mx, my)
        if length:
            mx, my = mx / length, my / length
            yaw = math.radians(self.yaw)
            fx, fy = math.sin(yaw), math.cos(yaw)
            rx, ry = math.cos(yaw), -math.sin(yaw)
            speed = self.sprint_speed if self.keys['shift'] else self.speed
            self.move((fx * my + rx * mx) * speed * dt,
                      (fy * my + ry * mx) * speed * dt)

        self.vz -= self.gravity * dt
        z = self.player.getZ() + self.vz * dt
        if z <= 1.0:
            z, self.vz, self.on_ground = 1.0, 0.0, True
        else:
            self.on_ground = False
        self.player.setZ(z)
        self.player.setX(max(-19, min(19, self.player.getX())))
        self.player.setY(max(-19, min(19, self.player.getY())))
        self.update_camera()

        self.ft += dt
        self.frames += 1
        if self.ft >= .5:
            self.fps_value = int(self.frames / self.ft)
            self.ft, self.frames = 0, 0
        state = 'YERDE' if self.on_ground else 'HAVADA'
        mouse = 'AKTİF' if self.mouse_captured else 'SERBEST'
        self.status.setText(f'Konum: {self.player.getX():.1f}, {self.player.getY():.1f}\nDurum: {state} | Mouse: {mouse}')
        self.fps.setText(f'FPS: {self.fps_value}')
        return Task.cont


if __name__ == '__main__':
    EclipseGame().run()
