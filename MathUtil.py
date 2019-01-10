import numbers
from math import sqrt, pi, acos, sin, cos
from random import random

EPSILON = 0.00001


def clip(val, lower=0.0, upper=1.0):
    if isinstance(val, list):
        return [clip(v, lower, upper) for v in val]
    return max(lower, min(upper, val))


class Vec2:

    def __init__(self, xx=None, yy=None):
        if xx is None:
            self.x = 0
            self.y = 0

        elif isinstance(xx, Vec2):
            self.x = xx.x
            self.y = xx.y

        elif yy is None:
            self.x = xx
            self.y = xx
        else:
            self.x = xx
            self.y = yy

    def normalize(self):
        length = self.length()
        if length > 0:
            self.x /= length
            self.y /= length

    def unit(self):
        length = self.length()
        if length > 0:
            return Vec3(self.x / length, self.y / length)
        return self

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Vec2(self.x * other, self.y * other)
        elif isinstance(other, Vec2):
            return Vec2(self.x * other.x, self.y * other.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def length2(self):
        return self.x ** 2 + self.y ** 2

    def length(self):
        return sqrt(self.length2())

    def __rmul__(self, other):
        return self * other

    def __str__(self):
        return f"Vec2<{self.x} {self.y}>"

    def __eq__(self, other):
        if abs(self.x - other.x) > EPSILON:
            return False
        if abs(self.y - other.y) > EPSILON:
            return False
        return True

    def distance(self, other):
        return (self-other).length()

    def distance2(self, other):
        return (self-other).length2()


class Vec3:

    def __init__(self, xx=None, yy=None, zz=None):
        if xx is None:
            self.x = 0
            self.y = 0
            self.z = 0

        elif isinstance(xx, Vec3):
            self.x = xx.x
            self.y = xx.y
            self.z = xx.z

        elif yy is None:
            self.x = xx
            self.y = xx
            self.z = xx
        else:
            self.x = xx
            self.y = yy
            self.z = zz

    def normalize(self):
        length = self.length()
        if length > 0:
            self.x /= length
            self.y /= length
            self.z /= length

    def unit(self):
        length = self.length()
        if length > 0:
            return Vec3(self.x / length, self.y / length, self.z / length)
        return Vec3(self)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Vec3(self.x * other, self.y * other, self.z * other)
        elif isinstance(other, Vec3):
            return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            return Vec3(self.x / other, self.y / other, self.z / other)
        else:
            raise ValueError("Cant div by Vec3")

    def length2(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def length(self):
        return sqrt(self.length2())

    def cross_product(self, other):
        return Vec3(self.y * other.z - other.y * self.z,
                    self.z * other.x - other.z * self.x,
                    self.x * other.y - other.x * self.y)

    def rotate(self, rotation):
        if abs(rotation.x) > rotation.y:
            Nt = Vec3(rotation.z,0,-rotation.x) / sqrt(rotation.x**2 + rotation.z**2)
        else:
            Nt = Vec3(0,-rotation.z, rotation.y) / sqrt(rotation.y**2 + rotation.z**2)

        Nb = rotation.cross_product(Nt)

        x = self.x * Nb.x + self.y * rotation.x + self.z * Nt.x
        y = self.x * Nb.y + self.y * rotation.y + self.z * Nt.y
        z = self.x * Nb.z + self.y * rotation.z + self.z * Nt.z

        self.x = x
        self.y = y
        self.z = z

        self.normalize()

    def rotated(self, rotation):
        if abs(rotation.x) > abs(rotation.y):
            Nt = Vec3(rotation.z,0,-rotation.x) / sqrt(rotation.x**2 + rotation.z**2)
        else:
            Nt = Vec3(0,-rotation.z, rotation.y) / sqrt(rotation.y**2 + rotation.z**2)

        Nb = rotation.cross_product(Nt)

        x = self.x * Nb.x + self.y * rotation.x + self.z * Nt.x
        y = self.x * Nb.y + self.y * rotation.y + self.z * Nt.y
        z = self.x * Nb.z + self.y * rotation.z + self.z * Nt.z

        return Vec3(x, y, z)

    def distance(self, other):
        return (self-other).length()

    def distance2(self, other):
        return (self-other).length2()

    @staticmethod
    def point_on_hemisphere(normal = None):
        theta = random()*2*pi
        phi = acos(1-2*random())

        if not normal:
            return Vec3(sin(phi)*cos(theta), abs(sin(phi) * sin(theta)), cos(phi))

        return Vec3.point_on_hemisphere().rotated(normal)

    def __rmul__(self, other):
        return self * other

    def __str__(self):
        return f"Vec3<{self.x} {self.y} {self.z}>"

    def toList(self):
        return [self.x, self.y, self.z]

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __eq__(self, other):
        if abs(self.x - other.x) > EPSILON:
            return False
        if abs(self.y - other.y) > EPSILON:
            return False
        if abs(self.z - other.z) > EPSILON:
            return False
        return True

    def __hash__(self):
        return hash((self.x, self.y, self.z))
