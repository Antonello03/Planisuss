import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from math import *

fig, ax = plt.subplots()
x, y = [], []
line, = plt.plot([], [], 'bo-')

def init():
    ax.set_xlim(0, 10*pi)
    ax.set_ylim(-1, 1)
    return line,

def update(frame):
    x.append(frame/10)
    y.append(sin(frame/10))
    line.set_data(x, y)
    return line,

ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=5)

plt.show()
