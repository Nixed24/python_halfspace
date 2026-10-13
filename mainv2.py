import numpy as np
from enum import Enum
import matplotlib.pyplot as plt

class InsideStates(Enum):
    INSIDE = -1
    ON_SURFACE = 0
    OUTSIDE = +1

class UnionTypes(Enum):
    UNION = +1
    INTERSECTION = 0
    SUBTRACTIONS = -1

class Surface:
    def __init__(self):
        pass

    def implicit_function(self, point):
        return 0

    def inside(self, point):
        if self.implicit_function(point) < 0:
            return InsideStates.OUTSIDE
        elif self.implicit_function(point) > 0:
            return InsideStates.OUTSIDE
        else:
            return InsideStates.ON_SURFACE

    def intersection(self, point, surface):
        np.max([self.implicit_function(point), surface.implicit_function(point)])

    def union(self, point, surface):
        np.min([self.implicit_function(point), surface.implicit_function(point)])

    def subtraction(self, point, surface):
        np.max([self.implicit_function(point), -surface.implicit_function(point)])

class Plane(Surface):
    def __init__(self, n, d):
        super().__init__()
        self.normal = n / np.linalg.norm(n)
        self.d = d

    def implicit_function(self, point):
        return np.dot(point, self.normal) - self.d

    def distance_to_in(self, point, v):
        return (self.d - np.dot(self.normal, point))/np.dot(self.normal, v)

class CompositeSurface(Surface):
    def __init__(self, surfaces, union_type):
        super().__init__()
        self.surfaces = np.array(surfaces)
        self.union_type = union_type

    """
    def add_surface(self, surface):
        self.surfaces = np.append(self.surfaces, surface)"""

    def implicit_function(self, point):
        if self.union_type == UnionTypes.UNION:
            return np.max([surface.implicit_function(point) for surface in self.surfaces])
        elif self.union_type == UnionTypes.INTERSECTION:
            return self.intersection(point)
        else:
            return None

def sdf_plotter_xy(xmin, xmax, ymin, ymax, shape,
                n=250, v_min=-1, v_max=1):
    x = np.linspace(xmin,xmax,n)
    y = np.linspace(ymin,ymax,n)

    distances = np.array([
        [shape.implicit_function([xx, yy, 0]) for xx in x]
        for yy in y
    ])

    plt.figure(figsize=(7, 6))
    heatmap = plt.imshow(
        distances,
        extent=[x.min(), x.max(), y.min(), y.max()],
        origin="lower",
        cmap="coolwarm",
        vmin=v_min,
        vmax=v_max,
    )

    plt.colorbar(heatmap, label="Distance")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("SDF at z = 0")
    plt.axis("equal")
    plt.show()

def main():
    planes = [Plane([1,0,0], 1),
            Plane([0,1,0], 1),
            Plane([0,0,1], 1),
            Plane([-1,0,0], 2),
            Plane([0,-1,0], 2),
            Plane([0,0,-1], 1)]
    planes2 = [Plane([1, 0, 0], -1),
              Plane([0, 1, 0], -1),
              Plane([0, 0, 1], 1),
              Plane([-1, 0, 0], 4),
              Plane([0, -1, 0], 4),
              Plane([0, 0, -1], 1)]

    cube_dictionary = {
        Plane([1, 0, 0], 1):UnionTypes.INTERSECTION,
        Plane([0, 1, 0], 1):UnionTypes.INTERSECTION,
        Plane([0, 0, 1], 1):UnionTypes.INTERSECTION,
        Plane([-1, 0, 0], 2):UnionTypes.INTERSECTION,
        Plane([0, -1, 0], 2):UnionTypes.INTERSECTION,
        Plane([0, 0, -1], 1):UnionTypes.INTERSECTION
    }

    cube = CompositeSurface(planes, UnionTypes.INTERSECTION)
    cube2 = CompositeSurface(planes2, UnionTypes.INTERSECTION)

    cube_union = CompositeSurface([cube,cube2], UnionTypes.UNION)
    cube_intersection = CompositeSurface([cube,cube2], UnionTypes.INTERSECTION)
    sdf_plotter_xy(-5,5,-5,5,cube)
    sdf_plotter_xy(-5,5,-5,5,cube2)
    sdf_plotter_xy(-5,5,-5,5,cube_union)
    sdf_plotter_xy(-5,5,-5,5,cube_intersection)

if __name__ == "__main__":
    main()