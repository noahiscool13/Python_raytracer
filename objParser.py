from MathUtil import *
from SceneObjects import *

def parse(data):
    data = data.splitlines()
    scene = Scene()

    for row in data:
        if row:
            r = row.split()
            if r[0] == "v":
                scene.points.append(Point(Vec3(float(r[1]),float(r[2]),float(r[3]))))
            if r[0] == "f":
                scene.triangles.append(Triangle(scene.points[int(r[1])-1],scene.points[int(r[2])-1],scene.points[int(r[3])-1]))
            if r[0] == "light":
                scene.lights.append(Light(scene.points[int(r[1])-1],scene.points[int(r[2])-1]))
            if r[0] == "camera":
                scene.camera = Camera(Point(scene.points[int(r[1])-1].pos,scene.points[int(r[2])-1].pos))
    scene.calc_vertex_normals()
    return scene