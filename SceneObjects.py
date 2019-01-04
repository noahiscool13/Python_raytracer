from random import random, uniform

from MathUtil import *
from math import *

from copy import deepcopy

from OpenGL.GL import *
from OpenGL.GLU import *


class Hit:
    def __init__(self, obj, t):
        self.obj = obj
        self.t = t


class Material:
    def __init__(self, Ka = Vec3(0.2), Kd=Vec3(), Ks=Vec3(), Ke  = Vec3(), Ni = 1, d = 1, Ns=2, smoothNormal=False):
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks
        self.Ke = Ke
        self.Ni = Ni
        self.d = d
        self.Ns = Ns
        self.smoothNormal = smoothNormal


class Point:
    def __init__(self, pos, normal=None):
        self.pos = pos
        if normal:
            self.normal = normal
        else:
            self.normal = Vec3(0)

    def __eq__(self, other):
        return self.pos == other.pos and self.normal == other.normal

    def toList(self):
        return self.pos.toList()

    def __hash__(self):
        return hash((self.pos, self.normal))


class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def intersect(self, other):
        if isinstance(other, Scene):
            tnear = inf
            firstTri = None
            for tri in other.objects:
                intersection = self.intersect(tri)

                if intersection is not False:
                    if intersection.t < tnear:
                        tnear = intersection.t
                        firstTri = intersection.obj

            if not firstTri:
                return False

            return Hit(firstTri, tnear)

        if isinstance(other, Triangle):

            tv0 = other.a.pos
            tv1 = other.b.pos
            tv2 = other.c.pos

            edge1 = tv1 - tv0
            edge2 = tv2 - tv0

            h = self.direction.cross_product(edge2)
            a = edge1.dot(h)

            if -EPSILON < a < EPSILON:
                return False

            f = 1.0 / a
            s = self.origin - tv0
            u = f * (s.dot(h))

            if u < 0 or u > 1:
                return False

            q = s.cross_product(edge1)
            v = f * self.direction.dot(q)

            if v < 0 or u + v > 1:
                return False

            t = f * edge2.dot(q)

            if t < EPSILON:
                return False

            return Hit(other, t)

        elif isinstance(other, AAbox):

            # https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-box-intersection

            tmin = (other.min_corner.x - self.origin.x) / self.direction.x
            tmax = (other.max_corner.x - self.origin.x) / self.direction.x

            if tmin > tmax:
                tmin, tmax = tmax, tmin

            tymin = (other.min_corner.y - self.origin.y) / self.direction.y
            tymax = (other.max_corner.y - self.origin.y) / self.direction.y

            if tymin > tymax:
                tymin, tymax = tymax, tymin

            if (tmin > tymax) or (tymin > tmax):
                return False

            if tymin > tmin:
                tmin = tymin

            if tymax < tmax:
                tmax = tymax

            tzmin = (other.min_corner.z - self.origin.z) / self.direction.z
            tzmax = (other.max_corner.z - self.origin.z) / self.direction.z

            if tzmin > tzmax:
                tzmin, tzmax = tzmax, tzmin

            if (tmin > tzmax) or (tzmin > tmax):
                return False

            if tzmin > tmin:
                tmin = tzmin

            if tzmax < tmax:
                tmax = tzmax

            return Hit(other, min(tmin, tmax))

        elif isinstance(other, AABB):
            if self.intersect(other.box):

                tnear = inf
                firstObj = None

                for obj in other.objects:
                    intersection = self.intersect(obj)

                    if intersection is not False:

                        if intersection.t < tnear:
                            tnear = intersection.t
                            firstObj = intersection.obj

                if firstObj:
                    return Hit(firstObj, tnear)

            return False

        elif isinstance(other, KDtree):
            distL = self.intersect(other.left.box)
            distR = self.intersect(other.right.box)

            if distL is False and distR is False:
                return False

            if distL is False:
                return self.intersect(other.right)

            if distR is False:
                return self.intersect(other.left)

            if distL.t < distR.t:
                hit = self.intersect(other.left)
                if hit is not False:
                    hit_point = self.after(hit.t)
                    if other.left.box.intersect(hit_point):
                        return hit
                return self.intersect(other.right)

            hit = self.intersect(other.right)
            if hit is not False:
                hit_point = self.after(hit.t)
                if other.right.box.intersect(hit_point):
                    return hit
                return hit
            return self.intersect(other.left)

    def intersect_uv(self, other):
        if isinstance(other, Triangle):
            edge1 = other.b.pos - other.a.pos
            edge2 = other.c.pos - other.a.pos

            h = self.direction.cross_product(edge2)
            a = edge1.dot(h)

            f = 1.0 / a
            s = self.origin - other.a.pos
            u = f * (s.dot(h))

            q = s.cross_product(edge1)
            v = f * self.direction.dot(q)

            return u, v

    def after(self, t):
        return self.origin + self.direction * t


