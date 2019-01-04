from MathUtil import *
from SceneObjects import *


def parce_mtl(data, scene):
    data = data.splitlines()

    scene.materials = {}

    mtl = Material()
    mtl_name = "default"

    for line in data:
        if line:
            l = line.split()

            if l[0] == "newmtl":
                scene.materials[mtl_name] = mtl

                mtl = Material()

                mtl_name = l[1]

            elif l[0] == "Ns":
                mtl.Ns = float(l[1])

            elif l[0] == "Ka":
                mtl.Ka = Vec3(float(l[1]), float(l[2]), float(l[3]))

            elif l[0] == "Kd":
                mtl.Kd = Vec3(float(l[1]), float(l[2]), float(l[3]))

            elif l[0] == "Ks":
                mtl.Ks = Vec3(float(l[1]), float(l[2]), float(l[3]))

            elif l[0] == "Ke":
                mtl.Ke = Vec3(float(l[1]), float(l[2]), float(l[3]))

            elif l[0] == "Ni":
                mtl.Ni = float(l[1])

            elif l[0] == "d":
                mtl.d = float(l[1])

    scene.materials[mtl_name] = mtl


def parse_obj(data):
    data = data.splitlines()
    scene = Scene()

    vertex_normals = []

    fixoverlap = False

    pl = []
    ps = set()

    mtl = Material()

    for row in data:
        if row:
            if row == "#fixoverlap":
                fixoverlap = True

            r = row.split()

            if r[0] == "mtllib":
                with open(r[1], "r") as file:
                    parce_mtl(file.read(),scene)
                    mtl = scene.materials["default"]

            if r[0] == "usemtl":
                mtl = scene.materials[r[1]]

            if r[0] == "v":
                p = Point(Vec3(float(r[1]), float(r[2]), float(r[3])))
                if fixoverlap:
                    if p in ps:
                        for n in scene.points:
                            if n == p:
                                scene.points.append(n)
                                break
                    else:
                        scene.points.append(p)
                        pl.append(p)
                        ps.add(p)
                else:
                    scene.points.append(p)

            if r[0] == "vn":
                vertex_normals.append(Vec3(float(r[1]), float(r[2]), float(r[3])))

            if r[0] == "f":

                face_points = []

                for p in range(1,len(r)):
                    ps = r[p].split("/")
                    face_points.append(scene.points[int(ps[0]) - 1])

                    if len(ps) > 1:
                        pass

                    if len(ps) > 2:
                        pass
                        #p1.normal = vertex_normals[int(ps[2])-1]

                for p in range(len(face_points)-2):
                    scene.objects.append(
                        Triangle(face_points[0], face_points[p+1], face_points[p+2],material=mtl)
                    )

    scene.calc_vertex_normals()

    return scene


def parse_senario(data, scene):
    data = data.splitlines()

    scene.rendersize = (20, 10)
    scene.ss = 4

    for row in data:
        if row:
            r = row.split()
            if r[0] == "point_light":
                scene.lights.append(
                    Light(Vec3(float(r[1]), float(r[2]), float(r[3])), Vec3(float(r[4]), float(r[5]), float(r[6]))))
            if r[0] == "camera":
                scene.camera = Camera(
                    Point(Vec3(float(r[1]), float(r[2]), float(r[3])), Vec3(float(r[4]), float(r[5]), float(r[6]))))
            if r[0] == "render_size":
                scene.rendersize = (int(r[1]), int(r[2]))
            if r[0] == "ss":
                scene.ss = int(r[1])






