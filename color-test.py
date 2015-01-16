import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

"""
Script that loops through a series of color showing a plot
with that color and asking if it should be added to the list of colors.
The list of chosen color is then printed at the end.
"""


n = 1000
x = np.random.rand(n)
y = np.random.rand(n)

colors = []

C = 10
for i in range(C):
    color = cm.jet(1.*i/C)
    plt.figure()
    plt.scatter(x,y,c=color)
    plt.show()

    answer=''
    while not (answer == 'y' or answer == 'n'):

        answer = raw_input('Add the color to the list? (y/n)')
        answer = answer.lower()

        if answer == 'y':
            print 'Color added to list.'
            colors.append(color)
        elif answer == 'n':
            print 'Color not added to list.'
        else:
            print 'Could not understand answer, please try again.'


print 'Chosen colors are:'
print '------------------'
for color in colors:
    print color



