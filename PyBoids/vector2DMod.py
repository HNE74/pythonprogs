#############################################################
# vector2DMod.py
# Implements a 2 dimensional vector and some vector ops.
# by Heiko Nolte / August 2010
# distributed: GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#############################################################

from math import *

class Vector2D():

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    # Adds provided vector to current vector
    def addVec(self, vec):
        result = Vector2D(self.x, self.y)
        result.x = result.x + vec.x
        result.y = result.y + vec.y
        return result

    # Subtracts provided vector from current vector
    def subVec(self, vec):
        result = Vector2D(self.x, self.y)
        result.x = result.x - vec.x
        result.y = result.y - vec.y
        return result

    # Divides vector by scalar
    def divScalar(self, scalar):
        result = Vector2D(self.x, self.y)
        result.x = result.x / scalar
        result.y = result.y / scalar
        return result

    # Multiplies vector by scalar
    def mulScalar(self, scalar):
        result = Vector2D(self.x, self.y)
        result.x = result.x * scalar
        result.y = result.y * scalar
        return result

    # Calculates vector magnitude
    def mag(self):
        result = sqrt(pow(self.x, 2) + pow(self.y, 2))
        return result

