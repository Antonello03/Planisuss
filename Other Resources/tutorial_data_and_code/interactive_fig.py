# interactive_fig.py
"""
Example of interactive figure using matplotlib.

Mouse clicking prints the mouse location.
Keyboard pressing prints the pressed key.
If the pressed key is in ('R', 'r', 'G', 'g', 'B', 'b'), 
the figure displays only the corresponding channel.
If 'a' or 'A' is pressed, the full color image is displayed.
"""

import numpy as np
import matplotlib.pyplot as plt

def normalize_matrix(data):
    """ Rescale a matrix in [0, 1] """
    return (data-np.nanmin(data))/(np.nanmax(data)-np.nanmin(data))

def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

def on_key(event):
    print('you pressed', event.key, event.xdata, event.ydata)
    if event.key == 'r' or event.key == 'R':
        meteo = np.dstack((rain, np.zeros_like(rain), np.zeros_like(rain)))
        title = 'Rain - Lombardy 2020'
    if event.key == 'g' or event.key == 'G':
        meteo = np.dstack((np.zeros_like(temp), temp, np.zeros_like(temp)))
        title = 'Temperature - Lombardy 2020'
    if event.key == 'b' or event.key == 'B':
        meteo = np.dstack((np.zeros_like(wind), np.zeros_like(wind), wind))
        title = 'Wind speed - Lombardy 2020'
    if event.key == 'a' or event.key == 'A':
        meteo = np.dstack((rain, temp, wind))
        title = 'Lombardy 2020'
    if event.key in 'rRgGbBaA':
        fig = plt.figure(1)
        plt.imshow(meteo)
        plt.title(title)
        fig.canvas.draw()


rain = normalize_matrix(np.load('PR_2020.npy'))
temp = normalize_matrix(np.load('TEMP2m_2020.npy'))
wind = normalize_matrix(np.load('VU_2020_VV_2020.npy'))

meteo = np.dstack((rain, temp, wind))
   
fig = plt.figure(1)
plt.imshow(meteo)
plt.title('Lombardy 2020')

cid = fig.canvas.mpl_connect('button_press_event', onclick)
cid = fig.canvas.mpl_connect('key_press_event', on_key)

#for key in ('keymap.all_axes', 'keymap.grid', 'keymap.grid_minor'):
#    plt.rcParams[key] = ''

plt.show()

