from hex import *
import random
from panda3d.core import GeomVertexFormat, GeomVertexData, Geom, GeomVertexWriter,\
    GeomTriangles, GeomLines

class TerrainBuilder:
    def __init__(self,xscale,yscale,deltarand):
        self.dx = xscale
        self.dy = yscale / math.sqrt(3)
        self.pt_count = 0
        self.pt_list = []
        self.pt_map = dict()
        self.deltarand = deltarand

    def get(self,pt):
        if pt not in self.pt_map:
            self.pt_map[pt] = len(self.pt_list)
            self.pt_list.append(pt)
        return self.pt_map[pt]

    def export(self,heightMap):
        vdata = GeomVertexData('data', GeomVertexFormat.getV3(), Geom.UHDynamic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        for pt in self.pt_list:
            vertex.addData3f(
                self.dx*pt.x, # + self.deltarand*(0.5-random.random()),
                self.dy*pt.y, # + self.deltarand*(0.5-random.random()),
                heightMap(pt) )
        return vdata

    def surfaceOfTriangles(self,triangles):
        prim = GeomTriangles(Geom.UHStatic)
        for t in triangles:
            v = t.getVertices()
            prim.addVertices(self.get(v[0]), self.get(v[1]), self.get(v[2]))
        return prim

    def surfaceOfHexes(self,hexes):
        return self.surfaceOfTriangles([t for h in hexes for t in h.getTriangles()])

    def linesOfEdges(self,edges):
        prim = GeomLines(Geom.UHStatic)
        for e in edges:
            prim.addVertices( self.get(e.a), self.get(e.b) )
        return prim

    def linesOfTriangles(self,triangles):
        return self.linesOfEdges([e for t in triangles for e in t.getEdges()])

    def linesOfHexes(self,hexes):
        return self.linesOfEdges([e for h in hexes for e in h.getEdges()])
