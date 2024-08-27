from planisuss_constants import *

class Species:
    def __init__(self):
        pass

class Animal(Species):
    def __init__(self, coordinates: tuple):
        self.coords = coordinates
        pass

class Vegetob():

    """
    Our cute plants, growing each day... unable to move...
    """
    
    def __init__(self, density = 0):
        super().__init__()
        self.density = density

    def grow(self, times:int = 1):
        """Grow the Vegetob"""
        if not isinstance(times, int):
            raise ValueError("times must be an integer")
        for _ in range(times):
            if self.density + GROWING <= MAX_GROWTH:
                self.density += GROWING
            else:
                self.density = MAX_GROWTH

    def reduce(self, amount:int = 5):
        """Apply Grazing Effect"""
        if not isinstance(amount, int):
            raise ValueError("amount must be an integer")
        if self.density - amount >= 0:
            self.density -= amount
        else:
            self.density = 0

    def __repr__(self):
        return "Vegetob"

class Erbast(Animal):

    def __init__(self):
        super().__init__(self)

    def __repr__(self):
        return "Erbast"

class Carvis(Animal):

    def __init__(self):
        super().__init__(self)

    def __repr__(self):
        return "Carviz"

class SocialGroup:
    """
    Holds knowledge about the environment
    """

    def __init__(self, components):
        self.components = components

    def getComponents(self):
        return self.components

class Herd(SocialGroup):

    def __init__(self, components):
        super().__init__(self, components)
        pass

class Pride(SocialGroup):

    def __init__(self, components):
        super().__init__(self, components)
        pass