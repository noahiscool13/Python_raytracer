from SceneObjects import *


def ambiant(material, scene):
    return material.Ka * scene.ambiant_light


def emittance(material):
    return material.Ke


def direct(material):
    return material.Kd


def diffuse(normal, posHit, lightPos, material=Material(Kd=Vec3(1)), uv=Vec2(0, 0)):
    lightDirection = (lightPos - posHit).unit()
    return max(lightDirection.dot(normal), 0) * material.Kd


def specular(normal, posHit, lightPos, cameraPos, material, uv=(0,0)):
    lightDirection = (lightPos - posHit).unit()
    reflec = (2 * (normal.dot(lightDirection)) * normal - lightDirection)
    spec = max((cameraPos - posHit).unit().dot(reflec), 0)
    return spec ** material.Ns * material.Ks


def check_if_visable(pos, light, triangle, scene):
    direction = (pos - light)
    #max_dist = direction.length()
    direction.normalize()

    ray = Ray(light, direction)
    hit = ray.intersect(scene)

    if hit:
        return hit.obj == triangle
    return False
    # for obj in objects:
    #     dist = ray.intersect(obj)
    #     if dist:
    #         if dist.obj != triangle:
    #             if dist.t < max_dist:
    #                 return False
    # return True

def texture_map_kd(material,uv):
    return material.map_Kd.get_value(uv)
