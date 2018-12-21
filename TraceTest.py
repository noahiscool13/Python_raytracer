from objParser import *
from RayTraceCore import *

with open("teapot.obj", "r") as file:
    scene = parse(file.read())
    triangles = scene.triangles
    lights = scene.lights
    camera = scene.camera

# for x in triangles:
#     print(x)
# print(lights[0])
render(triangles, lights, camera)
