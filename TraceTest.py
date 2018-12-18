from objParser import *
from RayTraceCore import *

with open("box.obj", "r") as file:
    scene = parse(file.read())
    triangles = scene.triangles
    lights = scene.lights

for x in triangles:
    print(x)
print(lights[0])
render(triangles, lights, 0, 0)
