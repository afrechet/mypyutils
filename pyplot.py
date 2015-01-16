"""
Various pyplot related utils.
@author Alexandre Frechette (afrechet@cs.ubc.ca)
"""
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def getPalette(n):
    dx = 0.1
    colormap = plt.cm.rainbow
    palette = [colormap(dx + (1.0-dx)*i/float(n-1)) for i in range(n)]     

    return palette


def plotsGrid(n,plotfunc,gridw=None,gridh=None,sharex=False,sharey=False,diagonalnoshare=False):
    """Uses a user defined plotting function to create a grid of plots.

    Arguments:
    n -- the total number
    plotfunc -- a user-defined function that takes figure index, x and y integer grid coordinates, grid width, grid height and axes and plots
        the desired plots grid entry at (x,y).
            plotfunc(i,x,y,gridw,gridh,ax)

    Keyword Arguments:
    gridw -- the desired width of the plots grid.
    gridh -- the desired height of the plots grid.
    sharex -- indicates whether the x-axis should be shared.
    sharey -- indicates whether the y-axis should be shared.
    diagonalnoshare -- indicates whether the diagonal should not share axes.
    """
    if gridw == None and gridh == None:
        gridw = int(math.ceil(math.sqrt(n)))
        gridh = int(math.ceil(n/float(gridw)))
    else:
        if gridw == None:
            gridw = int(math.ceil(n/float(gridh)))
        elif gridh == None:
            gridh = int(math.ceil(n/float(gridw)))
    if gridw*gridh < n:
        raise Exception('Plots grid dimensions (%d,%d) are too small to support the required %d plots.' % (gridw,gridh,n))

    ax = None
    for i in range(n):
        
        x = i%gridw
        y = i/gridw
        
        if diagonalnoshare and x==y: 
            plt.subplot(gridh,gridw,i+1)
        else:
            if sharex and sharey:
                ax = plt.subplot(gridh,gridw,i+1,sharey=ax,sharex=ax)
            elif sharex:
                ax = plt.subplot(gridh,gridw,i+1,sharex=ax)
            elif sharey:
                ax = plt.subplot(gridh,gridw,i+1,sharey=ax)
            else:
                ax = plt.subplot(gridh,gridw,i+1)


        plotfunc(i,x,y,gridw,gridh,ax)

def customboxplot(data,x=1,percentiles=(25,50,75),dataplot=True,mean=False,bannotate=True,bcolor='b',bccolor='r',bmcolor='r',bwidth=0.5,dcolor='k',dmarker='.',dalpha = 0.25,jitter=0,label=None,ax=None):
    """Plots a customized boxplot.

    The data is first plot on a column, and a box bounding the provided percentiles
    is plotted, with a middle line at the middle statistic.

    Arguments:
    data -- a list of numbers to plot.

    Keyword Arguments:
    x -- the horizontal position at which to plot the data.
    percentiles -- a triple consisting of the three percentiles at which to plot the box.
    dataplot --- whether to also plot the data points on a single line.
    mean -- whether to also plot the mean as a dashed line with central color.
    bannotate -- whether to annotate the box plot with the percentiles or not.
    bcolor -- the color for the box.
    bccolor -- the color of the central line in the box.
    bmcolor -- the color of the mean line in the box, if any.
    bwidth -- width of the box to plot.
    dcolor -- the color for the data scatter plot.
    dmarker -- the marker for the data scatter plot.
    dalpha -- the alpha (transparency) value for the data scatter plot.
    jitter -- the jitter amount (jitter/2 * rand(-1,1) will be added to every x-value of the data points).
    label -- a label for the provided data.
    ax -- the axes on which to plot; uses pyplot defaults if None provided.
    """

    #Verify and preprocess input.
    if not 0<=dalpha<=1:
        raise Exception('Provided data transparency dalpha (%f) must be in [0,1].' % dalpha)

    if not min(percentiles)>=0 or not max(percentiles)<=100:
        raise Exception('Provided percentiles (%s) must be in [0,100].' % str(percentiles))

    if bwidth < 0:
        raise Exception('Provided box width bwidth (%f) must be greater than zero.' % bwidth)
    bwidth = float(bwidth)

    if not len(percentiles) == 3:
        raise Exception('Must provide exactly three percentiles (provided %s).' % str(percentiles))
    percentiles = sorted(percentiles)

    if ax == None:
        ax=plt.gca()

    #Scatter plot the data
    xjitter = (np.random.rand(len(data))*2-[1]*len(data))*jitter/2.0
    if dataplot:
        if label == None:
            ax.plot([x]*len(data)+xjitter,data,dcolor+dmarker,alpha=dalpha)
        else:
            ax.plot([x]*len(data)+xjitter,data,color=dcolor,linestyle='',marker=dmarker,alpha=dalpha,label=label)

    #Plot the box
    lowbox = stats.scoreatpercentile(data, percentiles[0])
    midline = stats.scoreatpercentile(data, percentiles[1])
    meanline = np.mean(data)
    highbox = stats.scoreatpercentile(data, percentiles[2])

    boxside = bwidth/2.0

    ax.plot([x-boxside,x+boxside],[lowbox,lowbox],bcolor)
    ax.plot([x-boxside,x+boxside],[highbox,highbox],bcolor)
    ax.plot([x-boxside,x-boxside],[lowbox,highbox],bcolor)
    ax.plot([x+boxside,x+boxside],[lowbox,highbox],bcolor)

    ax.plot([x-boxside,x+boxside],[midline,midline],bccolor)
    if mean:
        ax.plot([x-boxside,x+boxside],[meanline,meanline],bmcolor+'--')

    #Annotate the box
    if bannotate:
        ax.annotate(' Q'+str(percentiles[0]), xy = (x+boxside,lowbox),horizontalalignment='left', verticalalignment='center')
        ax.annotate(' Q'+str(percentiles[1]), xy = (x+boxside,midline),horizontalalignment='left', verticalalignment='center')
        ax.annotate(' Q'+str(percentiles[2]), xy = (x+boxside,highbox),horizontalalignment='left', verticalalignment='center')
        if mean:
            ax.annotate('mean     ', xy = (x-boxside,meanline), horizontalalignment = 'right', verticalalignment = 'center')

    #Format x-axis
    plt.xlim([x-2,x+2])
    ax.set_xticklabels([])
    ax.set_xticks([])

