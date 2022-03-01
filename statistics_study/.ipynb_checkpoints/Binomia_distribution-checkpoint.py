# Create 1000 normally distributed points
# with mean of 0 and standard deviation of 1.
import numpy as np
import matplotlib.pyplot as plt

N = 100000000
values = np.random.normal(loc=0,
                          scale=1,
                          size=N)
plt.subplot(1, 1, 1)
plt.hist(values, color="black",density=True)
plt.ylabel("Frequency (N={})".format(N))
plt.tight_layout()
plt.show()