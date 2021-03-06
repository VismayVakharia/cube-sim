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

        self.ultra_centers = [Piece(PieceType.CENTER, color_list,
                                    Vector(0, 0, 0), orient_vec())]

        self.pieces = self.ultra_centers + self.centers + self.corners + self.edges

        self.face_turns  = {"R": Vector( 1,  0,  0),
                            "U": Vector( 0,  1,  0),
                            "F": Vector( 0,  0,  1),
                            "L": Vector(-1,  0,  0),
                            "D": Vector( 0, -1,  0),
                            "B": Vector( 0,  0, -1)}
        self.slice_turns = {"M": Vector(-1,  0,  0),
                            "E": Vector( 0, -1,  0),
                            "S": Vector( 0,  0,  1)}
        self.whole_turns = {"x": Vector( 1,  0,  0),
                            "y": Vector( 0,  1,  0),
                            "z": Vector( 0,  0,  1)}
        self.double_turns = {move.lower(): vec for (move, vec) in self.face_turns.items()}

    def _rotate(self, axis: Vector, multiplier: int = -1, turn_type: str = "face"):
        axis = axis.as_array()
        rotation_vec = axis * multiplier * (np.pi/2)
        rotation_quat = quaternion.from_rotation_vector(rotation_vec)

        assert turn_type in ["face", "double", "slice", "whole"], "invalid turn type"

        for piece in self.pieces:
            pos = piece.position.as_array()
            if turn_type == "face":
                condition = np.dot(pos, axis) > 0.5
            elif turn_type == "double":
                condition = np.dot(pos, axis) > -0.5
            elif turn_type == "slice":
                condition = abs(np.dot(pos, axis)) <= 0.5
            else:  # turn_type == "whole"
                condition = True

            if condition:  # TODO: generalize for nxn cube
                piece.orientation = rotation_quat * piece.orientation
                piece.position = Vector(*quaternion.rotate_vectors(rotation_quat, pos))

    def rotate(self, move: str):
        multiplier = -1
        if 1 <= len(move) <= 2:
            if len(move) == 2:
                if move[1] == "'":
                    multiplier = 1
                elif move[1] == "2":
                    multiplier = 2
                else:
                    return False
                move = move[0]

            if move in self.face_turns:
                self._rotate(self.face_turns[move], multiplier, turn_type="face")
            elif move in self.double_turns:
                self._rotate(self.double_turns[move], multiplier, turn_type="double")
            elif move in self.slice_turns:
                self._rotate(self.slice_turns[move], multiplier, turn_type="slice")
            elif move in self.whole_turns:
                self._rotate(self.whole_turns[move], multiplier, turn_type="whole")
            else:  # invalid move
                return False
            return True
        else:
            return False


if __name__ == "__main__":
    cube = Cube(3)
    print(*cube.corners, sep="\n")
    print(*cube.edges, sep="\n")
    print(*cube.centers, sep="\n")
    cube.rotate("R")
    print("Rotated Cube")
    print(*cube.corners, sep="\n")
    print(*cube.edges, sep="\n")
    print(*cube.centers, sep="\n")
