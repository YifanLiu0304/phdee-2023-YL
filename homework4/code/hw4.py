# -*- coding: utf-8 -*-
"""
Homework 4

Created on Thu Jan 29 11:41:03 2023

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

wdpath = '/Users/yifanliu/Documents/GitHub/phdee-2023-YL/homework4'
#wdpath = r'C:\Users\enact\Dropbox (GaTech)\phdee-2023-YL\phdee-2023-YL\homework4'
outputpath = wdpath + '/output/'
datapath = wdpath + '/data/'

np.random.seed(4)

# Load the data set
df = pd.read_csv(datapath + "/fishbycatch.csv")
# Convert these panel data from wide to long form
df = pd.wide_to_long(df, stubnames=['shrimp','salmon','bycatch'], i='firm', j='month')
df.reset_index(inplace=True)
df.columns

# Q1
# Group the data by month and treatment
grouped = df.groupby(['month', 'treated'])
# Reset the index
grouped = grouped.mean().reset_index()
# Plot the Value column
plt.plot(grouped[grouped['treated'] == 1]['month'], grouped[grouped['treated'] == 1]['bycatch'], label='Treatment')
plt.plot(grouped[grouped['treated'] == 0]['month'], grouped[grouped['treated'] == 0]['bycatch'], label='Control')
# Add title and labels
plt.title('Treatment and Control Trends of Bycatch Pounds by Month')
plt.xlabel('Month')
plt.ylabel('Pounds of Bycatch')
# Specify the x-axis ticks
plt.xticks(grouped['month'].unique())
# Show legend
plt.legend()
# Show plot
os.chdir(outputpath)
plt.savefig('Q1.pdf',format='pdf')
plt.show()

## Before the treatment in January 2018 (Month 13), it seems there are parallel trends before treatment.


# Q2
# January 2018 (Month 13), December 2017 (Month 12)
# Define conditions
pre = grouped['month'] == 12
post = grouped['month'] == 13
control = grouped['treated'] == 0
treat = grouped['treated'] == 1

print(round(grouped[treat&post][['bycatch']].iloc[0]['bycatch'],2))
print(round(grouped[treat&pre][['bycatch']].iloc[0]['bycatch'],2))
print(round(grouped[control&post][['bycatch']].iloc[0]['bycatch'],2))
print(round(grouped[control&pre][['bycatch']].iloc[0]['bycatch'],2))

DID = (grouped[treat&post][['bycatch']].iloc[0]['bycatch'] - grouped[treat&pre][['bycatch']].iloc[0]['bycatch']) - (grouped[control&post][['bycatch']].iloc[0]['bycatch'] - grouped[control&pre][['bycatch']].iloc[0]['bycatch'])
DID = round(DID,2)
DID

## The estimate is -9591.35.
## It evluates the treatment effect of the program on the quantity of bycatch.


# Q3
# (a)
# Observations in January 2018 (Month 13) and December 2017 (Month 12) only
df1 = df[df['month'].isin([12, 13])]
df1['pre'] = (df1['month'] == 12).astype(int)
df1['post'] = (df1['month'] == 13).astype(int)
# Create the interaction term
df1['treated:post'] = df1['treated'] * df1['post']
ols1 = sm.OLS(df1['bycatch'],sm.add_constant(df1[['pre','treated','treated:post']])).fit()
betaols = ols1.params.to_numpy() # save estimated parameters
params, = np.shape(betaols) # save number of estimated parameters
nobs1 = int(ols1.nobs)
result1 = ols1.params
result1

# Bootstrap by hand and get confidence intervals -----------------------------
## Set values and initialize arrays to output to
breps = 1000 # number of bootstrap replications
olsbetablist1 = np.zeros((breps,params))

## Get an index of the data we will sample by sampling with replacement
bidx = np.random.choice(nobs1,(nobs1,breps)) # Generates random numbers on the interval [0,nobs3] and produces a nobs3 x breps sized array

## Sample with replacement to get the size of the sample on each iteration
for r in range(breps):
    ### Sample the data
    datab = df1.iloc[bidx[:,r]]
    
    ### Perform the estimation
    olsb = sm.OLS(datab['bycatch'],sm.add_constant(datab[['pre','treated','treated:post']])).fit()
    
    ### Output the result
    olsbetablist1[r,:] = olsb.params.to_numpy()
    
## Extract 2.5th and 97.5th percentile
lb = np.percentile(olsbetablist1,2.5,axis = 0,interpolation = 'lower')
ub = np.percentile(olsbetablist1,97.5,axis = 0,interpolation = 'higher')

# Regression output table with CIs
## Format estimates and confidence intervals
betaols = np.round(betaols,2)

lbP = pd.Series(np.round(lb,2)) # Round to two decimal places and get a Pandas Series version
ubP = pd.Series(np.round(ub,2))
ci = '(' + lbP.map(str) + ', ' + ubP.map(str) + ')'

## Get output in order
order = [1,2,3,0]
output1 = pd.DataFrame(np.column_stack([betaols,ci])).reindex(order)

## Row and column names
rownames = pd.concat([pd.Series(['Pre-period(lambda)','Treatment group(gamma)','When a firm is treated (delta))','Constant','Observations']),pd.Series([' ',' ',' ',' '])],axis = 1).stack() # Note this stacks an empty list to make room for CIs
colnames = ['Estimates']

## Append CIs, # Observations, row and column names
output1 = pd.DataFrame(output1.stack().append(pd.Series(nobs1)))
output1.index = rownames
output1.columns = colnames

## Output directly to LaTeX
os.chdir(outputpath)
output1.to_latex('Q3a.tex')


# Q3
# (b)















