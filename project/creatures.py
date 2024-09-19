from planisuss_constants import *
import numpy as np
import sys

#TODO - define graze for herds

def getDirection(myCoords:tuple ,otherCoords:tuple):
    """given to coords tuple return direction"""
    myX, myY = myCoords
    otherX, otherY = otherCoords
    if otherX < myX:
        if otherY < myY:
            return 'NW'
        elif otherY == myY:
            return 'N'
        else:
            return 'NE'
    elif otherX == myX:
        if otherY < myY:
            return 'O'
        elif otherY == myY:
            return None
        else:
            return 'E'
    else:
        if otherY < myY:
            return 'SW'
        elif otherY == myY:
            return 'S'
        else:
            return 'SE'
def getOppositeDirection(myCoords:tuple, otherCoords:tuple):
    return getDirection(otherCoords, myCoords)
def getCellInDirection(myCoords:tuple, direction:str):
    x,y = myCoords
    if direction == "N":
        return (x-1,y)
    elif direction == "NE":
        return (x-1,y+1)
    elif direction == "E":
        return (x,y+1)
    elif direction == "SE":
        return (x+1,y+1)
    elif direction == "S":
        return (x+1,y)
    elif direction == "SW":
        return (x+1,y-1)
    elif direction == "W":
        return (x,y-1)
    elif direction == "NW":
        return (x-1,y-1)
    else:
        return myCoords

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
        self.socialGroup = None
        self.inSocialGroup = False
        self.alive = True
        self.neighborhoodDistance = neighborhoodDistance
        self.preferredDirection = None
        self.preferredDirectionIntensity = 1 # number from 0 to 1
        pass

    def getCoords(self):
        return self.coords
    
    def getSocialGroup(self):
        return self.socialGroup

    def getEnergy(self):
        return self.energy

    def getCell(self, grid:'WorldGrid'):
        return grid[self.getCoords()]

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
            if self.age % 10 == 0:
                self.energy -= AGING
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
        
    def rankMoves(self, worldGrid:'WorldGrid'):
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
    ID = 1

    CARVIZ_DANGER = 0.75
    VEG_NEED = 0.01
    ENERGY_WEIGHT = 0.1 # scales how much energy matters overall
    ENERGY_WEIGHT2 = 0.8 # lower value -> more likely to stay even at high energy levels
    ENERGY_EXPONENT = 0.8 # regulates how much the percentage of energy matters
    ESCAPE_DECAY = 0.8 #for how much time an erbast wants to go in the opposite direction of the last saw carviz
    ESCAPE_THRESHOLD = 0.3 #Under which value erbast no longer run away
    NOT_EATING_SA_REDUCTION = 0.05

    def __init__(self, coordinates: tuple, energy:int = MAX_ENERGY_E, lifetime:int = MAX_LIFE_E, age:int = 0, SocialAttitude:float = 0.5):
        super().__init__(coordinates, energy, lifetime, age, SocialAttitude)
        self.id = Erbast.ID
        Erbast.ID += 1

    def rankMoves(self, worldGrid:'WorldGrid'): #TODO - Erbast is Still too stupid, need to add a preference in direction opposite to last danger which decays in time
        """
        This method calculates the desirability scores for each cell in the given neighborhood and returns a sorted list of pairs [value, ].
        
        rankMoves updates internal parameters, hence if used more times with the same configuration results may differ
        """

        neighborhood = self.getNeighborhood(worldGrid)
        LandCell = getattr(sys.modules['world'], 'LandCell')
        neighborhood = [cell for cell in neighborhood if isinstance(cell, LandCell)]
        desirabilityScores = {cell:0 for cell in neighborhood}
        presentCell = self.getCell(worldGrid) # presentCell should be in neighborhood

        for cell in desirabilityScores:

            carvizDangerValue = cell.numCarviz * Erbast.CARVIZ_DANGER
            desirabilityScores[cell] -= carvizDangerValue

            # also neighbouring cells, if in range, should become more dangerous, but a bit less
            if(cell.numCarviz > 0):
                x,y = cell.getCoords()

                self.preferredDirection = getOppositeDirection(presentCell.getCoords(), (x,y)) #store last escape direction
                self.preferredDirectionIntensity = 1 # raise intensity

                nearbyCords = [(x-1, y-1),(x, y-1),(x+1, y-1),(x-1, y+1),(x, y+1),(x+1, y+1),(x-1, y),(x+1, y)]
                nearbyCells = [worldGrid[coords] for coords in nearbyCords]
                CellsInRange = [cell for cell in nearbyCells if cell in neighborhood]
                for cell in CellsInRange:
                    # print(f"cell {cell.getCoords()} is dangerous, it's desirability is now: {desirabilityScores[cell]}")
                    desirabilityScores[cell] -= carvizDangerValue * 0.6
                    # print(f"nerfed to {desirabilityScores[cell]} ")

            # TODO - this could still be a problem -> if two individuals are next to each other they might never join in a herd (but they could end up in the same cell for other reasons) -> maybe there aren't problems if the other reasons are enough

            if presentCell != cell and presentCell.numErbast < cell.numErbast: # this avoid herds or individuals in swapping position indefinitely, instead the smaller group will join the bigger one, aslo self counting is avoided
                desirabilityScores[cell] += cell.numErbast * self.socialAttitude

            desirabilityScores[cell] += cell.getVegetobDensity() * Erbast.VEG_NEED
            desirabilityScores[cell] = round(desirabilityScores[cell], 2)

        # Staying likability evaluation
        desirabilityScores[presentCell] += ((100 - self.energy)**Erbast.ENERGY_EXPONENT * Erbast.ENERGY_WEIGHT) - Erbast.ENERGY_WEIGHT2
        desirabilityScores[presentCell] = round(desirabilityScores[presentCell], 2)
        
        # Running away from carviz
        escapeCellCoords = getCellInDirection(presentCell.getCoords(), self.preferredDirection)
        escapeCell = worldGrid[escapeCellCoords]
        if escapeCell in neighborhood and escapeCell != presentCell and self.preferredDirectionIntensity > Erbast.ESCAPE_THRESHOLD:
            # print(f"Oh no I'm {self}, I'm in {self.getCoords()} and there's a Carviz nearby, better go in {escapeCell.getCoords()}")
            desirabilityScores[escapeCell] += self.preferredDirectionIntensity
            desirabilityScores[escapeCell] = round(desirabilityScores[escapeCell],2)
            self.preferredDirectionIntensity *= Erbast.ESCAPE_DECAY

        desScoresList = [[item[1],item[0].getCoords()] for item in desirabilityScores.items()]

        return sorted(desScoresList, key=lambda x:x[0], reverse = True)

    def graze(self, availableVegetob:int) -> int: # Vegetob reduction should be handled by environment becaus of herds dynamics
        """returns grazed amount"""
        if self.energy + availableVegetob <= MAX_ENERGY_E:
            self.energy += availableVegetob
            eatenVeg = availableVegetob
        else:
            self.energy = MAX_ENERGY_E
            eatenVeg = MAX_ENERGY_E - self.energy
        return eatenVeg
        
    def __repr__(self):
        return f"Erbast {self.id}"

