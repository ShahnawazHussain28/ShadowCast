import cv2
import numpy as np
from box import Box, WallType, Wall

SIZE = 50
RESOLUTION = 15

COLOR = {
    WallType.NORTH: (255, 0, 0), # blue
    WallType.SOUTH: (0, 255, 0), # green
    WallType.EAST: (0, 0, 255), # red
    WallType.WEST: (255, 0, 255), # magenta
}

image = cv2.imread("zoro.png", cv2.IMREAD_UNCHANGED)
image = cv2.resize(image, (480, 480))
image_alpha = image[:, :, 3]
_, image_bin = cv2.threshold(image_alpha, 126, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(image_bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

img_contours = cv2.drawContours(image, contours, -1, (255, 255, 255), 1)

height, width = image.shape[:2]

def intersection_to_2d(intersection, wall: Wall):
    intersection = np.int16((intersection - wall.origin) * RESOLUTION)
    if wall.name == WallType.NORTH:
        intersection = np.delete(intersection, 1)
    elif wall.name == WallType.SOUTH:
        intersection = np.delete(intersection, 1)
    elif wall.name == WallType.EAST:
        intersection = np.delete(intersection, 0)
    elif wall.name == WallType.WEST:
        intersection = np.delete(intersection, 0)
    
    return intersection

def draw_carvings(carvings, image, color):
    carvings = [np.array(c).reshape((-1, 1, 2)).astype(np.int32) for c in carvings]
    cv2.polylines(image, carvings, isClosed=False, color=color, thickness=1)

def debug_carvings(carvings, title=""):
    print(title)
    l = []
    for c in carvings:
        l.extend(c[0])
    l = np.array(l)
    print(min(l[:, 0]), max(l[:, 0]), min(l[:, 1]), max(l[:, 1]))

def place_box(x=width/2, y=height/2):
    display_image = image.copy()
    x = x - SIZE/2
    y = y - SIZE/2
    box = Box(x, y, SIZE, SIZE/2)
    carvings = {
        WallType.SOUTH: [],
        WallType.EAST: [],
        WallType.NORTH: [],
        WallType.WEST: [],
    }

    for c in contours:
        carving = []
        prevWall = None
        for coord in c:
            row, col = coord[0]
            wall, intersection = box.get_intersection([row, col, 0.0])
            if wall is not None:
                intersection2d = intersection_to_2d(intersection, wall)
                if prevWall is not None and wall.name != prevWall.name:
                    carvings[prevWall.name].append([carving])
                    carving = []
                carving.append(intersection2d)
                prevWall = wall
                intersection = np.int16(intersection)
                cv2.line(display_image, tuple(coord[0]), tuple(np.int16(intersection[:2])), COLOR[wall.name], 1)

        if prevWall is not None:
            carvings[prevWall.name].append([carving])

    north_wall = np.zeros((int(SIZE*RESOLUTION/2), SIZE*RESOLUTION, 3), dtype=np.uint8)
    south_wall = north_wall.copy()
    east_wall = north_wall.copy()
    west_wall = north_wall.copy()
    draw_carvings(carvings[WallType.NORTH], north_wall, COLOR[WallType.NORTH])
    draw_carvings(carvings[WallType.SOUTH], south_wall, COLOR[WallType.SOUTH])
    draw_carvings(carvings[WallType.EAST], east_wall, COLOR[WallType.EAST])
    draw_carvings(carvings[WallType.WEST], west_wall, COLOR[WallType.WEST])
    cv2.imshow("North wall", cv2.flip(north_wall, 0))
    cv2.imshow("South wall", south_wall)
    cv2.imshow("East wall", cv2.flip(cv2.rotate(east_wall, cv2.ROTATE_90_COUNTERCLOCKWISE), 0))
    cv2.imshow("West wall", cv2.rotate(west_wall, cv2.ROTATE_90_CLOCKWISE))
    cv2.imshow("Image", display_image)








place_box()

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        place_box(x, y)



cv2.setMouseCallback('Image', click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()
