from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import DirectLabel
from panda3d.core import AmbientLight, DirectionalLight, Fog, PointLight, TextNode, Vec3, Vec4, WindowProperties
import math
import random

class EclipseGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.set_background_color(.006,.009,.018,1)
        self.keys={k:False for k in ('w','a','s','d','shift')}
        self.speed=5.5; self.sprint_speed=9.0; self.gravity=23; self.jump_speed=8.5
        self.vz=0; self.on_ground=True; self.health=100; self.stamina=100
        self.radius=.62; self.yaw=0; self.pitch=-10; self.target_pitch=-10
        self.mouse_captured=True; self.sensitivity=.03; self.paused=False
        self.flashlight=True; self.camera_distance=7.8; self.camera_height=2.7
        self.obstacles=[]; self.terminals=[]; self.found=set(); self.message_timer=0
        self.bob=0; random.seed(42)
        self.world(); self.player(); self.lights(); self.hud(); self.input()
        self.capture(); self.taskMgr.add(self.update,'eclipse_update')

    def box(self,name,x,y,z,sx,sy,sz,c,solid=False,lightoff=False):
        m=self.loader.loadModel('models/box'); m.setName(name); m.reparentTo(self.render)
        m.setPos(x,y,z); m.setScale(sx,sy,sz); m.setColor(*c)
        if lightoff: m.setLightOff()
        if solid: self.obstacles.append((x,y,sx,sy,z+sz))
        return m

    def tree(self,x,y,s=1):
        self.box('trunk',x,y,1.1*s,.28*s,.28*s,1.1*s,(.14,.06,.025,1),True)
        for z,r in ((2.1,1.2),(2.8,.95),(3.4,.65)):
            self.box('leaves',x,y,z*s,r*s,r*s,.55*s,(.018,.09,.04,1))

    def building(self,x,y,sx,sy,h,c):
        self.box('building',x,y,h,sx,sy,h,(.065,.075,.09,1),True)
        self.box('roof',x,y,h*2.04,sx*1.05,sy*1.05,.1,(.015,.02,.03,1))
        for yy in (-sy*.62,0,sy*.62):
            self.box('window',x+sx*1.01,y+yy,h*1.15,.035,.38,.43,c,False,True)

    def lamp(self,x,y):
        self.box('pole',x,y,2.8,.08,.08,2.8,(.045,.05,.06,1),True)
        self.box('lamp',x,y,5.5,.22,.22,.1,(1,.68,.25,1),False,True)
        p=PointLight('street'); p.setColor(Vec4(1,.58,.22,1)); p.setAttenuation((1,.12,.03))
        n=self.render.attachNewNode(p); n.setPos(x,y,5.35); self.render.setLight(n)

    def world(self):
        self.box('ground',0,0,-.35,32,32,.35,(.035,.048,.044,1))
        for ix in range(-6,7):
            for iy in range(-6,7):
                if random.random()<.7:
                    self.box('ground_detail',ix*4.7,iy*4.7,.01,2.1,2.1,.012,random.choice([( .045,.058,.052,1),(.052,.064,.057,1),(.03,.042,.039,1)]))
        road=(.026,.029,.034,1)
        self.box('road',0,0,.03,4.5,32,.03,road); self.box('road_cross',0,0,.035,32,4.5,.035,road)
        for q in range(-28,29,4):
            self.box('mark',0,q,.07,.1,1.05,.018,(.68,.58,.3,1),False,True)
            self.box('mark',q,0,.072,1.05,.1,.018,(.68,.58,.3,1),False,True)
        self.box('sidewalk',7,0,.08,1.1,31,.08,(.085,.09,.088,1),True)
        self.box('sidewalk',-7,0,.08,1.1,31,.08,(.085,.09,.088,1),True)
        self.box('sidewalk',0,7,.085,31,1.1,.085,(.085,.09,.088,1),True)
        self.box('sidewalk',0,-7,.09,31,1.1,.09,(.085,.09,.088,1),True)
        self.building(-13,12,3.4,4,3.4,(.12,.42,.56,1)); self.building(13,12,4,3.2,4.1,(.45,.2,.14,1))
        self.building(-13,-12,3,3.5,3,(.16,.4,.27,1)); self.building(13,-12,4,3,3.7,(.42,.27,.1,1))
        for x,y,s in [(-22,-20,1.1),(-19,-15,.8),(-24,9,1),(-19,19,.9),(20,19,1),(24,9,.8),(21,-20,1.1),(-20,-2,.8),(21,2,.9),(27,23,.9)]: self.tree(x,y,s)
        for x,y in [(-4,-16),(4,-8),(-4,0),(4,8),(-4,16),(-16,-4),(-8,4),(8,-4),(16,4)]: self.lamp(x,y)
        self.box('crate',9,8,.85,1.2,1.2,.85,(.28,.17,.07,1),True)
        self.box('crate',10.6,8.1,.65,.9,.9,.65,(.22,.13,.055,1),True)
        self.box('barrier',-9,6,.65,2.8,.38,.65,(.15,.16,.17,1),True)
        self.box('container',9,-10,1.4,2.2,3.8,1.4,(.045,.17,.21,1),True)
        for i,(x,y) in enumerate([(-9,-4),(6,14),(17,-3)]):
            t=self.box('terminal',x,y,1.1,.65,.42,1.1,(.025,.22,.28,1),True)
            self.box('screen',x,y-.45,1.25,.38,.025,.24,(.1,.75,.95,1),False,True)
            self.terminals.append((t,f'Terminal {i+1}'))
        wall=(.015,.02,.03,1)
        self.box('north',0,31.5,2.4,32,.5,2.4,wall,True); self.box('south',0,-31.5,2.4,32,.5,2.4,wall,True)
        self.box('east',31.5,0,2.4,.5,32,2.4,wall,True); self.box('west',-31.5,0,2.4,.5,32,2.4,wall,True)
        for _ in range(100):
            self.box('dust',random.uniform(-29,29),random.uniform(-29,29),random.uniform(.3,6),.015,.015,.015,(.5,.58,.65,.18),False,True)

    def player(self):
        self.p=self.render.attachNewNode('Player'); self.p.setPos(0,-2,1)
        b=self.loader.loadModel('models/box'); b.reparentTo(self.p); b.setScale(.58,.4,.98); b.setColor(.07,.18,.23,1)
        j=self.loader.loadModel('models/box'); j.reparentTo(self.p); j.setScale(.63,.43,.67); j.setPos(0,0,.05); j.setColor(.11,.13,.15,1)
        h=self.loader.loadModel('models/box'); h.reparentTo(self.p); h.setScale(.4,.38,.42); h.setPos(0,0,1.42); h.setColor(.38,.45,.45,1)

    def lights(self):
        a=AmbientLight('ambient'); a.setColor(Vec4(.16,.19,.25,1)); self.render.setLight(self.render.attachNewNode(a))
        d=DirectionalLight('moon'); d.setColor(Vec4(.58,.66,.84,1)); n=self.render.attachNewNode(d); n.setHpr(-35,-62,0); self.render.setLight(n)
        self.pl=PointLight('player_light'); self.pl.setColor(Vec4(.65,.8,1,1)); self.pl.setAttenuation((1,.12,.035))
        self.pln=self.render.attachNewNode(self.pl); self.pln.reparentTo(self.p); self.pln.setPos(0,.5,1.4); self.render.setLight(self.pln)
        f=Fog('fog'); f.setColor(.006,.009,.018); f.setExpDensity(.0105); self.render.setFog(f)
        for _ in range(70): self.box('star',random.uniform(-45,45),random.uniform(-45,45),random.uniform(14,28),.015,.015,.015,(.55,.65,.82,1),False,True)

    def hud(self):
        self.title=DirectLabel(text='ECLIPSE',scale=.055,pos=(-1.28,0,.91),text_align=TextNode.ALeft,text_fg=(.42,.8,1,1),frameColor=(0,0,0,0))
        self.obj=DirectLabel(text='GÖREV: 3 terminali keşfet',scale=.034,pos=(-1.28,0,.82),text_align=TextNode.ALeft,text_fg=(.86,.9,.96,1),frameColor=(0,0,0,0))
        self.stats=DirectLabel(text='',scale=.031,pos=(-1.28,0,.72),text_align=TextNode.ALeft,text_fg=(.68,.77,.85,1),frameColor=(0,0,0,0))
        self.msg=DirectLabel(text='',scale=.04,pos=(0,0,-.76),text_align=TextNode.ACenter,text_fg=(1,.82,.42,1),frameColor=(0,0,0,0))
        DirectLabel(text='WASD | SHIFT koş | SPACE zıpla | F fener | E etkileşim | P duraklat | ESC mouse',scale=.031,pos=(0,0,-.92),text_align=TextNode.ACenter,text_fg=(.66,.72,.8,1),frameColor=(0,0,0,0))
        self.fps=DirectLabel(text='FPS: --',scale=.031,pos=(1.28,0,.91),text_align=TextNode.ARight,text_fg=(.68,.75,.84,1),frameColor=(0,0,0,0))
        self.ft=0; self.frames=0; self.fpsv=0

    def input(self):
        for k in ('w','a','s','d'):
            self.accept(k,self.key,[k,True]); self.accept(k+'-up',self.key,[k,False])
        self.accept('shift',self.key,['shift',True]); self.accept('shift-up',self.key,['shift',False])
        self.accept('space',self.jump); self.accept('f',self.toggle_flash); self.accept('e',self.interact)
        self.accept('p',self.pause); self.accept('escape',self.toggle_mouse)

    def key(self,k,v): self.keys[k]=v
    def jump(self):
        if not self.paused and self.on_ground: self.vz=self.jump_speed; self.on_ground=False
    def pause(self): self.paused=not self.paused; self.message('Oyun duraklatıldı' if self.paused else 'Oyun devam ediyor')
    def toggle_flash(self):
        self.flashlight=not self.flashlight
        if self.flashlight:self.render.setLight(self.pln)
        else:self.render.clearLight(self.pln)
        self.message('Fener açıldı' if self.flashlight else 'Fener kapatıldı')
    def message(self,t): self.msg['text']=t; self.message_timer=2.0

    def capture(self):
        p=WindowProperties(); p.setCursorHidden(True); self.win.requestProperties(p); self.center()
    def center(self): self.win.movePointer(0,self.win.getXSize()//2,self.win.getYSize()//2)
    def toggle_mouse(self):
        self.mouse_captured=not self.mouse_captured; p=WindowProperties(); p.setCursorHidden(self.mouse_captured); self.win.requestProperties(p)
        if self.mouse_captured:self.center()
    def mouse(self):
        if not self.mouse_captured or self.paused:return
        cx,cy=self.win.getXSize()//2,self.win.getYSize()//2; q=self.win.getPointer(0)
        dx=q.getX()-cx; dy=q.getY()-cy
        if dx or dy:
            self.yaw-=dx*self.sensitivity; self.target_pitch=max(-52,min(28,self.target_pitch-dy*self.sensitivity)); self.center()

    def blocked(self,x,y):
        for ox,oy,hx,hy,top in self.obstacles:
            if self.p.getZ()-.82<top:
                qx=max(ox-hx,min(x,ox+hx)); qy=max(oy-hy,min(y,oy+hy))
                if (x-qx)**2+(y-qy)**2<self.radius**2:return True
        return False
    def move(self,dx,dy):
        x,y=self.p.getX(),self.p.getY()
        if not self.blocked(x+dx,y):self.p.setX(x+dx)
        x,y=self.p.getX(),self.p.getY()
        if not self.blocked(x,y+dy):self.p.setY(y+dy)
    def interact(self):
        if self.paused:return
        best=999; near=None
        for n,label in self.terminals:
            d=(n.getPos(self.render)-self.p.getPos(self.render)).length()
            if d<best:best=d;near=label
        if near and best<3.3:
            self.found.add(near); self.obj['text']=f'GÖREV: {len(self.found)}/3 terminal bulundu'; self.message(near+' incelendi')
            if len(self.found)==3:self.message('BÖLGE KEŞFİ TAMAMLANDI!')

    def camera(self):
        self.pitch+=(self.target_pitch-self.pitch)*.12; self.p.setH(self.yaw)
        y=math.radians(self.yaw); p=math.radians(self.pitch); hd=self.camera_distance*math.cos(p); t=self.p.getPos()+Vec3(0,0,1.05)
        self.camera.setPos(t.x-math.sin(y)*hd,t.y-math.cos(y)*hd,t.z+self.camera_height+self.camera_distance*math.sin(p)); self.camera.lookAt(t)

    def update(self,task):
        dt=min(globalClock.getDt(),.05); self.mouse()
        if not self.paused:
            mx=(-1 if self.keys['a'] else 0)+(1 if self.keys['d'] else 0); my=(1 if self.keys['w'] else 0)+(-1 if self.keys['s'] else 0)
            moving=math.hypot(mx,my)>0
            if moving:
                l=math.hypot(mx,my); mx/=l; my/=l; y=math.radians(self.yaw); fx,fy=math.sin(y),math.cos(y); rx,ry=math.cos(y),-math.sin(y)
                sprint=self.keys['shift'] and self.stamina>1; sp=self.sprint_speed if sprint else self.speed
                self.move((fx*my+rx*mx)*sp*dt,(fy*my+ry*mx)*sp*dt)
                self.stamina=max(0,self.stamina-28*dt) if sprint else min(100,self.stamina+16*dt); self.bob+=dt*(12 if sprint else 8)
            else:self.stamina=min(100,self.stamina+22*dt)
            self.vz-=self.gravity*dt; z=self.p.getZ()+self.vz*dt
            if z<=1:z=1; self.vz=0; self.on_ground=True
            else:self.on_ground=False
            self.p.setZ(z); self.p.setX(max(-29,min(29,self.p.getX()))); self.p.setY(max(-29,min(29,self.p.getY())))
        self.camera()
        self.message_timer-=dt
        if self.message_timer<=0:self.msg['text']=''
        self.ft+=dt; self.frames+=1
        if self.ft>=.5:self.fpsv=int(self.frames/self.ft); self.ft=0; self.frames=0
        state='YERDE' if self.on_ground else 'HAVADA'; mouse='AKTİF' if self.mouse_captured else 'SERBEST'
        self.stats['text']=f'CAN: {self.health}%  STAMINA: {int(self.stamina)}%\nKONUM: {self.p.getX():.1f}, {self.p.getY():.1f}\nDURUM: {state} | FENER: {"AÇIK" if self.flashlight else "KAPALI"} | MOUSE: {mouse}'
        self.fps['text']=f'FPS: {self.fpsv}'
        return Task.cont

if __name__=='__main__': EclipseGame().run()