class Carviz(Animal): # TODO - what if we add a "hiding in tall grass" dynamic?
    """
    Angry boy very hungry

    Carvizes aren't as friendly as Erbasts, their social attitude score goes from 0 offensive to 1 friendly
    """
    ID = 1

    VEG_NEED = 0.005 # carvist do not need vegetob, but it makes sense for them to look for erbast in food rich zones
    ERBAST_NEED = 1.2
    ENERGY_WEIGHT = 0.1 # scales how much energy matters overall
    ENERGY_WEIGHT2 = 0.8 # lower value -> more likely to stay even at high energy levels
    ENERGY_EXPONENT = 0.65 # regulates how much the percentage of energy matters

    def __init__(self, coordinates: tuple, energy:int = MAX_ENERGY_C, lifetime:int = MAX_LIFE_C, age:int = 0, SocialAttitude:float = 0.5):
        super().__init__(coordinates, energy, lifetime, age, SocialAttitude)
        self.id = Carviz.ID
        Carviz.ID += 1

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

    def __init__(self, components : list[Animal]):

        self.coords = (-1,-1)
        if (len(components) > 0):
            self.coords = components[0].getCoords()
            for animal in components:
                if not isinstance(animal, Animal):
                    raise Exception(f"All Individuals should be Animals, received instead {animal}")
                if animal.getCoords() != self.coords:
                    raise Exception(f"All Animals should inhabit the same cell, individual {animal} is in {animal.getCoords()}, it should be in {self.coords}")

        self.components = components
        
        for el in self.components:
            el.inSocialGroup = True
            el.socialGroup = self

        self.numComponents = len(components)
        self.neighborhoodDistance = NEIGHBORHOOD_SOCIAL
        self.groupSociality = 0

    def getCoords(self):
        return self.coords
    
    def getGroupSociality(self):
        totSocial = 0
        for component in self.components:
            totSocial += component.socialAttitude
        return round(totSocial / self.numComponents , 2)
    
    def getGroupEnergy(self):
        totalEnergy = 0
        for component in self.components:
            totalEnergy += component.energy
        return round(totalEnergy / self.numComponents , 2)

    def getComponents(self):
        return self.components
    
    def addComponent(self, animal:Animal):
        if not isinstance(animal, Animal):
            raise ValueError("animal must be an instance of Animal")
        
        self.components.append(animal)
        animal.inSocialGroup = True
        animal.socialGroup = self
        self.numComponents += 1

    def joinGroups(self, other:'SocialGroup'):
        self.components.extend(other.components)
        self.numComponents = len(self.components)
        # join knowledge        
    
    def loseComponent(self, animal:Animal):
        if not isinstance(animal, Animal):
            raise ValueError("animal must be an instance of Animal")
        
        self.components.remove(animal)
        animal.inSocialGroup = False
        animal.socialGroup = None
        self.numComponents -= 1
        return animal

    def getCell(self, grid:'WorldGrid'):
        return grid[self.getCoords()]

    def getNeighborhood(self, worldGrid:'WorldGrid', d = None):
        x, y = self.coords[0], self.coords[1]
        d = d if d is not None else self.neighborhoodDistance
        cands = worldGrid[x - d : x + d + 1, y - d : y + d + 1].reshape(-1)
        # cands = np.delete(cands,len(cands)//2)
        return cands
    
    def __repr__(self):
        return f"SocialGroup, components:{self.components}"
    
