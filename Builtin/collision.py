__author__ = 'Docopoper'
from globals import *
import globals
import base_engine

class CollisionResult(object):
    def __init__(self, surfaces, dist, dx, dy, allowed_surfaces):
        self.surfaces = self.filter_surfaces(surfaces, allowed_surfaces)
        self.dist = dist
        self.dx = dx * dist
        self.dy = dy * dist
        self.allowed_surfaces = allowed_surfaces
        #print self.surfaces, self.dist, self.dx, self.dy, self.allowed_surfaces

    def filter_surfaces(self, surfaces, allowed_surfaces):
        return surfaces

    def __nonzero__(self):
        return self.dist > 0

class Collision(object):
    collision_grid = instance_grid.InstanceGrid("bbox_collide", "disabled", "no_collide")
    line_grid = line_grid.LineGrid("disabled", "no_collide")

    def collision_position(self, inst, x, y, surfaces=(), layers=None, dx=None, dy=None):
        cols = self.collision_rectangle(inst.bbox_collide[0] + x, inst.bbox_collide[1] + y,
                                       inst.bbox_collide[2] + x, inst.bbox_collide[3] + y,
                                       layers)
        try:
            cols.remove(inst)
        except KeyError: pass

        if dx is None:
            dx = x - inst.x

        if dy is None:
            dy = y - inst.y

        #ensure dx, dy is normalised
        m = sqrt(dx * dx + dy * dy)
        if m != 0:
            dx /= m
            dy /= m

        max_dist = 0
        prec_cols = {}
        inst_mesh = inst._collision_mesh

        #Check for precise collisions
        for col in cols:
            col_mesh = col._collision_mesh

            col_surfaces, dist = inst_mesh.colliding(col_mesh, col.x - x, col.y - y, -dx, -dy)
            if dist > max_dist:
                prec_cols.clear()
                max_dist = dist

            if dist == max_dist:
                for surface in col_surfaces:
                    try:
                        prec_cols[surface].add(col)
                    except KeyError:
                        prec_cols[surface] = {col}

        return CollisionResult(prec_cols, max_dist, -dx, -dy, surfaces)

    def collision_rectangle(self, x1, y1, x2, y2, layers=None):
        rtn = set()
        found = self.collision_grid.instances_rectangle(x1, y1, x2, y2, layers)
        for inst in found:
            if (x2 > inst.bbox_collide[0] + inst.x
            and y2 > inst.bbox_collide[1] + inst.y
            and x1 < inst.bbox_collide[2] + inst.x
            and y1 < inst.bbox_collide[3] + inst.y):
                rtn.add(inst)
        return rtn


    def instance_update_collision(self, inst):
        self.collision_grid.instance_update(inst)

    def instance_abort_collision(self, inst):
        self.collision_grid.instance_abort_update(inst)

    def movement_phase(self):
        self.line_grid.update_collision_dicts()

        for layer in engine.layers.itervalues():
            layer.x += layer.hspeed
            layer.y += layer.vspeed

        print self.line_grid.lines_rectangle(engine.mouse_x, engine.mouse_y,
                                             engine.mouse_x, engine.mouse_y)


collision = Collision()