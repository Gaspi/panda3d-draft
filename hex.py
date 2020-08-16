class Point:
    __slots__ = ['x', 'y']
    def __init__(self,x,y):
        self.x=x
        self.y=y

class Triangle:
    __slots__ = ['i', 'j']
    def __init__(self,i,j):
        self.i=i
        self.j=j

    def isUp(self):
        return (self.i + self.j) % 2 == 0
    def isDown(self):
        return not self.isUp()

    def direct_neighbors(self):
        return [
            (self.i+1,self.j),
            (self.i-1,self.j),
            (self.i,self.j + (-1 if isUp(self.i,self.j)) else 1)  ]

    def center(self):
        return Point(2*self.i, 3*self.j + (1 if isUp(self.i,self.j) else 2))

    def vertices(self):
        2i = 2*self.i
        3j = 3*self.j
        if self.isUp():
            return [ Point(2i+1,3j ), Point(2i-1,3j), Point(2i,3j+3) ]
        else:
            return [ Point(2i-1,3j+3 ), Point(2i+1,3j+3), Point(2i,3j) ]
