__author__ = 'Docopoper'
from globals import *

class GameObject(object):

    instance_id = -1
    module_name = ""
    class_name = ""
    temporary = False # Whether the object gets destroyed when deactivated / disabled
    section_persist = False # Whether the object gets destroyed when changing level section
    hspeed = 0
    vspeed = 0
    x_start = 0
    y_start = 0
    is_local = True # Whether this object has been defined at the local scope and can only exist in this level
    depth = 0

    _x = 0
    _y = 0
    _always_active = False # Whether the object will deactivate when off screen or not
    _always_visible = False # Whether the object will become invisible when off screen or not
    _no_collide = False # If true the instance won't even be considered for collisions
    _bbox_select = (-16, -16, 16, 16) # Bounding box for selection in the editor
    _bbox_active = (-16, -16, 16, 16) # Bounding box to determine when this object activates and deactivates
    _bbox_visible = (-16, -16, 16, 16) # Bounding box to determine when this object is visible on screen
    _bbox_collide = (-16, -16, 16, 16) # Bounding box to determine when this object is going to make a collision neutral to the player
    _destroyed = False
    _layer = None
    _drawing_layer = "default"
    _drawing_layer_depth = 0
    _hp = None
    _disabled = False # Whether the object will be permanently inactive due to being disabled. Usually by the layer being disabled
    _active = False # Whether the object is active and is receiving events as opposed to being too far off screen
    _visible = False # Whether the object is visible and receiving draw events as opposed to being off screen at all

    def __init__(self):
        self._disabled_old = {} # Used in updating the object positions on instance grids (such as for collisions)
        self._x_old = {}
        self._y_old = {}
        self._layer_old = {}
        self._bbox_old = {}
        self._drawables = []

    @property
    def drawing_layer(self):
        return self._drawing_layer

    @drawing_layer.setter
    def drawing_layer(self, value):
        self._drawing_layer = value
        for drawable in self._drawables:
            drawable.update_group()

    @property
    def destroyed(self):
        return self._destroyed

    @property
    def no_collide(self):
        return self._no_collide

    @no_collide.setter
    def no_collide(self, value):
        if self._no_collide != value:
            self._no_collide = value
            collision.instance_update_collision(self)

    @property
    def always_active(self):
        return self._always_active

    @always_active.setter
    def always_active(self, value):
        if self._always_active != value:
            if value:
                self.active = True
            self._always_active = value
            engine.instance_update_activity(self)

    @property
    def always_visible(self):
        return self._always_visible

    @always_visible.setter
    def always_visible(self, value):
        if self._always_visible != value:
            if value:
                self.visible = True
            self._always_visible = value
            engine.instance_update_visibility(self)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if self._x != value:
            self._x = value
            collision.instance_update_collision(self)
            engine.instance_update_activity(self)
            engine.instance_update_visibility(self)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if self._y != value:
            self._y = value
            collision.instance_update_collision(self)
            engine.instance_update_activity(self)
            engine.instance_update_visibility(self)

    @property
    def bbox_collide(self):
        return self._bbox_collide

    @bbox_collide.setter
    def bbox_collide(self, value):
        if self._bbox_collide != value:
            self._bbox_collide = value
            collision.instance_update_collision(self)
            engine.instance_update_activity(self)
            engine.instance_update_visibility(self)

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        if self._layer != value:
            if self._layer is not None:
                self._layer.instances.remove(self)

            self._layer = value
            self._layer.instances.add(self)

            if engine.current_instance == self:
                engine.current_layer = value

            collision.instance_update_collision(self)
            engine.instance_update_activity(self)
            engine.instance_update_visibility(self)

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        if self.temporary and value:
            self.destroy()
        else:
            if value and not self._disabled:
                engine.instance_disable(self)
                collision.instance_update_collision(self)
                engine.instance_update_activity(self)
                engine.instance_update_visibility(self)
            elif not value and self._disabled:
                engine.instance_enable(self)
                collision.instance_update_collision(self)
                engine.instance_update_activity(self)
                engine.instance_update_visibility(self)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        if not self.always_active:
            if self.temporary and not value:
                self.destroy()
            else:
                if value and not self._active:
                    engine.instance_activate(self)
                elif not value and self._active:
                    engine.instance_deactivate(self)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        if not self.always_visible:
            if value and not self._visible:
                engine.instance_show(self)
            elif not value and self._visible:
                engine.instance_hide(self)

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        if self._hp is not None and value <= 0 < self._hp:
            self._hp = value
            self.on_die()
        else:
            self._hp = value

    def on_die(self):
        pass

    def on_init(self):
        pass

    def on_create(self):
        pass

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def on_visible(self):
        pass

    def on_invisible(self):
        pass

    def on_enable(self):
        pass

    def on_disable(self):
        pass

    def on_destroy(self):
        pass

    def destroy(self):
        engine.instance_destroy(self)