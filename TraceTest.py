from objParser import *
from RayTraceCore import *

if __name__ == '__main__':

    with open("teapot.obj", "r") as file:
        scene = parse(file.read())
        scene.optimize_scene(amount=20)
        triangles = scene.objects
        lights = scene.lights
        camera = scene.camera

    # for x in triangles:
    #     print(x)
    # print(lights[0])
    render(scene)
