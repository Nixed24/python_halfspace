#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 14:08:05 2026

@author: deck
"""

EPSILON = 10 ** -8

import numpy as np
from matplotlib import pyplot as plt

def magnitude_3(vector):
    return np.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
def to_unit_vector(vector):
    if vector[0] == 0 and vector[1] == 0 and vector[2] == 0:
        return vector
    return vector / magnitude_3(vector)
class Plane:
    def get_dummy_point(self):
        if self.normal[0] != 0:
            return np.array([(self.distance/self.normal[0]), 0,0])
        elif self.normal[1] != 0:
            return np.array([0, self.distance/self.normal[1],0])
        else:
            return np.array([0, 0, self.distance/self.normal[2]])
        # then crash
        # whoops forgot numpy doesn't crash if there's a div by zero
        return np.array([np.nan, np.nan, np.nan])
    def __init__(self, normal, distance):
        self.normal = normal
        self.distance = distance
        self.dummy_point = self.get_dummy_point()
    def get_half_space_value(self, point):
        return np.dot((point - self.dummy_point), self.normal)
    def get_displacement_from(self, point):
        return (magnitude_3(point) * np.dot(self.normal, to_unit_vector(point))) - self.distance
    def get_distance_from(self, point):
        return np.abs(self.get_displacement_from(point))
    def get_displacement_in_direction(self, point, vec):
        cos_theta = np.dot(self.normal, vec)
        if cos_theta == 0:
            return np.nan
        perp_disp = self.get_displacement_from(point)
        vec_disp = perp_disp / cos_theta
        return vec_disp * np.sign(self.get_half_space_value(point))
# Normal vectors for solids must point outwards (radially away from solid centre (convex remember))
# -> points inside bounded volume will fall under a condition:
# dot product of subtraction between unique point and a random point on each plane will always be negative
# for all planes simultaneously
# as the angle will be greater than pi/2 for each
class Solid:
    def __init__(self, plane_array, dummy_point, complement=False):
        self.complement = complement
        self.dummy_point = dummy_point 
        # if i were to use some routine to make all plane normal vectors point radially outward from dummy_point, a point inside the solid
        self.plane_array = plane_array
    def inside(self, point):
        half_space_evaluation_array = []
        for plane in self.plane_array:
            half_space_evaluation_array.append(plane.get_half_space_value(point))
        condition = max(half_space_evaluation_array)
        if self.complement == True:
            condition = -1 * condition
        if condition < 0:
            return -1 #inside
        if condition == 0: # tolerance (and also possibly tolerance for inside/outside)
            return 0 #on surface
        return 1 #outside
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
class CompoundSolid:
    def __init__(self, solid_array, relationship_array):
        self.solid_array = solid_array
        self.relationship_array = relationship_array
        if self.relationship_array == "auto":
            self.relationship_array = np.zeros(len(solid_array))
        # column n: relationship of solid at n'th index of solid_array to compound solid
        # -1: OR (union)
        # 1: AND (intersection? just semantic)
    def inside(self, point):
        inside_array = []
        for i, s in enumerate(self.solid_array):
            current_inside = s.inside(point)
            inside_array.append(current_inside)
            if current_inside == 1 and self.relationship_array[i] == 1:
                return 1 # We are outside of an AND solid => can't be inside => stop
            if current_inside == -1 and self.relationship_array[i] == -1:
                return -1 # We are inside of an OR solid => must be inside => stop
            """
            ### dangerous
            if current_inside == 0 and self.relationship_array[i] == -1:
                return 0 # We are on the surface of an OR solid => must be at least on surface => stop?
            ### This isn't exactly accurate because being on the surface of a U subsolid could also coincide with being inside another subsolid
            ### in which case the output would be ambiguous
            """
        return min(inside_array)

D = 1    

def plot_cube_lines(axes):
    axes.plot((-1 * D, D), ((-1 * D), (-1 * D)), "y-", ms=2)
    axes.plot((-1 * D, D), ((D), (D)), "y-", ms=2)
    axes.plot((-1 * D, -1 * D), ((-1 * D), (D)), "y-", ms=2)
    axes.plot((D, D), ((-1 * D), (D)), "y-", ms=2)
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

# inside test

test_space_x = np.random.uniform(-2, 2, 1)
test_space_y = np.random.uniform(-2, 2, 1)
test_space_z = np.random.uniform(-2, 2, 1)

test_space = np.vstack((test_space_x, test_space_y, test_space_z))

inside_points = []
surface_points = []
outside_points = []

inside_test = np.zeros(test_space.shape[1])

for i in range (test_space.shape[1]):
    if cube.inside(test_space[:,i]) == -1:
        inside_test[i] = -1
    elif cube.inside(test_space[:,i]) == 1:
        inside_test[i] = 1
    else:
        inside_test[i] = 0
fig, (axes_xy, axes_xz, axes_yz) = plt.subplots(1, 3, figsize=(18,6))
axes_xy.set_title("xy")
set_lims(axes_xy)
axes_xz.set_title("xz")
set_lims(axes_xz)
axes_yz.set_title("yz")
set_lims(axes_yz)
for i in range (test_space.shape[1]):
    if inside_test[i] == -1:
        axes_xy.plot(test_space[:,i][0], test_space[:,i][1], "go", ms=3)
        axes_xz.plot(test_space[:,i][0], test_space[:,i][2], "go", ms=3)
        axes_yz.plot(test_space[:,i][1], test_space[:,i][2], "go", ms=3)
    elif inside_test[i] == 0:
        axes_xy.plot(test_space[:,i][0], test_space[:,i][1], "bo", ms=3)
        axes_xz.plot(test_space[:,i][0], test_space[:,i][2], "bo", ms=3)
        axes_yz.plot(test_space[:,i,1], test_space[:,i][2], "bo", ms=3)
    elif inside_test[i] == 1:
        axes_xy.plot(test_space[:,i][0], test_space[:,i][1], "ro", ms=3)
        axes_xz.plot(test_space[:,i][0], test_space[:,i][2], "ro", ms=3)
        axes_yz.plot(test_space[:,i][1], test_space[:,i][2], "ro", ms=3)
plot_cube_lines(axes_xy)
plot_cube_lines(axes_xz)
plot_cube_lines(axes_yz)
axes_xy.grid()
axes_xz.grid()
axes_yz.grid()

##############


#colour contour plot or something like that
# distance test: short

##############

# distance test: long

test_space_x_1 = np.linspace(96, 64, 64)
test_space_x_2 = np.linspace(-96, -64, 64)
test_space_x = np.append(test_space_x_1, test_space_x_2)
test_space_y_1 = np.linspace(96, 64, 64)
test_space_y_2 = np.linspace(-96, -64, 64)
test_space_y = np.append(test_space_y_1, test_space_y_2)
test_space_z = np.zeros(128)

mesh_x = np.zeros((128,128))
mesh_y = np.zeros((128,128))
mesh_z = np.zeros((128,128))
dummy_z = 9
for i_y, y in enumerate(test_space_y):
    for i_x, x in enumerate(test_space_x):
        mesh_x[i_y][i_x] = x
        mesh_y[i_y][i_x] = y
        mesh_z[i_y][i_x] = cube.get_nearest_plane(np.array([x,y,dummy_z])).get_distance_from(np.array([x,y,dummy_z]))
        #plane_buffer = cube.get_nearest_plane(np.array([x,y,0]))


##############
                