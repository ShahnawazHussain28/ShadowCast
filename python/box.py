import numpy as np
from enum import Enum
from matplotlib.axes import Axes
from matplotlib import patches

class WallType(Enum):
    BASE = 0
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

class Wall:
    def __init__(self, name, p1, p2, p3):
        """
        p1: Origin corner point [x, y, z]
        p2: Corner defining the first edge (width)
        p3: Corner defining the second edge (height)
        """
        self.name = name
        self.origin = np.array(p1)
        self.u_axis = np.array(p2) - self.origin
        self.v_axis = np.array(p3) - self.origin
        self.width = np.linalg.norm(self.u_axis)
        self.height = np.linalg.norm(self.v_axis)
        n = np.cross(self.u_axis, self.v_axis)
        self.normal = n / np.linalg.norm(n)
        self.unit_normal = self.normal / np.linalg.norm(self.normal)
        self.d = np.dot(self.unit_normal, self.origin)

    def get_point(self, u, v):
        """
        Returns a 3D coordinate for local parameters u and v.
        u, v should be between 0 and 1.
        """
        return self.origin + u * self.u_axis + v * self.v_axis

    def get_points(self):
        """
        Returns a list of the 4 corner points [x, y, z] in order:
        (0,0), (1,0), (1,1), (0,1)
        """
        corners = [
            self.get_point(0, 0),  # Origin (P1)
            self.get_point(1, 0),  # Along u_axis (P2)
            self.get_point(1, 1),  # Opposite corner (P2 + v_axis)
            self.get_point(0, 1),  # Along v_axis (P3)
        ]
        return np.array(corners)
    
    def is_inside(self, point, tol=1e-6):
        """Checks if a point [x, y, z] is on this finite rectangle."""
        p = np.array(point)        
        if abs(np.dot(self.unit_normal, p) - self.d) > tol:
            return False
            
        rel_p = p - self.origin
        basis = np.array([self.u_axis, self.v_axis]).T
        coords, _, _, _ = np.linalg.lstsq(basis, rel_p, rcond=None)
        u, v = coords
        
        return (0 - tol <= u <= 1 + tol) and (0 - tol <= v <= 1 + tol)

    def intersects(self, line: 'Line', tol=1e-6):
        denom = np.dot(self.unit_normal, line.vector)
        if abs(denom) < tol:
            return None
        t = np.dot(self.unit_normal, self.origin - line.p1) / denom
        if not (0 <= t <= 1):
            return None
        hit_point = line.p1 + t * line.vector
        if self.is_inside(hit_point, tol):
            return hit_point


class Ray:
    def __init__(self, origin, direction):
        self.origin = np.array(origin)
        dir_arr = np.array(direction)
        self.direction = dir_arr / np.linalg.norm(dir_arr)

    def get_point(self, t) -> np.ndarray:
        """Returns the 3D position at distance 't' from the origin."""
        return self.origin + t * self.direction

class Line:
    def __init__(self, p1, p2):
        self.p1 = np.array(p1)
        self.p2 = np.array(p2)
        self.vector = p2 - p1
        self.length = np.linalg.norm(self.vector)
        self.unit_vector = self.vector / self.length
    
    def get_point(self, t):
        """
        Returns a 3D coordinate for local parameter t.
        t should be between 0 and 1.
        """
        return self.p1 + t * self.unit_vector


class Box:
    def __init__(self, x, y, size, height):
        # center of the box
        self.x = x
        self.y = y
        self.size = size
        self.center = np.array([x+size/2, y+size/2, 0])
        self.light = self.center + np.array([0, 0, height+30])
        self.height = height
        self.base = Wall(
            WallType.BASE,
            [x, y, 0],
            [x+size, y, 0],
            [x, y+size, 0],
        )
        self.north = Wall(
            WallType.NORTH,
            [x, y+size, 0],
            [x+size, y+size, 0],
            [x, y+size, height],
        )
        self.east = Wall(
            WallType.EAST,
            [x+size, y+size, 0],
            [x+size, y, 0],
            [x+size, y+size, height],
        )
        self.south = Wall(
            WallType.SOUTH,
            [x+size, y, 0],
            [x, y, 0],
            [x+size, y, height],
        )
        self.west = Wall(
            WallType.WEST,
            [x, y, 0],
            [x, y+size, 0],
            [x, y, height],
        )
    
    def draw(self, ax: Axes):
        ax.add_patch(patches.Polygon(self.base.get_points()[:, :2], closed=True))
        ax.add_patch(patches.Polygon(self.north.get_points()[:, :2], closed=True, edgecolor='black', linewidth=1))
        ax.add_patch(patches.Polygon(self.east.get_points()[:, :2], closed=True, edgecolor='black', linewidth=1))
        ax.add_patch(patches.Polygon(self.south.get_points()[:, :2], closed=True, edgecolor='black', linewidth=1))
        ax.add_patch(patches.Polygon(self.west.get_points()[:, :2], closed=True, edgecolor='black', linewidth=1))
    
    def get_intersection(self, point: np.ndarray):
        # shoot light rays from the destination to the light source
        line = Line(point, self.light)
        walls = [self.base, self.north, self.east, self.south, self.west]
        closest_intersection = float('inf')
        closest_wall = None
        closest_point = None
        for wall in walls:
            hit = wall.intersects(line)
            if hit is not None:
                dist = np.linalg.norm(hit - point)
                if dist < closest_intersection:
                    closest_intersection = dist
                    closest_wall = wall
                    closest_point = hit
                
        return closest_wall, closest_point