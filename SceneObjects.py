from MathUtil import *

class Triangle():
    def __init__(self, a, b, c, kd=Vec3(1, 1, 1)):
        self.a = a
        self.b = b
        self.c = c
        self.kd = kd


    def normal(self):
        aToB = self.b - self.a
        aToC = self.c - self.a

        return aToB.cross_product(aToC).unit()

class Light:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color