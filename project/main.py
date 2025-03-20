import random
import logging
from datetime import datetime
from interface import Interface
from world import Environment
from creatures import Erbast, Carviz, Herd, Pride

def simulation(map_selection=False, dynamic=False):
    animation = Interface()
    animation.run_simulation(map_selection=map_selection, dynamic=dynamic)

if __name__ == "__main__":
    simulation(map_selection=False, dynamic=False)