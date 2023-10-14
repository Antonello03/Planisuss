import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def init():
    # Initialization code (if any)
    pass

def update(frame):
    # Update code based on the frame number
    # For example, update a line plot
    line.set_ydata(np.sin(x + frame * 0.1))
    return line,

# Create a figure and axes
fig, ax = plt.subplots()

# Generate x data
x = np.linspace(0, 2 * np.pi, 100)

# Initialize a line plot
line, = ax.plot(x, np.sin(x))

# Create the animation
ani = FuncAnimation(fig, update, frames=100, init_func=init, interval=50, blit=True)

# Show the plot
plt.show()
