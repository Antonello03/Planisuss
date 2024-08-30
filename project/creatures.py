from planisuss_constants import *
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

    def getCoords(self):
        return self.coords

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
        #cands = np.delete(cands,len(cands)//2)
        return cands
        
    def rankMoves(self, neighborhood:'NDArray'):
        """Given an array of neighboring cells, evaluates the desired next move"""
        #each animal ranks the choices individually assigning them a desirability score from 0-1, then if the socialgroup decision is acceptable (scaled by the socialattitude) it is followed
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
    """
    Herbivore dude eat grass and die

    Erbasts are generally friendly, their socialAttitude score goes from low - 0 to high - 1
    """
    id = 0

    CARVIZ_DANGER = 0.75
    VEG_NEED = 0.01
    ENERGY_WEIGHT = 0.1 # scales how much energy matters overall
    ENERGY_WEIGHT2 = 0.8 # lower value -> more likely to stay even at high energy levels
    ENERGY_EXPONENT = 0.8 # regulates how much the percentage of energy matters

    def __init__(self, coordinates: tuple, energy:int = MAX_ENERGY_E, lifetime:int = MAX_LIFE_E, age:int = 0, SocialAttitude:float = 0.5):
        super().__init__(coordinates, energy, lifetime, age, SocialAttitude)
        self.ID = Erbast.id
        Erbast.id += 1

    def rankMoves(self, worldGrid:'WorldGrid'): # TODO - i could implement a logic where cells near a carviz are less likely and far from it are more likely
        """
        This method calculates the desirability scores for each cell in the given neighborhood and returns a sorted list of pairs [value, ].
        """
        neighborhood = self.getNeighborhood(worldGrid)
        desirabilityScores = [[0,cell.coords] for cell in neighborhood] # at the beginnign all cells are equal
        # all possible cells evaluation
        for i in range(len(neighborhood)):
            desirabilityScores[i][0] -= neighborhood[i].numCarviz * Erbast.CARVIZ_DANGER
            desirabilityScores[i][0] += neighborhood[i].numErbast * self.socialAttitude
            desirabilityScores[i][0] += neighborhood[i].getVegetobDensity() * Erbast.VEG_NEED
            desirabilityScores[i][0] = round(desirabilityScores[i][0], 2)

        # Staying likability evaluation
        presentIndex =  len(desirabilityScores)//2
        desirabilityScores[presentIndex][0] += ((100 - self.energy)**Erbast.ENERGY_EXPONENT * Erbast.ENERGY_WEIGHT) - Erbast.ENERGY_WEIGHT2
        desirabilityScores[presentIndex][0] -= self.socialAttitude # remove self-counting
        desirabilityScores[presentIndex][0] = round(desirabilityScores[presentIndex][0], 2)
        desirabilityScores[presentIndex][1] = "stay"

        return sorted(desirabilityScores, key= lambda x : x[0], reverse = True)

    def graze(self, grazingAmount): # Vegetob reduction should be handled by environment becaus of herds dynamics
        if self.energy + grazingAmount <= MAX_ENERGY_E:
            self.energy += grazingAmount
        else:
            self.energy = MAX_ENERGY_E
        
    def __repr__(self):
        return f"Erbast {self.id}"

class Carviz(Animal): # TODO - what if we add a "hiding in tall gras" dynamic?
    """
    Angry boy very hungry

    Carvizes aren't as friendly as Erbasts, their social attitude score goes from 0 offensive to 1 friendly
    """
    id = 0

    VEG_NEED = 0.005 # carvist do not need vegetob, but it makes sense for them to look for erbast in food rich zones
    ERBAST_NEED = 1.2
    ENERGY_WEIGHT = 0.1 # scales how much energy matters overall
    ENERGY_WEIGHT2 = 0.8 # lower value -> more likely to stay even at high energy levels
    ENERGY_EXPONENT = 0.65 # regulates how much the percentage of energy matters

    def __init__(self, coordinates: tuple, energy:int = MAX_ENERGY_C, lifetime:int = MAX_LIFE_C, age:int = 0, SocialAttitude:float = 0.5):
        super().__init__(coordinates, energy, lifetime, age, SocialAttitude)
        self.id = Carviz.id
        Carviz.id += 1

    def rankMoves(self, worldGrid: 'WorldGrid'):
        """Ranks the moves in the neighborhood based on desirability scores."""
        neighborhood = self.getNeighborhood(worldGrid)

        desirabilityScores = [[0,cell.coords] for cell in neighborhood] # at the beginnign all cells are equal
        # all possible cells evaluation
        for i in range(len(neighborhood)):
            desirabilityScores[i][0] += neighborhood[i].numErbast * Carviz.ERBAST_NEED
            desirabilityScores[i][0] += neighborhood[i].getVegetobDensity() * Carviz.VEG_NEED
            desirabilityScores[i][0] += neighborhood[i].numCarviz * (self.socialAttitude - 0.5) # A carviz might want to stay alone
            desirabilityScores[i][0] = round(desirabilityScores[i][0], 2)

        # Staying likability evaluation - carviz are very unlikely to stay still, they're constantly looking for Erbasts
        presentIndex =  len(desirabilityScores)//2
        desirabilityScores[presentIndex][0] -= ((100 - self.energy)**Carviz.ENERGY_EXPONENT * Carviz.ENERGY_WEIGHT) #when the energy is lwo a prey must be found
        desirabilityScores[presentIndex][0] -= (self.socialAttitude - 0.5) # remove self-counting
        desirabilityScores[presentIndex][0] = round(desirabilityScores[presentIndex][0], 2)
        desirabilityScores[presentIndex][1] = "stay"
        
        return sorted(desirabilityScores, key= lambda x : x[0], reverse = True)

    def __repr__(self):
        return f"Carviz {self.id}"

class SocialGroup: # TODO what particular information may be stored by a socialGroup?
    """
    Holds knowledge about the environment
    """

    def __init__(self, components:list[Animal]):
        self.components = components

    def getComponents(self):
        return self.components
    
    def addComponent(self, animal:Animal):
        self.components.append(animal)
    

class Herd(SocialGroup):

    def __init__(self, components):
        super().__init__(self, components)
        pass

class Pride(SocialGroup):

    def __init__(self, components):
        super().__init__(self, components)
        pass