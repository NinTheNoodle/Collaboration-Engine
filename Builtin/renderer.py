__author__ = 'Docopoper'

from globals import *
import globals
import weakref

class DrawingLayer(pyglet.graphics.OrderedGroup):
    def __init__(self, order):
        super(DrawingLayer, self).__init__(order)
        self.drawables = weakref.WeakSet()

class Renderer(object):
    drawing_layers = {"backdrop":   DrawingLayer(0),
                      "background": DrawingLayer(1),
                      "default":    DrawingLayer(2),
                      "foreground": DrawingLayer(3),
                      "hud":        DrawingLayer(4)}

    batch = pyglet.graphics.Batch()
    tex_draw = None
    buffers = pyglet.image.get_buffer_manager()
    bfr_col = buffers.get_color_buffer()

    window_invalidated = True
    window_hidden = False

    drawables_to_show = []
    drawables_to_hide = []

    def update_drawable_visibility(self):
        for drawable in self.drawables_to_hide:
            if not drawable.require_draw:
                drawable.disabled = True

        for drawable in self.drawables_to_show:
            drawable.disabled = False
            drawable.require_draw = False

        self.drawables_to_hide = self.drawables_to_show
        self.drawables_to_show = []


    def draw(self):
        self.update_drawable_visibility()

        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.bfr_col.gl_buffer)

        glFramebufferTexture2DEXT(GL_DRAW_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT,
                                  self.tex_draw.target, self.tex_draw.id, 0)

        globals.camera.projection_world()

        self.batch.draw()

        glBindFramebufferEXT(GL_DRAW_FRAMEBUFFER_EXT, 0)

    #recreate the drawing texture if the window has been resized
    def _validate_window(self):
        if self.window_invalidated:
            self.tex_draw = pyglet.image.Texture.create_for_size(GL_TEXTURE_2D, globals.window.width, globals.window.height, internalformat=GL_RGB)
            self.window_invalidated = False


renderer = Renderer()