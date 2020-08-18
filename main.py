import random
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import PerspectiveLens, TextNode, TextureStage, \
    TexGenAttrib, GeomVertexFormat, GeomVertexData, \
    GeomTriangles, GeomLines, \
    Geom, GeomVertexWriter, GeomNode
from pandac.PandaModules import Material, VBase4

from hex import *

class HexTerrainBuilder:
    def __init__(self,dx,dy):
        self.dx = dx
        self.dy = dy / math.sqrt(3)
        self.pt_count = 0
        self.pt_list = []
        self.pt_map = dict()
        self.tri_map = dict()
        self.edge_map = dict()
        self.hexedge_map = dict()

    def addPoint(self,pt):
        if pt not in self.pt_map:
            self.pt_map[pt] = (self.pt_count, None)
            self.pt_list.append( (pt,None) )
            self.pt_count += 1
        return self.pt_map[pt][0]

    def setPoint(self,pt,data):
        ptid = self.addPoint(pt)
        self.pt_map[pt] = (ptid, data)
        self.pt_list[ptid] = (pt,data)

    def addTriangle(self,t):
        if t not in self.tri_map:
            self.tri_map[t] = [ self.addPoint(pt) for pt in t.getVertices() ]
            for e in t.getEdges():
                self.addEdge(e)

    def addEdge(self,edge):
        if edge not in self.edge_map:
            self.edge_map[edge] = ( self.addPoint(edge.a), self.addPoint(edge.b) )

    def addHexEdge(self,edge):
        if edge not in self.hexedge_map:
            self.hexedge_map[edge] = ( self.addPoint(edge.a), self.addPoint(edge.b) )

    def addHex(self,h):
        for t in h.getTriangles():
            self.addTriangle(t)
        for e in h.getEdges():
            self.addHexEdge(e)

    def exportPoints(self):
        vdata = GeomVertexData('data', GeomVertexFormat.getV3(), Geom.UHDynamic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        for (pt,data) in self.pt_list:
            vertex.addData3f(self.dx*pt.x, self.dy*pt.y, 0)
        return vdata

    def exportSurfaceNode(self):
        vdata = self.exportPoints()
        geom = Geom(vdata)

        prim = GeomTriangles(Geom.UHStatic)
        for t in self.tri_map.values():
            prim.addVertices( t[0] , t[1] , t[2] )
        geom.addPrimitive(prim)

        node = GeomNode('surface')
        node.addGeom(geom)
        return node

    def exportEdgesNode(self):
        vdata = self.exportPoints()
        geom = Geom(vdata)

        prim = GeomLines(Geom.UHStatic)
        for t in self.edge_map.values():
            prim.addVertices(t[0], t[1])
        geom.addPrimitive(prim)

        node = GeomNode('edges')
        node.addGeom(geom)
        return node

    def exportHexEdgesNode(self):
        vdata = self.exportPoints()
        geom = Geom(vdata)

        prim = GeomLines(Geom.UHStatic)
        for t in self.hexedge_map.values():
            prim.addVertices(t[0], t[1])
        geom.addPrimitive(prim)

        node = GeomNode('edges')
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

        # Display instructions
        add_title("Panda3D Simple Game")
        add_msg(0.06, "[Esc]: Quit")
        add_msg(0.12, "[E]: Move Forward")
        add_msg(0.18, "[S]: Move Left")
        add_msg(0.24, "[F]: Move Right")
        add_msg(0.30, "[D]: Move Back")
        add_msg(0.36, "[R]: Jump")
        add_msg(0.42, "Arrow Keys: Look Around")

        self.msg_cam_x = add_msg(0.48, "x=0")
        self.msg_cam_y = add_msg(0.54, "y=0")
        self.msg_cam_z = add_msg(0.60, "z=0")
        self.msg_cam_h = add_msg(0.66, "h=0")
        self.msg_cam_p = add_msg(0.72, "p=0")
        self.msg_cam_r = add_msg(0.78, "r=0")

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
        self.camera.setPos(0, 0, 1)
        self.heading = -95.0
        self.pitch = 0.0

        # Load level geometry
        #self.level_model = self.loader.loadModel('models/level')
        #self.level_model.reparentTo(self.render)
        #self.level_model.setTexGen(TextureStage.getDefault(),
        #                           TexGenAttrib.MWorldPosition)
        #self.level_model.setTexProjector(TextureStage.getDefault(),
        #                                 self.render, self.level_model)
        #self.level_model.setTexScale(TextureStage.getDefault(), 4)

        self.generate()

        # Main loop
        self.taskMgr.add(self.update, 'main loop')

    def generate(self):
        tb = HexTerrainBuilder(1.,1.)
        for h in hexCircle( Hex(0,0), 2):
            tb.addHex(h)
        self.surface = self.render.attachNewNode(tb.exportSurfaceNode())
        self.surface.setColor(0,0,1,1)

        self.edges = self.render.attachNewNode(tb.exportEdgesNode())
        self.edges.setColor(1,0,0,1)

        self.hexedges = self.render.attachNewNode(tb.exportHexEdgesNode())
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
        self.msg_cam_h.text = "h=" + str(self.camera.getH())
        self.msg_cam_p.text = "p=" + str(self.camera.getP())
        self.msg_cam_r.text = "r=" + str(self.camera.getR())

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
