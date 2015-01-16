import numpy as np
import matplotlib.pyplot as plt
import scipy

import mypyutils


def testcustomboxplot():
    data = np.random.rand(100)

    mypyutils.pyplot.customboxplot(data)

    plt.show()

def testplotECDF():
    data = np.random.rand(100)

    mypyutils.pyplot.plotECDF(data)

    plt.show()

def testplotHeatMap():

    data = np.random.rand(10,10)
    xlabels = range(10)
    ylabels = range(10)
    values = dict()
    for i in xlabels:
        if i not in values.keys():
            values[i] = dict()
        for j in ylabels:
            values[i][j] = data[i][j]


    mypyutils.pyplot.plotHeatMap(values,xlabels,ylabels)

    plt.show()

def testplotsGrid():

    n = 10

    def plotfunc(i,x,y,figw,figh,ax):
        datax = np.random.rand(i*100)
        datay = np.random.rand(i*100)
        plt.scatter(datax,datay,color=plt.cm.gist_rainbow(1.*i/n))
        plt.title('i=%d,x=%d,y=%d' % (i,x,y))
        if i+figh >= n:
            plt.xlabel(r"$x$")
        if i%figh == 0:
            plt.ylabel(r"$y$")

    mypyutils.pyplot.plotsGrid(n,plotfunc)

    plt.show()

#testcustomboxplot()
#testplotECDF()
#testplotHeatMap()
testplotsGrid()
