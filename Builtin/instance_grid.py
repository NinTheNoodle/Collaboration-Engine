__author__ = 'Docopoper'
from math import ceil
import globals

next_id = 0

class InstanceGrid(object):
    def __init__(self, bbox_name, *disabling_variables):
        global next_id
        self.updates = set()
        self.bbox = bbox_name
        self.disabling_variables = disabling_variables + ("destroyed",)
        self.id = next_id
        next_id += 1



    def update_collision_dicts(self):
        for inst in self.updates:
            try:
                layer_from = inst._layer_old[self.id]
                bbox_from = inst._bbox_old[self.id]
                x_from = inst._x_old[self.id]
                y_from = inst._y_old[self.id]

                if not inst._disabled_old[self.id]:
                    for pos in self._box_to_cells(x_from, y_from, bbox_from, layer_from.cell_size):
                        try:
                            layer_from.instance_dict[self.id][pos].remove(inst)
                        except KeyError: pass
            except KeyError: pass # In this case - the instance is new to the grid. No need to deal with its old position.

            layer_to = inst.layer
            bbox_to = getattr(inst, self.bbox)
            x_to = inst.x - layer_to.x
            y_to = inst.y - layer_to.y

            disabled = False
            for var in self.disabling_variables:
                if getattr(inst, var):
                    disabled = True
                    break

            if not disabled:
                for pos in self._box_to_cells(x_to, y_to, bbox_to, layer_to.cell_size):
                    try:
                        layer_to.instance_dict[self.id][pos].add(inst)
                    except KeyError: # The position doesn't exist
                        try:
                            layer_to.instance_dict[self.id][pos] = {inst}
                        except KeyError: # The layer has no entry for this grid
                            layer_to.instance_dict[self.id] = {}
                            layer_to.instance_dict[self.id][pos] = {inst}

            inst._disabled_old[self.id] = inst._disabled
            inst._layer_old[self.id] = layer_to
            inst._bbox_old[self.id] = bbox_to
            inst._x_old[self.id] = x_to
            inst._y_old[self.id] = y_to

        self.updates.clear()

    def instances_rectangle(self, x1, y1, x2, y2):
        self.update_collision_dicts()
        rect = (x1, y1, x2, y2)
        found = set()
        for layer in globals.engine.layers.itervalues():
            for cell in self._box_to_cells(-layer.x, -layer.y, rect, layer.cell_size):
                try:
                    found |= layer.instance_dict[self.id][cell]
                except KeyError: pass
        return found

    def instance_update(self, inst):
        disabled = False
        for var in self.disabling_variables:
            if getattr(inst, var):
                disabled = True
                break

        if not disabled:
            self.updates.add(inst)

    def instance_abort_update(self, inst):
        try:
            self.updates.remove(inst)
        except KeyError: pass

    # noinspection PyArgumentList
    def _box_to_cells(self, x, y, bbox, cell_size):
        return [(xx, yy)
                for yy in
                xrange(int((y + bbox[1]) // cell_size),
                       int(ceil(float(y + bbox[3]) / cell_size)))
                for xx in
                xrange(int((x + bbox[0]) // cell_size),
                       int(ceil(float(x + bbox[2]) / cell_size)))
                ]