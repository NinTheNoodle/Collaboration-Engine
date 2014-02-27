__author__ = 'Docopoper'

import globals as gbl


keys_down = set()
keys_pressed = set()
keys_released = set()

mouse_down = set()
mouse_pressed = set()
mouse_released = set()

mouse_x = 0
mouse_y = 0

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

@window.event
def on_mouse_press(x, y, button, modifiers):
    mouse_down.add(button)
    mouse_pressed.add(button)

@window.event
def on_mouse_release(x, y, button, modifiers):
    mouse_down.remove(button)
    mouse_released.add(button)

@window.event
def on_mouse_motion(x, y, dx, dy):
    mouse_x = x
    mouse_y = y