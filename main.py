import numpy as np
import matplotlib.pyplot as plt

class Plane:
    def __init__(self, normal, d):
        self.d = d
        n_hat = np.linalg.norm(normal)
        self.normal = np.array(normal)/n_hat

    def distance(self, point):
        return np.dot(self.normal, point) - self.d

# https://github.com/fogleman/sdf/blob/d58a6fc6/sdf/d3.py
class Box:
    def __init__(self, length_x, length_y, length_z, center=[0,0,0]):
        self.half_extent = np.array([length_x, length_y, length_z])

    def distance(self, point):
        distance = np.abs(point) - self.half_extent
        return np.linalg.norm(np.maximum(distance, 0.0)) + np.minimum(np.maximum(distance[0], np.maximum(distance[1],distance[2])), 0.0)

    def inside(self, point):
        return self.distance(point) < 0

def box_test():
    cube = Box(1,1,1)
    print(cube.distance(np.array([2,0,0])))

class CompositeSolid:
    def __init__(self, solids, union_type):
        self.solids = solids
        self.union_type = union_type

    def distance(self,point):
        if self.union_type == "union":
            return np.min([solid.distance(point) for solid in self.solids])



class CompositePlanes:
    def __init__(self, planes):
        self.planes = np.array(planes)

    def inside(self, point):
        is_inside = True
        for plane in self.planes:
            #print(plane.distance(point))
            is_inside = is_inside and plane.distance(point) < 0

        return is_inside

    def on_surface(self, point):
        for plane in self.planes:
            if plane.distance(point) == 0:
                return True

        return False

#     T | F
#Var  0   1   1   0
#Ins  0   1   0   1
#     0   0   1   1


    def closest_surface(self, point):
        epsilon = 1e-6

        distances = []
        point = np.array(point)

        plane_id = -1

        is_inside = self.inside(point)

        for plane in self.planes:
            plane_id += 1
            distance = plane.distance(point)
            if is_inside:
                test_point = point - (distance - epsilon) * plane.normal
            else:
                test_point = point - (distance + epsilon)*plane.normal

            if distance == 0:
                return plane_id

            if self.inside(test_point) ^ is_inside:
                #print("!!!")
                distances.append([plane_id, np.abs(distance)])

        if not distances:
           distances = [[i, np.abs(plane.distance(point))] for i, plane in enumerate(self.planes)]

        distances = np.array(distances)

        minimal_distance_plane_id = int(distances[np.argmin(distances[:, 1])][0])

        return minimal_distance_plane_id

    def distance(self, point):
        return self.planes[self.closest_surface(point)].distance(point)

def main():
    planes_1=[Plane([1,0,0], 1),
            Plane([0,1,0], 1),
            Plane([0,0,1], 1),
            Plane([-1,0,0], 1),
            Plane([0,-1,0], 1),
            Plane([0,0,-1], 1),]

    planes_2 = [Plane([-1, 0, 0], 1),
                  Plane([0, -1, 0], 1),
                  Plane([0, -1, 0], 1),
                  Plane([-2, 0, 0], 1),
                  Plane([0, -2, 0], 1),
                  Plane([0, 0, -2], 1), ]

    cube =  Box(2,2,2)
    cube_2 = CompositePlanes(planes_2)
    composite = CompositeSolid([cube,cube_2], "union")
    """
    print(cube.on_surface([1,0,0]))
    print(cube.inside([0,0,0]))
    print(cube.inside([3,4,5]))

    print(cube.closest_surface([0,2.5,0]))
    print(cube.distance([0,2.5,0]))
    """
    x = np.linspace(3,-3,100)
    y = np.linspace(3,-3,100)

    distances = np.array([
        [cube.distance([xx, yy, 0]) for xx in x]
        for yy in y
    ])
    print(distances)

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
    plt.title("Cube distance heatmap at z = 0")
    plt.axis("equal")
    plt.show()

    """
    rnd = np.random.uniform(-1.5, 1.5, size=(5000, 3))
    rnd[:, 2] = 0
    inside_points = np.array([r for r in rnd if cube.inside(r)])
    print(inside_points)
    #print(inside_points)

    plt.plot(inside_points[:, 0], inside_points[:, 1], ".")

    plt.xlim(-1.5, 1.5)
    plt.ylim(-1.5, 1.5)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Cube inside points at z = 0")
    plt.axis("equal")
    plt.show()
    """

    x2 = np.linspace(1.5, -2.5, 100)
    y2 = np.linspace(1.5, -2.5, 100)

    distances2 = np.array([
        [composite.distance([xx, yy, 0]) for xx in x2]
        for yy in y2
    ])
    print(distances2)
    plt.figure(figsize=(7, 6))
    heatmap2 = plt.imshow(
        distances2,
        extent=[x2.min(), x2.max(), y2.min(), y2.max()],
        origin="lower",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
    )
    plt.colorbar(heatmap2, label="Distance")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Composite distance heatmap at z = 0")
    plt.axis("equal")
    plt.show()

if __name__ == "__main__":
    box_test()
    main()
