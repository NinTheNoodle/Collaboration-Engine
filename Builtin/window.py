__author__ = 'Docopoper'

from globals import *
import globals
import engine

window = pyglet.window.Window(resizable=True, width=800, height=600)
window.set_minimum_size(200, 150)

@window.event
def on_resize(width, height):
    engine.window_invalidated = True


@window.event
def on_draw():
    globals.Camera.projection_default()
    try:
        Engine.tex_draw.blit(0, 0)
    except AttributeError: Engine.validate_window()


@window.event
def on_key_press(symbol, modifiers):
    Engine.keys_down.add(symbol)
    Engine.keys_pressed.add(symbol)


@window.event
def on_key_release(symbol, modifiers):
    try:
        Engine.keys_down.remove(symbol)
    except KeyError: pass

    Engine.keys_released.add(symbol)


@window.event
def on_mouse_press(x, y, button, modifiers):
    Engine.mouse_down.add(button)
    Engine.mouse_pressed.add(button)


@window.event
def on_mouse_release(x, y, button, modifiers):
    try:
        Engine.mouse_down.remove(button)
    except KeyError: pass

    Engine.mouse_released.add(button)


@window.event
def on_mouse_motion(x, y, dx, dy):
    Engine.mouse_x = x
    Engine.mouse_y = y


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    on_mouse_motion(x, y, dx, dy)