import matplotlib.pyplot as plt
import numpy as np
import random

x = list(np.arange(0, 20, 1))
y1 = [random.randint(0, 20) for a in x]
#print(y1)
pltMatrix = []
indCol = []

fig, axs = plt.subplots(6, 10, sharex=True, sharey=True)
#plt.xticks(size=1)

for col in range(6):
  indCol = []
  for row in range(10):
    y = [random.randint(0, 20) for a in x]
    indCol = indCol + [[x, y]]
    axs[col, row].plot(x, y)
  pltMatrix = pltMatrix + [indCol]
  
#print(len(pltMatrix[0]))
#plt.plot(pltMatrix[0][0][0], pltMatrix[0][0][1])

#fig, axs = plt.subplots(6, 5)

plt.show()

