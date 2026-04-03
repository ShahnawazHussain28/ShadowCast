from box import Box, WallType
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patches

SIZE = 50

def main():
    fig, ax = plt.subplots()
    image = plt.imread("image.png", format="png")
    height, width = image.shape[:2]
    box = Box(width/2-100, height/2, SIZE, SIZE/2)
    ax.set_ylim([height, 0])
    ax.set_xlim([0, width])
    ax.set_aspect('equal', adjustable='box')
    ax.imshow(image)
    box.draw(ax)

    alpha_coords = np.argwhere(image[:, :, 3] > 0)
    alpha_coords = alpha_coords[::10]

    ax.plot(alpha_coords[:, 1], alpha_coords[:, 0], 'y.', markersize=0.3)


    fig, ax2 = plt.subplots()
    ax2.set_ylim([box.north.height+5, -5])
    ax2.set_xlim([-5, box.north.width+5])
    ax2.set_aspect('equal', adjustable='box')
    points = box.north.get_points() - box.north.origin
    new_points = []
    for point in points:
        new_points.append([point[0], point[2]])

    ax2.add_patch(patches.Polygon(new_points, closed=True))

    x_coords = []
    y_coords = []
    for i, coord in enumerate(alpha_coords):
        wall, intersection = box.get_intersection([coord[0], coord[1], 0])
        if wall and wall.name == WallType.NORTH:
            ax.add_line(plt.Line2D([coord[1], box.center[0]], [coord[0], box.center[1]]))
            c = intersection - box.north.origin
            x_coords.append(c[0])
            y_coords.append(c[2])

    ax2.plot(x_coords, y_coords, 'ko', markersize=1)

    plt.show()


main()
