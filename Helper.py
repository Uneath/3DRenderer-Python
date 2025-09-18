import math
from copy import *
from typing import Union
import numpy

class Vector3D:
    I: 'Vector3D'
    def __init__(self, x:float =0.0, y:float=0.0, z:float =0.0):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, index:int) -> float:
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        if index == 2:
            return self.z
        raise IndexError

    def __setitem__(self, index:int, value:float):
        if index == 0:
            self.x = value
            return
        if index == 1:
            self.y = value
            return
        if index == 2:
            self.z = value
            return
        raise IndexError


    def ToColor(self) -> str:
        clone = Vector3D()
        clone.x = numpy.clip(self.x, 0, 1)
        clone.y = numpy.clip(self.y, 0, 1)
        clone.z = numpy.clip(self.z, 0, 1)
        return "#"+"0x{:02X}".format(int(clone.x*255))[2:] + "0x{:02X}".format(int(clone.y*255))[2:] +"0x{:02X}".format(int(clone.z*255))[2:]

    def ToRGBA(self) -> tuple[int, int, int, int]:
        return numpy.clip(int(self.x*255), 0, 255), numpy.clip(int(255*self.y), 0, 255), numpy.clip(int(255*self.z), 0, 255),255

    def ToRGB(self) -> tuple[int, int, int]:
        return numpy.clip(int(self.x * 255), 0, 255), numpy.clip(int(255 * self.y), 0, 255), numpy.clip(int(255 * self.z), 0,
                                                                                                 255)

    def Unit(self):
        return self*(1/abs(self))

    def abs(self) -> float:
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def __abs__(self) -> float:return self.abs()

    def __add__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __neg__(self) -> 'Vector3D':
        return Vector3D(-self.x, -self.y, -self.z)

    def __sub__(self, other: 'Vector3D') -> 'Vector3D':
        return self + (-other)



    #Scalar product
    def __mul__(self: 'Vector3D', other: float|int) -> 'Vector3D':
        return Vector3D(self.x * other, self.y * other, self.z * other)

    #Dot product
    def Dot(self: 'Vector3D', other:'Vector3D') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def Cross(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.y * other.z - self.z * other.y,
                        self.z * other.x - self.x * other.z,
                        self.x * other.y - self.y * other.x)

    def PowElements(self,exponent: float) -> 'Vector3D':
        return Vector3D(self.x**exponent, self.y**exponent, self.z**exponent)

    def __pow__(self, exponent: int):
        vec: Union['Vector3D',float] = copy(self)
        for i in range(1,exponent):
            if isinstance(vec, Vector3D):
                vec = vec.Dot(self)
            else:
                vec = self*vec
        return vec

Vector3D.I = Vector3D(1,1,1)

class Row:
    def __init__(self, components: Vector3D, total: float):
        self.components:Vector3D = components
        self.total:float = total

    def __getitem__(self, index:int) -> float:
        return self.components[index]

    def __setitem__(self, index:int, value:float):
        self.components[index] = value

    def __sub__(self, other: 'Row') -> None:
        self.components -= other.components
        self.total -= other.total

    def __mul__(self, other: float) -> 'Row':
        return Row(self.components * other, self.total*other)

    def ComponentRemoval(self, remover: 'Row', index: int):
        amount: float = self.components[index]/remover[index]
        self - remover*amount


class Matrix3D:
    def __init__(self, elements: tuple[float, float, float, float, float, float, float, float, float] =
    (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)):
        self._elements: list[float] = list(elements)


    def __setitem__(self, index: int, value: float):
        self._elements[index] = value

    def __getitem__(self, index: int) -> float:
        return self._elements[index]

    def VecMult(self, vector: Vector3D) -> Vector3D:
        returnVector: Vector3D = Vector3D()
        for ri in range(3):  # return index
            for ii in range(3):  # input index
                returnVector[ri] += self[ri * 3 + ii] * vector[ii]
        return returnVector

    def MatMult(self, matrix: 'Matrix3D') -> 'Matrix3D':
        returnMatrix = Matrix3D()
        for kol in range(3):
            for row in range(3):
                returnMatrix[kol + 3 * row] = (self[row * 3 + 0] * matrix[kol + 0] +
                                               self[row * 3 + 1] * matrix[kol + 3] +
                                               self[row * 3 + 2] * matrix[kol + 6])
        return returnMatrix

