 
import numpy as np
import matplotlib.pyplot as plt

rain = np.load('PR_2020.npy')
temp = np.load('TEMP2m_2020.npy')
wind = np.load('VU_2020_VV_2020.npy')

plt.figure(1)
plt.imshow(rain)
plt.colorbar()
plt.title('Rain 2020')
plt.savefig('Figure_2a.png', bbox_inches='tight')

plt.figure(2)
plt.imshow(temp)
plt.colorbar()
plt.title('Temperature 2020')
plt.savefig('Figure_2b.png', bbox_inches='tight')

plt.figure(3)
plt.imshow(wind)
plt.colorbar()
plt.title('Wind speed 2020')
plt.savefig('Figure_2c.png', bbox_inches='tight')


plt.show()

