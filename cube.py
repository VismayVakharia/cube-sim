#!/bin/python3.8
# -*- coding: utf-8 -*-

import enum
from typing import Union, Tuple
import itertools
import numpy as np
import quaternion

Quaternion = quaternion.quaternion


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

    def __mul__(self, other: Union[float, int]):
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

    def as_array(self):
        return np.array([self.x, self.y, self.z])


class PieceType(enum.Enum):
    CENTER = 1
    EDGE = 2
    CORNER = 3

    def __str__(self):
        return self.name


Color = int
Colors = Tuple[Color, Color, Color, Color, Color, Color]


class Piece(object):
    def __init__(self, _type: PieceType, colors: Colors, position: Vector, orientation: Quaternion):
        self.type = _type
        self.colors = colors
        self.position = position
        self.orientation = orientation

    def __repr__(self):
        return "{type} piece at {position} with {orientation}".format(**self.__dict__)


class Cube(object):
    def __init__(self, size):
        self.size = size

        assert size != 1, "1x1 cube is not supported yet!"

        # corners
        orient_vec = lambda: Quaternion(1, 0, 0, 0)
        color_list = (1, 2, 3, 4, 5, 6)

        dist = (size - 1) / 2.
        _corners = list(itertools.product(*[[-dist, dist]] * 3))
        self.corners = []
        for corner in _corners:
            position_vec = Vector(*corner)
            self.corners.append(Piece(PieceType.CORNER, color_list,
                                      position_vec, orient_vec()))

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
                                    position_vec, orient_vec()))

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
                                      position_vec, orient_vec()))

        self.pieces = self.centers + self.corners + self.edges

    def _rotate(self, axis: Vector, multiplier: int = -1):
        axis = axis.as_array()
        rotation_vec = axis * multiplier * (np.pi/2)
        rotation_quat = quaternion.from_rotation_vector(rotation_vec)

        for piece in self.pieces:
            pos = piece.position.as_array()
            if np.dot(pos, axis) > 0.5:  # TODO: generalize for nxn cube
                piece.orientation = rotation_quat * piece.orientation
                piece.position = Vector(*quaternion.rotate_vectors(rotation_quat, pos))

    def rotate(self, move: str):
        multiplier = -1
        if len(move) == 2:
            if move[1] == "'":
                multiplier = 1
            else:
                multiplier = 2
            move = move[0]
        opposite_moves = {"L": "R", "B": "F", "D": "U"}
        move_directions = {"R": Vector(1, 0, 0),
                           "U": Vector(0, 1, 0),
                           "F": Vector(0, 0, 1)}
        flip_axis = 1
        if move in opposite_moves:
            move = opposite_moves[move]
            flip_axis = -1
        self._rotate(move_directions[move] * flip_axis, multiplier)


if __name__ == "__main__":
    cube = Cube(3)
    print(*cube.corners, sep="\n")
    print(*cube.edges, sep="\n")
    print(*cube.centers, sep="\n")
    cube._rotate(Vector(1, 0, 0), 1)
    cube.rotate("R")
    print("Rotated Cube")
    print(*cube.corners, sep="\n")
    print(*cube.edges, sep="\n")
    print(*cube.centers, sep="\n")
