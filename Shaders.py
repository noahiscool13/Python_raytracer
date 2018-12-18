from math import *

from MathUtil import *
from SceneObjects import *

def diffuse(object, posHit, light):
    lightDirection = (light.pos - posHit).unit()
    return abs(lightDirection.dot(object.normal())) * light.color * object.kd


def check_if_in_light(pos, light, triangles):
    direction = (light.pos - pos)
    target_dist = direction.length()
    direction.normalize()

    ray = Ray(light.pos, direction)

    for triangle in triangles:
        dist = ray.intersect(triangle)
        if dist>EPSILON and abs(dist-target_dist)<EPSILON:
            return False
    return True