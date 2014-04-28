__author__ = 'Docopoper'
from globals import *
import globals
import base_engine

class Collision(object):
    def layers_move(self):
        for layer in engine.layers.itervalues():
            layer.move(layer.hspeed, layer.vspeed)

collision = Collision()