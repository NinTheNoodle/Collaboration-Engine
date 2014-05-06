__author__ = 'Docopoper'

from globals import *
import globals
import sys
import os


#engine interface - all variables visible to the outside world
class Engine(object):
    path = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))

    working_fps = 30
    fps = working_fps

    frame = 0
    time = 0

    keys_down = set()
    keys_pressed = set()
    keys_released = set()

    mouse_down = set()
    mouse_pressed = set()
    mouse_released = set()

    mouse_x = 0
    mouse_y = 0

    section_tags = set()
    layers = {}
    visibility_regions = []
    activity_regions = []

    event_types = []
    current_layer = None
    current_instance = None # Which instance is having its event called at the moment

    current_music = None

    @property
    def editor_mode(self): return editor_mode
    @editor_mode.setter
    def editor_mode(self, value):
        global desired_editor_mode
        desired_editor_mode = value

    def instance_create(self, module_name, class_name, layer_name, x=0, y=0, **kwargs):
        inst = engine.get_class(module_name, class_name)()
        inst.layer = engine.layers[layer_name]
        inst.x_start = inst.x = x
        inst.y_start = inst.y = y
        inst.module_name = module_name
        inst.class_name = class_name

        engine.get_enabled_instances(inst.module_name, inst.class_name).add(inst)
        engine.get_invisible_instances(inst.module_name, inst.class_name).add(inst)
        engine.get_inactive_instances(inst.module_name, inst.class_name).add(inst)

        for key, value in kwargs.iteritems():
            setattr(inst, key, value)

        engine.get_all_instances(module_name, class_name).add(inst)
        event_handler.add_handlers(inst)
        self.instance_update_handler_draw(inst)
        self.instance_update_handler_tick(inst)
        inst.on_create()

        return inst

    def instance_destroy(self, instance):
        if instance._destroyed: return
        instance._destroyed = True

        instance.on_destroy()
        instance.layer.instances.remove(instance)
        event_handler.remove_handlers(instance)
        try:
            engine.get_all_instances(instance.module_name, instance.class_name).remove(instance)
        except KeyError: pass
        try:
            engine.get_inactive_instances(instance.module_name, instance.class_name).remove(instance)
        except KeyError: pass
        try:
            engine.get_active_instances(instance.module_name, instance.class_name).remove(instance)
        except KeyError: pass
        try:
            engine.get_invisible_instances(instance.module_name, instance.class_name).remove(instance)
        except KeyError: pass
        try:
            engine.get_visible_instances(instance.module_name, instance.class_name).remove(instance)
        except KeyError: pass
        try:
            engine.get_enabled_instances(instance.module_name, instance.class_name).remove(instance)
        except KeyError: pass
        try:
            engine.get_disabled_instances(instance.module_name, instance.class_name).remove(instance)
        except KeyError: pass

    def layer_x(self, layer):
        return layers[layer].x

    def layer_y(self, layer):
        return layers[layer].y

    def activity_region(self, x1, y1, x2, y2):
        self.activity_regions.append((x1, y1, x2, y2))

    def visibility_region(self, x1, y1, x2, y2):
        self.visibility_regions.append((x1, y1, x2, y2))

    #region Instance state manipulation functions
    def instance_disable(self, inst):
        try:
            engine.get_enabled_instances(inst.module_name, inst.class_name).remove(inst)
        except KeyError: pass
        engine.get_disabled_instances(inst.module_name, inst.class_name).add(inst)
        inst._disabled = True
        self.instance_update_handler_draw(inst)
        self.instance_update_handler_tick(inst)
        inst.on_disable()

    def instance_enable(self, inst):
        try:
            engine.get_disabled_instances(inst.module_name, inst.class_name).remove(inst)
        except KeyError: pass
        engine.get_enabled_instances(inst.module_name, inst.class_name).add(inst)
        inst._disabled = False
        self.instance_update_handler_draw(inst)
        self.instance_update_handler_tick(inst)
        inst.on_enable()

    def instance_activate(self, inst):
        try:
            engine.get_inactive_instances(inst.module_name, inst.class_name).remove(inst)
        except KeyError: pass
        engine.get_active_instances(inst.module_name, inst.class_name).add(inst)
        inst._active = True
        self.instance_update_handler_tick(inst)
        inst.on_activate()

    def instance_deactivate(self, inst):
        try:
            engine.get_active_instances(inst.module_name, inst.class_name).remove(inst)
        except KeyError: pass
        engine.get_inactive_instances(inst.module_name, inst.class_name).add(inst)
        inst._active = False
        self.instance_update_handler_tick(inst)
        inst.on_deactivate()

    def instance_show(self, inst):
        try:
            engine.get_invisible_instances(inst.module_name, inst.class_name).remove(inst)
        except KeyError: pass
        engine.get_visible_instances(inst.module_name, inst.class_name).add(inst)
        inst._visible = True
        self.instance_update_handler_draw(inst)
        inst.on_visible()

    def instance_hide(self, inst):
        try:
            engine.get_visible_instances(inst.module_name, inst.class_name).remove(inst)
        except KeyError: pass
        engine.get_invisible_instances(inst.module_name, inst.class_name).add(inst)
        inst._visible = False
        self.instance_update_handler_draw(inst)
        inst.on_invisible()

    def instance_update_handler_draw(self, inst):
        if not inst.disabled and inst.visible:
            event_handler.add_handlers(inst, "on_draw")
        else:
            event_handler.remove_handlers(inst, "on_draw")

    def instance_update_handler_tick(self, inst):
        if not inst.disabled and inst.active:
            event_handler.add_handlers(inst, "on_tick")
        else:
            event_handler.remove_handlers(inst, "on_tick")
    #endregion

    #find the currently scoped class of the given name
    def _get_object(self, module_name, object_type, object_name):
        try:
            return objects_local[object_type][(module_name, object_name)]
        except KeyError:
            try:
                return objects_global[object_type][(module_name, object_name)]
            except KeyError:
                you_done_goofed = "Unknown " + object_type + " '" + str(object_name) + "' in module '" + str(module_name) + "'"
                raise KeyError(you_done_goofed)

    #region get_object convenience methods
    def get_class(self, module_name="*", class_name=None):
        if module_name == "*":
            return  set(objects_local["class"].values()) | set(objects_global["class"].values())
        return engine._get_object(module_name, "class", class_name)

    def get_sprite(self, module_name="*", sprite_name=None):
        if module_name == "*":
            return  set(objects_local["sprite"].values()) | set(objects_global["sprite"].values())
        return wrappers.Sprite(engine._get_object(module_name, "sprite", sprite_name))

    def get_sound(self, module_name="*", sound_name=None):
        if module_name == "*":
            return  set(objects_local["sound"].values()) | set(objects_global["sound"].values())
        return wrappers.Sound(engine._get_object(module_name, "sound", sound_name))

    def get_music(self, module_name="*", music_name=None):
        if module_name == "*":
            return  set(objects_local["music"].values()) | set(objects_global["music"].values())
        return engine._get_object(module_name, "music", music_name)

    def get_resource(self, module_name="*", resource_name=None):
        if module_name == "*":
            return  set(objects_local["resource"].values()) | set(objects_global["resource"].values())
        return engine._get_object(module_name, "resource", resource_name)

    def get_all_instances(self, module_name="*", class_name=None):
        if module_name == "*":
            return  set([x for y in objects_local["instance"].values() + objects_global["instance"].values() for x in y])
        return engine._get_object(module_name, "instance", class_name)

    def get_active_instances(self, module_name="*", class_name=None):
        if module_name == "*":
            return  set([x for y in objects_local["active instance"].values() + objects_global["active instance"].values() for x in y])
        return engine._get_object(module_name, "active instance", class_name)

    def get_inactive_instances(self, module_name="*", class_name=None):
        if module_name == "*":
            return  set([x for y in objects_local["inactive instance"].values() + objects_global["inactive instance"].values() for x in y])
        return engine._get_object(module_name, "inactive instance", class_name)

    def get_visible_instances(self, module_name="*", class_name=None):
        if module_name == "*":
            return  set([x for y in objects_local["visible instance"].values() + objects_global["visible instance"].values() for x in y])
        return engine._get_object(module_name, "visible instance", class_name)

    def get_invisible_instances(self, module_name="*", class_name=None):
        if module_name == "*":
            return  set([x for y in objects_local["invisible instance"].values() + objects_global["invisible instance"].values() for x in y])
        return engine._get_object(module_name, "invisible instance", class_name)

    def get_enabled_instances(self, module_name="*", class_name=None):
        if module_name == "*":
            return  set([x for y in objects_local["enabled instance"].values() + objects_global["enabled instance"].values() for x in y])
        return engine._get_object(module_name, "enabled instance", class_name)

    def get_disabled_instances(self, module_name="*", class_name=None):
        if module_name == "*":
            return  set([x for y in objects_local["disabled instance"].values() + objects_global["disabled instance"].values() for x in y])
        return engine._get_object(module_name, "disabled instance", class_name)
    #endregion

    #region Class registration functions

    def _register_class_dict(self, module_name, class_name, class_ref, dictionary):
        dictionary["class"][(module_name, class_name)] = class_ref
        dictionary["instance"][(module_name, class_name)] = set()
        dictionary["active instance"][(module_name, class_name)] = set()
        dictionary["inactive instance"][(module_name, class_name)] = set()
        dictionary["visible instance"][(module_name, class_name)] = set()
        dictionary["invisible instance"][(module_name, class_name)] = set()
        dictionary["enabled instance"][(module_name, class_name)] = set()
        dictionary["disabled instance"][(module_name, class_name)] = set()

    #register a new object on the local scope
    def _register_object_local(self, module_name, object_type, object_name, object_ref):
        objects_local[object_type][(module_name, object_name)] = object_ref

    #region register_object_local convenience methods
    def register_class_local(self, module_name, class_name, class_ref):
        self._register_class_dict(module_name, class_name, class_ref, objects_local)

    def register_sprite_local(self, module_name, sprite_name, image_ref):
        engine._register_object_local(module_name, "sprite", sprite_name, image_ref)

    def register_sound_local(self, module_name, sound_name, sound_ref):
        engine._register_object_local(module_name, "sound", sound_name, sound_ref)

    def register_music_local(self, module_name, music_name, music_ref):
        engine._register_object_local(module_name, "music", music_name, music_ref)

    def register_resource_local(self, module_name, resource_name, file_name):
        engine._register_object_local(module_name, "resource", resource_name, file_name)
    #endregion

    #register a new object on the global scope
    def _register_object_global(self, module_name, object_type, object_name, object_ref):
        objects_global[object_type][(module_name, object_name)] = object_ref
        object_ref.is_local = False

    #region register_object_local convenience methods
    def register_class_global(self, module_name, class_name, class_ref):
        self._register_class_dict(module_name, class_name, class_ref, objects_global)

    def register_sprite_global(self, module_name, sprite_name, image_ref):
        engine._register_object_global(module_name, "sprite", sprite_name, image_ref)

    def register_sound_global(self, module_name, sound_name, sound_ref):
        engine._register_object_global(module_name, "sound", sound_name, sound_ref)

    def register_music_global(self, module_name, music_name, file_name):
        engine._register_object_global(module_name, "music", music_name, file_name)

    def register_resource_global(self, module_name, resource_name, file_name):
        engine._register_object_global(module_name, "resource", resource_name, file_name)
    #endregion

    #endregion

    #recreate the drawing texture if the window has been resized
    def _validate_window(self):
        global window_invalidated

        if window_invalidated:
            global tex_draw
            tex_draw = pyglet.image.Texture.create_for_size(GL_TEXTURE_2D, globals.window.width, globals.window.height, internalformat=GL_RGB)
            window_invalidated = False

    def _instances_update_states(self):
        #go through each instance and check to see if it should be active and visible
        for inst in self.get_all_instances():
            active = inst.always_active
            visible = inst.always_visible

            if not active:
                for x1, y1, x2, y2 in self.activity_regions:
                    if (inst.bbox_active[0] + inst.x < x2
                    and inst.bbox_active[1] + inst.y < y2
                    and inst.bbox_active[2] + inst.x > x1
                    and inst.bbox_active[3] + inst.y > y1):
                        active = True
                        break

            if not visible:
                for x1, y1, x2, y2 in self.visibility_regions:
                    if (inst.bbox_visible[0] + inst.x < x2
                    and inst.bbox_visible[1] + inst.y < y2
                    and inst.bbox_visible[2] + inst.x > x1
                    and inst.bbox_visible[3] + inst.y > y1):
                        visible = True
                        break

            inst.active = active
            inst.visible = visible

        self.activity_regions = []
        self.visibility_regions = []


