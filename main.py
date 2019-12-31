#!/bin/python3.8
# -*- coding: utf-8 -*-

import enum
from typing import List, Union, Tuple, Dict, Set
import itertools
import numpy as np


class Vector(object):

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __add__(self, other: Union['Vector', Tuple[float, float, float], list]):
        res = Vector(self.x, self.y, self.z)
        if isinstance(other, Vector):
            nx, ny, nz = other.x, other.y, other.z
        else:
            nx, ny, nz = other
        res.x += nx
        res.y += ny
        res.z += nz
        return res

    def __mul__(self, other: float):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __sub__(self, other):
        return self + other*(-1)

    def __eq__(self, other: 'Vector'):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __ne__(self, other: 'Vector'):
        return (self.x, self.y, self.z) != (other.x, other.y, other.z)

    def __str__(self):
        # return "Point:({x}, {y}, {z})".format(**self.__dict__)
        return "<{0.x}, {0.y}, {0.z}>".format(self)

    def __repr__(self):
        return "<{0.x}, {0.y}, {0.z}>".format(self)

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def midpoint(self, other: 'Vector'):
        return tuple(i/2 for i in self + other)


class PieceType(enum.Enum):
    CENTER = 1
    EDGE = 2
    CORNER = 3

    def __str__(self):
        return self.name


Color = int
Colors = Tuple[Color, Color, Color, Color, Color, Color]


class Piece(object):
    def __init__(self, _type: PieceType, colors: Colors, position: Vector, orientation: Tuple[Vector, Vector]):
        self.type = _type
        self.colors = colors
        self.position = position
        self.orientation = orientation

    def __repr__(self):
        return "{type} piece at {position} with orientations {orientation}".format(**self.__dict__)


class Cube(object):
    def __init__(self, size):
        self.size = size

        assert size != 1, "1x1 cube is not supported yet!"

        # corners
        orient_vec = (Vector(1, 0, 0), Vector(0, 1, 0))
        color_list = (1, 2, 3, 4, 5, 6)

        dist = (size - 1) / 2.
        _corners = list(itertools.product(*[[-dist, dist]] * 3))
        self.corners = []
        for corner in _corners:
            position_vec = Vector(*corner)
            self.corners.append(Piece(PieceType.CORNER, color_list,
                                      position_vec, orient_vec))

        # edges
        _edge_groups = list(itertools.product(*([[-dist, dist]] * 2)))
        _edges = []

        offsets = np.linspace((3-size)/2, (size-3)/2, size-2)
        for c1, c2 in _edge_groups:
            _edges.extend((edge_offset, c1, c2) for edge_offset in offsets)
            _edges.extend((c1, edge_offset, c2) for edge_offset in offsets)
            _edges.extend((c1, c2, edge_offset) for edge_offset in offsets)

        self.edges = []
        for edge in _edges:
            position_vec = Vector(*edge)
            self.edges.append(Piece(PieceType.EDGE, color_list,
                                    position_vec, orient_vec))

        # centers
        _center_groups = [-dist, dist]
        _centers = []

        center_offsets_x, center_offsets_y = np.meshgrid(offsets, offsets)
        center_offsets = list(zip(center_offsets_x.flatten(), center_offsets_y.flatten()))

        for c in _center_groups:
            _centers.extend((c, center_offset[0], center_offset[1]) for center_offset in center_offsets)
            _centers.extend((center_offset[0], c, center_offset[1]) for center_offset in center_offsets)
            _centers.extend((center_offset[0], center_offset[1], c) for center_offset in center_offsets)

        self.centers = []
        for center in _centers:
            position_vec = Vector(*center)
            self.centers.append(Piece(PieceType.CENTER, color_list,
                                      position_vec, orient_vec))


if __name__ == "__main__":
    cube = Cube(3)
    print(cube.corners, sep="\n")
    print(cube.edges, sep="\n")
    print(*cube.centers, sep="\n")
