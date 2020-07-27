import matplotlib.pyplot as plt
import numpy as np


x = [40, 60, 80, 100]

plt.plot(x, x, label="temp")
plt.xlabel('training set percentage')

plt.title("simple plot")

plt.legend()

plt.show()
