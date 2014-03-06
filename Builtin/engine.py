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

    @staticmethod
    def instance_create(name, x=0, y=0, *args, **kwargs):
        inst = get_class(name)()
        inst.x = x
        inst.y = y
        instances.add(inst)
        event_handler.push_handlers(inst)
        try:
            inst.on_create(args, kwargs)
        except AttributeError as e:
            #ensure that only exceptions that were created by the create function not existing are ignored
            if e.message != inst.__class__.__name__ + " instance has no attribute 'on_create'":
                raise

#internal set of existing instances
instances = set()
#internal dictionaries of class names to class references
classes_global = {}
classes_local = {}


#find the currently scoped class of the given name
def get_class(name):
    try:
        return classes_local[name]
    except KeyError:
        return classes_global[name]


#register a new class on the local scope
def register_class_local(class_name, class_ref):
    classes_local[class_name] = class_ref


#register a new class on the local scope
def register_class_global(class_name, class_ref):
    classes_global[class_name] = class_ref


#Dispatches events to all objects in the system
class EventHandler(pyglet.event.EventDispatcher):
    #Update all objects
    def tick(self, dt):
        engine.fps = 1 / dt

        self.dispatch_event("on_tick")
        self.dispatch_event("on_draw")

        #Clear the inputs from last frame
        engine.keys_released.clear()
        engine.keys_pressed.clear()
        engine.mouse_released.clear()
        engine.mouse_pressed.clear()

    def on_tick(self):
        pass

EventHandler.register_event_type("on_tick")
EventHandler.register_event_type("on_draw")

event_handler = EventHandler()

pyglet.clock.schedule_interval(event_handler.tick, 1.0 / engine.working_fps)

###############################


class TestObj:
    def on_create(self, args, kwargs):
        print args, kwargs

    def on_tick(self):
        if mouse.LEFT in engine.mouse_pressed:
            print engine.mouse_x, engine.mouse_y

register_class_global("Test", TestObj)
engine.instance_create("Test", 0, 0)