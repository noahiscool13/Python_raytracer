from objParser import *
from RayTraceCore import *

with open("box.obj", "r") as file:
    scene = parse(file.read())
    triangles = scene.triangles
    lights = scene.lights

#triangles = [Triangle(Vec3(0,5,-2),Vec3(-0.2,-5,-2), Vec3(0.2,-5,-2))]
lights = [Light(Vec3(0, 0, -2), Vec3(1))]
for x in triangles:
    print(x)
print(lights[0])
render(triangles, lights, 0, 0)
