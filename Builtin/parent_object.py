import Builtin.wrappers

__author__ = 'Docopoper'
from globals import *
from Builtin.collidable import CollisionRectangle, CollisionMesh, CollisionNull

class GameObject(object):

    instance_id = -1
    module_name = ""
    class_name = ""
    layer_name = ""
    temporary = False # Whether the object gets destroyed when deactivated / disabled
    section_persist = False # Whether the object gets destroyed when changing level section
    is_local = True # Whether this object has been defined at the local scope and can only exist in this level
    depth = 0
    bbox_surface = "None" # Returned as the surface when a simple bounding box is used

    _hspeed = 0
    _vspeed = 0
    _x_start = 0
    _y_start = 0
    _layer_start = None
    _x = 0
    _y = 0
    _x_previous = 0
    _y_previous = 0
    _hspeed_previous = 0
    _vspeed_previous = 0
    _always_active = False # Whether the object will deactivate when off screen or not
    _always_visible = False # Whether the object will become invisible when off screen or not
    _no_collide = False # If true the instance won't even be considered for collisions
    _bbox_select = (-16, -16, 16, 16) # Bounding box for selection in the editor
    _bbox_active = (-16, -16, 16, 16) # Bounding box to determine when this object activates and deactivates
    _bbox_visible = (-16, -16, 16, 16) # Bounding box to determine when this object is visible on screen
    _bbox_collide = (-16, -16, 16, 16) # Bounding box to determine when this object is going to make a collision
    _collision_mesh = None # Precise collision mesh for an object
    _destroyed = False
    _layer = None
    _layer_previous = None
    _drawing_layer = "default"
    _collision_disabled_previous = True
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
        self._collision_mesh = CollisionNull()

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
    def x_start(self):
        return self._x_start + self.layer_start.x

    @property
    def y_start(self):
        return self._y_start + self.layer_start.y

    @property
    def layer_start(self):
        return self._layer_start

    @property
    def x(self):
        return self._x + self.layer.x

    @x.setter
    def x(self, value):
        value -= self.layer.x
        if self._x != value:
            self._x = value
            collision.instance_update_collision(self)
            engine.instance_update_activity(self)
            engine.instance_update_visibility(self)

    @property
    def hspeed(self):
        return self._hspeed

    @hspeed.setter
    def hspeed(self, value):
        if self._hspeed != value:
            self._hspeed = value
            if self._collision_mesh is not None:
                if self._vspeed == 0 and value == 0:
                    collision.line_grid.collidable_abort_constant_update(self._collision_mesh)
                else:
                    collision.line_grid.collidable_constant_update(self._collision_mesh)

    @property
    def vspeed(self):
        return self._vspeed

    @vspeed.setter
    def vspeed(self, value):
        if self._vspeed != value:
            self._vspeed = value
            if self._collision_mesh is not None:
                if self._hspeed == 0 and value == 0:
                    collision.line_grid.collidable_abort_constant_update(self._collision_mesh)
                else:
                    collision.line_grid.collidable_constant_update(self._collision_mesh)

    @property
    def angle(self):
        return self._collision_mesh.angle

    @angle.setter
    def angle(self, value):
        if self._collision_mesh.angle != value:
            self._collision_mesh.angle = value
            collision.instance_update_collision(self)

    @property
    def scale(self):
        return self._collision_mesh.scale

    @scale.setter
    def scale(self, value):
        if self._collision_mesh.scale != value:
            self._collision_mesh.scale = value
            collision.instance_update_collision(self)

    @property
    def y(self):
        return self._y + self.layer.y

    @y.setter
    def y(self, value):
        value -= self.layer.y
        if self._y != value:
            self._y = value
            collision.instance_update_collision(self)
            engine.instance_update_activity(self)
            engine.instance_update_visibility(self)

    @property
    def bbox_collide(self):
        return self._collision_mesh.bbox

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
    def user_disabled(self):
        return self._disabled

    @property
    def disabled(self):
        return self._disabled or self.layer.disabled

    @disabled.setter
    def disabled(self, value):
        if self.temporary and value:
            self.destroy()
        else:
            if value and not self._disabled:
                self._disabled = True
                if not self.layer.disabled:
                    engine.instance_disable(self)
            elif not value and self._disabled:
                self._disabled = False
                if not self.layer.disabled:
                    engine.instance_enable(self)

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

    def set_collision_rectangle(self, x1, y1, x2, y2, sur_top, sur_right=None, sur_bottom=None, sur_left=None):
        collision_mesh = CollisionRectangle(self, x1, y1, x2, y2, sur_top, sur_right, sur_bottom, sur_left)
        if self.bbox_collide != collision_mesh.bbox:
            collision.instance_update_collision(self)
        self._collision_mesh = collision_mesh

    def set_collision_mesh(self, *data):
        collision_mesh = CollisionMesh(self, *data)
        if self.bbox_collide != collision_mesh.bbox:
            collision.instance_update_collision(self)
        self._collision_mesh = collision_mesh