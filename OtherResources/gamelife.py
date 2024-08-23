# gamelife.py

""" Implementation of the Conway's Game of Life """

def grid_init(N):
    """ Returns an empty NxN grid """
    grid = list()
    for row in range(0, N):
        r = list()
        for col in range(0, N):
            r.append(0)
        grid.append(r)
    return grid

def grid_display(grid, N):
    """ Display NxN grid """
    for row in range(0, N):
        for col in range(0, N):
            print(' ', grid[row][col], end = '')
        print()
    print()

def grid_evolve(grid, N):
    """ Return the next generation grid """
    # evolution of a generation
    next = grid_init(N)
    for row in range(0, N):
        for col in range(0, N):
            # compute the # neighbors of [row][col] cell
            neigh = 0
            for i in range(max(0, row-1), min(N, row+2)):
                # exploring the neighborhood in row direction
                for j in range(max(0, col-1), min(N, col+2)):
                    # exploring the neighborhood in col direction
                    neigh += grid[i][j]                
            neigh -= grid[row][col]
            
            # compute the status of the [row][col] cell in the next generation
            if grid[row][col] == 1:
                # live cell
                if 2 <= neigh <=3:
                    next[row][col] = 1
                # otherwise it is already empty
            else:
                # dead cell
                if neigh == 3:
                    next[row][col] = 1

    return next

#### MAIN ####

# data structure
# A matrix of integers
#  0: dead cell
#  1: live cell

# initialization of a NxN empty grid
N = 5 # size of the grid (N x N)
grid = grid_init(N)

steps = 10 # duration of the simulation

#print(grid)

# blinker
grid[2][1] = 1
grid[2][2] = 1
grid[2][3] = 1


# visualization
grid_display(grid, N)

for s in range(1, steps+1):
    # next generation
    print('time:', s)
    grid = grid_evolve(grid, N)
    grid_display(grid, N)
