import numpy as np
from enum import Enum
from config import Config
import cv2

class WallType(Enum):
    BASE = 0
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

config = Config()

ELEVATION_FACTOR = config.elevation_factor

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

class Box:
    def __init__(self, x, y, size, height):
        self.x = x
        self.y = y
        self.size = size
        self.center = np.array([x+size/2, y+size/2, 0])
        self.light = self.center + np.array([0, 0, height*ELEVATION_FACTOR])
        self.height = height
        self.base = Wall(
            WallType.BASE,
            [x, y, 0],
            [x+size, y, 0],
            [x, y+size, 0],
        )
        self.north = Wall(
            WallType.NORTH,
            [x, y, 0],
            [x+size, y, 0],
            [x, y, height],
        )
        self.east = Wall(
            WallType.EAST,
            [x+size, y, 0],
            [x+size, y+size, 0],
            [x+size, y, height],
        )
        self.south = Wall(
            WallType.SOUTH,
            [x, y+size, 0],
            [x+size, y+size, 0],
            [x, y+size, height],
        )
        self.west = Wall(
            WallType.WEST,
            [x, y, 0],
            [x, y+size, 0],
            [x, y, height],
        )
    
    def get_wall(self, wall_name):
        if wall_name == WallType.NORTH:
            return self.north
        elif wall_name == WallType.EAST:
            return self.east
        elif wall_name == WallType.SOUTH:
            return self.south
        elif wall_name == WallType.WEST:
            return self.west
        else:
            return self.base
    
    def draw(self, image_bin):
        image = cv2.cvtColor(image_bin, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(image, (int(self.x), int(self.y)), (int(self.x+self.size), int(self.y+self.size)), (0,0,0), -1)
        return image

    @staticmethod
    def project_to_z0(light: np.ndarray, point: np.ndarray):
        t = -light[2] / (point[2] - light[2])
        x = light[0] + t * (point[0] - light[0])
        y = light[1] + t * (point[1] - light[1])
        return x, y