class Triangle():
    def __init__(self, a, b, c, material=Material()):
        self.a = a
        self.b = b
        self.c = c
        self.material = material

    def add_norm_to_vertices(self):
        norm = self.un_normalized_normal()

        self.a.normal += norm
        self.b.normal += norm
        self.c.normal += norm

    def normal(self):
        return self.un_normalized_normal().unit()

    def un_normalized_normal(self):
        aToB = self.b.pos - self.a.pos
        aToC = self.c.pos - self.a.pos

        return aToB.cross_product(aToC)

    def __str__(self):
        return f"Triangle<{self.a} {self.b} {self.c}>"

    def toList(self):
        return [self.a.toList(), self.b.toList(), self.c.toList()]

    def __iter__(self):
        yield self.a
        yield self.b
        yield self.c

    def box(self):
        xmin = min(self.a.pos.x, self.b.pos.x, self.c.pos.x)
        ymin = min(self.a.pos.y, self.b.pos.y, self.c.pos.y)
        zmin = min(self.a.pos.z, self.b.pos.z, self.c.pos.z)

        xmax = max(self.a.pos.x, self.b.pos.x, self.c.pos.x)
        ymax = max(self.a.pos.y, self.b.pos.y, self.c.pos.y)
        zmax = max(self.a.pos.z, self.b.pos.z, self.c.pos.z)

        minvec = Vec3(xmin, ymin, zmin)
        maxvec = Vec3(xmax, ymax, zmax)

        return AAbox(minvec, maxvec)


class Light:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color

    def __str__(self):
        return f"Light<{self.pos} {self.color}>"


class Camera:
    def __init__(self, point):
        self.point = point


class Scene:
    def __init__(self, triangles=[], points=[], lights=[], camera=None, ambiant_light = Vec3(1)):
        self.objects = triangles
        self.lights = lights
        self.camera = camera
        self.points = points
        self.ambiant_light = ambiant_light

    def calc_vertex_normals(self):
        for shape in self.objects:
            shape.add_norm_to_vertices()

        for point in self.points:
            point.normal.normalize()

    def optimize_scene(self, method="KDTree", amount=1):
        if method == "KDTree":
            box = AABB()

            for obj in self.objects:
                box.add(obj)

            self.objects = [KDtree.build(amount, box, root=True)]


class RowSettings:
    def __init__(self, scene, width=8, height=4, fov=30, row=0, ss=4):
        self.scene = scene
        self.width = width
        self.height = height
        self.fov = fov
        self.aspectratio = width / height
        self.invWidth = 1 / width
        self.invHeight = 1 / height
        self.angle = tan(pi * 0.5 * fov / 180)
        self.row = row
        self.ss = ss


