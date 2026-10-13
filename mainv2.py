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
            return InsideStates.INSIDE
        elif self.implicit_function(point) > 0:
            return InsideStates.OUTSIDE
        else:
            return InsideStates.ON_SURFACE

    def intersection(self, point, surface):
        return np.max([self.implicit_function(point), surface.implicit_function(point)])

    def union(self, point, surface):
        return np.min([self.implicit_function(point), surface.implicit_function(point)])

    def subtraction(self, point, surface):
        return np.max([self.implicit_function(point), -surface.implicit_function(point)])

    def distance_to_in(self, p, v):
        # b - starting point
        # v - unit vector along ray
        return 0

class Plane(Surface):
    def __init__(self, n, d):
        super().__init__()
        self.normal = n / np.linalg.norm(n)
        self.d = d

    def implicit_function(self, point):
        return np.dot(point, self.normal) - self.d

    def distance_to_in(self, p, v):
        return (self.d - np.dot(self.normal, p))/np.dot(self.normal, v)

class Sphere(Surface):
    def __init__(self, radius, center):
        super().__init__()
        self.radius = radius
        self.center = center

    def implicit_function(self, point):
        return np.linalg.norm(point - self.center)**2 - self.radius

    def distance_to_in(self, p, v):
        b = 2*np.dot((p - self.center), v)
        c = - 2*np.dot(self.center, p) - self.radius + np.linalg.norm(p)**2

        return 0.5*(-c - np.sqrt(b**2 - 4*c))

class CompositeSurface(Surface):
    def __init__(self, surfaces, union_type):
        super().__init__()
        self.surfaces = np.array(surfaces)
        self.union_type = union_type

    def add_surface(self, surface):
        self.surfaces = np.append(self.surfaces, surface)

    def implicit_function(self, point):
        if self.union_type == UnionTypes.UNION:
            return np.min([surface.implicit_function(point) for surface in self.surfaces])
        elif self.union_type == UnionTypes.INTERSECTION:
            return np.max([surface.implicit_function(point) for surface in self.surfaces])
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

def inside_plotter_xy(mi, ma, shape, n):
    rnd = np.random.uniform(mi, ma, size=(n, 3))
    rnd[:, 2] = 0

    inside_points = np.array([r for r in rnd if shape.inside(r) == InsideStates.INSIDE])
    surface_points = np.array([r for r in rnd if shape.inside(r) == InsideStates.OUTSIDE])
    plt.figure(figsize=(5, 5))
    plt.plot(inside_points[:, 0], inside_points[:, 1], ".g")
    plt.plot(surface_points[:, 0], surface_points[:, 1], ".r")
    plt.xlim(mi, ma)
    plt.ylim(mi, ma)
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


    cube = CompositeSurface(planes, UnionTypes.INTERSECTION)
    cube2 = CompositeSurface(planes2, UnionTypes.INTERSECTION)

    cube_union = CompositeSurface([cube,cube2], UnionTypes.UNION)
    cube_intersection = CompositeSurface([cube,cube2], UnionTypes.INTERSECTION)

    inside_plotter_xy(-1.25,1.25,cube, 10000)
    inside_plotter_xy(-3,3,cube_union, 10000)
    sdf_plotter_xy(-3,3,-3,3,cube)
    sdf_plotter_xy(-3,3,-3,3,cube2)
    sdf_plotter_xy(-3,3,-3,3,cube_union)
    sdf_plotter_xy(-3,3,-3,3,cube_intersection)
    inside_plotter_xy(-3,3,cube_intersection,10000)
    xmin = -3
    xmax = 3
    ymin = -3
    ymax = 3
    n = 300

    x = np.linspace(xmin, xmax, n)
    y = np.linspace(ymin, ymax, n)

    distances = np.array([
        [cube2.subtraction([xx, yy, 0], cube) for xx in x]
        for yy in y
    ])
    plt.figure(figsize=(7, 6))
    heatmap = plt.imshow(
        distances,
        extent=[x.min(), x.max(), y.min(), y.max()],
        origin="lower",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
    )

    plt.colorbar(heatmap, label="Distance")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("SDF at z = 0")
    plt.axis("equal")
    plt.show()

if __name__ == "__main__":
    main()