from objParser import *
from RayTraceCore import *

if __name__ == '__main__':

    with open("teapot.obj", "r") as file:
        scene = parse(file.read())
        triangles = scene.triangles
        lights = scene.lights
        camera = scene.camera

    # for x in triangles:
    #     print(x)
    # print(lights[0])
    render(scene)
