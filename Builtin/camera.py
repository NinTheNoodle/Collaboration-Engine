__author__ = 'Docopoper'

from globals import *
import globals


class camera:
    x = 0
    y = 300
    view_width = 800
    view_height = 600

    @staticmethod
    def projection_world():
        try:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glMatrixMode(GL_PROJECTION)

            glLoadIdentity()

            gluOrtho2D(
                camera.x - camera.view_width / 2,
                camera.x + camera.view_width / 2,
                camera.y - camera.view_height / 2,
                camera.y + camera.view_height / 2)

            glMatrixMode(GL_MODELVIEW)

            glLoadIdentity()
        except pyglet.gl.lib.GLException: pass

    @staticmethod
    def projection_default():
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glMatrixMode(GL_PROJECTION)

        glLoadIdentity()

        gluOrtho2D(
            0,
            globals.window.width,
            0,
            globals.window.height)

        glMatrixMode(GL_MODELVIEW)

        glLoadIdentity()

    @staticmethod
    def screen_to_world(pos):
        return pos[0] + camera.x - globals.window.width / 2, pos[1] + camera.y - globals.window.height / 2

    @staticmethod
    def world_to_screen(pos):
        return pos[0] - camera.x + globals.window.width / 2, pos[1] - camera.y + globals.window.height / 2