def plotECDF(data,color='k',linewidth=1.0,label=None):
    """Plots the empirical cumulative distribution function of the given data.

    Arguments:
        data -- a list of real data points.

    Keyword arguments:
        color -- the color of the plot line.
        linewidth -- the width of the plot line.
        label -- the label of the plot line, for legend purpose.
    """
    x = sorted(data)
    y = np.array(range(1,len(x)+1))/float(len(x))
    if label == None:
        plt.plot(x,y,color=color,linewidth=linewidth)
    else:
        plt.plot(x,y,color=color,label=label,linewidth=linewidth)


def plotHeatMap(values,xlabels,ylabels,colormap=None, minvalue=None,maxvalue=None,calpha=0.8,ax=None,annotate=False):
    """Plots a grid heatmap where the the (i,j)-th grid cell has color proportional to the
    value in values[xlabels[i]][ylabels[j]].

    Arguments:
        values -- a matrix of values as doubly list.
        xlabels -- the x-axis labels (length should be equal to values x-length).
        ylabels -- the y-axis labels (length should be equal to values y-length).


   Keyword arguments:
        colormap -- the colormap to use for deciding colors. Values are bounded in [0,1] with the minvalue and maxvalue, and then
                the color map is used to select the color.
        minvalue -- absolute minimum value allowed (any value smaller will be colored as the minvalue - 0 on the colormap).
        maxvalue -- absolute maximum value allowed (any value larger will be cored as the maxvalue - 1 on the colormap).
        calpha -- the alpha (transparency) value for the colored cells.
        annotate -- whether to annotate the map with the values itself.

   """

    #Verify the inputs.
    if not len(xlabels) == len(values):
        raise Exception('x-labels do not have same length as values length.')
    for i in range(len(xlabels)):
        if not len(ylabels) == len(values[i]):
            raise Exception('y-labels do not have the same length as values[%d] length.' % i)

    if colormap == None:
        colormap = plt.cm.binary

    if ax == None:
        ax=plt.gca()

    #Create the array of color values.
    mincolor = None
    maxcolor = None
    colors = np.zeros(shape=(len(xlabels),len(ylabels)))
    for i in range(len(xlabels)):
        colors[i] = [0]*len(ylabels)
        for j in range(len(ylabels)):

            value = values[i][j]

            colors[i][j] = value

    #Plot the heatmap
    plt.pcolor(colors,cmap=colormap, alpha=calpha, vmin=minvalue, vmax=maxvalue)

    #Format it
    ax.set_frame_on(False)

    ax.invert_yaxis()
    ax.xaxis.tick_top()

    plt.xticks(rotation=90)

    ax.set_yticks(np.arange(colors.shape[0])+0.5, minor=False)
    ax.set_xticks(np.arange(colors.shape[1])+0.5, minor=False)

    ax.set_xticklabels(ylabels, minor=False)
    ax.set_yticklabels(xlabels, minor=False)
    plt.xticks(rotation=90)

    ax = plt.gca()

    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
        
    if annotate:
        for y in range(colors.shape[0]):
            for x in range(colors.shape[1]):
                plt.text(x + 0.5, y + 0.5, '%.2f' % values[y][x],
                        horizontalalignment='center',
                        verticalalignment='center',
                        )
        
        
        

