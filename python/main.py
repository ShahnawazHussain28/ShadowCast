import cv2
import numpy as np
from box import Box, WallType
from config import Config

FILE_NAME = Config.file_name

IMAGE_RESOLUTION = Config.image_resolution
SIZE = Config.box_size
PAPER_W = Config.paper_width
PAPER_H = Config.paper_height
PADDING = Config.paper_padding
ELEVATION_FACTOR = Config.elevation_factor

WALL_SIZE = int((PAPER_W - 2*PADDING) / 4)

image = cv2.imread("input/"+FILE_NAME, cv2.IMREAD_UNCHANGED)
image = cv2.resize(image, (IMAGE_RESOLUTION, IMAGE_RESOLUTION))
image_alpha = image[:, :, 3]
_, image_bin = cv2.threshold(image_alpha, 126, 255, cv2.THRESH_BINARY)

height, width = image.shape[:2]

def draw_carvings(carvings, image, color):
    carvings = [np.array(c).reshape((-1, 1, 2)).astype(np.int32) for c in carvings]
    cv2.polylines(image, carvings, isClosed=False, color=color, thickness=1)

def place_images_on_a4(base_wall, north_wall, south_wall, east_wall, west_wall):
    paper = np.ones((PAPER_H, PAPER_W, 3), dtype=np.uint8) * 255
    outline_thickness = 1
    w = PAPER_W - PADDING*2
    unit = int(w/4)
    base_wall = cv2.resize(base_wall, (unit*2, unit*2))
    north_wall = cv2.resize(north_wall, (unit*2, unit))
    south_wall = cv2.resize(south_wall, (unit*2, unit))
    east_wall = cv2.resize(east_wall, (unit, unit*2))
    west_wall = cv2.resize(west_wall, (unit, unit*2))
    cv2.rectangle(north_wall, (0, 0), (unit*2-1, unit-1), (0, 0, 0), outline_thickness)
    cv2.rectangle(south_wall, (0, 0), (unit*2-1, unit-1), (0, 0, 0), outline_thickness)
    cv2.rectangle(east_wall, (0, 0), (unit-1, unit*2-1), (0, 0, 0), outline_thickness)
    cv2.rectangle(west_wall, (0, 0), (unit-1, unit*2-1), (0, 0, 0), outline_thickness)
    cv2.circle(base_wall, (unit, unit), int(unit*0.1), (0, 0, 0), -1)

    paper[PADDING+unit:PADDING+unit*3, PADDING+unit:PADDING+unit*3, :] = base_wall
    paper[PADDING:PADDING+unit, PADDING+unit:PADDING+unit*3, :] = north_wall
    paper[PADDING+unit*3:PADDING+w, PADDING+unit:PADDING+unit*3, :] = south_wall
    paper[PADDING+unit:PADDING+unit*3, PADDING+unit*2+unit:PADDING+w, :] = east_wall
    paper[PADDING+unit:PADDING+unit*3, PADDING:PADDING+unit, :] = west_wall
    cv2.rectangle(paper, (PADDING + unit*2 - int(ELEVATION_FACTOR*unit/2), PADDING*2 + w - 10), (PADDING+unit*2 + int(ELEVATION_FACTOR*unit/2), PADDING*2 + w + 10), (0, 0, 0), -1)

    return paper

def place_box(x=width/2, y=height/2):
    display_image = image.copy()
    x = x - SIZE/2
    y = y - SIZE/2
    box = Box(x, y, SIZE, SIZE/2)

    wall_canvases = {
        WallType.SOUTH: np.zeros((WALL_SIZE, WALL_SIZE*2), dtype=np.uint8),
        WallType.EAST: np.zeros((WALL_SIZE, WALL_SIZE*2), dtype=np.uint8),
        WallType.NORTH: np.zeros((WALL_SIZE, WALL_SIZE*2), dtype=np.uint8),
        WallType.WEST: np.zeros((WALL_SIZE, WALL_SIZE*2), dtype=np.uint8),
    }
    for wall_name, canvas in wall_canvases.items():
        wall = box.get_wall(wall_name)
        for v in range(WALL_SIZE):
            for u in range(WALL_SIZE*2):
                norm_u = u / (WALL_SIZE * 2)
                norm_v = v / WALL_SIZE
                point = wall.get_point(norm_u, norm_v)
                zx, zy = Box.project_to_z0(box.light, point)
                if 0 <= zx <= IMAGE_RESOLUTION and 0 <= zy <= IMAGE_RESOLUTION:
                    if image_bin[int(zy), int(zx)] == 255:
                        canvas[v, u] = 255


    base_wall = np.ones((WALL_SIZE*2, WALL_SIZE*2, 3), dtype=np.uint8) * 255
    north_wall = cv2.cvtColor(wall_canvases[WallType.NORTH], cv2.COLOR_GRAY2BGR)
    south_wall = cv2.cvtColor(wall_canvases[WallType.SOUTH], cv2.COLOR_GRAY2BGR)
    east_wall = cv2.cvtColor(wall_canvases[WallType.EAST], cv2.COLOR_GRAY2BGR)
    west_wall = cv2.cvtColor(wall_canvases[WallType.WEST], cv2.COLOR_GRAY2BGR)
    north_wall = cv2.flip(north_wall, 0)
    east_wall = cv2.flip(cv2.rotate(east_wall, cv2.ROTATE_90_COUNTERCLOCKWISE), 0)
    west_wall = cv2.rotate(west_wall, cv2.ROTATE_90_CLOCKWISE)
    cv2.imshow("Image", display_image)

    paper = place_images_on_a4(base_wall, north_wall, south_wall, east_wall, west_wall)
    cv2.imshow("Paper", cv2.resize(paper, (int(PAPER_W/4), int(PAPER_H/4))))
    cv2.imwrite("output/"+FILE_NAME, paper)
    print("Saved to " + "output/" + FILE_NAME)

place_box()

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        place_box(x, y)



cv2.setMouseCallback('Image', click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()
