from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / 'main.py'
BACKUP = ROOT / 'main.py.backup_visuals'

text = MAIN.read_text(encoding='utf-8')
BACKUP.write_text(text, encoding='utf-8')

old = '''        m = self.loader.loadModel('models/box')
        m.setName(name)
        m.reparentTo(parent if parent is not None else self.render)
        m.setPos(x, y, z)
        m.setScale(sx, sy, sz)
        m.setColor(*c)
        if lightoff:
            m.setLightOff()
        if solid:
            self.obstacles.append((x, y, sx, sy, z + sz))
        return m'''
new = '''        m = self.loader.loadModel('models/box')
        m.setName(name)
        target = parent if parent is not None else self.render
        m.reparentTo(target)
        m.setPos(x, y, z)
        m.setScale(sx, sy, sz)
        m.setColor(*c)
        if lightoff:
            m.setLightOff()
        if solid and parent is None:
            self.obstacles.append((x, y, sx, sy, z + sz))
        return m'''
if old not in text:
    raise SystemExit('box() block not found')
text = text.replace(old, new, 1)

old = '''        self.yaw = 0.0
        self.pitch = -6.0'''
new = '''        self.yaw = 0.0
        self.target_yaw = 0.0
        self.pitch = -6.0'''
if old not in text:
    raise SystemExit('yaw initialization not found')
text = text.replace(old, new, 1)

old = '''        if dx or dy:
            # Mouse yaw directly turns the character. Third-person camera follows it.
            self.yaw -= dx * self.sensitivity
            self.target_pitch = max(-55, min(38, self.target_pitch - dy * self.sensitivity))
            self.center()'''
new = '''        if dx or dy:
            # Mouse controls the shared target rotation for character + camera.
            self.target_yaw -= dx * self.sensitivity
            self.target_pitch = max(-55, min(38, self.target_pitch - dy * self.sensitivity))
            self.center()'''
if old not in text:
    raise SystemExit('mouse block not found')
text = text.replace(old, new, 1)

old = '''        dt = min(globalClock.getDt(), .05)
        self.mouse()

        if not self.paused:'''
new = '''        dt = min(globalClock.getDt(), .05)
        self.mouse()
        yaw_delta = (self.target_yaw - self.yaw + 180.0) % 360.0 - 180.0
        self.yaw += yaw_delta * min(1.0, dt * 14.0)

        if not self.paused:'''
if old not in text:
    raise SystemExit('update header not found')
text = text.replace(old, new, 1)

old = '''            target = self.p.getPos() + Vec3(0, 0, 1.55)
            horizontal = self.camera_distance * math.cos(p)'''
new = '''            target = self.p.getPos() + Vec3(0, 0, 1.35)
            horizontal = self.camera_distance * math.cos(p)'''
text = text.replace(old, new, 1)

# Remove the most artificial blocky props.
text = re.sub(r"\n        self\.box\('crate_a'.*?\n        self\.box\('crate_b'.*?\n", "\n", text, count=1, flags=re.DOTALL)
text = re.sub(r"\n        self\.box\('container'.*?\n", "\n", text, count=1, flags=re.DOTALL)
text = re.sub(r"\n        self\.box\('barrier'.*?\n        self\.box\('barrier_stripe'.*?\n", "\n", text, count=1, flags=re.DOTALL)

MAIN.write_text(text, encoding='utf-8')
print('Eclipse visual/character/camera fix applied.')
print('Backup created:', BACKUP)
