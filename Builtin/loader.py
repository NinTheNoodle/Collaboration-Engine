__author__ = 'Docopoper'

from globals import *


class Loader:
    pass


ball_image = pyglet.image.load(r'C:\Users\Docopoper\Desktop\Vulpix.png')
ball = pyglet.sprite.Sprite(ball_image)


class TestObj(Object):
    def on_create(self, args, kwargs):
        print args, kwargs, self.x, self.y

    def on_tick(self):
        ball.x, ball.y = self.x, self.y

    def on_draw(self):
        ball.draw()

Engine.register_class_global("Test", TestObj)
Engine.instance_create("Test", (0, 10))