 
import numpy as np
import matplotlib.pyplot as plt

rainbow = plt.imread('Rainbow_in_Budapest.jpg')

plt.figure(1)
plt.imshow(rainbow)
plt.savefig('Figure_5.png', bbox_inches='tight')

plt.show()

print(rainbow.shape)
print(rainbow)
