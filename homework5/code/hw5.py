#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Homework 5

Created on Thu Feb 16 13:34:12 2023

@author: Yifan Liu

"""


# Clear all

from IPython import get_ipython
get_ipython().magic('reset -sf')

# Import packages - you may need to type "conda install numpy" the first time you use a package, for example.

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy.optimize import minimize
from scipy import stats

# Set working directories and seed

wdpath = '/Users/yifanliu/Documents/GitHub/phdee-2023-YL/homework5'
outputpath = wdpath + '/output'
datapath = wdpath + '/data'

np.random.seed(123)

# Load the data set

df = pd.read_csv(datapath + "/instrumentalvehicles.csv")
df.columns


# Q1: OLS 
ols = sm.OLS(df['price'],sm.add_constant(df.drop(['price','weight','height','length'],axis = 1))).fit()
ols.summary()

os.chdir(outputpath)
with open("Q1.tex", "w") as f: f.write(ols.summary().as_latex())


# Q2: 
# The price also affects the fuel effciency in miles per gallon.

# Q3: IV
# (a)
# (b)
# (c)

















