from globals import *

__author__ = 'Docopoper'


class Sprite:

    def __init__(self, spr):
        self.spr = pyglet.sprite.Sprite(spr)

    def draw(self, x, y):
        self.spr.x, self.spr.y = x, y
        self.spr.draw()


class Sound:

    def __init__(self, snd):
        self.snd = snd

    def play(self):
        self.snd.play()


class Music:

    def __init__(self, mus):
        self.mus = mus

    def play(self):
        self.mus.play()