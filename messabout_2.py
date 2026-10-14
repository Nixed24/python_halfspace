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

def magnitude_3(vector):
    return np.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
def to_unit_vector(vector):
    if vector[0] == 0 and vector[1] == 0 and vector[2] == 0:
        return vector
    return vector / magnitude_3(vector)
class Surface:
    def __init__(self):
        return 0
    def implicit_function(self, point):
        return 0
    def intersection(self, point, vec):
        return 0
    def inside(self, point):
        return 0
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
    def __init__(self, surf_array, dummy_point, complement=False):
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
# inside test
space_size = 500

cube_12 = CompoundSolid([cube, cube_2], "auto")

test_space_x = np.random.uniform(-2, 2, space_size)
test_space_y = np.random.uniform(-2, 2, space_size)
test_space_z = np.zeros(space_size)
test_space = np.vstack((test_space_x, test_space_y, test_space_z))

inside_test = np.zeros(test_space.shape[1])

for i in range (test_space.shape[1]):
    if cube_12.inside(test_space[:,i]) == -1:
        inside_test[i] = -1
    elif cube_12.inside(test_space[:,i]) == 1:
        inside_test[i] = 1
    else:
        inside_test[i] = 0
fig, axes_xy = plt.subplots(1, 1, figsize=(6,6))
axes_xy.set_title("xy inside test")
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
plot_cube_lines(axes_xy)
plot_cube_2_lines(axes_xy)
axes_xy.grid()

##############


#colour contour plot or something like that
# distance test: short

##############

# distance test: long


test_space_x = np.linspace(-1.5, 4.5, 128)
test_space_y = np.linspace(-1.5, 4.5, 128)
test_space_z = np.zeros(128)

mesh_x = np.zeros((128,128))
mesh_y = np.zeros((128,128))
mesh_z = np.zeros((128,128))
dummy_z = 0
for i_y, y in enumerate(test_space_y):
    for i_x, x in enumerate(test_space_x):
        mesh_x[i_y][i_x] = x
        mesh_y[i_y][i_x] = y
        mesh_z[i_y][i_x] = np.abs(cube_12.get_shortest_distance_in_direction(np.array([x, y, dummy_z])))
        #plane_buffer = cube.get_nearest_plane(np.array([x,y,0]))
fig, ax = plt.subplots(1,1, figsize=(6,6))
ax.set_title("directional distance test")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.contourf(mesh_x, mesh_y, mesh_z)

##############
                