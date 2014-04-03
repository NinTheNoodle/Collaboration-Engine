__author__ = 'Docopoper'

from globals import *
import globals
import base_engine

window = pyglet.window.Window(resizable=True, width=800, height=600)
window.set_minimum_size(200, 150)
window.hidden = False


@window.event
def on_hide():
    window.hidden = True
    base_engine.window_hidden = True


@window.event
def on_show():
    window.hidden = False


@window.event
def on_resize(width, height):
    try:
        w = pyglet.image._nearest_pow2(base_engine.tex_draw.width)
        h = pyglet.image._nearest_pow2(base_engine.tex_draw.height)
    except AttributeError:
        base_engine.window_invalidated = True
        return

    if not (w / 2 < window.width < w
    and h / 2 < window.height < h):
        base_engine.window_invalidated = True


@window.event
def on_draw():
    if base_engine.window_hidden:
        return
    globals.camera.projection_default()
    try:
        base_engine.tex_draw.blit(0, 0)
    except AttributeError: engine.validate_window()


@window.event
def on_key_press(symbol, modifiers):
    engine.keys_down.add(symbol)
    engine.keys_pressed.add(symbol)


@window.event
def on_key_release(symbol, modifiers):
    try:
        engine.keys_down.remove(symbol)
    except KeyError: pass

    engine.keys_released.add(symbol)


@window.event
def on_mouse_press(x, y, button, modifiers):
    engine.mouse_down.add(button)
    engine.mouse_pressed.add(button)


@window.event
def on_mouse_release(x, y, button, modifiers):
    try:
        engine.mouse_down.remove(button)
    except KeyError: pass

    engine.mouse_released.add(button)


@window.event
def on_mouse_motion(x, y, dx, dy):
    engine.mouse_x = x * (float(camera.view_width) / window.width) - camera.x - camera.view_width / 2
    engine.mouse_y = y * (float(camera.view_height) / window.height) - camera.y - camera.view_height / 2


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    on_mouse_motion(x, y, dx, dy)