class HitMark:
    def __init__(self, color:Vector3D, distance:float, opacity: float = 1, normal:Vector3D = Vector3D(1)):
        self.color: Vector3D = color
        self.distance: float = distance
        self.opacity: float = opacity
        self.normal: Vector3D = normal


    def ToColor(self) -> str:
        return self.color.ToColor()

    def __str__(self):
        return f"(color: {self.color}, dist: {self.distance}, op: {self.opacity})"

class Fov:
    def __init__(self, fovWidth: float = 1.0, fovHeight: float=0.75):
        self.fovWidth = fovWidth
        self.fovHeight = fovHeight

    def __str__(self)->str:
        return f"({self.fovWidth}, {self.fovHeight})"


class PhysicalTilt:
    def __init__(self,tiltX: float = 0.0, tiltY: float = 0.0,tiltZ: float = 0.0):
        self._Matrix = Matrix3D()
        self._InverseMatrix = Matrix3D()
        self.tiltX: float = tiltX
        self.tiltY: float = tiltY
        self.tiltZ: float = tiltZ
        self._CalcRotMat()

    def RotateVector(self, vector:Vector3D) -> Vector3D:
        return self._Matrix.VecMult(vector)

    def InverseRotateVector(self, vector:Vector3D) -> Vector3D:
        return self._InverseMatrix.VecMult(vector)

    def _CalcRotMat(self) -> None:
        cx: float = math.cos(self.tiltX)
        cy: float = math.cos(self.tiltY)
        cz: float = math.cos(self.tiltZ)
        sx: float = math.sin(self.tiltX)
        sy: float = math.sin(self.tiltY)
        sz: float = math.sin(self.tiltZ)

        rotMatX: Matrix3D = Matrix3D((1,  0,  0,
                                      0, cx, sx,
                                      0,-sx, cx))

        rotMatY: Matrix3D = Matrix3D(( cy, 0,-sy,
                                        0, 1,  0,
                                       sy, 0, cy))

        rotMatZ: Matrix3D = Matrix3D(( cz, sz, 0,
                                      -sz, cz, 0,
                                        0,  0, 1))
        self._Matrix = rotMatZ.MatMult(rotMatY.MatMult(rotMatX))

        rotMatX = Matrix3D((1, 0, 0,
                                      0, cx, -sx,
                                      0, sx, cx))

        rotMatY = Matrix3D((cy, 0, sy,
                                      0, 1, 0,
                                      -sy, 0, cy))

        rotMatZ = Matrix3D((cz, -sz, 0,
                                      sz, cz, 0,
                                      0, 0, 1))

        self._InverseMatrix = rotMatX.MatMult(rotMatY.MatMult(rotMatZ))

    def Rot(self,tiltX: float = 0, tiltY: float = 0, tiltZ: float = 0) -> 'PhysicalTilt':
        self.tiltX = (self.tiltX + tiltX)%(2*math.pi)
        self.tiltY = (self.tiltY + tiltY)%(2*math.pi)
        self.tiltZ = (self.tiltZ + tiltZ)%(2*math.pi)

        self._CalcRotMat()
        return self

    def __str__(self)->str:
        return str(self.__repr__()) + f"\ttiltX: {self.tiltX}, \ttiltY: {self.tiltY}, \ttiltZ: {self.tiltZ}"

class CameraTilt:
    def __init__(self, tiltX: float = 0, tiltY: float =0 ):
        self.rotMat: Matrix3D = Matrix3D()
        self.inverseRotMat: Matrix3D = Matrix3D()
        self.tiltX = 0
        self.tiltY = 0
        self.RotX(tiltX)
        self.RotY(tiltY)

    #        | 1  0  0 |           | c 0 s |
    # xRot = | 0  c  s |    yRot = | 0 1 0 |
    #        | 0 -s  c |           |-s 0 c |
    #        |    cy     0    sy|
    # prod = | -sxsy    cx  sxcy|
    #        | -cxsy   -sx  cxcy|
    def _CalcRotMat(self) -> None:
        #Y*X
        cx: float = math.cos(self.tiltX)
        cy: float = math.cos(self.tiltY)
        sx: float = math.sin(self.tiltX)
        sy: float = math.sin(self.tiltY)
        self.rotMat = Matrix3D((   cy, -sx*sy,  cx*sy,
                                  0.0,     cx,    sx,
                                  -sy,  -sx*cy,  cx*cy))
        self.inverseRotMat = Matrix3D((    cy, -sx*sy,  -cx*sy,
                                         0.0,     cx,   - sx,
                                          sy,  sx*cy,  cx*cy))

