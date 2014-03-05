__author__ = 'Docopoper'

from globals import *


#engine interface - all variables visible to the outside world
class engine:
    working_fps = 30
    fps = working_fps

    keys_down = set()
    keys_pressed = set()
    keys_released = set()

    mouse_down = set()
    mouse_pressed = set()
    mouse_released = set()

    mouse_x = 0
    mouse_y = 0

    objects = set()


#Dispatches events to all objects in the system
class EventHandler(pyglet.event.EventDispatcher):
    #Update all objects
    def tick(self, dt):
        engine.fps = 1 / dt

        self.dispatch_event("on_tick")

        #Clear the inputs from last frame
        engine.keys_released.clear()
        engine.keys_pressed.clear()
        engine.mouse_released.clear()
        engine.mouse_pressed.clear()

    def on_tick(self):
        pass

EventHandler.register_event_type("on_tick")

event_handler = EventHandler()

pyglet.clock.schedule_interval(event_handler.tick, 1.0 / engine.working_fps)

###############################


class TestObj:
    def on_tick(self):
        if mouse.LEFT in engine.mouse_pressed:
            print engine.mouse_x, engine.mouse_y

test_obj = TestObj()
event_handler.push_handlers(test_obj)
engine.objects.add(test_obj)