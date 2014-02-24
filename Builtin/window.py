__author__ = 'Docopoper'

import globals as gbl


keys_down = set()
keys_pressed = set()
keys_released = set()

window = gbl.pyglet.window.Window(resizable=True, width=800, height=600)
window.set_minimum_size(200, 150)


@window.event
def on_draw():
    window.set_caption(str(gbl.engine.fps))
    window.clear()


@window.event
def on_key_press(symbol, modifiers):
    keys_down.add(symbol)
    keys_pressed.add(symbol)


@window.event
def on_key_release(symbol, modifiers):
    keys_down.remove(symbol)
    keys_released.add(symbol)