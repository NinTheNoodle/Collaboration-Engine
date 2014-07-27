__author__ = 'Docopoper'
from globals import *
import globals
import base_engine
#from math import sqrt, atan2, sin, cos, pi

class Collidable(object):
    def closest_surface(self, x, y):
        return "None"
    def collision_point(self, x, y):
        return False
    def colliding(self, collidable, x_diff, y_diff):
        return False

class CollisionRect(Collidable):
    def closest_surface(self, x, y):
        return "None"
    def collision_point(self, x, y):
        return False
    def colliding(self, collidable, x_diff, y_diff):
        return False

class CollisionMesh(Collidable):
    _angle = 0
    _scale = 1
    def __init__(self, *data):
        self.points = list(data[::2])
        self.surfaces = list(data[1::2])

        #the direction each
        self.surface_angles = [(atan2(self.points[(i + 1) % len(self.points)][1] - self.points[i][1],
                                     self.points[(i + 1) % len(self.points)][0] - self.points[i][0]) + pi / 2) % (pi * 2)
                               for i in xrange(len(self.points))]

        print [degrees(a) for a in self.surface_angles], self.points

        #distances and directions from each point to the origin of this mesh (0,0)
        self.point_distances = [sqrt(p[0] ** 2 + p[1] ** 2) for p in self.points]
        self.point_angles = [atan2(p[1], p[0]) for p in self.points]

        self.bbox = tuple(map(min, zip(*self.points)) + map(max, zip(*self.points)))

    def collision_point(self, x, y):
        xinters = None
        n = len(self.points)
        inside = False

        p1x,p1y = self.points[0]
        for i in range(n+1):
            p2x,p2y = self.points[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y

        return inside

    def closest_surface(self, x, y):
        min_dist = 99999999999
        min_surface = "None"
        for i in xrange(len(self.points)):
            if self.surfaces[i] == "None":
                continue

            x1, y1 = self.points[i]
            x2, y2 = self.points[(i + 1) % len(self.points)]

            px = x2-x1
            py = y2-y1

            something = px*px + py*py

            u =  ((x - x1) * px + (y - y1) * py) / float(something)

            if u > 1:
                u = 1
            elif u < 0:
                u = 0

            xx = x1 + u * px
            yy = y1 + u * py

            dx = xx - x
            dy = yy - y

            dist = dx*dx + dy*dy

            if dist < min_dist:
                min_dist = dist
                min_surface = self.surfaces[i]

        return min_surface

    def colliding(self, mesh, x_diff, y_diff):
        collisions = set()
        for point in self.points:
            x, y = point[0] - x_diff, point[1] - y_diff
            if mesh.collision_point(x, y):
                collisions.add(mesh.closest_surface(x, y))

        for i, point in enumerate(mesh.points):
            x, y = point[0] + x_diff, point[1] + y_diff
            if self.collision_point(x, y):
                collisions.add(mesh.surfaces[i])
                collisions.add(mesh.surfaces[(i - 1) % len(mesh.surfaces)])

        try:
            collisions.remove("None")
        except KeyError: pass
        return collisions

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self.transform(self.scale, value)

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self.transform(value, self.angle)

    def transform(self, scale, angle):
        self._scale, scale = scale, scale / float(self.scale)
        self._angle, angle = angle, angle - self.angle

        if scale != 1:
            self.point_distances = [p * scale for p in self.point_distances]

        if angle != 0:
            self.point_angles = [p + angle for p in self.point_angles]

        for i in xrange(len(self.points)):
            a = self.point_angles[i]
            d = self.point_distances[i]
            self.points[i] = (d * engine.cos_table(a), d * engine.sin_table(a))

        self.bbox = tuple(map(min, zip(*self.points)) + map(max, zip(*self.points)))

    def __eq__(self, other):
        return self.points == other.points

class CollisionResult(object):
    def __init__(self, surfaces, dist, dx, dy, allowed_surfaces):
        self.surfaces = self.filter_surfaces(surfaces, allowed_surfaces)
        self.dist = dist
        self.dx = dx * dist
        self.dy = dy * dist
        self.allowed_surfaces = allowed_surfaces
        print self.surfaces, self.dist, self.dx, self.dy, self.allowed_surfaces

    def filter_surfaces(self, surfaces, allowed_surfaces):
        return surfaces

    def __nonzero__(self):
        return self.dist > 0

class Collision(object):
    collision_grid = instance_grid.InstanceGrid("bbox_collide", "disabled", "no_collide")

    def layers_move(self):
        for layer in engine.layers.itervalues():
            layer.x += layer.hspeed
            layer.y += layer.vspeed

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
        #The instance has no precise mesh, calculate it one
        no_inst_mesh = inst_mesh is None

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


collision = Collision()