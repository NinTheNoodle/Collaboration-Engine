__author__ = 'Docopoper'
from globals import *
import globals
import base_engine
from math import ceil

class Collision(object):
    collision_grid = instance_grid.InstanceGrid("bbox_collide")

    def layers_move(self):
        for layer in engine.layers.itervalues():
            layer.move(layer.hspeed, layer.vspeed)

    def collision_position(self, inst, x, y):
        rtn = self.collision_rectangle(inst.bbox_collide[0] + x, inst.bbox_collide[1] + y,
                                       inst.bbox_collide[2] + x, inst.bbox_collide[3] + y)
        try:
            rtn.remove(inst)
        except KeyError: pass
        return rtn

    def collision_rectangle(self, x1, y1, x2, y2):
        rtn = set()
        found = self.collision_grid.instances_rectangle(x1, y1, x2, y2)
        for inst in found:
            if (x2 > inst.bbox_collide[0] + inst.x
            and y2 > inst.bbox_collide[1] + inst.y
            and x1 < inst.bbox_collide[2] + inst.x
            and y1 < inst.bbox_collide[3] + inst.y):
                rtn.add(inst)
        return rtn

    def instance_update_collision(self, inst):
        if not inst._no_collide:
            self.collision_grid.instance_update(inst)

    def instance_abort_collision(self, inst):
        self.collision_grid.instance_remove(inst)


collision = Collision()