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
from linearmodels.iv import IVGMM

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
# The endogeneity might result from simultaneity.
# While the fuel efficiency affects the price, the price also affects the fuel effciency in miles per gallon.
# In other words, the fuel efficiency and the price are determined by each other.
# A change in error term causes the price to change, which causes the fuel efficiency to change. Therefore, the error term and the fuel efficiency are not independent.


# Q3: IV
# add a column of ones named "one"
df = df.assign(one = pd.Series(1, index=df.index))
# (a) "weight" as the excluded instrument
# regress X on Z
# PWX = Z*inv(Z'*Z)*Z'*X
Z1 = df[['one','weight','car']]
X = df[['one','mpg','car']]
PWX1 = np.matrix (Z1 @ np.linalg.inv(Z1.T @ Z1)) @ np.matrix(Z1.T) @ X
# regress y on the fitted value 
# beta_2sls = inv(PWX'*PWX)*PWX'*y
y = df['price']
beta1 = np.linalg.inv(PWX1.T @ PWX1) @ PWX1.T @ y


# (b)
df['weight2'] = df['weight'].apply(lambda x: x**2) 
# regress X on Z
# PWX = Z*inv(Z'*Z)*Z'*X
Z2 = df[['one','weight2','car']]
X = df[['one','mpg','car']]
PWX2 = np.matrix (Z2 @ np.linalg.inv(Z2.T @ Z2)) @ np.matrix(Z2.T) @ X
# regress y on the fitted value 
y = df['price']
beta2 = np.linalg.inv(PWX2.T @ PWX2) @ PWX2.T @ y


# (c)
# regress X on Z
# PWX = Z*inv(Z'*Z)*Z'*X
Z3 = df[['one','height','car']]
X = df[['one','mpg','car']]
PWX3 = np.matrix (Z3 @ np.linalg.inv(Z3.T @ Z3)) @ np.matrix(Z3.T) @ X
# regress y on the fitted value 
y = df['price']
beta3 = np.linalg.inv(PWX3.T @ PWX3) @ PWX3.T @ y

# (d)
# (e)
beta = pd.concat([beta1, beta2, beta3], axis=1)
# change the row names
new_index = ['constant', 'mpg', 'car']
beta.index = new_index
# change the column names
new_columns = ['weight as IV', 'weight2 as IV','height as IV']
beta.columns = new_columns
beta

## Output directly to LaTeX
os.chdir(outputpath) # Output directly to LaTeX folder
beta.to_latex('3e.tex')


# Q4: IVGMM
# Define dependent, independent, and excluded variables
exog = df[['one', 'car']]
endog = df['mpg']
z = df['weight']

# Define IVGMM model
model = IVGMM(dependent = y, endog = endog, exog = exog, instruments=z)

# Fit the model
results = model.fit()
results
os.chdir(outputpath) # Output directly to LaTeX folder
beta.to_latex('Q4.tex')















