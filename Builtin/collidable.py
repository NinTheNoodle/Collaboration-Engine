__author__ = 'Docopoper'

from globals import *

class Collidable(object):
    bbox = (0, 0, 0, 0)
    surfaces = []
    _points = []
    _points_next = []
    _points_previous = []
    _points_next_previous = []
    is_rectangle = False
    _angle = 0
    _scale = 1
    _point_distances = None
    _point_angles = None
    inst = None

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        self.is_rectangle = False
        self._point_distances = None
        self._point_angles = None
        self._points = self._points_next = value
        self._calculate_rotatable_mesh()
        self.update_bounding_box()
        collision.line_grid.collidable_abort_update(self)

    @property
    def points_next(self):
        return self._points_next

    @points_next.setter
    def points_next(self, value):
        self.is_rectangle = False
        self._point_distances = None
        self._point_angles = None
        self._points_next = value
        self._calculate_rotatable_mesh()
        collision.line_grid.collidable_update(self)

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

    @property
    def lines(self):
        for i in xrange(len(self._points)):
            yield self._points[i] + self._points[(i + 1) % len(self._points)]

    @property
    def lines_next(self):
        for i in xrange(len(self._points_next)):
            yield self._points_next[i] + self._points_next[(i + 1) % len(self._points_next)]

    @property
    def _lines_previous(self):
        for i in xrange(len(self._points_previous)):
            yield self._points_previous[i] + self._points_previous[(i + 1) % len(self._points_previous)]

    @property
    def _lines_next_previous(self):
        for i in xrange(len(self._points_next_previous)):
            yield self._points_next_previous[i] + self._points_next_previous[(i + 1) % len(self._points_next_previous)]

    def _update_points(self):
        self._points_previous = self._points[:]
        self._points_next_previous = self._points_next[:]
        self._points = self._points_next[:]
        self.update_bounding_box()

    def _calculate_rotatable_mesh(self):
        #distances and directions from each point to the origin of this mesh (0,0)
        self._point_distances = [sqrt(p[0] ** 2 + p[1] ** 2) for p in self._points_next]
        self._point_angles = [atan2(p[1], p[0]) for p in self._points_next]

    def update_bounding_box(self):
        self.bbox = tuple(map(min, zip(*self._points)) + map(max, zip(*self._points)))

    def transform(self, scale, angle):
        if self._point_distances is None or self._point_angles is None:
            self._calculate_rotatable_mesh()

        self.is_rectangle = False
        self._scale, scale = scale, scale / float(self.scale)
        self._angle, angle = angle, angle - self.angle

        if scale != 1:
            self._point_distances = [p * scale for p in self._point_distances]

        if angle != 0:
            self._point_angles = [p - angle for p in self._point_angles]

        for i in xrange(len(self._points_next)):
            a = self._point_angles[i]
            d = self._point_distances[i]
            self._points_next[i] = (d * engine.cos_table(a), d * engine.sin_table(a))

        collision.line_grid.collidable_update(self)

    def _raycastLine(self, x1, y1, x2, y2, ray_x, ray_y, ray_dx, ray_dy):
        #Translated to python and modified from http://alienryderflex.com/intersect/

        # Fail if either line segment is zero-length.
        if (ray_dx == 0 and ray_dy == 0) or (x1 == x2 and y1 == y2):
            return None

        # Make x1, y1 the origin
        x1 -= ray_x
        y1 -= ray_y
        x2 -= ray_x
        y2 -= ray_y

        newX = x1 * ray_dx + y1 * ray_dy
        y1   = y1 * ray_dx - x1 * ray_dy
        x1   = newX

        newX = x2 * ray_dx + y2 * ray_dy
        y2   = y2 * ray_dx - x2 * ray_dy
        x2   = newX

        #  Fail if segment line 2 doesn't cross line 1.
        if y1 < 0 and y2 < 0 or y1 >= 0 and y2 >= 0:
            return None

        # Discover the intersection point
        pos = x2 + (x1 - x2) * y2 / (y2 - y1)

        # Fail if the line crosses the ray behind its origin
        if pos < 0:
            return None

        return pos

    def closest_side(self, x, y):
        min_dist = 99999999999
        min_side = None
        for i in xrange(len(self._points)):
            if self.surfaces[i] == "None":
                continue

            x1, y1 = self._points[i]
            x2, y2 = self._points[(i + 1) % len(self._points)]

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
                min_side = i

        return min_side, min_dist

    def raycast_get_side(self, x, y, dx, dy):
        if (dx, dy) == (0, 0):
            return self.closest_side(x, y)

        # Returns a tuple containing the first side hit and the distance to it along the ray
        min_dist = 99999999999
        min_side = None
        for i in xrange(len(self._points)):
            if self.surfaces[i] == "None":
                continue

            x1, y1 = self._points[i]
            x2, y2 = self._points[(i + 1) % len(self._points)]

            dist = self._raycastLine(x1, y1, x2, y2, x, y, dx, dy)

            if dist is not None and dist < min_dist:
                min_dist = dist
                min_side = i

        return min_side, min_dist

    def collision_point(self, x, y):
        if self.is_rectangle:
            return self.bbox[0] < x < self.bbox[2] and self.bbox[1] < y < self.bbox[3]

        xinters = None
        n = len(self._points)
        inside = False

        p1x,p1y = self._points[0]
        for i in range(n+1):
            p2x,p2y = self._points[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y

        return inside

    def colliding(self, collidable, x_diff, y_diff, dx, dy):
        if collidable.is_rectangle and self.is_rectangle:
            return self._rect_to_rect(collidable, x_diff, y_diff)

        return self._poly_to_poly(collidable, x_diff, y_diff, dx, dy)

    def _poly_to_poly(self, collidable, x_diff, y_diff, dx, dy):
        collisions = set()
        max_dist = 0
        for point in self._points:
            x, y = point[0] - x_diff, point[1] - y_diff
            if collidable.collision_point(x, y):
                side = collidable.raycast_get_side(x, y, dx, dy)
                if side[0] is not None:
                    if side[1] > max_dist:
                        collisions.clear()
                        max_dist = side[1]
                    collisions.add(collidable.surfaces[side[0]])

        for i, point in enumerate(collidable.points):
            x, y = point[0] + x_diff, point[1] + y_diff
            if self.collision_point(x, y):
                side = self.raycast_get_side(x, y, -dx, -dy)
                if side[0] is not None:
                    if side[1] > max_dist:
                        collisions.clear()
                        max_dist = side[1]
                    collisions |= collidable._blocking_surface(dx, dy, i)

        try:
            collisions.remove("None")
        except KeyError: pass
        return collisions, max_dist

    def _rect_to_rect(self, collidable, x_diff, y_diff):
        if not (self.bbox[2] > collidable.bbox[0] + x_diff and
                self.bbox[3] > collidable.bbox[1] + y_diff and
                self.bbox[0] < collidable.bbox[2] + x_diff and
                self.bbox[1] < collidable.bbox[3] + y_diff):
            return set(), 0

        dist_left = self.bbox[2] - collidable.bbox[0] - x_diff
        dist_top = self.bbox[3] - collidable.bbox[1] - y_diff
        dist_right = collidable.bbox[2] - self.bbox[0] + x_diff
        dist_bottom = collidable.bbox[3] - self.bbox[1] + y_diff

        if dist_top < dist_left:
            if dist_right < dist_top:
                if dist_bottom < dist_right:
                    min_sur = 2
                    min_dist = dist_bottom
                else:
                    min_sur = 1
                    min_dist = dist_right
            else:
                if dist_bottom < dist_top:
                    min_sur = 2
                    min_dist = dist_bottom
                else:
                    min_sur = 0
                    min_dist = dist_top

        else:
            if dist_right < dist_left:
                if dist_bottom < dist_right:
                    min_sur = 2
                    min_dist = dist_bottom
                else:
                    min_sur = 1
                    min_dist = dist_right
            else:
                if dist_bottom < dist_left:
                    min_sur = 2
                    min_dist = dist_bottom
                else:
                    min_sur = 3
                    min_dist = dist_left

        min_sur = collidable.surfaces[min_sur]
        if min_sur != "None":
            return {min_sur}, min_dist
        else:
            return set(), 0

    def _blocking_surface(self, dx, dy, point):
        dx, dy = dy, -dx

        x1, y1 = self._points[(point - 1) % len(self._points)]
        x2, y2 = self._points[point]
        x3, y3 = self._points[(point + 1) % len(self._points)]

        dx1 = x2 - x1
        dy1 = y2 - y1

        dx2 = x3 - x2
        dy2 = y3 - y2

        dot1 = abs(dx * dx1 + dy * dy1)
        dot2 = abs(dx * dx2 + dy * dy2)

        if dot1 > dot2:
            return {self.surfaces[(point - 1) % len(self._points)]}

        if dot1 == dot2:
            return {self.surfaces[(point - 1) % len(self._points)], self.surfaces[point]}

        return {self.surfaces[point]}


class CollisionRectangle(Collidable):
    def __init__(self, inst, x1, y1, x2, y2, sur_top, sur_right=None, sur_bottom=None, sur_left=None):
        #Ensure the correct arguments were given
        if sur_right is None and sur_bottom is None and sur_left is None:
            sur_left = sur_bottom = sur_right = sur_top
        elif not (sur_right is not None and sur_bottom is not None and sur_left is not None):
            raise ArgumentError("Either four surfaces or one surface must be given")

        self.inst = inst
        self.is_rectangle = True
        self.bbox = (x1, y1, x2, y2)
        self.surfaces = [sur_top, sur_right, sur_bottom, sur_left]
        #print self.surfaces
        self._points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        self._points_next = self._points[:]
        self._points_next_previous = self._points_previous = [(None, None)] * len(self._points)
        collision.line_grid.collidable_update(self)



class CollisionMesh(Collidable):
    def __init__(self, inst, *data):
        if len(data) % 2 != 0:
            raise ArgumentError("An even number of data arguments must be given in the format (x1,y1),'surface1',(x2,y2),'surface2'...")

        self.inst = inst
        self._points = list(data[::2])
        self.surfaces = list(data[1::2])


        self._points_next = self._points[:]
        self._points_next_previous = self._points_previous = [(None, None)] * len(self._points)
        self.update_bounding_box()
        collision.line_grid.collidable_update(self)

class CollisionNull(object):
    bbox = (0, 0, 0, 0)