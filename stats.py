"""
Various statistical related utilities.
@author Alexandre Frechette (afrechet@cs.ubc.ca)
"""
import numpy as np
import scipy as stats
import random

def bootstrap(data,n=None,seed=None):
    """Return a bootstrap sample in list form of the provided data.

    Arguments:
    data - a sequence of data samples.

    Keyword Arguments:
    n - the size of the boostrap sample to take, defaults the provided data size.
    seed - the seed to use when sampling, defaults to no seed.
    """

    #Verify the input.
    if n == None:
        n = len(data)
    if n<=0:
        raise Exception('Provided size of bootstrap sample n (%d) must be strictly positive.' % n)
    if not seed == None:
        random.seed(seed)

    #Construct bootstrap sample.
    bs = []
    for i in range(n):
        bs.append(random.choice(data))

    return bs

