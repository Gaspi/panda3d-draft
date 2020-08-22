import random
from hex import *

class HexMap():
    def __init__(self,hexes,zscale):
        self.hexz = { h : zscale*random.random() for h in hexes }
        self.triz = [t for h in self.hexz for t in h.getTriangles()]

    def getHexZ(self,h):
        return self.hexz[h] if h in self.hexz else 0

    def getPtZ(self,pt):
        i = (pt.x + 1) // 3
        j = pt.y // 6
        return self.getHexZ( Hex(i,j) )

    def getTriZ(self,t):
        (a,b) = t.getBase()
        (self.getPtZ(a) + self.getPtZ(b)) / 2.

    def getTriGrad(self,t):
        vs = t.getVertices()
        a = vs[0]
        b = vs[1]
        c = vs[2]
        z0 = (self.getPtZ(a) + self.getPtZ(b)) / 2.
        vx = (self.getPtZ(a) - self.getPtZ(b)) / 2.
        vy = z0 - self.getPtZ(c)
        return (z0,vx,vy) if t.isDown() else (z0,-vx,-vy)

    def _erode(self,h):
        return (
            4*self.getHexZ(h) +
            sum([ self.getHexZ(a) for a in h.getAdjacents()])
            ) / 10
    def erode(self):
        self.hexz = { h : self._erode(h) for h in self.hexz }
