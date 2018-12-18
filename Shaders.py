from MathUtil import *

def diffuse(object, posHit, light):
    lightDirection = (light.pos - posHit).unit()
    #return Vec3(1.0)
    #print(lightDirection.dot(object.normal())* light.color * object.kd)
    return abs(lightDirection.dot(object.normal())) * light.color * object.kd