 
import numpy as np
import matplotlib.pyplot as plt

A = np.asarray([[5, 9, 6, 1, 6], [6, 4, 0, 5, 9],
                [3, 6, 8, 8, 2], [0, 9, 5, 9, 6]])

plt.imshow(A, cmap='Greys_r')
plt.yticks([0, 1, 2, 3])
plt.colorbar()
plt.savefig('Figure_1a.png', bbox_inches='tight')

plt.figure(2)
plt.imshow(A)
plt.yticks([0, 1, 2, 3])
plt.colorbar()
plt.savefig('Figure_1b.png', bbox_inches='tight')
plt.show()

