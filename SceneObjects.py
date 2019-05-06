from random import random, uniform, choices
from bisect import insort
from MathUtil import *
from math import *

try:
    from math import inf
except:
    inf = 10**99

from copy import deepcopy

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    headless = False
except:
    headless = True


class CompositeObject:
    pass


class Hit:
    def __init__(self, obj, t):
        self.obj = obj
        self.t = t

    def __bool__(self):
        return True

    def __lt__(self, other):
        return self.t < other.t


class Material:
    def __init__(self, Ka = Vec3(0.2), Kd=Vec3(0), Ks=Vec3(0), Ke  = Vec3(), Ni = 1, d = 1, Ns=2, smoothNormal=False):
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
        return "Triangle<{} {} {}".format(self.a, self.b, self.c)

        # no support for this on the HPC 10 cluster
        #return f"Triangle<{self.a} {self.b} {self.c}>"

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

    def area(self):
        edge1 = self.b.pos - self.a.pos
        edge2 = self.c.pos - self.a.pos

        cross =  edge1.cross_product(edge2)
        double_area = cross.length()
        return double_area/2

    def random_point_on_surface(self):
        edge1 = self.b.pos - self.a.pos
        edge2 = self.c.pos - self.a.pos

        a = 1
        b = 1

        while a+b > 1:
            a = random()
            b = random()

        return self.a.pos + edge1 * a + edge2 * b



class Light:
    def __init__(self, pos, color, softness=0.1):
        self.true_pos = pos
        self.pos = pos
        self.color = color
        self.softness = softness

    def random_translate(self):
        self.pos = self.true_pos + Vec3((random()-0.5)*self.softness,
                                        (random()-0.5)*self.softness,
                                        (random()-0.5)*self.softness)

    def __str__(self):
        return "Light<{} {}>".format(self.pos, self.color)


        # no support for this on the HPC 10 cluster
        #return f"Light<{self.pos} {self.color}>"


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
        self.emitters_set = False
        self.emitters = None
        self.total_light_set = False
        self.total_light_val = None
        self.light_powers = []

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

    def all_emittors(self):
        if self.emitters_set:
            return self.emitters
        else:
            emittors = []

            for light in self.lights:
                emittors.append(light)

            for obj in self.objects:
                if isinstance(obj, CompositeObject):
                    for objc in obj.objects:
                        if objc.material.Ke.length2() > 0:
                            emittors.append(objc)
                else:
                    if obj.material.Ke.length2() > 0:
                        emittors.append(obj)

            self.emitters = emittors
            self.emitters_set = True

            return emittors

    def total_light(self):
        if self.total_light_set:
            return self.total_light_val

        else:
            total = 0

            for obj in self.all_emittors():
                if isinstance(obj, Light):
                    total += obj.color.avg()
                    self.light_powers.append(obj.color.avg())

                elif isinstance(obj, Triangle):
                    total += obj.material.Ke.avg() * obj.area()
                    self.light_powers.append(obj.material.Ke.avg() * obj.area())

            self.total_light_set = True
            self.total_light_val = total

            return total

    def random_weighted_light(self):
        self.total_light()

        # TODO change to cum_weights, that should be faster
        return choices(population=self.all_emittors(), weights=self.light_powers, k=1)[0]



class RowSettings:
    def __init__(self, scene, width=8, height=4, fov=30, row=0, ss=4, mode="recursive"):
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
        self.mode = mode


