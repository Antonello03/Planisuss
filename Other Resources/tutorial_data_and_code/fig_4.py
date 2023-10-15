 
import numpy as np
import matplotlib.pyplot as plt

def normalize_matrix(data):
    """ Rescale a matrix in [0, 1] """
    return (data-np.nanmin(data))/(np.nanmax(data)-np.nanmin(data))


rain = normalize_matrix(np.load('PR_2020.npy'))
temp = normalize_matrix(np.load('TEMP2m_2020.npy'))
wind = normalize_matrix(np.load('VU_2020_VV_2020.npy'))

meteo = np.dstack((rain, temp, wind))
     
plt.figure(1)
plt.imshow(meteo)
plt.title('Lombardy 2020')
plt.savefig('Figure_4.png', bbox_inches='tight')

plt.show()

