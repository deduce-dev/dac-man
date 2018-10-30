import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Time taken to finish the "" dataset by several methods
# Normal (1): 0:03:39.588023
# Pool (3): 0:01:28.592517
# MPI (1): 0:01:16.359235

# Fixing random state for reproducibility
np.random.seed(19680801)


plt.rcdefaults()
fig, ax = plt.subplots()

# Example data
runtypes = ('Single-Process', 'Multiprocessing (8 cores)', 'MPI (8 cores)')
y_pos = np.arange(len(runtypes))

#performance = [3.39, 1.28, 1.16]
#performance = [219, 88, 76]

#### Task Rate
performance = [1.36, 3.4, 3.9]

#performance = [
#    datetime.strptime("3.39", "%H:%M:%S.%f"), 
#    datetime.strptime("0:01:28.592517", "%H:%M:%S.%f"), 
#    datetime.strptime("0:01:16.359235", "%H:%M:%S.%f")
#]

plt.gcf().autofmt_xdate()

ax.barh(y_pos, performance, align='center',
        color='green', ecolor='black')
ax.set_yticks(y_pos)
ax.set_yticklabels(runtypes)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Tasks per Second')
ax.set_ylabel('Task Managers')
#ax.set_title('ALS Dataset: # of files: 300, Size of file: 30, Total Size: 600')

plt.tight_layout()

plt.show()