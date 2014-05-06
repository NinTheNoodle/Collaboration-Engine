__author__ = 'Docopoper'
from globals import *
import globals
import base_engine
from math import ceil

class Collision(object):
    updates = set()

    def layers_move(self):
        for layer in engine.layers.itervalues():
            layer.move(layer.hspeed, layer.vspeed)

    def update_collision_dicts(self):
        for inst in self.updates:
            layer_from = inst._layer_col_old
            layer_to = inst._layer
            bbox_from = inst._bbox_collide_col_old
            bbox_to = inst._bbox_collide
            x_from = inst._x_col_old
            x_to = inst._x - layer_to._x
            y_from = inst._y_col_old
            y_to = inst._y - layer_to._y

            if not inst._disabled_col_old and layer_from is not None:
                for pos in self.box_to_cells(x_from, y_from, bbox_from, layer_from.cell_size):
                    try:
                        layer_from.collision_dict[pos].remove(inst)
                    except KeyError: pass

            if not inst._disabled:
                for pos in self.box_to_cells(x_to, y_to, bbox_to, layer_to.cell_size):
                    try:
                        layer_to.collision_dict[pos].add(inst)
                    except KeyError: layer_to.collision_dict[pos] = {inst}

            inst._disabled_col_old = inst._disabled
            inst._layer_col_old = layer_to
            inst._bbox_collide_col_old = bbox_to
            inst._x_col_old = x_to
            inst._y_col_old = y_to

        self.updates.clear()



    def collision_position(self, inst, x, y):
        rtn = self.collision_rectangle(inst._bbox_collide[0] + x, inst._bbox_collide[1] + y,
                                       inst._bbox_collide[2] + x, inst._bbox_collide[3] + y)
        try:
            rtn.remove(inst)
        except KeyError: pass
        return rtn

    def collision_rectangle(self, x1, y1, x2, y2):
        self.update_collision_dicts()
        rect = (x1, y1, x2, y2)
        found = set()
        rtn = set()
        for layer in engine.layers.itervalues():
            for cell in self.box_to_cells(-layer._x, -layer._y, rect, layer.cell_size):
                try:
                    found |= layer.collision_dict[cell]
                except KeyError: pass

        for inst in found:
            if (x2 > inst.bbox_collide[0] + inst.x
            and y2 > inst.bbox_collide[1] + inst.y
            and x1 < inst.bbox_collide[2] + inst.x
            and y1 < inst.bbox_collide[3] + inst.y):
                rtn.add(inst)
        return rtn

    def instance_update_collision(self, inst):
        if not inst._no_collide:
            self.updates.add(inst)

    def instance_abort_collision(self, inst):
        try:
            self.updates.remove(inst)
        except KeyError: pass

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