class AAbox:
    def __init__(self, min_corner, max_corner):
        self.min_corner = min_corner
        self.max_corner = max_corner

    def size(self):
        x = self.max_corner.x - self.min_corner.x
        y = self.max_corner.y - self.min_corner.y
        z = self.max_corner.z - self.min_corner.z

        return Vec3(x, y, z)

    def surface_area(self):
        size = self.size()
        surfaceTop = size.x * size.z
        surfaceFront = size.x * size.y
        surfaceSide = size.y * size.z
        return 2 * (surfaceTop + surfaceFront + surfaceSide)

    def extend(self, box):
        xmin = min(self.min_corner.x, box.min_corner.x)
        ymin = min(self.min_corner.y, box.min_corner.y)
        zmin = min(self.min_corner.z, box.min_corner.z)

        xmax = max(self.max_corner.x, box.max_corner.x)
        ymax = max(self.max_corner.y, box.max_corner.y)
        zmax = max(self.max_corner.z, box.max_corner.z)

        self.min_corner = Vec3(xmin, ymin, zmin)
        self.max_corner = Vec3(xmax, ymax, zmax)

    def intersect(self, other):
        if isinstance(other, Triangle):
            # TODO better implementation of this, this has false positives

            if other.a.pos.x < self.min_corner.x \
                    and other.b.pos.x < self.min_corner.x \
                    and other.c.pos.x < self.min_corner.x:
                return False

            if other.a.pos.y < self.min_corner.y \
                    and other.b.pos.y < self.min_corner.y \
                    and other.c.pos.y < self.min_corner.y:
                return False

            if other.a.pos.z < self.min_corner.z \
                    and other.b.pos.z < self.min_corner.z \
                    and other.c.pos.z < self.min_corner.z:
                return False

            if other.a.pos.x > self.max_corner.x \
                    and other.b.pos.x > self.max_corner.x \
                    and other.c.pos.x > self.max_corner.x:
                return False

            if other.a.pos.y > self.max_corner.y \
                    and other.b.pos.y > self.max_corner.y \
                    and other.c.pos.y > self.max_corner.y:
                return False

            if other.a.pos.z > self.max_corner.z \
                    and other.b.pos.z > self.max_corner.z \
                    and other.c.pos.z > self.max_corner.z:
                return False

            return True

        elif isinstance(other, Vec3):
            if other.x < self.min_corner.x:
                return False
            if other.y < self.min_corner.y:
                return False
            if other.z < self.min_corner.z:
                return False

            if other.x > self.max_corner.x:
                return False
            if other.y > self.max_corner.y:
                return False
            if other.z > self.max_corner.z:
                return False

            return True

    def draw_gl(self):
        glPushAttrib(GL_POLYGON_MODE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBegin(GL_QUADS)
        glColor3f(1, 0.6, 0.4);
        glVertex3f(self.min_corner.x, self.min_corner.y, self.min_corner.z)
        glVertex3f(self.max_corner.x, self.min_corner.y, self.min_corner.z)
        glVertex3f(self.max_corner.x, self.max_corner.y, self.min_corner.z)
        glVertex3f(self.min_corner.x, self.max_corner.y, self.min_corner.z)

        glVertex3f(self.min_corner.x, self.min_corner.y, self.max_corner.z)
        glVertex3f(self.max_corner.x, self.min_corner.y, self.max_corner.z)
        glVertex3f(self.max_corner.x, self.max_corner.y, self.max_corner.z)
        glVertex3f(self.min_corner.x, self.max_corner.y, self.max_corner.z)

        glEnd()

        glPopAttrib()

        glBegin(GL_LINES)
        glVertex3f(self.min_corner.x, self.min_corner.y, self.min_corner.z)
        glVertex3f(self.min_corner.x, self.min_corner.y, self.max_corner.z)

        glVertex3f(self.max_corner.x, self.min_corner.y, self.min_corner.z)
        glVertex3f(self.max_corner.x, self.min_corner.y, self.max_corner.z)

        glVertex3f(self.max_corner.x, self.max_corner.y, self.min_corner.z)
        glVertex3f(self.max_corner.x, self.max_corner.y, self.max_corner.z)

        glVertex3f(self.min_corner.x, self.max_corner.y, self.min_corner.z)
        glVertex3f(self.min_corner.x, self.max_corner.y, self.max_corner.z)

        glEnd()


class AABB:
    def __init__(self, box=None, objects=None):
        self.box = box
        if objects:
            self.objects = objects
        else:
            self.objects = []

    def add(self, other):
        self.objects.append(other)

        if self.box:
            self.box.extend(other.box())

        else:
            self.box = other.box()

    def add_norm_to_vertices(self):
        for shape in self.objects:
            shape.add_norm_to_vertices()

    def draw_gl(self):
        self.box.draw_gl()


class KDtree:
    def __init__(self, depth, box):
        self.depth = depth
        self.box = box

    @staticmethod
    def build(depth, box, objects=None, root=False):
        if isinstance(box, AABB):
            return KDtree.build(depth, box.box, box.objects, root)

        if depth <= 0 or len(objects) < 30:
            return AABB(box, objects)

        best_cost = inf

        boxSize = box.size()
        for _ in range(16):
            cutLen = uniform(0, boxSize.x)

            leftMax = deepcopy(box.max_corner)
            leftMax.x -= cutLen

            rightMin = deepcopy(box.min_corner)
            rightMin.x += boxSize.x - cutLen

            leftBox = AAbox(box.min_corner, leftMax)
            rightBox = AAbox(rightMin, box.max_corner)

            lObj = []
            rObj = []

            for obj in objects:
                # print(obj)
                if leftBox.intersect(obj):
                    lObj.append(obj)

                if rightBox.intersect(obj):
                    rObj.append(obj)

            cost = leftBox.surface_area() * len(lObj) + rightBox.surface_area() * len(rObj)

            if cost < best_cost:
                best_cost = cost
                best_left_box = leftBox
                best_right_box = rightBox
                best_left_objects = lObj
                best_right_objects = rObj

        for _ in range(16):
            cutLen = uniform(0, boxSize.y)

            leftMax = deepcopy(box.max_corner)
            leftMax.y -= cutLen

            rightMin = deepcopy(box.min_corner)
            rightMin.y += boxSize.y - cutLen

            leftBox = AAbox(box.min_corner, leftMax)
            rightBox = AAbox(rightMin, box.max_corner)

            lObj = []
            rObj = []

            for obj in objects:
                # print(obj)
                if leftBox.intersect(obj):
                    lObj.append(obj)

                if rightBox.intersect(obj):
                    rObj.append(obj)

            cost = leftBox.surface_area() * len(lObj) + rightBox.surface_area() * len(rObj)

            if cost < best_cost:
                best_cost = cost
                best_left_box = leftBox
                best_right_box = rightBox
                best_left_objects = lObj
                best_right_objects = rObj

        for _ in range(16):
            cutLen = uniform(0, boxSize.z)

            leftMax = deepcopy(box.max_corner)
            leftMax.z -= cutLen

            rightMin = deepcopy(box.min_corner)
            rightMin.z += boxSize.z - cutLen

            leftBox = AAbox(box.min_corner, leftMax)
            rightBox = AAbox(rightMin, box.max_corner)

            lObj = []
            rObj = []

            for obj in objects:
                # print(obj)
                if leftBox.intersect(obj):
                    lObj.append(obj)

                if rightBox.intersect(obj):
                    rObj.append(obj)

            cost = leftBox.surface_area() * len(lObj) + rightBox.surface_area() * len(rObj)

            if cost < best_cost:
                best_cost = cost
                best_left_box = leftBox
                best_right_box = rightBox
                best_left_objects = lObj
                best_right_objects = rObj

        tree = KDtree(depth, box)

        tree.left = KDtree.build(depth - 1, best_left_box, best_left_objects)
        tree.right = KDtree.build(depth - 1, best_right_box, best_right_objects)

        if root:
            tree.objects = objects

        return tree

    def draw_gl(self):
        self.box.draw_gl()
        self.left.draw_gl()
        self.right.draw_gl()
