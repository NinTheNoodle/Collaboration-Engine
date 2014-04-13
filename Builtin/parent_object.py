__author__ = 'Docopoper'


class GameObject(object):
    x = 0
    y = 0
    active = False
    visible = False
    always_active = False
    always_visible = False
    hspeed = 0
    vspeed = 0
    bbox = (-16, -16, 16, 16)
    x_start = 0
    y_start = 0
    is_local = True

    def on_create(self):
        pass

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def on_destroy(self):
        pass

    def destroy(self):
        pass