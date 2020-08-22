import random
from hex import *

class GameMap():

    def __init__(self,radius,zscale):
        self.hexes = hexCircle( Hex(0,0), radius)
        self.heights = { h : zscale*random.random() for h in self.hexes }

    def getHexes(self):
        return self.hexes
    def getTriangles(self):
        return [t  for h in self.getHexes() for t in h.getTriangles()]

    def heightOfHex(self,h):
        return self.heights[h] if h in self.heights else 0
    def heightMap(self,pt):
        i = (pt.x + 1) // 3
        j = pt.y // 6
        return self.heightOfHex( Hex(i,j) )

    def _erode(self,h):
        return (
            4*self.heightOfHex(h) +
            sum([ self.heightOfHex(a) for a in h.getAdjacents()])
            ) / 10
    def erode(self):
        self.heights = { h : self._erode(h) for h in self.hexes }
