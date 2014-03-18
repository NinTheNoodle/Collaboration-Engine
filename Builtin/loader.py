__author__ = 'Docopoper'

from globals import *


class loader:
    pass


ball_image = pyglet.image.load(r'C:\Users\Docopoper\Desktop\Vulpix.png')
engine.register_sprite_global("Testmod", "Vulpix", ball_image)


class TestObj:
    x = 0
    y = 0

    spr = engine.get_sprite("Testmod", "Vulpix")

    settings = ["spr"]

    def on_create(self):
        self.sprite = pyglet.sprite.Sprite(self.spr)

    def on_tick(self):
        if key.MOTION_LEFT in engine.keys_down: self.x -= 2
        if key.MOTION_RIGHT in engine.keys_down: self.x += 2
        if key.MOTION_UP in engine.keys_down: self.y += 2
        if key.MOTION_DOWN in engine.keys_down: self.y -= 2

        if key.Z in engine.keys_pressed: engine.editor_mode = not engine.editor_mode
        self.sprite.x, self.sprite.y = self.x, self.y

    def on_draw(self):
        self.sprite.draw()

engine.register_class_global("Testmod", "Test", TestObj)
engine.instance_create("Testmod", "Test", 0, 0)