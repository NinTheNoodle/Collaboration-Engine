__author__ = 'Docopoper'
from globals import *

class GameObject(object):
    x = 0
    y = 0
    module_name = ""
    class_name = ""
    disabled = False # Whether the object will be permanently inactive due to being disabled. Usually by the layer being disabled
    active = False # Whether the object is active and is receiving events as opposed to being too far off screen
    visible = False # Whether the object is visible and receiving draw events as opposed to being off screen at all
    temporary = False # Whether the object gets destroyed when deactivated
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

    def on_create(self):
        pass

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def on_destroy(self):
        pass

    def destroy(self):
        engine.instance_destroy(self)

    def disable(self):
        pass