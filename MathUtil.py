import numbers
from math import sqrt

EPSILON = 0.00001


class Vec2:

    def __init__(self, xx=None, yy=None):
        if xx is None:
            self.x = 0
            self.y = 0
        elif yy is None:
            self.x = xx
            self.y = xx
        else:
            self.x = xx
            self.y = yy

    def normalize(self):
        length = self.length()
        self.x /= length
        self.y /= length

    def unit(self):
        length = self.length()
        return Vec3(self.x / length, self.y / length)

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


class Vec3:

    def __init__(self, xx=None, yy=None, zz=None):
        if xx is None:
            self.x = 0
            self.y = 0
            self.z = 0
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
        self.x /= length
        self.y /= length
        self.z /= length

    def unit(self):
        length = self.length()
        return Vec3(self.x / length, self.y / length, self.z / length)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Vec3(self.x * other, self.y * other, self.z * other)
        elif isinstance(other, Vec3):
            return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def length2(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def length(self):
        return sqrt(self.length2())

    def cross_product(self, other):
        return Vec3(self.y * other.z - other.y * self.z,
                    self.z * other.x - other.z * self.x,
                    self.x * other.y - other.x * self.y)

    def __rmul__(self, other):
        return self * other

    def __str__(self):
        return f"Vec3<{self.x} {self.y} {self.z}>"

    def toList(self):
        return [self.x,self.y,self.z]

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
