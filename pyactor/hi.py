

class Papi(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y

class Hijo(Papi):
    def __init__(self,x,y,z):
        super(Hijo,self).__init__(x,y)
        self.z = z + self.y


h = Hijo(1,2,3)
print h.x,h.y,h.z
