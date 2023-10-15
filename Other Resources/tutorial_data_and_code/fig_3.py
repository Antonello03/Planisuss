 
import numpy as np
import matplotlib.pyplot as plt

rain = np.load('PR_2020.npy')
temp = np.load('TEMP2m_2020.npy')
wind = np.load('VU_2020_VV_2020.npy')

plt.figure(1)
plt.imshow(rain, cmap='Greys_r')
plt.colorbar()
plt.title('Rain 2020')
plt.savefig('Figure_3a.png', bbox_inches='tight')

plt.figure(2)
plt.imshow(temp, cmap='Greys_r')
plt.colorbar()
plt.title('Temperature 2020')
plt.savefig('Figure_3b.png', bbox_inches='tight')

plt.figure(3)
plt.imshow(wind, cmap='Greys_r')
plt.colorbar()
plt.title('Wind speed 2020')
plt.savefig('Figure_3c.png', bbox_inches='tight')


plt.show()

