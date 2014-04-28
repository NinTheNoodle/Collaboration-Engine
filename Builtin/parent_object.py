__author__ = 'Docopoper'
from globals import *

class GameObject(object):
    x = 0
    y = 0
    module_name = ""
    class_name = ""
    _destroyed = False
    _layer = None
    _hp = None
    _disabled = False # Whether the object will be permanently inactive due to being disabled. Usually by the layer being disabled
    _active = False # Whether the object is active and is receiving events as opposed to being too far off screen
    _visible = False # Whether the object is visible and receiving draw events as opposed to being off screen at all
    temporary = False # Whether the object gets destroyed when deactivated / disabled
    section_persist = False # Whether the object gets destroyed when changing level section
    level_persist = False # Whether the object gets destroyed when changing level - only valid for global instances
    always_active = False # Whether the object will deactivate when off screen or not
    always_visible = False # Whether the object will become invisible when off screen or not
    hspeed = 0
    vspeed = 0
    bbox_full = (-16, -16, 16, 16) # Bounding box to fully encompass the object
    bbox_active = (-16, -16, 16, 16) # Bounding box to determine when this object activates and deactivates
    bbox_visible = (-16, -16, 16, 16) # Bounding box to determine when this object is visible on screen
    bbox_collide = (-16, -16, 16, 16) # Bounding box to determine when this object is going to make a collision neutral to the player
    bbox_hurt = (-16, -16, 16, 16) # Bounding box to determine when this object is going to make a collision harmful to the player
    bbox_help = (-16, -16, 16, 16) # Bounding box to determine when this object is going to make a collision helpful to the player
    x_start = 0
    y_start = 0
    is_local = True # Whether this object has been defined at the local scope and can only exist in this level

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
            elif not value and self._disabled:
                engine.instance_enable(self)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
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