engine = Engine()

editor_mode = False  # the actual state of being in editor mode or not - updated at the end of a tick
desired_editor_mode = editor_mode  # what to set _editor_mode to at the end of the tick

buffers = pyglet.image.get_buffer_manager()
bfr_col = buffers.get_color_buffer()

tex_draw = None

#internal dictionaries of names to references
dictionary_template = {"class": {}, "sprite": {}, "sound": {}, "music": {}, "resource": {},
                       "instance": {}, "active instance": {}, "inactive instance": {}, "visible instance": {},
                       "invisible instance": {}, "enabled instance": {}, "disabled instance": {}}
objects_global = dictionary_template.copy()
objects_local = dictionary_template.copy()

layers = {}

loaded_sections = {}

window_invalidated = True
window_hidden = False

#Dispatches events to all objects in the system
class EventHandler:

    events = {}
    #Update all objects
    def tick(self, dt):
        global window_hidden
        if window_hidden:
            window_hidden = globals.window.hidden
            return

        wrappers.music_tick(dt)

        engine.fps = 1 / dt
        engine.frame += 1
        engine.time += dt

        engine._instances_update_states()
        camera.on_tick()

        globals.collision.layers_move()

        if engine.editor_mode:
            camera.view_width = globals.window.width
            camera.view_height = globals.window.height
            self.dispatch_event("on_editor_begin_tick")
            self.dispatch_event("on_editor_tick")
            self.dispatch_event("on_editor_end_tick")
        else:
            self.dispatch_event("on_begin_tick")
            self.dispatch_event("on_tick")
            self.dispatch_event("on_end_tick")

        engine._validate_window()
        self.draw()

        #Clear the inputs from last frame
        engine.keys_released.clear()
        engine.keys_pressed.clear()
        engine.mouse_released.clear()
        engine.mouse_pressed.clear()
        global editor_mode
        editor_mode = desired_editor_mode

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

    #Loop through the set of all registered events of that type and call them
    def dispatch_event(self, event):
        for inst, func in self.events[event].copy():
            engine.current_instance = inst
            engine.current_layer = inst.layer
            func()

    #Add a new event type
    def register_event_type(self, event):
        engine.event_types.append(event)
        self.events[event] = set()

    #Add each instance's related method into the given event set
    def add_handlers(self, instance, *handlers):
        if len(handlers) == 0:
            handlers = engine.event_types

        for handler in handlers:
            try:
                self.events[handler].add((instance, getattr(instance, handler)))
            except AttributeError: pass

    #Remove each instance's related method from the given event set
    def remove_handlers(self, instance, *handlers):
        if len(handlers) == 0:
            handlers = engine.event_types

        for handler in handlers:
            try:
                self.events[handler].remove((instance, getattr(instance, handler)))
            except AttributeError: pass
            except KeyError: pass


event_handler = EventHandler()

event_handler.register_event_type("on_begin_tick")
event_handler.register_event_type("on_editor_begin_tick")
event_handler.register_event_type("on_tick")
event_handler.register_event_type("on_editor_tick")
event_handler.register_event_type("on_end_tick")
event_handler.register_event_type("on_editor_end_tick")
event_handler.register_event_type("on_draw")
event_handler.register_event_type("on_editor_draw")

pyglet.clock.schedule_interval(event_handler.tick, 1.0 / engine.working_fps)
pyglet.clock.set_fps_limit(engine.working_fps)

import wrappers