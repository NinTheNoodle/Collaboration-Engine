__author__ = 'Docopoper'

import globals as gbl

objects = set()


#engine interface - all variables visible to the outside world
class engine:
    working_fps = 30
    fps = working_fps


#Update all objects
def on_tick(dt):
    engine.fps = 1 / dt
    for obj in objects.copy():
        obj.on_tick()

    gbl.keys_released.clear()
    gbl.keys_pressed.clear()


gbl.pyglet.clock.schedule_interval(on_tick, 1.0 / engine.working_fps)