__author__ = 'Docopoper'

import globals as gbl

#engine interface - all variables visible to the outside world
class engine:
    working_fps = 30
    fps = working_fps

def on_tick(dt):
    engine.fps = 1 / dt

gbl.pyglet.clock.schedule_interval(on_tick, 1.0 / engine.working_fps)