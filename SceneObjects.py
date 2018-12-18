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

    def __str__(self):
        return f"Triangle<{self.a} {self.b} {self.c}>"

class Light:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color

    def __str__(self):
        return f"Light<{self.pos} {self.color}>"