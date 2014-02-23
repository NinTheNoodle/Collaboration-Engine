__author__ = 'Docopoper'

import globals as gbl


window = gbl.pyglet.window.Window(resizable=True)

@window.event
def on_draw():
    window.set_caption(str(gbl.engine.fps))
    window.clear()


