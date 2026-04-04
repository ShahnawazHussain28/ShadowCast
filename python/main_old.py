from box import Box, WallType
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patches
import cv2

SIZE = 50

def main():
    fig, ax = plt.subplots()
    image_original = cv2.imread("image.png", cv2.IMREAD_UNCHANGED)
    height, width = image_original.shape[:2]
    box = Box(width/2-100, height/2, SIZE, SIZE/2)
    ax.set_ylim([height, 0])
    ax.set_xlim([0, width])
    ax.set_aspect('equal', adjustable='box')
    ax.imshow(image_original)
    box.draw(ax)

    image = image_original[:, :, 3]
    _, image = cv2.threshold(image, 126, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    print(len(contours), contours[0])
    img_contours = cv2.drawContours(image_original.copy(), contours, -1, (255, 255, 255), 3)
    
    alpha_coords = np.argwhere(image > 0)
    alpha_coords = alpha_coords[::10]

    ax.plot(alpha_coords[:, 1], alpha_coords[:, 0], 'y.', markersize=0.3)


    fig, ax2 = plt.subplots()
    ax2.set_ylim([box.north.height+5, -5])
    ax2.set_xlim([-5, box.north.width+5])
    ax2.set_aspect('equal', adjustable='box')
    points = box.north.get_points() - box.north.origin
    new_points = []
    for point in points:
        new_points.append([point[0]+SIZE, point[2]])

    ax2.add_patch(patches.Polygon(new_points, closed=True))

    x_coords = []
    y_coords = []
    for coord in alpha_coords:
        row, col = coord
        wall, intersection = box.get_intersection([col, row, 0.0])
        if wall and wall.name == WallType.NORTH:
            ax.add_line(plt.Line2D([col, box.center[0]], [row, box.center[1]]))
            c = intersection - box.north.origin
            x_coords.append(c[0]+SIZE)
            y_coords.append(c[2])

    ax2.plot(x_coords, y_coords, 'ko', markersize=1)
    ax.imshow(img_contours)
    plt.show()


main()