class Herd(SocialGroup): # TODO - Add Herd Escape rankMoves logic

    """
    Joining a Herd has several advantages for an Erbast

     - Knowledge about past visited cells
     - Knowledge about predators
     - In a Herd you have multiple eyes hence you'll be able to identify dangers at a longer distance +1 neighborhood Distance
    """

    ID = 1

    def __init__(self, components: list[Erbast]):
        super().__init__(components)
        self.id = Herd.ID
        Herd.ID += 1
        self.preferredDirection = None
        self.preferredDirectionIntensity = 1 # number from 0 to 1

    def rankMoves(self, worldGrid:'WorldGrid'):
        """
        Method used by a SocialGroup to decide the next move.
        Differently from Individual method of choice and Herd can take into account more factors like
        - dangers at a longer distance
        - TODO 
        """
        #each animal ranks the choices individually assigning them a desirability score from 0-1,
        #then if the socialgroup decision is acceptable (scaled by the socialattitude) it is followed

        # First of all the Herd makes a decision based on its knowledge

        neighborhood = self.getNeighborhood(worldGrid, d = self.neighborhoodDistance)
        reachableCells = self.getNeighborhood(worldGrid, d = 1)
        LandCell = getattr(sys.modules['world'], 'LandCell')
        neighborhood = [el for el in neighborhood if isinstance(el, LandCell)]
        reachableCells = [el for el in reachableCells if isinstance(el, LandCell)]
        # print(f"neighborhood Cells: {[cell.getCoords() for cell in neighborhood]}\nreachableCells: {[cell.getCoords() for cell in reachableCells]}")
        desirabilityScores = {cell:0 for cell in neighborhood}
        groupSociality = self.getGroupSociality()
        groupEnergy = self.getGroupEnergy()
        presentCell = self.getCell(worldGrid) # presentCell should be in neighborhood

        for cell in desirabilityScores:

            carvizDangerValue = cell.numCarviz * Erbast.CARVIZ_DANGER
            desirabilityScores[cell] -= carvizDangerValue

            # also neighbouring cells, if in range, should become more dangerous, but a bit less
            # herd has a better sense of danger and try to stay as far as possible from carvizes
            if(cell.numCarviz > 0):
                x,y = cell.getCoords()

                self.preferredDirection = getOppositeDirection(presentCell.getCoords(), (x,y)) #store last escape direction
                self.preferredDirectionIntensity = 1 # raise intensity

                nearbyCords = [(x-1, y-1),(x, y-1),(x+1, y-1),(x-1, y+1),(x, y+1),(x+1, y+1),(x-1, y),(x+1, y)]
                nearbyCords_2 = [(x-2, y-2),(x-1, y-2),(x, y-2),(x+1, y-2),(x+2, y-2),
                                 (x-2, y+2),(x-1, y+2),(x, y+2),(x+1, y+2),(x+2, y+2),
                                 (x-2, y-1),(x+2, y-1),(x-2, y),(x+2, y),(x-2, y+1),(x+2, y+1)]

                nearbyCells = [worldGrid[coords] for coords in nearbyCords]
                nearbyCells_2 = [worldGrid[coords] for coords in nearbyCords_2]

                CellsInRange = [cell for cell in nearbyCells if cell in reachableCells]
                CellsInRange_2 = [cell for cell in nearbyCells_2 if cell in reachableCells]

                for cell in CellsInRange:
                    # print(f"cell {cell.getCoords()} is dangerous, it's desirability is now: {desirabilityScores[cell]}")
                    desirabilityScores[cell] -= carvizDangerValue * 0.6
                    # print(f"nerfed to {desirabilityScores[cell]} ")
                for cell in CellsInRange_2:
                    desirabilityScores[cell] -= carvizDangerValue * 0.4

            if presentCell != cell and presentCell.numErbast < cell.numErbast:
                desirabilityScores[cell] += cell.numErbast * groupSociality

            desirabilityScores[cell] += cell.getVegetobDensity() * Erbast.VEG_NEED
            desirabilityScores[cell] = round(desirabilityScores[cell], 2)

        # Staying likability evaluation
        desirabilityScores[presentCell] += ((100 - groupEnergy)**Erbast.ENERGY_EXPONENT * Erbast.ENERGY_WEIGHT) - Erbast.ENERGY_WEIGHT2
        desirabilityScores[presentCell] = round(desirabilityScores[presentCell], 2)
        
        #Runnin away from Carviz
        escapeCellCoords = getCellInDirection(presentCell.getCoords(), self.preferredDirection)
        escapeCell = worldGrid[escapeCellCoords]
        if escapeCell in neighborhood and escapeCell != presentCell and self.preferredDirectionIntensity > Erbast.ESCAPE_THRESHOLD:
            # print(f"Oh no I'm {self}, I'm in {self.getCoords()} and there's a Carviz nearby, better go in {escapeCell.getCoords()}")
            desirabilityScores[escapeCell] += self.preferredDirectionIntensity
            desirabilityScores[escapeCell] = round(desirabilityScores[escapeCell],2)
            self.preferredDirectionIntensity *= Erbast.ESCAPE_DECAY

        desScoresList = [[item[1],item[0].getCoords()] for item in desirabilityScores.items() if item[0] in reachableCells]

        return sorted(desScoresList, key=lambda x:x[0], reverse = True)

    def joinGroups(self, other: SocialGroup):
        super().joinGroups(other)
        for el in other.getComponents():
            el.socialGroup = self
            el.inSocialGroup = True

    def _getVegetobDistribution(self, energies:list[int], availableVegetob: int) -> list[int]:
        """
        internal method to asses which Erbasts are going to eat and how much, vegetob is iteratively assigned to the lowest energy erbasts untile exhaustion
        returns vegetob assignments.
        The method assumes energies are in increasing order.
        
        Example: energies: [12, 12, 20], available Vegetob: 18
        the algorithm progressively assign the available Vegetob to the i hungriest erbasts.
        - i = 1 -> [12, 12, 20] assignedV: [0, 0, 0] (no assignement since 12 - 12 = 0)
        - i = 2 -> [21, 21, 20] assignedV: [9, 9, 0] (first energies of 1 and 2 are raised to 20 because 20 - 12 = 8, then the remaining 2 energy is distribuited)
        """
        assignedV = [0 for i in range(len(energies))]
        i = 1 #index of next higher v
        while availableVegetob > 0 and i <= len(energies):
            if i < len(energies): #standard case
                v = energies[i] - energies[i-1] # check how much to balance
            else: # all erbasts have the same energy
                v = availableVegetob
            
            #check if we have enough vegetob
            if v * i < availableVegetob:
                for j in range(i):
                    assignedV[j] += v
                availableVegetob -= v * i #update available Vegetob
            else:
                splittedV = availableVegetob // i #assign splitted remaining vegetob
                for j in range(i):
                    assignedV[j] += splittedV
                availableVegetob -= splittedV * i
                if availableVegetob > 0:
                    for j in range(availableVegetob): #assign eventual surplus
                        assignedV[j] += 1
                    availableVegetob = 0
            i += 1
        assignedV = [(lambda x: MAX_ENERGY_E - y if x + y > MAX_ENERGY_E else x)(x) for x,y in zip(assignedV, energies)] # energy should be below maxEnergy
        return assignedV

    def graze(self, availableVegetob:int) -> int: # Vegetob reduction should be handled by environment becaus of herds dynamics
        """returns grazed amount, updates herds components energy"""
        # for each erbast I need to understand if it has eaten or not and how much he needs to eat
        energies = {erb : erb.getEnergy() for erb in self.getComponents()}
        energies = dict(sorted(energies.items(), key=lambda item: item[1])) #sort by values
        energiesList = list(energies.values())
        assignedVegetobs = self._getVegetobDistribution(energiesList, availableVegetob)
        for erb, veg in zip(energies, assignedVegetobs):
            if veg > 0:
                erb.graze(veg)
            else: #if not eating reduce socialAttitude
                erb.socialAttitude -= Erbast.NOT_EATING_SA_REDUCTION
        return sum(assignedVegetobs)

    def __repr__(self):
        return f"Herd {self.id}, components:{self.components}"

class Pride(SocialGroup):

    ID = 1

    def __init__(self, components: list[Carviz]):
        super().__init__(self, components)
        self.id = Carviz.ID
        Carviz.ID += 1

    def rankMoves(self, worldGrid:'WorldGrid'):
        #each animal ranks the choices individually assigning them a desirability score from 0-1, then if the socialgroup decision is acceptable (scaled by the socialattitude) it is followed
        pass

    def joinGroups(self, other: SocialGroup):
        super().joinGroups(other)
        for el in other:
            other.pride = self

    def __repr__(self):
        return f"Pride {self.id}, components: {self.components}"
        