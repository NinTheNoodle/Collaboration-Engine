__author__ = 'Docopoper'
from math import ceil
import globals

class LineGrid(object):
    def __init__(self, *disabling_variables):
        self.updates = set()
        self.disabling_variables = disabling_variables + ("destroyed",)
        self.constant_updates = set()

    def update_collision_dicts(self):
        for collidable in self.updates:
            inst = collidable.inst
            x, y, hspeed, vspeed, layer = inst._x, inst._y, inst.hspeed, inst.vspeed, inst.layer
            x_previous, y_previous  = inst._x_previous, inst._y_previous
            hspeed_previous, vspeed_previous = inst._hspeed_previous, inst._vspeed_previous
            layer_previous = inst._layer_previous

            disabled_previous = inst._collision_disabled_previous
            disabled = False
            for var in self.disabling_variables:
                if getattr(inst, var):
                    disabled = True
                    break

            for line_from, line_to, line_from_previous, line_to_previous in zip(collidable.lines,
                                                                                collidable.lines_next,
                                                                                collidable._lines_previous,
                                                                                collidable._lines_next_previous):
                if not disabled_previous and line_from_previous[0] is not None:
                    line_from_previous_x1 = line_from_previous[0]
                    line_from_previous_y1 = line_from_previous[1]
                    line_from_previous_x2 = line_from_previous[2]
                    line_from_previous_y2 = line_from_previous[3]

                    line_to_previous_x1 = line_to_previous[0] + hspeed_previous
                    line_to_previous_y1 = line_to_previous[1] + vspeed_previous
                    line_to_previous_x2 = line_to_previous[2] + hspeed_previous
                    line_to_previous_y2 = line_to_previous[3] + vspeed_previous

                    x1_previous = min(line_from_previous_x1, line_from_previous_x2, line_to_previous_x1, line_to_previous_x2)
                    y1_previous = min(line_from_previous_y1, line_from_previous_y2, line_to_previous_y1, line_to_previous_y2)
                    x2_previous = max(line_from_previous_x1, line_from_previous_x2, line_to_previous_x1, line_to_previous_x2)
                    y2_previous = max(line_from_previous_y1, line_from_previous_y2, line_to_previous_y1, line_to_previous_y2)

                    bbox_previous = (x1_previous, y1_previous, x2_previous, y2_previous)

                    for pos in self._box_to_cells(x_previous, y_previous, bbox_previous, layer_previous.cell_size):
                        try:
                            layer_previous.line_dict[pos].remove(inst)
                        except KeyError: pass

                if not disabled:
                    line_from_x1 = line_from[0]
                    line_from_y1 = line_from[1]
                    line_from_x2 = line_from[2]
                    line_from_y2 = line_from[3]

                    line_to_x1 = line_to[0] + hspeed
                    line_to_y1 = line_to[1] + vspeed
                    line_to_x2 = line_to[2] + hspeed
                    line_to_y2 = line_to[3] + vspeed

                    x1 = min(line_from_x1, line_from_x2, line_to_x1, line_to_x2)
                    y1 = min(line_from_y1, line_from_y2, line_to_y1, line_to_y2)
                    x2 = max(line_from_x1, line_from_x2, line_to_x1, line_to_x2)
                    y2 = max(line_from_y1, line_from_y2, line_to_y1, line_to_y2)

                    bbox = (x1, y1, x2, y2)

                    for pos in self._box_to_cells(x, y, bbox, layer.cell_size):
                        try:
                            layer.line_dict[pos].add(inst)
                        except KeyError: # The position doesn't exist
                            layer.line_dict[pos] = {inst}

            collidable._update_points()
            inst._hspeed_previous, inst._vspeed_previous = hspeed, vspeed
            inst._x_previous, inst._y_previous = x, y
            inst._layer_previous = layer
            inst._collision_disabled_previous = disabled

        self.updates = self.constant_updates.copy()

    def lines_rectangle(self, x1, y1, x2, y2):
        rect = (x1, y1, x2, y2)
        found = set()

        for layer in globals.engine.layers.itervalues():
            if not layer.disabled:
                dx, dy = layer.hspeed, layer.vspeed

                layer_rect = (rect[0] + min(dx, 0), rect[1] + min(dy, 0),
                              rect[2] + max(dx, 0), rect[3] + max(dy, 0))

                for cell in self._box_to_cells(-layer.x, -layer.y, layer_rect, layer.cell_size):
                    #print cell
                    try:
                        found |= layer.line_dict[cell]
                    except KeyError: pass
        return found

    def collidable_abort_update(self, collidable):
        try:
            self.updates.remove(collidable)
        except KeyError: pass

    def collidable_update(self, collidable):
        self.updates.add(collidable)

    def collidable_constant_update(self, collidable):
        self.constant_updates.add(collidable)

    def collidable_abort_constant_update(self, collidable):
        try:
            self.constant_updates.remove(collidable)
        except KeyError: pass

    # noinspection PyArgumentList
    def _box_to_cells(self, x, y, bbox, cell_size):
        return [(xx, yy)
                for yy in
                xrange(int((y + bbox[1]) // cell_size),
                       int(1 + (float(y + bbox[3]) // cell_size)))
                for xx in
                xrange(int((x + bbox[0]) // cell_size),
                       int(1 + (float(x + bbox[2]) // cell_size)))
                ]