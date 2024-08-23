import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def init_grid(N):
    """Initialize the NxN grid with a Glider and a LWSS."""
    grid = np.zeros((N, N), dtype=int)

    # Glider
    glider = np.array([[0, 255, 0],
                       [0, 0, 255],
                       [255, 255, 255]])
    grid[1:4, 1:4] = glider

    grid [30:33,30:33] = glider

    # Lightweight Spaceship (LWSS)
    lwss = np.array([[255, 255, 255, 255, 0],
                     [0, 0, 0, 0, 255],
                     [255, 0, 0, 0, 255],
                     [0, 255, 255, 255, 255]])
    
    grid[30:34, 5:10] = lwss
    grid[10:14, 10:15] = lwss

    return grid


def update(frameNum, img, grid, N):
    """Update the grid for animation."""
    newGrid = grid.copy()
    for i in range(N):
        for j in range(N):
            total = int((grid[i, (j-1)%N] + grid[i, (j+1)%N] +
                         grid[(i-1)%N, j] + grid[(i+1)%N, j] +
                         grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+1)%N] +
                         grid[(i+1)%N, (j-1)%N] + grid[(i+1)%N, (j+1)%N]) / 255)
            if grid[i, j]  == ON:
                if (total < 2) or (total > 3):
                    newGrid[i, j] = OFF
            else:
                if total == 3:
                    newGrid[i, j] = ON
    img.set_data(newGrid)
    grid[:] = newGrid[:]
    return img,

# Parameters
N = 100  # Grid size
ON = 255  # Alive cell
OFF = 0  # Dead cell
UPDATE_INTERVAL = 1  # in milliseconds
grid = init_grid(N)

# Create the plot
fig, ax = plt.subplots()
img = ax.imshow(grid, interpolation='nearest', cmap='gray')
ani = FuncAnimation(fig, update, fargs=(img, grid, N, ),
                    interval=UPDATE_INTERVAL,
                    save_count=50)

plt.show()
