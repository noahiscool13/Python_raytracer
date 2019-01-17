from math import *

from MathUtil import *
from SceneObjects import *

def ambiant(material, scene):
    return material.Ka * scene.ambiant_light

def emittance(material):
    return material.Ke

def direct(material):
    return material.Kd


def diffuse(normal, posHit, lightPos, material):
    lightDirection = (lightPos - posHit).unit()
    return max(lightDirection.dot(normal), 0) * material.Kd


def specular(normal, posHit, lightPos, cameraPos, material):
    lightDirection = (lightPos - posHit).unit()
    reflec = (2 * (normal.dot(lightDirection)) * normal - lightDirection)
    spec = max((cameraPos - posHit).unit().dot(reflec), 0)
    return spec ** material.Ns * material.Ks


def check_if_in_light(pos, light, triangle, objects):
    direction = (pos - light.pos)
    direction.normalize()

    ray = Ray(light.pos, direction)

    for obj in objects:
        dist = ray.intersect(obj)
        if dist:
            if dist.obj != triangle:
                return False
    return True
