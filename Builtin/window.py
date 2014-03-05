__author__ = 'Docopoper'

from globals import *

window = pyglet.window.Window(resizable=True, width=800, height=600)
window.set_minimum_size(200, 150)


@window.event
def on_draw():
    window.set_caption(str(engine.fps))
    window.clear()


@window.event
def on_key_press(symbol, modifiers):
    engine.keys_down.add(symbol)
    engine.keys_pressed.add(symbol)


@window.event
def on_key_release(symbol, modifiers):
    engine.keys_down.remove(symbol)
    engine.keys_released.add(symbol)


@window.event
def on_mouse_press(x, y, button, modifiers):
    engine.mouse_down.add(button)
    engine.mouse_pressed.add(button)


@window.event
def on_mouse_release(x, y, button, modifiers):
    engine.mouse_down.remove(button)
    engine.mouse_released.add(button)


@window.event
def on_mouse_motion(x, y, dx, dy):
    engine.mouse_x = x
    engine.mouse_y = y