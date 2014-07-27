__author__ = 'Docopoper'

from globals import *
import globals


class Camera:
    x = 0
    y = 0
    view_width = 800
    view_height = 600
    active_scale = 1
    visible_scale = 1

    def on_tick(self):
        if self.visible_scale > 0:
            globals.engine.visibility_region(self.x - self.visible_scale * self.view_width / 2,
                                             self.y - self.visible_scale * self.view_height / 2,
                                             self.x + self.visible_scale * self.view_width / 2,
                                             self.y + self.visible_scale * self.view_height / 2)

        if self.active_scale > 0:
            globals.engine.activity_region(self.x - self.active_scale * self.view_width / 2,
                                           self.y - self.active_scale * self.view_height / 2,
                                           self.x + self.active_scale * self.view_width / 2,
                                           self.y + self.active_scale * self.view_height / 2)

    def projection_world(self):
        try:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glMatrixMode(GL_PROJECTION)

            glLoadIdentity()

            gluOrtho2D(
                camera.x - camera.view_width / 2,
                camera.x + camera.view_width / 2,
                camera.y + camera.view_height / 2,
                camera.y - camera.view_height / 2)

            glMatrixMode(GL_MODELVIEW)

            glLoadIdentity()
        except pyglet.gl.lib.GLException: pass

    def projection_default(self):
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

    def screen_to_world(self, pos):
        return pos[0] + camera.x - globals.window.width / 2, pos[1] + camera.y - globals.window.height / 2

    def world_to_screen(self, pos):
        return pos[0] - camera.x + globals.window.width / 2, pos[1] - camera.y + globals.window.height / 2

camera = Camera()