from objParser import *
from RayTraceCore import *

if __name__ == '__main__':
    with open("monte-carlo.obj", "r") as file:
        scene = parse_obj(file.read())
    with open("monte-carlo.senario") as file:
        parse_senario(file.read(), scene)
    with open("monte-carlo.mtl") as file:
        parce_mtl(file.read(), scene)
    scene.optimize_scene(amount=20)
    triangles = scene.objects
    lights = scene.lights
    camera = scene.camera

    render(scene)
