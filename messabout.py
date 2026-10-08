#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 14:08:05 2026

@author: deck
"""

EPSILON = 10 ** -8

import numpy as np
def magnitude_3(vector):
    return vector[0]**2 + vector[1]**2 + vector[2]**2
def to_unit_vector(vector):
    return vector / magnitude_3(vector)
class Plane:
    def __init__(self, normal, distance):
        self.normal = normal
        self.distance = distance
    def get_dummy_point(self):
        try:
            return np.array([(self.distance/self.normal[0]), 0,0])
        except ZeroDivisionError:
            try:
                return np.array([0, self.distance/self.normal[1],0])
            except ZeroDivisionError:
                return np.array([0, 0, self.distance/self.normal[2]])
        # then crash
        return
    def get_displacement_from(self, point):
        return (magnitude_3(point) * np.dot(self.normal, point)) - self.distance
    def get_distance_from(self, point):
        return np.abs(self.get_displacement_from(self, point))
# Normal vectors for solids must point outwards (radially away from solid centre (convex remember))
# -> points inside bounded volume will fall under a condition:
# dot product of subtraction between unique point and a random point on each plane will always be negative
# for all planes simultaneously
# as the angle will be greater than pi/2 for each
class Solid:
    def __init__(self, plane_array):
        self.plane_array = plane_array
    def inside(self, point):
        for plane in self.plane_array:
            test_point = plane.get_dummy_point()
            if np.dot((point - test_point), plane.normal) > 0:
                return False
        return True
    def get_nearest_plane(self, point):
        distances = []
        for plane in self.plane_array:
            distances.append(plane.get_distance_from(point))
        if self.inside(point) == True:
            return np.argmin(distances)
        current_min_index = np.argmin(distances)
        for i in range (len(self.plane_array)):
            if self.inside(point + (-1 * self.plane_array[current_min_index].normal * distances[current_min_index]) + EPSILON) == False:
                distances = np.delete(distances, current_min_index)
            else:
                return current_min_index
        return

# define planes
D = 1
planes = [Plane([1,0,0], D),Plane([-1,0,0], D),Plane([0,1,0], D),Plane([0,-1,0], D),Plane([0,0,1], D),Plane([0,0,-1], D)]
cube = Solid(planes)

test_space_x = np.linspace(-1.9, -1.1, 100)
test_space_y = np.linspace(-1.99, -1.1, 100)
test_space_z = np.linspace(-1.99, -1.1, 100)
#test_mesh = np.meshgrid(test_space_x, test_space_y, test_space_z)
inside_test = cube.inside([0,0,0])

for i in range (100):
    for j in range(100):
        for k in range (100):
            if cube.inside([test_space_x[i],test_space_y[j],test_space_z[k]]) == True:
                print("he ATE them")
print("donesies")
    