from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import PerspectiveLens, TextNode, TextureStage, TexGenAttrib,\
    Geom, GeomNode

from hex import *
from gamemap import *
from terrain import TerrainBuilder

xscale=1.
yscale=1.
zscale=10.
true_yscale = yscale / math.sqrt(3)
radiusmap=6

deltarand = 0.4 * min(2*xscale,3*true_yscale)

hexes = hexCircle( Hex(0,0), radiusmap)
gamemap = HexMap(hexes,zscale)
gamemap.erode()

def trianglePos(x,y):
    (dx,rx) = divmod(x /       xscale , 1.)
    (dy,ry) = divmod(y / (3. * true_yscale), 1.)
    i = int(dx)
    j = int(dy)
    ysep = ry if (i^j)%2 == 0 else 1-ry
    return ( Triangle(i+1,j),rx-1,ry) if rx > ysep else ( Triangle(i,j),rx,ry)

def getZ(x,y):
    (t,rx,ry) = trianglePos(x,y)
    (z0,vx,vy) = gamemap.getTriGrad(t)
    return z0 + rx*vx + ry*vy

def nodeOfPrim(vdata,prim,name):
    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode(name)
    node.addGeom(geom)
    return node

def add_msg(pos, msg):
    """Function to put instructions on the screen."""
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1),
                        parent=base.a2dTopLeft, align=TextNode.ALeft,
                        pos=(0.08, -pos - 0.04), scale=.05)

def add_title(text):
    """Function to put title on the screen."""
    return OnscreenText(text=text, style=1, pos=(-0.1, 0.09), scale=.08,
                        parent=base.a2dBottomRight, align=TextNode.ARight,
                        fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))

class Game(ShowBase):
    """Sets up the game, camera, controls, and loads models."""
    def __init__(self):
        ShowBase.__init__(self)

        add_title("Panda3D Simple Game")
        # Display instructions
        #add_msg(0.06, "[Esc]: Quit")
        #add_msg(0.12, "[E]: Move Forward")
        #add_msg(0.18, "[S]: Move Left")
        #add_msg(0.24, "[F]: Move Right")
        #add_msg(0.30, "[D]: Move Back")
        #add_msg(0.36, "[R]: Jump")
        #add_msg(0.42, "Arrow Keys: Look Around")
        self.msg_cam_x = add_msg(0.48, "x=0")
        self.msg_cam_y = add_msg(0.54, "y=0")
        self.msg_cam_z = add_msg(0.60, "z=0")
        self.msg_cam   = add_msg(0.66, "tri=(0,0)")
        #self.msg_cam_h = add_msg(0.66, "h=0")
        #self.msg_cam_p = add_msg(0.72, "p=0")
        #self.msg_cam_r = add_msg(0.78, "r=0")

        # Setup controls
        self.keys = {}
        for key in ['arrow_left', 'arrow_right', 'arrow_up', 'arrow_down',
                    'e', 'd', 's', 'f']:
            self.keys[key] = 0
            self.accept(key, self.push_key, [key, 1])
            self.accept('shift-%s' % key, self.push_key, [key, 1])
            self.accept('%s-up' % key, self.push_key, [key, 0])
        self.accept('r', self.jump)
        self.accept('escape', __import__('sys').exit, [0])
        self.disableMouse()

        # Setup camera
        lens = PerspectiveLens()
        lens.setFov(60)
        lens.setNear(0.01)
        lens.setFar(1000.0)
        self.cam.node().setLens(lens)
        self.camera.setPos(0, 0, zscale)
        self.heading = 0.0
        self.pitch   = 0.0

        # Load level geometry
        self.generate()

        # Main loop
        self.taskMgr.add(self.update, 'main loop')

    def generate(self):
        terrain = TerrainBuilder(xscale,yscale,deltarand)
        surface = terrain.surfaceOfHexes( gamemap.hexz.keys() )
        borders = terrain.linesOfHexes( gamemap.hexz.keys() )
        lines   = terrain.linesOfTriangles( gamemap.triz )
        terrain.setHeightMap( gamemap.getPtZ )
        vdata = terrain.export()

        self.surface = self.render.attachNewNode(
            nodeOfPrim(vdata,surface,"surface"))
        self.surface.setColor(0,0,1,1)

        self.edges = self.render.attachNewNode(
            nodeOfPrim(vdata,lines,"lines"))
        self.edges.setColor(1,0,0,1)

        self.hexedges = self.render.attachNewNode(
            nodeOfPrim(vdata,borders,"borders"))
        self.hexedges.setColor(0,1,0,1)
        self.hexedges.setRenderModeThickness(4)

    def jump(self):
        pass

    def push_key(self, key, value):
        self.keys[key] = value

    def update_msg(self):
        self.msg_cam_x.text = "x=" + str(self.camera.getX())
        self.msg_cam_y.text = "y=" + str(self.camera.getY())
        self.msg_cam_z.text = "z=" + str(self.camera.getZ())
        self.msg_cam.text = "tri=" + str(getZ(self.camera.getX(), self.camera.getY()))
        #self.msg_cam_h.text = "h=" + str(self.camera.getH())
        #self.msg_cam_p.text = "p=" + str(self.camera.getP())
        #self.msg_cam_r.text = "r=" + str(self.camera.getR())

    def update(self, task):
        """ Updates the camera based on the keyboard input. """
        dt = globalClock.getDt()
        dx = 3 * dt * (self.keys['f']-self.keys['s'])
        dz = 3 * dt * (self.keys['d']-self.keys['e'])
        self.camera.setPos(self.camera, dx, -dz, 0) # Set position with relation to itself: move
        self.heading += 90 * dt * (self.keys['arrow_left']-self.keys['arrow_right'])
        self.pitch   += 90 * dt * (self.keys['arrow_up']  -self.keys['arrow_down'] )
        self.camera.setHpr(self.heading, self.pitch, 0)
        self.update_msg()
        return task.cont


game = Game()
game.run()
