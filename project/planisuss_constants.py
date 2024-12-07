# planisuss_constants.py
"""
Collection of the main constants defined for the 
"Planisuss" project.

Values can be modified according to the envisioned behavior of the 
simulated world.

---
v 1.00
Stefano Ferrari
2023-02-07
"""

### Game constants

NUMDAYS = 50     # Length of the simulation in days

# geometry
NUMCELLS = 50     # size of the (square) grid (NUMCELLS x NUMCELLS)
NUMCELLS_R = 1000    # number of rows of the (potentially non-square) grid
NUMCELLS_C = 1000    # number of columns of the (potentially non-square) grid

# social groups
NEIGHBORHOOD = 1     # radius of the region that a social group can evaluate to decide the movement
NEIGHBORHOOD_E = 1   # radius of the region that a herd can evaluate to decide the movement
NEIGHBORHOOD_C = 2   #  radius of the region that a pride can evaluate to decide the movement

NEIGHBORHOOD_SOCIAL = 2     # radius of the region that a social group can evaluate to decide the movement
NEIGHBORHOOD_HERD = 2   # radius of the region that a herd can evaluate to decide the movement
NEIGHBORHOOD_PRIDE = 3   #  radius of the region that a pride can evaluate to decide the movement

MEMORY_SOCIAL = 10      # amount of cells a social group can remember to have visited to decide the movement

MAX_HERD = 1000      # maximum numerosity of a herd
MAX_PRIDE = 100      # maximum numerosity of a pride

# individuals
MAX_ENERGY = 100     # maximum value of Energy
MAX_ENERGY_E = 100   # maximum value of Energy for Erbast
MAX_ENERGY_C = 100   # maximum value of Energy for Carviz

ENERGY_LOSS = -5      # Energy lost by moving each day

MAX_LIFE = 10000     # maximum value of Lifetime
MAX_LIFE_E = 10000   # maximum value of Lifetime for Erbast
MAX_LIFE_C = 10000   # maximum value of Lifetime for Carviz

AGING = 20           # energy lost each month
AGING_E = 20          # energy lost each month for Erbast
AGING_C = 20          # energy lost each month for Carviz

GROWING = 1          # Vegetob density that grows per day.

# our constants

MAX_GROWTH = 200