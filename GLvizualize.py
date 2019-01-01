import pygame

from OpenGL.GL import *
from OpenGL.GLU import *

from pygame.locals import *

from objParser import parse
from Shaders import *

from RayTraceCore import *




def main():
    pygame.init()
    display = (800, 400)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

    gluPerspective(30, (display[0] / display[1]), 0.1, 50.0)

    glTranslatef(*-scene.camera.point.pos)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[K_LEFT]:
            glRotatef(3, 0, 0, 1)
        if keys_pressed[K_RIGHT]:
            glRotatef(-3, 0, 0, 1)
        if keys_pressed[K_UP]:
            glRotatef(3, 1, 0, 0)
        if keys_pressed[K_DOWN]:
            glRotatef(-3, 1, 0, 0)

        if keys_pressed[K_w]:
            glTranslatef(0, 0.1, 0)
        if keys_pressed[K_s]:
            glTranslatef(0, -0.1, 0)
        if keys_pressed[K_a]:
            glTranslatef(-0.1, 0, 0)
        if keys_pressed[K_d]:
            glTranslatef(0.1, 0, 0)

        if keys_pressed[K_SPACE]:
            glTranslatef(0, 0, -0.2)
        if keys_pressed[K_LSHIFT]:
            glTranslatef(0.0, 0, 0.2)

        # glRotatef(1, 3, 1, 1)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for obj in scene.objects:

            if isinstance(obj, Triangle):

                glBegin(GL_TRIANGLES)
                for point in obj:
                    glColor4fv((*diffuse(point.normal,point.pos,lights[0].pos,obj.properties.Kd), 1))
                    glVertex3fv(point.toList())
                glEnd()

            if isinstance(obj,KDtree):
                obj.draw_gl()
                for objc in obj.objects:
                    glBegin(GL_TRIANGLES)
                    for point in objc:
                        glColor4fv((*diffuse(point.normal, point.pos, lights[0].pos, objc.properties.Kd), 1))
                        glVertex3fv(point.toList())
                    glEnd()

        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == "__main__":
    with open("teapot.obj", "r") as file:
        scene = parse(file.read())
        objects = scene.objects
        lights = scene.lights
        scene.optimize_scene(amount=8)

        render(scene)
    main()
