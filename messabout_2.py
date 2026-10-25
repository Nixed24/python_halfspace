#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 14:08:05 2026

@author: deck
"""
import numpy as np
from matplotlib import pyplot as plt

EPSILON = 10 ** -8
INFINITY_POINT = np.array([np.inf, np.inf, np.inf])
np.seterr(all="warn")
def magnitude_3(vector):
    return np.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
def to_unit_vector(vector):
    if vector[0] == 0 and vector[1] == 0 and vector[2] == 0:
        return vector
    return vector / magnitude_3(vector)
def shortest_vector_point_line(p_1, v_1, p_2):
    return -1
def shortest_vector_between_lines(p_1, p_2, v_1, v_2):
    M = np.array([[np.dot(v_1, v_1), -1 * np.dot(v_1,v_2)],
                  [np.dot(v_1 ,v_2), -1 * np.dot(v_2, v_2)]])
    v = np.array([np.dot((p_2 - p_1), v_1),np.dot((p_2 - p_1), v_2)])
    try:
        M_inv = np.linalg.inv(M)
    except np.linalg.LinAlgError:
        return shortest_vector_point_line(p_1, v_1, p_2)
    lambda_p, mu_p = np.matmul(M_inv, v)[0], np.matmul(M_inv, v)[1]
    point_1 = p_1 + (lambda_p * v_1)
    point_2 = p_2 + (mu_p * v_2)
    vector = point_2 - point_1
    return vector
class Surface:
    def __init__(self):
        return 0
    def implicit_function(self, point):
        return 0
    def intersection(self, point, vec):
        return 0
    def inside(self, point):
        return 0
class Quadric(Surface):
    def __init__(self, M=None):
        self.M = M
        if self.M == None:
            M = np.identity(4)
            M[-1][-1] = -1
            self.M = M
    def make_cylinder(self):
        M = np.identity(4)
        M[-1][-1] = -1
        M[2][2] = 0
        self.M = M
        return
    def make_rugby_ball(self):
        M = np.identity(4)
        M[-1][-1] = -1
        M[1][1] = 0.33
        self.M = M
        return
    def translate(self, vec):
        if vec.shape != (3,):
            print("No.")
            return
        vec = -1 * vec
        matrix_affine = np.identity(4)
        for i in range (3):
            matrix_affine[i][-1] = vec[i]
        new_M = np.transpose(matrix_affine) @ self.M @ matrix_affine
        self.M = new_M
        return
    def rotate_matrix(self, rotation_matrix):
        if rotation_matrix.shape != (3,3):
            print("No.")
            return
        matrix_affine = np.identity(4)
        for i in range (3):
            for j in range(3):
                matrix_affine[i][j] = rotation_matrix[i][j] 
        new_M = np.transpose(matrix_affine) @ self.M @ matrix_affine
        self.M = new_M
    def implicit_function(self, point):
        p_affine = np.array([*point, 1])
        x_M = np.vecmat(p_affine, self.M)
        x_M_x = np.dot(x_M, p_affine)
        if x_M_x < 0:
            return -1
        elif np.isclose(x_M_x, 0):
            return 0
        return 1
    def get_intersection_multipliers(self, point, vec):
        # In some cases, rays can be parallel to the surface, so need to implement something for that
        d_affine = np.array([*vec, 0])
        p_affine = np.array([*point, 1])
        d_dagger_M = np.vecmat(d_affine, self.M)
        a = np.dot(d_dagger_M, d_affine)
        b = np.dot((2 * d_dagger_M), p_affine)
        c = np.dot(np.vecmat(p_affine, self.M), p_affine)
        # Could do a discriminant check here
        dir_multipliers = np.roots([a,b,c])
        return dir_multipliers
    def intersection(self, point, vec):
        intersection_points = np.zeros(3)
        intersection_multipliers = self.get_intersection_multipliers(point, vec)
        for mult in intersection_multipliers:
            if mult >= 0:
                intersection_points = np.vstack((intersection_points, point + (mult * vec)))
        intersection_points = intersection_points[1:]
        return intersection_points
    def inside(self, point):
        return self.implicit_function(point)
class InfiniteCylinder(Surface):
    def get_major_axis(self, axis): # get any axis really i just say major for laughs
        major_idx = np.squeeze(np.argmax(axis))
        if np.max(axis) == 1:
            major_idx -= 1 # 0 -> 2 (-1); 1 -> 0, 2-> 1
        returned_array = np.zeros(3)
        returned_array[major_idx] = 1
        return returned_array
    def __init__(self, radius=1, axis=np.array([0,0,1]), pos=np.array([0,0,0])):
        self.radius = radius
        self.axis = to_unit_vector(axis)
        self.pos = pos
        
        self.major_axis = self.get_major_axis(axis)
        self.radial_axis = np.cross(self.major_axis, axis)
        self.azimuthal_axis = np.cross(self.radial_axis, self.axis)
        self.rotation_matrix = np.transpose(np.vstack((self.axis, self.radial_axis, self.azimuthal_axis)))
        self.diag_matrix = np.linalg.inv(self.rotation_matrix)
        self.diag_origin = np.matmul(self.diag_matrix, self.pos)
        self.r_idx = np.argmax(np.matmul(self.diag_matrix, self.radial_axis))
        self.a_idx = np.argmax(np.matmul(self.diag_matrix, self.azimuthal_axis))
    def implicit_function(self, point):
        try:
            diag_point = np.matmul(self.diag_matrix, point)
        except:
            print(self.diag_matrix)
            print(point)
            raise KeyboardInterrupt("Caught")
        perp_dist = np.sqrt((self.diag_origin[self.a_idx] - diag_point[self.a_idx])**2 + \
                    (self.diag_origin[self.r_idx] - diag_point[self.r_idx])**2)
        if perp_dist < self.radius:
            return -1
        if np.isclose(perp_dist, self.radius):
            return 0
        else:
            return 1
        return
    def intersection(self, point, vec=0):
        if isinstance(vec, int):
            vec = -1 * point
        diag_point = np.matmul(self.diag_matrix, point)
        diag_vec = np.matmul(self.diag_matrix, vec)
        j = self.r_idx
        k = self.a_idx
        a = diag_vec[j]**2 + diag_vec[k]**2
        b = 2 * (diag_point[j]*diag_vec[j] + diag_point[k]*diag_vec[k] -\
                 diag_vec[j]*self.diag_origin[j] - \
                 diag_vec[k]*self.diag_origin[k])
        c = diag_point[j]**2 + diag_point[k]**2 +\
            self.diag_origin[j]**2 + self.diag_origin[k]**2 -\
            2 * diag_point[j] * self.diag_origin[j] - \
            2 * diag_point[k] * self.diag_origin[k] -\
                self.radius**2
        if b**2 - 4 * a *c < 0:
            return INFINITY_POINT
        lambda_1 = (- b + np.sqrt(b**2 - 4 * a * c)) / (2*a)
        lambda_2 = (- b - np.sqrt(b**2 - 4 * a * c)) / (2*a)
        point_1 = point + lambda_1 * vec
        point_2 = point + lambda_2 * vec
        return_array = np.vstack((point_1, point_2))
        #print(return_array)
        return return_array
    def inside(self, point):
        return self.implicit_function(point)
class Plane(Surface):
    def __init__(self, normal, distance):
        self.normal = normal
        self.distance = distance
        # n_1 x + n_2 y + n_3 z = d
        # => implicit = n_1 x + n_2 y + n_3 z - d = 0
    def implicit_function(self, point):
        return np.dot(point, self.normal) - self.distance
    def intersection(self, point, vec=0):
        if isinstance(vec, int):
            vec = -1 * point
        if self.inside(point) > 0 and np.dot(self.normal, vec) > 0:
            return INFINITY_POINT
        if np.dot(self.normal, vec) == 0:
            return INFINITY_POINT
        mu = (self.distance - np.dot(self.normal, point))/(np.dot(self.normal, vec))
        if np.isnan(mu):
            return INFINITY_POINT
        return point + (mu * vec)
    def inside(self, point):
        i_f_value = self.implicit_function(point)
        if i_f_value > 0:
            return 1
        if np.isclose(i_f_value, 0):
            return 0
        else:
            return -1 # initially these were False/None/True but it was annoying
        
# Normal vectors for solids must point outwards (radially away from solid centre (convex remember))
# -> points inside bounded volume will fall under a condition:
# dot product of subtraction between unique point and a random point on each plane will always be negative
# for all planes simultaneously
# as the angle will be greater than pi/2 for each
class Solid:
    def __init__(self, surf_array, dummy_point=np.array([0,0,0]), complement=False):
        self.complement = complement
        self.dummy_point = dummy_point 
        # if i were to use some routine to make all plane normal vectors point radially outward from dummy_point, a point inside the solid
        self.surf_array = surf_array
    def inside(self, point):
        imp_func_values = []
        for surf in self.surf_array:
            imp_func_values.append(surf.implicit_function(point))
        condition = max(imp_func_values)
        if self.complement == True:
            condition = -1 * condition
        if condition < 0:
            return -1 #inside
        if np.isclose(condition, 0): # tolerance (and also possibly tolerance for inside/outside)
            return 0 #on surface
        return 1 #outside
    """
    def get_nearest_plane(self, point):
        distances = []
        for plane in self.plane_array:
            distances.append(plane.get_distance_from(point))
        if self.inside(point) == -1:
            return np.argmin(distances)
        current_min_index = np.argmin(distances)
        for i in range (len(self.plane_array)):
            if self.inside(point + (-1 * self.plane_array[current_min_index].normal * distances[current_min_index]) + (EPSILON * -1 * self.plane_array[current_min_index].normal)) == False:
                distances = np.delete(distances, current_min_index) 
                # This is bad because not meeting this condition doesn't mean it's not the closest plane
                # Is it only practical to think about points which have a vector (i.e trajectory) associated with them?
            else:
                return self.plane_array[current_min_index]
        return "error"
    """
    def get_shortest_distance_in_direction(self, point, vec=0): # This is basically DistanceToIn/Out
        if isinstance(vec, int):
            vec = -1 * point
        points = np.zeros(3)
        distances = []
        legal_distances = []
        for surf in self.surf_array:
            points = np.vstack((points, (surf.intersection(point, vec)))) # we use vstack in case we get multiple points from intersection()
        points = points[1:]
        #print(points)
        for i, p in enumerate(points):
            current_vector = p - point
            distances.append(magnitude_3(current_vector))
        if self.inside(point) == -1:
            return np.min(distances)
        for i in range (len(distances)):
            if self.inside(points[i]) <= 0:
                legal_distances.append(distances[i])
        if len(legal_distances) == 0:
            return np.inf
        #print(legal_distances)
        return min(legal_distances)
class CompoundSolid:
    def __init__(self, solid_array, relationship_array):
        self.solid_array = solid_array
        self.relationship_array = relationship_array
        if self.relationship_array == "auto":
            self.relationship_array = -1 * np.ones(len(solid_array))
        # column n: relationship of solid at n'th index of solid_array to compound solid
        # -1: OR (union)
        # 1: AND (intersection? just semantic)
    def implicit_function(self, point):
        i_f_array = []
        #inside takes precedent over being on the surface
        for i, s in enumerate(self.solid_array):
            current_i_f = s.inside(point)
            i_f_array.append(current_i_f)
            if current_i_f == 1 and self.relationship_array[i] == 1:
                return 1 # We are outside of an AND solid => can't be inside => stop
            if current_i_f == -1 and self.relationship_array[i] == -1:
                return -1 # We are inside of an OR solid => must be inside => stop
            """
            ### dangerous
            if current_inside == 0 and self.relationship_array[i] == -1:
                return 0 # We are on the surface of an OR solid => must be at least on surface => stop?
            ### This isn't exactly accurate because being on the surface of a U subsolid could also coincide with being inside another subsolid
            ### in which case the output would be ambiguous
            """
        return min(i_f_array)
    def inside(self, point):
        return self.implicit_function(point)
    def get_shortest_distance_in_direction(self, point):
        dists = []
        for i, s in enumerate(self.solid_array):
            
            dists.append(s.get_shortest_distance_in_direction(point))
        return min(dists)

D = 1    
def plot_cube_lines(axes):
    axes.plot((-1 * D, D), ((-1 * D), (-1 * D)), "b-", ms=2)
    axes.plot((-1 * D, D), ((D), (D)), "b-", ms=2)
    axes.plot((-1 * D, -1 * D), ((-1 * D), (D)), "b-", ms=2)
    axes.plot((D, D), ((-1 * D), (D)), "b-", ms=2)
    return
def plot_cube_2_lines(axes):
    axes.plot((1, 3), ((1), (1)), "b-", ms=2)
    axes.plot((1, 3), ((3), (3)), "b-", ms=2)
    axes.plot((1, 1), ((1), (3)), "b-", ms=2)
    axes.plot((3, 3), ((1), (3)), "b-", ms=2)
    return
def set_lims(axes, mult=2):
    axes.set_xlim(-mult * D,mult * D)
    axes.set_ylim(-mult * D,mult * D)
    
# define planes
planes = [Plane(np.array([1,0,0]), D),\
          Plane(np.array([-1,0,0]), D),\
          Plane(np.array([0,1,0]), D),\
          Plane(np.array([0,-1,0]), D),\
          Plane(np.array([0,0,1]), D),\
          Plane(np.array([0,0,-1]), D)]
cube = Solid(planes, [0,0,0])
planes_2 = [Plane(np.array([1,0,0]), 3),\
          Plane(np.array([-1,0,0]), -1),\
          Plane(np.array([0,1,0]), 3),\
          Plane(np.array([0,-1,0]), -1),\
          Plane(np.array([0,0,1]), D),\
          Plane(np.array([0,0,-1]), D)]
cube_2 = Solid(planes_2, [2,2,0])

infinite_cylinder = InfiniteCylinder(1, np.array([np.sqrt(2),np.sqrt(2),0]), np.array([-0.5,0,0]))
quadric_sphere = Quadric()
quadric_rugby_ball = Quadric()
quadric_rugby_ball.make_rugby_ball()
cap_1 = Plane(np.array([np.sqrt(2),np.sqrt(2),0]), np.sqrt(2))
cap_2 = Plane(np.array([-1 * np.sqrt(2),-1 * np.sqrt(2),0]), np.sqrt(2))
#infinite_cylinder_solid = Solid([infinite_cylinder])
infinite_cylinder_solid = Solid([infinite_cylinder, cap_1, cap_2])
quadric_sphere.translate(np.array([1,1,0]))
#quadric_rugby_ball.translate(np.array([-1,0.25,0]))
cs = 1/np.sqrt(2)
rotation = np.array([[cs,-1*cs,0],[cs,cs,0],[0,0,1]])
quadric_rugby_ball.rotate_matrix(rotation)
quadric_rugby_ball.translate(np.array([0.4,-0.4,0]))
qrb_solid = Solid([quadric_rugby_ball])
test_solid = qrb_solid

# inside test
space_size = 5000

cube_12 = CompoundSolid([cube, cube_2], "auto")

test_z = 0
test_space_x = np.random.uniform(-2, 2, space_size)
test_space_y = np.random.uniform(-2, 2, space_size)
test_space_z = np.ones(space_size) * test_z
test_space = np.vstack((test_space_x, test_space_y, test_space_z))

inside_test = np.zeros(test_space.shape[1])

for i in range (test_space.shape[1]):
    if test_solid.inside(test_space[:,i]) == -1:
        inside_test[i] = -1
    elif test_solid.inside(test_space[:,i]) == 1:
        inside_test[i] = 1
    else:
        inside_test[i] = 0
fig, axes_xy = plt.subplots(1, 1, figsize=(6,6))
axes_xy.set_title(f"xy inside test (z={test_z})")
axes_xy.set_xlabel("x")
axes_xy.set_ylabel("y")
set_lims(axes_xy)
for i in range (test_space.shape[1]):
    if inside_test[i] == -1:
        axes_xy.plot(test_space[:,i][0], test_space[:,i][1], "go", ms=3)
    elif inside_test[i] == 0:
        axes_xy.plot(test_space[:,i][0], test_space[:,i][1], "bo", ms=3)
    elif inside_test[i] == 1:
        axes_xy.plot(test_space[:,i][0], test_space[:,i][1], "ro", ms=3)
#plot_cube_lines(axes_xy)
#plot_cube_2_lines(axes_xy)
axes_xy.grid()

##############


#colour contour plot or something like that
# distance test: short

##############

# distance test: long


test_space_size_2 = 128
test_space_x = np.linspace(-2, 2, test_space_size_2)
test_space_y = np.linspace(-2, 2, test_space_size_2)
test_space_z = np.ones(test_space_size_2) * test_z

mesh_x = np.zeros((test_space_size_2,test_space_size_2))
mesh_y = np.zeros((test_space_size_2,test_space_size_2))
mesh_z = np.zeros((test_space_size_2,test_space_size_2))
dummy_z = 0
for i_y, y in enumerate(test_space_y):
    for i_x, x in enumerate(test_space_x):
        mesh_x[i_y][i_x] = x
        mesh_y[i_y][i_x] = y
        mesh_z[i_y][i_x] = np.abs(test_solid.get_shortest_distance_in_direction(np.array([x, y, dummy_z])))
        #plane_buffer = cube.get_nearest_plane(np.array([x,y,0]))
fig, ax = plt.subplots(1,1, figsize=(6,6))
ax.set_title(f"directional (toward origin) distance test (z = {test_z})")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.contourf(mesh_x, mesh_y, mesh_z)
##############
                