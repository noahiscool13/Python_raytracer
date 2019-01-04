from math import *

from MathUtil import *
from SceneObjects import *


def diffuse(normal, posHit, lightPos, material):
    lightDirection = (lightPos - posHit).unit()
    return max(lightDirection.dot(normal), 0) * material.Kd


def specular(normal, posHit, lightPos, cameraPos, material):
    lightDirection = (lightPos - posHit).unit()
    reflec = (2 * (normal.dot(lightDirection)) * normal - lightDirection)
    spec = max((cameraPos - posHit).unit().dot(reflec), 0)
    return spec ** material.Ns * material.Ks


def check_if_in_light(pos, light, triangle, triangles):
    direction = (light.pos - pos)
    target_dist = direction.length()
    direction.normalize()

    ray = Ray(light.pos, direction)

    for tri in triangles:
        dist = ray.intersect(tri)
        if dist:
            if dist.obj != triangle:
                return False
    return True
