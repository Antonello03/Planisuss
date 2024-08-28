from planisuss_constants import *
from world import *
import numpy as np

class Species:
    def __init__(self):
        pass

class Animal(Species):
    def __init__(self, coordinates: tuple, energy:int = MAX_ENERGY, lifetime:int = MAX_LIFE, age:int = 0, SocialAttitude:float = 0.5, neighborhoodDistance = NEIGHBORHOOD):
        super().__init__()
        self.coords = coordinates
        self.energy = energy
        self.lifetime = lifetime
        self.age = age
        self.socialAttitude = SocialAttitude
        self.alive = True
        self.neighborhoodDistance = neighborhoodDistance
        pass

    def ageStep(self, days:int = 1):
        """Increase the age of the animal by the specified number of days"""
        if self.alive:
            if not isinstance(days, int):
                raise ValueError("days must be an integer")
            if self.age + days <= self.lifetime:
                self.age += days
            else: 
                self.age = self.lifetime
                self.alive = False
        else:
            raise RuntimeError("Cannot age a dead animal")
        
    def getNeighborhood(self, worldGrid:'WorldGrid'):
        """
        This method return the neighborhood of the animal considered, this approach requires storing the worldGrid
        
        The worldGrid is passed as an argument to keep the Animal class loosely coupled 
        and focused solely on animal-specific behavior. This approach enhances flexibility, 
        maintainability, and testability by avoiding direct dependencies between Animal and 
        a specific WorldGrid instance.
        """
        x, y = self.coords[0], self.coords[1]
        d = self.neighborhoodDistance
        cands = worldGrid[x - d : x + d + 1, y - d : y + d + 1].reshape(-1)
        cands = cands.reshape(-1)
        cands = np.delete(cands,len(cands)//2)
        return cands
        
    def chooseMove(self, neighborhood:dict):
        """given a dictionary of coordinates and land cells evaluates the desired next Move"""

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
    """
    Herbivore dude eat grass and die
    """

    def __init__(self, coordinates: tuple, energy:int = MAX_ENERGY_E, lifetime:int = MAX_LIFE_E, age:int = 0, SocialAttitude:float = 0.5):
        super().__init__(coordinates, energy, lifetime, age, SocialAttitude)

    def __repr__(self):
        return "Erbast"

class Carviz(Animal):
    """
    Angry boy very hungry
    """

    def __init__(self, coordinates: tuple, energy:int = MAX_ENERGY_C, lifetime:int = MAX_LIFE_C, age:int = 0, SocialAttitude:float = 0.5):
        super().__init__(coordinates, energy, lifetime, age, SocialAttitude)

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