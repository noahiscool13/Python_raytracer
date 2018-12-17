def diffuse(object, posHit, light):
    lightDirection = (light.pos - posHit).unit()
    return -lightDirection.dot(object.normal()) * light.color * object.kd