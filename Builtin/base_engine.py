__author__ = 'Docopoper'

from globals import *
import globals


#engine interface - all variables visible to the outside world
class engine:
    working_fps = 30
    fps = working_fps

    editor_mode = False

    keys_down = set()
    keys_pressed = set()
    keys_released = set()

    mouse_down = set()
    mouse_pressed = set()
    mouse_released = set()

    mouse_x = 0
    mouse_y = 0

    @staticmethod
    def instance_create(module_name, class_name, x=0, y=0):
        inst = engine.get_class(module_name, class_name)()
        inst.x = x
        inst.y = y
        instances.add(inst)
        event_handler.push_handlers(inst)
        try:
            inst.on_create()
        except AttributeError as e:
            #ensure that only exceptions that were created by the create function not existing are ignored
            if e.message != inst.__class__.__name__ + " instance has no attribute 'on_create'":
                raise

        return inst

    #find the currently scoped class of the given name
    @staticmethod
    def get_object(module_name, object_type, object_name):
        try:
            return objects_local[object_type][(module_name, object_name)]
        except KeyError:
            try:
                return objects_global[object_type][(module_name, object_name)]
            except KeyError:
                you_done_goofed = "Unknown class '" + str(object_name) + "' in module '" + str(module_name) + "'"
                raise KeyError(you_done_goofed)

    #region get_object convenience methods
    @staticmethod
    def get_class(module_name, class_name):
        return engine.get_object(module_name, "class", class_name)

    @staticmethod
    def get_sprite(module_name, sprite_name):
        return engine.get_object(module_name, "sprite", sprite_name)

    @staticmethod
    def get_sound(module_name, sound_name):
        return engine.get_object(module_name, "sound", sound_name)

    @staticmethod
    def get_music(module_name, music_name):
        return engine.get_object(module_name, "music", music_name)

    @staticmethod
    def get_resource(module_name, resource_name):
        return engine.get_object(module_name, "resource", resource_name)
    #endregion

    #region Class registration functions
    #register a new object on the local scope
    @staticmethod
    def register_object_local(module_name, object_type, object_name, object_ref):
        objects_local[object_type][(module_name, object_name)] = object_ref

    #region register_object_local convenience methods
    @staticmethod
    def register_class_local(module_name, class_name, class_ref):
        return engine.register_object_local(module_name, "class", class_name, class_ref)

    @staticmethod
    def register_sprite_local(module_name, sprite_name, image_ref):
        return engine.register_object_local(module_name, "sprite", sprite_name, image_ref)

    @staticmethod
    def register_sound_local(module_name, sound_name, sound_ref):
        return engine.register_object_local(module_name, "sound", sound_name, sound_ref)

    @staticmethod
    def register_music_local(module_name, music_name, file_name):
        return engine.register_object_local(module_name, "music", music_name, file_name)

    @staticmethod
    def register_resource_local(module_name, resource_name, file_name):
        return engine.register_object_local(module_name, "resource", resource_name, file_name)
    #endregion

    #register a new object on the global scope
    @staticmethod
    def register_object_global(module_name, object_type, object_name, object_ref):
        objects_global[object_type][(module_name, object_name)] = object_ref

    #region register_object_local convenience methods
    @staticmethod
    def register_class_global(module_name, class_name, class_ref):
        return engine.register_object_global(module_name, "class", class_name, class_ref)

    @staticmethod
    def register_sprite_global(module_name, sprite_name, image_ref):
        return engine.register_object_global(module_name, "sprite", sprite_name, image_ref)

    @staticmethod
    def register_sound_global(module_name, sound_name, sound_ref):
        return engine.register_object_global(module_name, "sound", sound_name, sound_ref)

    @staticmethod
    def register_music_global(module_name, music_name, file_name):
        return engine.register_object_global(module_name, "music", music_name, file_name)

    @staticmethod
    def register_resource_global(module_name, resource_name, file_name):
        return engine.register_object_global(module_name, "resource", resource_name, file_name)
    #endregion

    #endregion

    #recreate the drawing texture if the window has been resized
    @staticmethod
    def validate_window():
        global window_invalidated

        if window_invalidated:
            global tex_draw
            tex_draw = pyglet.image.Texture.create_for_size(GL_TEXTURE_2D, globals.window.width, globals.window.height, internalformat=GL_RGB)
            window_invalidated = False


buffers = pyglet.image.get_buffer_manager()
bfr_col = buffers.get_color_buffer()

tex_draw = None

#internal set of existing instances
instances = set()

#internal dictionaries of names to references
objects_global = {"class": {}, "sprite": {}, "sound": {}, "music": {}, "resource": {}}
objects_local = {"class": {}, "sprite": {}, "sound": {}, "music": {}, "resource": {}}

window_invalidated = True
window_hidden = False


#Dispatches events to all objects in the system
class EventHandler(pyglet.event.EventDispatcher):
    #Update all objects
    def tick(self, dt):
        global window_hidden
        if window_hidden:
            window_hidden = globals.window.hidden
            return

        engine.fps = 1 / dt

        if engine.editor_mode:
            camera.view_width = globals.window.width
            camera.view_height = globals.window.height
            self.dispatch_event("on_editor_tick")
        else:
            self.dispatch_event("on_tick")
        engine.validate_window()
        self.draw()

        #Clear the inputs from last frame
        engine.keys_released.clear()
        engine.keys_pressed.clear()
        engine.mouse_released.clear()
        engine.mouse_pressed.clear()

    def draw(self):
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, bfr_col.gl_buffer)

        glFramebufferTexture2DEXT(GL_DRAW_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT,
                                  tex_draw.target, tex_draw.id, 0)

        globals.camera.projection_world()

        if engine.editor_mode:
            self.dispatch_event("on_editor_draw")
        else:
            self.dispatch_event("on_draw")

        glBindFramebufferEXT(GL_DRAW_FRAMEBUFFER_EXT, 0)


EventHandler.register_event_type("on_tick")
EventHandler.register_event_type("on_editor_tick")
EventHandler.register_event_type("on_draw")
EventHandler.register_event_type("on_editor_draw")

event_handler = EventHandler()

pyglet.clock.schedule_interval(event_handler.tick, 1.0 / engine.working_fps)
pyglet.clock.set_fps_limit(engine.working_fps)