__author__ = 'Docopoper'
from globals import *
import globals
import base_engine
from math import ceil

class Collision(object):
    def layers_move(self):
        for layer in engine.layers.itervalues():
            layer.move(layer.hspeed, layer.vspeed)

    def instance_update_collision_bbox(self, inst, bbox_from, bbox_to):
        if bbox_from != bbox_to:
            layer = inst.layer

            before_cells = self.box_to_cells(inst.x, inst.y, bbox_from, layer.cell_size)
            after_cells = self.box_to_cells(inst.x, inst.y, bbox_to, layer.cell_size)

            for pos in before_cells:
                try:
                    layer.collision_dict[pos].remove(inst)
                except KeyError: pass

            for pos in after_cells:
                layer.collision_dict[pos].add(inst)

    def instance_update_collision_position(self, inst, x_from, y_from, x_to, y_to):
        if (x_from, y_from) != (x_to, y_to):
            layer = inst.layer
            for pos in self.box_to_cells(x_from, y_from, inst.bbox_collision, layer.cell_size):
                try:
                    layer.collision_dict[pos].remove(inst)
                except KeyError: pass

            for pos in self.box_to_cells(x_to, y_to, inst.bbox_collision, layer.cell_size):
                layer.collision_dict[pos].add(inst)

    def instance_update_collision_layer(self, inst, layer_from, layer_to):
        for pos in self.box_to_cells(inst.x, inst.y, inst.bbox_collision, layer_from.cell_size):
            try:
                layer_from.collision_dict[pos].remove(inst)
            except KeyError: pass

        for pos in self.box_to_cells(inst.x, inst.y, inst.bbox_collision, layer_to.cell_size):
            layer_to.collision_dict[pos].add(inst)

    # noinspection PyArgumentList
    def box_to_cells(self, x, y, bbox, cell_size):
        return [(xx, yy)
                for yy in
                xrange(int((y + bbox[1]) // cell_size),
                       int(ceil(float(y + bbox[3]) / cell_size)))
                for xx in
                xrange(int((x + bbox[0]) // cell_size),
                       int(ceil(float(x + bbox[2]) / cell_size)))
                ]


collision = Collision()

print collision.box_to_cells(0, 0, (-32, -32, 32, 32), 32)