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

    visibility_grid = instance_grid.InstanceGrid("bbox_visible", "disabled", "always_visible")
    activity_grid = instance_grid.InstanceGrid("bbox_active", "disabled", "always_active")

    @property
    def editor_mode(self): return editor_mode
    @editor_mode.setter
    def editor_mode(self, value):
        global desired_editor_mode
        desired_editor_mode = value

    def instance_create(self, module_name, class_name, layer_name, x=0, y=0, **kwargs):
        inst = engine.get_class(module_name, class_name)()
        layer = engine.layers[layer_name]

        inst._layer_start = inst.layer = layer
        inst._y_start = y - layer._y
        inst._x_start = x - layer._x
        inst.x = x
        inst.y = y
        inst.module_name = module_name
        inst.class_name = class_name

        engine.get_enabled_instances(module_name, class_name).add(inst)
        engine.get_invisible_instances(module_name, class_name).add(inst)
        engine.get_inactive_instances(module_name, class_name).add(inst)
        engine.get_all_instances(module_name, class_name).add(inst)

        inst.on_init()
        for key, value in kwargs.iteritems():
            setattr(inst, key, value)

        event_handler.add_handlers(inst)
        self.instance_update_handler_draw(inst)
        self.instance_update_handler_tick(inst)
        inst.on_create()

        return inst

    def instance_destroy(self, instance):
        if instance.destroyed: return

        globals.collision.instance_update_collision(instance)
        engine.instance_update_activity(instance)
        engine.instance_update_visibility(instance)
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
            event_handler.add_handlers(inst, "on_draw", "on_editor_draw")
        else:
            event_handler.remove_handlers(inst, "on_draw", "on_editor_draw")

    def instance_update_handler_tick(self, inst):
        if not inst.disabled and inst.active:
            event_handler.add_handlers(inst,
                                       "on_begin_tick", "on_editor_begin_tick",
                                       "on_tick", "on_editor_tick",
                                       "on_end_tick", "on_editor_end_tick")
        else:
            event_handler.remove_handlers(inst,
                                          "on_begin_tick", "on_editor_begin_tick",
                                          "on_tick", "on_editor_tick",
                                          "on_end_tick", "on_editor_end_tick")
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

    def get_sprite(self, module_name="*", sprite_name=None, drawing_layer="default"):
        if module_name == "*":
            return  set(objects_local["sprite"].values()) | set(objects_global["sprite"].values())
        if sprite_name is None:
            raise ValueError("Sprite name not specified")
        return wrappers.Sprite(engine._get_object(module_name, "sprite", sprite_name),  drawing_layer)

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

    def instance_update_visibility(self, inst):
        if not inst.always_visible:
            self.visibility_grid.instance_update(inst)

    def instance_update_activity(self, inst):
        if not inst.always_active:
            self.activity_grid.instance_update(inst)

    def _instances_update_states(self):
        visible_changes = {}
        active_changes = {}

        for inst in self.get_active_instances():
            if not inst.disabled and not inst.always_active:
                active_changes[inst] = False

        for inst in self.get_visible_instances():
            if not inst.disabled and not inst.always_visible:
                visible_changes[inst] = False

        for x1, y1, x2, y2 in self.activity_regions:

            for inst in self.activity_grid.instances_rectangle(x1, y1, x2, y2):
                if (inst.bbox_active[0] + inst.x < x2
                and inst.bbox_active[1] + inst.y < y2
                and inst.bbox_active[2] + inst.x > x1
                and inst.bbox_active[3] + inst.y > y1):
                    active_changes[inst] = True

        for x1, y1, x2, y2 in self.visibility_regions:
            for inst in self.visibility_grid.instances_rectangle(x1, y1, x2, y2):
                if (inst.bbox_visible[0] + inst.x < x2
                and inst.bbox_visible[1] + inst.y < y2
                and inst.bbox_visible[2] + inst.x > x1
                and inst.bbox_visible[3] + inst.y > y1):
                    visible_changes[inst] = True

        for inst, value in active_changes.iteritems():
            inst.active = value

        for inst, value in visible_changes.iteritems():
            inst.visible = value

        self.activity_regions = []
        self.visibility_regions = []

engine = Engine()

editor_mode = False  # the actual state of being in editor mode or not - updated at the end of a tick
desired_editor_mode = editor_mode  # what to set _editor_mode to at the end of the tick

#internal dictionaries of names to references
dictionary_template = {"class": {}, "sprite": {}, "sound": {}, "music": {}, "resource": {},
                       "instance": {}, "active instance": {}, "inactive instance": {}, "visible instance": {},
                       "invisible instance": {}, "enabled instance": {}, "disabled instance": {}}
objects_global = dictionary_template.copy()
objects_local = dictionary_template.copy()

layers = {}

loaded_sections = {}

#Dispatches events to all objects in the system
class EventHandler:

    events = {}
    #Update all objects
    def tick(self, dt):
        global window_hidden
        if renderer.window_hidden:
            renderer.window_hidden = globals.window.hidden
            return

        wrappers.music_tick(dt)

        engine.fps = 1 / dt
        engine.frame += 1
        engine.time += dt

        if key.R in engine.keys_pressed: globals.loader.goto_level("Demo Level")

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

        camera.on_tick()
        renderer._validate_window()
        engine._instances_update_states()

        if engine.editor_mode:
            self.dispatch_event("on_editor_draw")
        else:
            self.dispatch_event("on_draw")


        renderer.draw()

        #Clear the inputs from last frame
        engine.keys_released.clear()
        engine.keys_pressed.clear()
        engine.mouse_released.clear()
        engine.mouse_pressed.clear()
        global editor_mode
        editor_mode = desired_editor_mode

    #Loop through the set of all registered events of that type and call them
    def dispatch_event(self, event):
        for inst, func in self.events[event].copy():
            if not inst.destroyed:
                engine.current_instance = inst
                engine.current_layer = inst.layer
                func()

    #Add a new event type
    def register_event_type(self, event, sort=False):
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
            except ValueError: pass


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