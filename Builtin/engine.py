__author__ = 'Docopoper'

from globals import *
import globals


#engine interface - all variables visible to the outside world
class Engine:
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

    buffers = pyglet.image.get_buffer_manager()
    bfr_col = buffers.get_color_buffer()

    tex_draw = None

    @staticmethod
    def instance_create(name, pos=(0, 0), *args, **kwargs):
        inst = Engine.get_class(name)()
        inst.x = pos[0]
        inst.y = pos[1]
        instances.add(inst)
        event_handler.push_handlers(inst)
        try:
            inst.on_create(args, kwargs)
        except AttributeError as e:
            #ensure that only exceptions that were created by the create function not existing are ignored
            if e.message != inst.__class__.__name__ + " instance has no attribute 'on_create'":
                raise

    #find the currently scoped class of the given name
    @staticmethod
    def get_class(name):
        try:
            return classes_local[name]
        except KeyError:
            return classes_global[name]

    #register a new class on the local scope
    @staticmethod
    def register_class_local(class_name, class_ref):
        classes_local[class_name] = class_ref

    #register a new class on the local scope
    @staticmethod
    def register_class_global(class_name, class_ref):
        classes_global[class_name] = class_ref

    #recreate the drawing texture if the window has been resized
    @staticmethod
    def validate_window():
        global window_invalidated

        if window_invalidated:
            Engine.tex_draw = pyglet.image.Texture.create(globals.window.width, globals.window.height, internalformat=GL_RGB)
            window_invalidated = False



#internal set of existing instances
instances = set()
#internal dictionaries of class names to class references
classes_global = {}
classes_local = {}

window_invalidated = True


#Dispatches events to all objects in the system
class EventHandler(pyglet.event.EventDispatcher):
    #Update all objects
    def tick(self, dt):
        Engine.fps = 1 / dt

        self.dispatch_event("on_tick")
        Engine.validate_window()
        self.draw()

        #Clear the inputs from last frame
        Engine.keys_released.clear()
        Engine.keys_pressed.clear()
        Engine.mouse_released.clear()
        Engine.mouse_pressed.clear()

    def draw(self):
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, Engine.bfr_col.gl_buffer)

        glFramebufferTexture2DEXT(GL_DRAW_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT,
                                  Engine.tex_draw.target, Engine.tex_draw.id, 0)

        globals.Camera.projection_world()
        self.dispatch_event("on_draw")

        glBindFramebufferEXT(GL_DRAW_FRAMEBUFFER_EXT, 0)


EventHandler.register_event_type("on_tick")
EventHandler.register_event_type("on_draw")

event_handler = EventHandler()

pyglet.clock.schedule_interval(event_handler.tick, 1.0 / Engine.working_fps)
pyglet.clock.set_fps_limit(Engine.working_fps)