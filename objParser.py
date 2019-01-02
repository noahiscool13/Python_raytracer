from MathUtil import *
from SceneObjects import *

def parse_obj(data):
    data = data.splitlines()
    scene = Scene()

    fixoverlap = False

    pl = []
    ps = set()

    for row in data:
        if row:
            if row == "#fixoverlap":
                fixoverlap = True
            r = row.split()
            if r[0] == "v":
                p = Point(Vec3(float(r[1]),float(r[2]),float(r[3])))
                if fixoverlap:
                    if p in ps:
                        for n in scene.points:
                            if n == p :
                                scene.points.append(n)
                                break
                    else:
                        scene.points.append(p)
                        pl.append(p)
                        ps.add(p)
                else:
                    scene.points.append(p)
            if r[0] == "f":
                scene.objects.append(Triangle(scene.points[int(r[1]) - 1], scene.points[int(r[2]) - 1], scene.points[int(r[3]) - 1]))

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
                scene.lights.append(Light(Vec3(float(r[1]),float(r[2]),float(r[3])), Vec3(float(r[4]),float(r[5]),float(r[6]))))
            if r[0] == "camera":
                scene.camera = Camera(Point(Vec3(float(r[1]),float(r[2]),float(r[3])), Vec3(float(r[4]),float(r[5]),float(r[6]))))
            if r[0] == "render_size":
                scene.rendersize = (int(r[1]),int(r[2]))
            if r[0] == "ss":
                scene.ss = int(r[1])