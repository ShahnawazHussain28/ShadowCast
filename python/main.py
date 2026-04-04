import cv2
import numpy as np
from box import Box, WallType

SIZE = 50

COLOR = {
    WallType.BASE: (255, 0, 0),
    WallType.SOUTH: (0, 255, 0),
    WallType.EAST: (0, 0, 255),
    WallType.NORTH: (255, 255, 0),
    WallType.WEST: (255, 0, 255),
}

image = cv2.imread("image.png", cv2.IMREAD_UNCHANGED)
image_alpha = image[:, :, 3]
_, image_bin = cv2.threshold(image_alpha, 126, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(image_bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

img_contours = cv2.drawContours(image, contours, -1, (255, 255, 255), 1)

height, width = image.shape[:2]
box = Box(width/2-100, height/2, SIZE, SIZE/2)

for c in contours:
    for coord in c:
        row, col = coord[0]
        wall, intersection = box.get_intersection([row, col, 0.0])
        if wall is not None:
            intersection = np.int16(intersection)
            cv2.line(image, tuple(coord[0]), tuple(np.int16(intersection[0:2:1])), COLOR[wall.name], 1)

image = box.draw_cv(image, (255,255,255))

cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
