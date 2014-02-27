__author__ = 'Docopoper'

import globals as gbl


#engine interface - all variables visible to the outside world
class engine:
    working_fps = 30
    fps = working_fps

    objects = set()


#Dispatches events to all objects in the system
class EventHandler(gbl.pyglet.event.EventDispatcher):
    #Update all objects
    def tick(self, dt):
        engine.fps = 1 / dt

        self.dispatch_event("on_tick")

        #Clear the inputs from last frame
        gbl.keys_released.clear()
        gbl.keys_pressed.clear()
        gbl.mouse_released.clear()
        gbl.mouse_pressed.clear()

    def on_tick(self):
        pass

EventHandler.register_event_type("on_tick")

event_handler = EventHandler()

gbl.pyglet.clock.schedule_interval(event_handler.tick, 1.0 / engine.working_fps)

###############################


class TestObj:
    def on_tick(self):
        if gbl.mouse.LEFT in gbl.mouse_pressed:
            print gbl.keys_down

test_obj = TestObj()
event_handler.push_handlers(test_obj)
engine.objects.add(test_obj)