class AAbox:
    def __init__(self, min_corner = None, max_corner = None):
        self.min_corner = min_corner
        self.max_corner = max_corner

    def size(self):
        if not self.min_corner:
            return 0

        x = self.max_corner.x - self.min_corner.x
        y = self.max_corner.y - self.min_corner.y
        z = self.max_corner.z - self.min_corner.z

        return Vec3(x, y, z)

    def surface_area(self):
        if not self.min_corner:
            return 0

        size = self.size()
        surfaceTop = size.x * size.z
        surfaceFront = size.x * size.y
        surfaceSide = size.y * size.z
        return 2 * (surfaceTop + surfaceFront + surfaceSide)

    def extend(self, box):
        if not self.min_corner:
            other_box = box.box()
            self.min_corner = other_box.min_corner
            self.max_corner = other_box.max_corner

        elif isinstance(box, Photon):
            xmin = min(self.min_corner.x, box.pos.x)
            ymin = min(self.min_corner.y, box.pos.y)
            zmin = min(self.min_corner.z, box.pos.z)

            xmax = max(self.max_corner.x, box.pos.x)
            ymax = max(self.max_corner.y, box.pos.y)
            zmax = max(self.max_corner.z, box.pos.z)

            self.min_corner = Vec3(xmin, ymin, zmin)
            self.max_corner = Vec3(xmax, ymax, zmax)

        elif isinstance(box, AAbox):
            xmin = min(self.min_corner.x, box.min_corner.x)
            ymin = min(self.min_corner.y, box.min_corner.y)
            zmin = min(self.min_corner.z, box.min_corner.z)

            xmax = max(self.max_corner.x, box.max_corner.x)
            ymax = max(self.max_corner.y, box.max_corner.y)
            zmax = max(self.max_corner.z, box.max_corner.z)

            self.min_corner = Vec3(xmin, ymin, zmin)
            self.max_corner = Vec3(xmax, ymax, zmax)

    def box(self):
        return self

    def margin_around(self, pos):
        if not self.intersect(pos):
            return False

        left = pos.x - self.min_corner.x
        right = self.max_corner.x = pos.x

        up = pos.y - self.min_corner.y
        down = self.max_corner.y = pos.y

        front = pos.z - self.min_corner.z
        back = self.max_corner.z = pos.z

        return min(left, right, up, down, front, back)

    def distance(self, pos):
        """"
        z<box.minz   box.minz<z<box.maxz   box.maxz<z
         1   2   3        10  11  12        19  20  21
           m####             ####              ####
       ^ 4 # 5 # 6        13 #14# 15        22 #23# 23
       ^   #####             ####              ###M
       | 7   8   9        16  17  18        25  26  27
       y
         x->>
        """

        if pos.z < self.min_corner.z:
            if pos.y < self.min_corner.y:
                # 1
                if pos.x < self.min_corner.x:
                    return self.min_corner.distance(pos)

                # 2
                if pos.x < self.max_corner.x:
                    return Vec2(pos.y, pos.z).distance(Vec2(self.min_corner.y, self.min_corner.z))

                # 3
                return Vec3(self.max_corner.x, self.min_corner.y, self.min_corner.z).distance(pos)

            if pos.y < self.max_corner.y:
                # 4
                if pos.x < self.min_corner.x:
                    return Vec2(pos.x, pos.z).distance(Vec2(self.min_corner.x, self.min_corner.z))

                # 5
                if pos.x < self.max_corner.x:
                    return self.min_corner.z - pos.z

                # 6
                return Vec2(pos.x, pos.z).distance(Vec2(self.max_corner.x, self.min_corner.z))


            # 7
            if pos.x < self.min_corner.x:
                return Vec3(self.min_corner.x, self.max_corner.y, self.min_corner.z).distance(pos)

            # 8
            if pos.x < self.max_corner.x:
                return Vec2(pos.y, pos.z).distance(Vec2(self.max_corner.y, self.min_corner.z))

            # 9
            return Vec3(self.max_corner.x, self.max_corner.y, self.min_corner.z).distance(pos)

        if pos.z < self.max_corner.z:
            if pos.y < self.min_corner.y:
                # 10
                if pos.x < self.min_corner.x:
                    return Vec2(pos.x, pos.y).distance(Vec2(self.min_corner.x, self.min_corner.y))

                # 11
                if pos.x < self.max_corner.x:
                    return self.min_corner.y - pos.y

                # 12
                return Vec2(pos.x, pos.y).distance(Vec2(self.max_corner.x, self.min_corner.y))

            if pos.y < self.max_corner.y:
                # 13
                if pos.x < self.min_corner.x:
                    return self.min_corner.x - pos.x

                # 14
                if pos.x < self.max_corner.x:
                    return 0

                # 15
                return pos.x - self.max_corner.x

            # 16
            if pos.x < self.min_corner.x:
                return Vec2(pos.x, pos.y).distance(Vec2(self.max_corner.x, self.min_corner.y))

            # 17
            if pos.x < self.max_corner.x:
                return pos.y - self.max_corner.y

            # 18
            return Vec2(pos.x, pos.y).distance(Vec2(self.max_corner.x, self.max_corner.y))

        if pos.y < self.min_corner.y:
            # 19
            if pos.x < self.min_corner.x:
                return Vec3(self.min_corner.x, self.min_corner.y, self.max_corner.z).distance(pos)

            # 20
            if pos.x < self.max_corner.x:
                return Vec2(pos.y, pos.z).distance(Vec2(self.min_corner.y, self.max_corner.z))

            # 21
            return Vec3(self.max_corner.x, self.min_corner.y, self.max_corner.z).distance(pos)

        if pos.y < self.max_corner.y:
            # 22
            if pos.x < self.min_corner.x:
                return Vec2(pos.x, pos.z).distance(Vec2(self.min_corner.x, self.max_corner.z))

            # 23
            if pos.x < self.max_corner.x:
                return pos.z - self.max_corner.z

            # 24
            return Vec2(pos.x, pos.z).distance(Vec2(self.max_corner.x, self.max_corner.z))

        # 25
        if pos.x < self.min_corner.x:
            return Vec3(self.min_corner.x, self.max_corner.y, self.max_corner.z).distance(pos)

        # 8
        if pos.x < self.max_corner.x:
            return Vec2(pos.y, pos.z).distance(Vec2(self.max_corner.y, self.max_corner.z))

        # 27
        return self.max_corner.distance(pos)

    @staticmethod
    def large_box(min_corner = None, max_corner = None):
        if min_corner:
            box_min_corner = min_corner - Vec3(1000)
        else:
            box_min_corner = Vec3(-1000)

        if max_corner:
            box_max_corner = max_corner + Vec3(1000)
        else:
            box_max_corner = Vec3(1000)

        return AAbox(box_min_corner, box_max_corner)


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

    def longest_axis(self):
        self_size = self.size()

        if self_size.x > self_size.y > self_size.z:
            return 0

        if self_size.y > self_size.z:
            return 1

        return 2

    def draw_gl(self):
        if not headless:
            glPushAttrib(GL_POLYGON_MODE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glBegin(GL_QUADS)
            glColor3f(1, 0.6, 0.4)
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


class AABB(CompositeObject):
    def __init__(self, box=None, objects=None):
        if not box:
            self.box = AAbox()
        else:
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

    def get_box_at(self, pos):
        return self

    def add_norm_to_vertices(self):
        for shape in self.objects:
            shape.add_norm_to_vertices()

    def draw_gl(self):
        self.box.draw_gl()


class LeftKDTree:
    def __init__(self, node, left=None, right=None, split=None):
        self.node = node
        self.left = left
        self.right = right
        self.split = split

    @staticmethod
    def build(box):
        longest_axis = box.box.longest_axis()

        if longest_axis == 0:
            box.photons.sort(key=lambda photon: photon.pos.x)
        elif longest_axis == 1:
            box.photons.sort(key=lambda photon: photon.pos.y)
        elif longest_axis == 2:
            box.photons.sort(key=lambda photon: photon.pos.z)

        photon_len = len(box.photons)

        if photon_len == 0:
            return None

        if photon_len == 1:
            return LeftKDTree(box.photons[0])

        median = photon_len // 2

        left = box.photons[:median]
        right = box.photons[median+1:]

        if longest_axis == 0:
            left_box = deepcopy(box.box)
            right_box = deepcopy(box.box)

            middle_x = box.photons[median].pos.x

            left_box.max_corner.x = middle_x
            right_box.min_corner.x = middle_x

        elif longest_axis == 1:
            left_box = deepcopy(box.box)
            right_box = deepcopy(box.box)

            middle_y = box.photons[median].pos.y

            left_box.max_corner.y = middle_y
            right_box.min_corner.y = middle_y

        elif longest_axis == 2:
            left_box = deepcopy(box.box)
            right_box = deepcopy(box.box)

            middle_z = box.photons[median].pos.z

            left_box.max_corner.z = middle_z
            right_box.min_corner.z = middle_z

        leftBox = PhotonBox(PhotonList(left), left_box)
        rightBox = PhotonBox(PhotonList(right), right_box)

        tree = LeftKDTree(box.photons[median], split=longest_axis)

        tree.left = LeftKDTree.build(leftBox)
        tree.right = LeftKDTree.build(rightBox)

        return tree


class KDtree(CompositeObject):
    def __init__(self, depth, box):
        self.depth = depth
        self.box = box

    def get_box_at(self, pos):
        if self.left.box.intersect(pos):
            return self.left.get_box_at(pos)

        elif self.right.box.intersect(pos):
            return self.right.get_box_at(pos)

        return False

    @staticmethod
    def nearest_neighbour_helper(pos, dist, photon, kd, excluding=None, max_dist=None):
        if isinstance(kd, PhotonBox):
            if excluding:
                hit = kd.nearest_neighbour_excluding(pos, excluding, max_dist)
            else:
                hit = kd.nearest_neighbour(pos, excluding)

            if not hit:
                return False

            nearest_photon = hit.obj
            nearest_dist = hit.t

            if nearest_dist < dist:
                return Hit(nearest_photon, nearest_dist)

            return False

        if kd.left.box.distance(pos) < dist:
            hit = KDtree.nearest_neighbour_helper(pos,dist,photon,kd.left, excluding, max_dist)
            if hit and hit.t < dist:
                dist = hit.t
                photon = hit.obj

        if kd.right.box.distance(pos) < dist:
            hit = KDtree.nearest_neighbour_helper(pos, dist, photon, kd.right, excluding, max_dist)
            if hit and hit.t < dist:
                dist = hit.t
                photon = hit.obj

        return Hit(photon, dist)

    def nearest_neighbour(self, pos, excluding = None, max_dist = None):
        box = self.get_box_at(pos)
        if not box:
            nearest_photon = None
            nearest_dist = inf
        else:
            if excluding:
                hit = box.nearest_neighbour_excluding(pos, excluding, max_dist)
            else:
                hit = box.nearest_neighbour(pos, max_dist)
            if not hit:
                return False
            nearest_photon = hit.obj
            nearest_dist = hit.t

        return KDtree.nearest_neighbour_helper(pos, nearest_dist,nearest_photon, self, excluding, max_dist)

    def k_nearest_neighbours(self, pos, k):
        lst = []

        for x in range(k):
            hit = self.nearest_neighbour(pos, lst)
            if hit:
                lst.append(hit.obj)
            else:
                return False

        return lst

    def k_nearest_neighbours_plane(self, pos, k, normal, max_dist = None):
        lst = []
        found = set()

        while len(lst) < k:
            hit = self.nearest_neighbour(pos, found)
            if hit:
                if hit.t > max_dist:
                    return lst

                found.add(hit.obj)
                if hit.obj.in_plane(pos, normal):
                    lst.append(hit.obj)
            else:
                return lst

        return lst

    @staticmethod
    def build(depth, box, objects=None, root=False):
        if isinstance(box, AABB):
            return KDtree.build(depth, box.box, box.objects, root)

        if isinstance(box, PhotonBox):

            if depth <= 0 or len(box.photons) < 25:
                return box

            longest_axis = box.box.longest_axis()

            if longest_axis == 0:
                box.photons.sort(key= lambda photon: photon.pos.x)
            elif longest_axis == 1:
                box.photons.sort(key= lambda photon: photon.pos.y)
            elif longest_axis == 2:
                box.photons.sort(key= lambda photon: photon.pos.z)

            photon_len = len(box.photons)

            median = photon_len//2

            left = box.photons[:median]
            right = box.photons[median:]

            if longest_axis == 0:
                left_box = deepcopy(box.box)
                right_box = deepcopy(box.box)

                middle_x = (left[-1].pos.x + right[0].pos.x)/2

                left_box.max_corner.x = middle_x
                right_box.min_corner.x = middle_x

            elif longest_axis == 1:
                left_box = deepcopy(box.box)
                right_box = deepcopy(box.box)

                middle_y = (left[-1].pos.y + right[0].pos.y) / 2

                left_box.max_corner.y = middle_y
                right_box.min_corner.y = middle_y

            elif longest_axis == 2:
                left_box = deepcopy(box.box)
                right_box = deepcopy(box.box)

                middle_z = (left[-1].pos.z + right[0].pos.z) / 2

                left_box.max_corner.z = middle_z
                right_box.min_corner.z = middle_z

            leftBox = PhotonBox(PhotonList(left), left_box)
            rightBox = PhotonBox(PhotonList(right), right_box)

            tree = KDtree(depth, box.box)

            tree.left = KDtree.build(depth-1, leftBox)
            tree.right = KDtree.build(depth - 1, rightBox)

            return tree


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
        if not headless:
            self.box.draw_gl()
            self.left.draw_gl()
            self.right.draw_gl()


class Photon:
    def __init__(self, pos, col, direction):
        self.pos = pos
        self.col = col
        self.direction = direction

    def __eq__(self, other):
        if not isinstance(other, Photon):
            return False

        if self.pos != other.pos:
            return False

        if self.col != other.col:
            return False

        if self.direction != other.direction:
            return False

        return True

    def __str__(self):
        return f"Photon <\n pos: {self.pos}\n col: {self.col}\n direction: {self.direction}\n>"

    def __hash__(self) -> int:
        return hash(self.pos) ^ hash(self.col) ^ hash(self.direction)

    def box(self):
        return AAbox(self.pos, self.pos)

    def distance(self, other):
        if isinstance(other, Vec3):
            return self.pos.distance(other)

        elif isinstance(other, Photon):
            return self.pos.distance(other.pos)

    def distance2(self, other):
        if isinstance(other, Vec3):
            return self.pos.distance2(other)

        elif isinstance(other, Photon):
            return self.pos.distance2(other.pos)

    def in_plane(self, pos, normal, margin=0.001):
        ax = pos-self.pos
        ax.normalize()
        return normal.dot(ax) < margin

    @staticmethod
    def generate_random_on_object(obj, power, dist = 0):
        if isinstance(obj, Triangle):
            obj_normal = obj.normal()
            pos = obj.random_point_on_surface() + obj_normal * EPSILON

            direction = Vec3.point_on_hemisphere(obj.normal())
            col = obj.material.Ke * power

            return Photon(pos+direction*dist, col, direction)

    def forward(self, scene, depth):
        if depth > 0:
            ray = Ray(self.pos, self.direction)

            bounce = ray.intersect(scene)

            if bounce:
                bounce_object = bounce.obj
                bounce_pos = ray.after(bounce.t - EPSILON)

                bounce_ds_r = bounce_object.material.Kd.x + bounce_object.material.Ks.x
                bounce_ds_g = bounce_object.material.Kd.y + bounce_object.material.Ks.y
                bounce_ds_b = bounce_object.material.Kd.z + bounce_object.material.Ks.z

                object_Kd = bounce_object.material.Kd.avg()
                object_Ks = bounce_object.material.Ks.avg()

                propability_reflection = max(bounce_ds_r, bounce_ds_g, bounce_ds_b)

                propability_difuse = object_Kd/(object_Kd+object_Ks)*propability_reflection


                propability_specular = propability_reflection - propability_difuse

                rnd = random()

                print(propability_difuse)

                if rnd < 0.5:

                    self.col /= 0.5
                    self.col *= bounce_object.material.Kd
                    self.col /= pi*2

                    bounce_photon = Photon(deepcopy(bounce_pos), deepcopy(self.col), Vec3.point_on_hemisphere(bounce_object.normal()))

                    #return bounce_photon.forward(scene, depth-1)
                    return [deepcopy(bounce_photon)] + bounce_photon.forward(scene, depth - 1)

                elif rnd < propability_difuse + propability_specular:
                    # TODO Add specular bounce
                    pass

                else:

                    self.col /= (1-propability_reflection)
                    self.col *= bounce_object.material.Kd/ (pi*2)
                    return [Photon(bounce_pos, self.col, Vec3.point_on_hemisphere(bounce_object.normal()))]

        return []


class PhotonList:
    def __init__(self, photons = None):
        self.photons = []
        if photons:
            self.photons = photons

    def __iter__(self):
        for photon in self.photons:
            yield photon


class PhotonBox:
    def __init__(self, photon_list, box = None):
        if box:
            self.box = box
            self.photons = photon_list.photons

        else:
            box = AAbox()

            for photon in photon_list:
                box.extend(photon)

            box = AAbox.large_box(box.min_corner, box.max_corner)

            self.box = box
            self.photons = photon_list.photons

    def nearest_neighbour(self, pos, max_dist = None):
        best_obj = None
        best_dist2 = inf

        for obj in self.photons:
            dist2 = obj.distance2(pos)

            if dist2 < best_dist2:
                best_dist2 = dist2
                best_obj = obj

        dist = sqrt(best_dist2)
        if max_dist:
            if dist > max_dist:
                return False

        return Hit(best_obj, dist)

    def nearest_neighbour_excluding(self, pos, exclusions, max_dist = None):
        best_obj = None
        best_dist2 = inf

        for obj in self.photons:
            if obj not in exclusions:
                dist2 = obj.distance2(pos)

                if dist2 < best_dist2:
                    best_dist2 = dist2
                    best_obj = obj

        dist = sqrt(best_dist2)
        if max_dist:
            if dist>max_dist:
                return False

        return Hit(best_obj, dist)

    def k_nearest_neighbours(self, pos, k):
        best_obj = []
        worst_pass_dist2 = 0

        if k > len(self.photons):
            for photon in self.photons:
                best_obj.append(Hit(photon, photon.distance(pos)))

            best_obj.sort()

            return best_obj

        for obj in self.photons:
            dist2 = obj.distance2(pos)

            if len(best_obj) < k:
                insort(best_obj, Hit(obj,sqrt(dist2)))
                worst_pass_dist2 = max(worst_pass_dist2, dist2)

            elif dist2 < worst_pass_dist2:
                best_obj = best_obj[:-1]
                insort(best_obj,Hit(obj,dist2))
                worst_pass_dist2 = best_obj[-1].t

        return best_obj

    def get_box_at(self, pos):
        return self

