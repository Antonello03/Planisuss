import random
import logging
from datetime import datetime
from interface import Interface
from world import Environment
from creatures import Erbast, Carviz, Herd, Pride

WORLD_CONFIGS = {
    "map1": {"seed": 1},
    "map2": {"seed": 42},
    "map3": {"seed": 10},
}

log_filename = f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
logging.basicConfig(
    filename="planisuss_events.log",  # Always logs to the same file
    filemode="w",        # "w" overwrites the file on each run
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)

def initializePopulation(environment, type:str = "test1", nErb = 10, nCarv = 10):
    grid_shape = environment.getGrid().shape
    land_cells = [(x, y) for x in range(grid_shape[0]) for y in range(grid_shape[1])
                  if environment.isLand(x, y)]

    if type == "test1":
        erb1 = Erbast((25,25), energy=100, name="schiavo 1")
        erb2 = Erbast((25,25), energy=5, name="schiavo 2")
        erb3 = Erbast((25,25), energy=5, name="schiavo 3")
        herd1 = Herd([erb1,erb2,erb3])
        environment.add(herd1)

        erbOther = Erbast((24,25), energy=100, name="schiavo 4")
        erbOther2 = Erbast((24,25), energy=5, name = "schiavo 5")
        herd2 = Herd([erbOther, erbOther2])
        environment.add(herd2)

        carv1 = Carviz((24, 24))
        carv2 = Carviz((24, 24))
        pride1 = Pride([carv1,carv2])
        environment.add(pride1)

        carv3 = Carviz((26,26))
        carv4 = Carviz((26,26), SocialAttitude = 0.8)
        carv5 = Carviz((26,26))
        pride2 = Pride([carv3,carv4,carv5])
        environment.add(pride2)

    if type == "test2":
        erb1 = Erbast((25,25), energy=60, name="schiavo 1")
        carv1 = Carviz((24, 24))
        environment.add(erb1)
        environment.add(carv1)
        environment.add(Carviz((26,26)))

    if type == "test_offsprings":

        erbs = [
            Erbast((25,25)),
            Erbast((25,25)),
            Erbast((25,25)),
            Erbast((28,28)),
            Erbast((28,28)),
            Erbast((30,30))
        ]

        carvs = [
            Carviz((24, 24)),
            Carviz((24, 24)),
            Carviz((24, 24)),
            Carviz((26, 26)),
            Carviz((26, 26)),
            Carviz((26, 26))
        ]

        for el in erbs:
            environment.add(el)
        for el in carvs:
            environment.add(el)

    if type == "one Erbast":
        erb = Erbast((25,25))
        environment.add(erb)

    if type == "random":
        for i in range(nErb):
            (x, y) = random.choice(land_cells)
            # coords = (random.randint(20,30), random.randint(20,30))
            erb = Erbast((x, y), SocialAttitude = random.random())
            environment.add(erb)

        for i in range(nCarv):
            (x, y) = random.choice(land_cells)
            # coords = (random.randint(20,30), random.randint(20,30))
            carv = Carviz((x, y), SocialAttitude = random.random())
            environment.add(carv)

def simulation():
    animation = Interface()
    animation.run_simulation()

if __name__ == "__main__":
    simulation()