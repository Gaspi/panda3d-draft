import math, random

class Point:
    __slots__ = ['x', 'y']
    def __init__(self,x,y):
        self.x=x
        self.y=y
    def __repr__(self):
        return "Point(%d,%d)" % (self.x, self.y)
    def __str__(self):
        return "(%d,%d)" % (self.x, self.y)
    def __hash__(self):
        return hash( (self.x,self.y) )
    def __eq__(self,other):
        return (self.x,self.y) == (other.x,other.y)
    def isVertex(self):
        return self.y % 3 == 0 and (self.x + self.y // 3) % 2 == 0
    def isCenter(self):
        return self.y % 3 != 0 and (self.x + self.y // 3) % 2 + self.y % 3 == 2
    def getTriangles(self):
        ic = self.x
        jc = self.y // 3
        return [  Triangle(ic  ,jc  ),
                  Triangle(ic-1,jc  ),
                  Triangle(ic-1,jc-1),
                  Triangle(ic  ,jc-1),
                  Triangle(ic+1,jc-1),
                  Triangle(ic+1,jc  )  ]
    def getAdjacents(self):
        return [ Point(self.x+2,self.y  ),
                 Point(self.x+1,self.y+3),
                 Point(self.x-1,self.y+3),
                 Point(self.x-2,self.y  ),
                 Point(self.x-1,self.y-3),
                 Point(self.x+1,self.y-3) ]
    def getEdges(self):
        return [ Edge(self,p) for p in self.getAdjacents() ]
    def d2(self,pt):
        return (self.x-pt.x)*(self.x-pt.x)+(self.y-pt.y)*(self.y-pt.y)
    def d(self,pt):
        return math.sqrt(self.d2(pt))
    def d1(self,pt):
        return abs(self.x-pt.x) + abs(self.y-pt.y)
    def getVertices(self):
        return [ self ]

class Edge:
    __slots__ = ['a', 'b']
    def __init__(self,a,b):
        self.a=a
        self.b=b
    def __repr__(self):
        return "Edge(%d,%d)" % (self.a, self.b)
    def __str__(self):
        return "(%d -> %d)" % (self.a, self.b)
    def __hash__(self):
        return hash( (self.a,self.b) )
    def __eq__(self,other):
        return (self.a,self.b) == (other.a,other.b)
    def getVertices(self):
        return [a,b]

# Triangle (0,0) is facing down with center (0,2)
#  - vertices are (-1,3) , (1,3) , (0,0)
#  - adjacent triangles are (1,0) , (-1,0) , (0,1)
class Triangle:
    __slots__ = ['i', 'j']
    def __init__(self,i,j):
        self.i=i
        self.j=j
    def __repr__(self):
        return "Triangle(%d,%d)" % (self.i, self.j)
    def __str__(self):
        return self.__repr__()
    def __hash__(self):
        return hash( (self.i,self.j) )
    def __eq__(self,other):
        return (self.i,self.j) == (other.i,other.j)

    def isDown(self):
        return (self.i ^ self.j) % 2 == 0
    def isUp(self):
        return not self.isDown()

    def getCenter(self):
        return Point(self.i, 3*self.j + (2 if self.isDown() else 1))

    def getVertices(self):
        i = self.i
        j3 = 3*self.j
        if self.isDown():
            return [ Point(i+1,j3+3 ), Point(i-1,j3+3), Point(i,j3) ]
        else:
            return [ Point(i-1,j3 ), Point(i+1,j3), Point(i,j3+3) ]

    def getBase(self):
        j3 = 3*self.j + (0 if self.isDown() else 3)
        return (Point(self.i+1,j3), Point(self.i-1,j3))

    def getEdges(self):
        v = self.getVertices()
        return [ Edge(v[i],v[(i+1)%3]) for i in range(3) ]

    def getHex(self):
        return Hex( (self.i+1)//3 , (self.j+1)//2 )

    def getAdjacents(self):
        return [
            Triangle(self.i+1,self.j),
            Triangle(self.i-1,self.j),
            Triangle(self.i  ,self.j + (1 if self.isDown() else -1) )  ]

# Hex (0,0) has center (0,0)
# Its triangles are
#  - N  ( 0, 0)
#  - NW (-1, 0)
#  - SW (-1,-1)
#  - S  ( 0,-1)
#  - SE ( 1,-1)
#  - NE ( 1, 0)
# Hex (0,1) is directly north of (0,0):
#  - center is (0,6)
# Hex (1,0) is north east of (0,0) and south-east of (0,1):
#  - center is (3,3)
class Hex:
    __slots__ = ['i', 'j']
    def __init__(self,i,j):
        self.i=i
        self.j=j
    def __repr__(self):
        return "Hex(%d,%d)" % (self.i, self.j)
    def __str__(self):
        return self.__repr__()
    def __hash__(self):
        return hash( (self.i,self.j) )
    def __eq__(self,other):
        return (self.i,self.j) == (other.i,other.j)


    # NE: i + n, j + (n + (i%2)    )//2
    # SE: i + n, j - (n - (i%2) + 1)//2
    # N : i    , j + n
    def path_NE_N(self,h):
        n = h.i - self.i
        m = self.j + (n+(self.i%2))//2 - h.j
        return (n,m)
    def path_SE_N(self,h):
        n = h.i - self.i
        m = self.j - (n+(self.i%2)+1)//2 - h.j
        return (n,m)
    def path_NE_SE(self,h):
        m = h.j - self.j + (self.i-1)//2 - (h.i-1)//2
        n = h.i - self.i + m
        return (n,m)
    def dist(self,h):
        dnen = self.path_NE_N(h)
        dsen = self.path_SE_N(h)
        dnese= self.path_NE_SE(h)
        return min( abs(dnen[0])+abs(dnen[1]),
                    abs(dsen[0])+abs(dsen[1]),
                    abs(dnese[0])+abs(dnese[1]) )

    def _center(self):
        return (3*self.i, 6*self.j + 3*(self.i%2))
    def getCenter(self):
        return Point(*self._center())

    def getVertices(self):
        xc,yc=self._center()
        return [ Point(xc+dx,yc+dy)
                 for (dx,dy) in
                 [ (2,0), (1,3), (-1,3), (-2,0),(-1,-3), (1,-3)] ]

    def getEdges(self):
        v = self.getVertices()
        return [ Edge(v[i],v[(i+1)%6]) for i in range(6) ]

    def getTriangles(self):
        ic = 3*self.i
        jc = 2*self.j + (self.i % 2)
        return [  Triangle(ic  ,jc  ),
                  Triangle(ic-1,jc  ),
                  Triangle(ic-1,jc-1),
                  Triangle(ic  ,jc-1),
                  Triangle(ic+1,jc-1),
                  Triangle(ic+1,jc  )  ]

    def getN(self):
        return Hex(self.i,self.j+1)
    def getS(self):
        return Hex(self.i,self.j-1)
    def getNE(self):
        return Hex(self.i+1,self.j+(self.i%2))
    def getNW(self):
        return Hex(self.i-1,self.j+(self.i%2))
    def getSE(self):
        return Hex(self.i+1,self.j-1+(self.i%2))
    def getSW(self):
        return Hex(self.i-1,self.j-1+(self.i%2))
    def getAdjacents(self):
        return [ self.getN(), self.getNW(), self.getSW(),
                 self.getS(), self.getSE(), self.getNE() ]

def hexGrid(i0,irange,j0,jrange):
    return [ Hex(i,j) for i in range(i0,irange) for j in range(j0,jrange) ]

def hexCircle(center,radius):
    return [ h for h in hexGrid(center.i-radius,2*radius+1,center.j-radius,2*radius+1)
             if center.dist(h) <= radius ]
