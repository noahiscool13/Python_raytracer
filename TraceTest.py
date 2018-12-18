from objParser import *
from RayTraceCore import *

with open("box.obj", "r") as file:
    triangles = parse(file.read())

#triangles = [Triangle(Vec3(0,5,-2),Vec3(-0.2,-5,-2), Vec3(0.2,-5,-2))]
lights = [Light(Vec3(0, 0, -1), Vec3(1))]
for x in triangles:
    print(x)
print(lights[0])
render(triangles, lights, 0, 0)