#All of my attempts to do linear algebra

# Works but I don't like that I do more than I need to: Y*X
#       xRot: Matrix3D = Matrix3D((1,0,0,
#                                  0,cx,sx,
#                                  0,-sx,cx))
#       yRot: Matrix3D = Matrix3D(( cy, 0, sy,
#                                    0, 1,  0,
#                                   -sy,0, cy))
#       self.rotMat = yRot.MatMult(xRot)


#Don't remember exactly what this one did, I think it rotates Y first, and it uses a bunch of calls to sin and cos, so I don't like it X*Y
#       self._rotMat = Matrix3D((  math.cos(self.tiltY),                         0.0,                     math.sin(self.tiltY),
#                                 -math.sin(self.tiltX)*math.sin(self.tiltY),    math.cos(self.tiltX),  math.sin(self.tiltX)*math.cos(self.tiltY),
#                                 -math.cos(self.tiltX)*math.sin(self.tiltY),   -math.sin(self.tiltX),  math.cos(self.tiltX)*math.cos(self.tiltY)))

#Inverse X rotation (?) Y*X
#       self.rotMat = Matrix3D((   cy, -sx*sy,  cx*sy,
#                                 0.0,     cx,    -sx,
#                                 -sy,  sx*cy,  cx*cy))


#Inverse Y rotation (?)  Y*X
#       self.rotMat = Matrix3D((   cy, -sx*sy, -cx*sy,
#                                 0.0,     cx,    -sx,
#                                  sy,  sx*cy,  cx*cy))

#
#       self.rotMat = Matrix3D((   cy,   0,   sy,
#                               -sx*sy,  cx, sx*cy,
#                               -cx*sy, -sx, cx*cy))


    def RotX(self, angle: float) -> None:
        self.tiltX = numpy.clip(self.tiltX + angle, -math.pi/2, math.pi/2)
        self._CalcRotMat()

    def RotY(self, angle: float) -> None:
        self.tiltY = (self.tiltY + angle)%(2*math.pi)
        self._CalcRotMat()

    def __str__(self)->str:
        return f"({self.tiltX}, {self.tiltY})"


class GaussMatrix:
    #instance: 'GaussMatrix'
    def __init__(self,vector1: Vector3D,vector2:Vector3D, vector3: Vector3D, values: Vector3D) -> None:
        self.rows: list[Row] = [Row(Vector3D(), 0),Row(Vector3D(), 0),Row(Vector3D(), 0)]
        self.LoadProblem(vector1, vector2,vector3, values)

    def __getitem__(self, index:int) -> Row:
        return self.rows[index]

    def __setitem__(self, index: int, value:Row):
        self.rows[index] = value

    
    def LoadProblem(self, vector1: Vector3D,vector2:Vector3D, vector3: Vector3D, values: Vector3D):
        for i in range(3):
            self[i].components[0] = vector1[i]
            self[i].components[1] = vector2[i]
            self[i].components[2] = vector3[i]
            self[i].total = values[i]

    def Subtracts(self,index:int) -> None:
        for i in range(3):
            if i == index:
                continue
            self[i].ComponentRemoval(self[index], index)

    def Check(self,index:int) -> bool:
        if self[index][index] == 0: return True
        self[index] *= (1/self[index][index])
        return False

    def SolveGaussMatrix(self) -> Vector3D|None:
        if self.Check(0): return None
        self.Subtracts(0)

        if self.Check(1): return None
        self.Subtracts(1)

        if self.Check(2): return None
        self.Subtracts(2)

        if self.Check(0): return None
        if self.Check(1): return None

        return Vector3D(self[0].total, self[1].total, self[2].total)
