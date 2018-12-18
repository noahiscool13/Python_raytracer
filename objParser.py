from MathUtil import *
from SceneObjects import *

def parse(data):
    data = data.splitlines()
    vertecies = []
    triangles = []
    lights = []

    for row in data:
        if row:
            r = row.split()
            if r[0] == "v":
                vertecies.append(Vec3(float(r[1]),float(r[2]),float(r[3])))
            if r[0] == "f":
                triangles.append(Triangle(vertecies[int(r[1])-1],vertecies[int(r[2])-1],vertecies[int(r[3])-1]))
            if r[0] == "light":
                lights.append(Light(vertecies[int(r[1])-1],vertecies[int(r[2])-1]))

    return Scene(triangles,lights)