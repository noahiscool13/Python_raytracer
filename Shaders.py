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


def check_if_in_light(pos, light, triangles):
    direction = (light.pos - pos)
    target_dist = direction.length()
    direction.normalize()

    ray = Ray(light.pos, direction)

    for triangle in triangles:
        dist = ray.intersect(triangle)
        if dist > EPSILON and abs(dist - target_dist) < EPSILON:
            return False
    return True
