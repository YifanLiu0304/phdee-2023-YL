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
#from statsmodels.stats.sandwich_covariance import CovarianceSwitcher

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
# plt.title('Treatment and Control Trends of Bycatch Pounds by Month')
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
ols1 = sm.OLS(df1['bycatch'],sm.add_constant(df1[['pre','treated','treated:post']])).fit(cov_type='cluster', cov_kwds={'groups': df1['firm']})
ols1.summary()
betaols = np.round(ols1.params.to_numpy(),2) # save estimated parameters
seols = ols1.bse.to_numpy() # save clustered standard errors
params, = np.shape(betaols) # save number of estimated parameters
nobs1 = np.round(int(ols1.nobs),0)


seols = pd.Series(np.round(seols,2)) 
seols = '(' + seols.map(str) +  ')'
## Get output in order
order = [2,3,0]
output1 = pd.DataFrame(np.column_stack([betaols,seols])).reindex(order)

## Row and column names
rownames = pd.concat([pd.Series(['Treatment group(gamma)','When a firm is treated (delta)','Constant','Observations']),pd.Series([' ',' ',' '])],axis = 1).stack() # Note this stacks an empty list to make room for standard errors
colnames = ['Estimates (clustered standard errors)']
# colnames = ['Estimates','(s.d.)']

## Append se, # Observations, row and column names
output1 = pd.DataFrame(output1.stack().append(pd.Series(nobs1)))
output1.index = rownames
output1.columns = colnames

## Output directly to LaTeX
os.chdir(outputpath)
output1.to_latex('Q3a.tex')

with open("Q3a_full.tex", "w") as f: f.write(ols1.summary().as_latex())



'''
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
'''


# Q3
# (b) full monthly sample
# Create a new variable to indicate the time period
df['pre'] = (df['month'] < 13).astype(int)
df['post'] = (df['month'] > 12).astype(int)
# Create the interaction term
df['treated:post'] = df['treated'] * df['post']
# create a set of indicator variables for the months
month_dummies = pd.get_dummies(df['month'], prefix='month')
df = pd.concat([df, month_dummies], axis=1)

ols2 = sm.OLS(df['bycatch'],sm.add_constant(df.drop(['firm','month','bycatch','firmsize','shrimp','salmon','pre','post','month_13'],axis = 1))).fit(cov_type='cluster', cov_kwds={'groups': df['firm']})
# make month 13 as the benchmark, also remove multilinearity
ols2.summary()
#ols2.bse

betaols2 = np.round(ols2.params.to_numpy(),2) # save estimated parameters
seols2 = ols2.bse.to_numpy() # save clustered standard errors
params, = np.shape(betaols2) # save number of estimated parameters
nobs2 = np.round(int(ols2.nobs),0)

seols2 = pd.Series(np.round(seols2,2)) 
seols2 = '(' + seols2.map(str) +  ')'
## Get output in order
order = [1,2,0]
output2 = pd.DataFrame(np.column_stack([betaols2,seols2])).reindex(order)

## Row and column names
rownames = pd.concat([pd.Series(['Treatment group(gamma)','When a firm is treated (delta)','Constant','Observations']),pd.Series([' ',' ',' '])],axis = 1).stack() # Note this stacks an empty list to make room for standard errors
colnames = ['Estimates (clustered standard errors)']

## Append se, # Observations, row and column names
output2 = pd.DataFrame(output2.stack().append(pd.Series(nobs2)))
output2.index = rownames
output2.columns = colnames

## Output directly to LaTeX
os.chdir(outputpath)
output1.to_latex('Q3b.tex')
with open("Q3b_full.tex", "w") as f: f.write(ols2.summary().as_latex())



# Q3
# (c) add control variables
ols3 = sm.OLS(df['bycatch'],sm.add_constant(df.drop(['firm','month','bycatch','pre','post','month_13'],axis = 1))).fit(cov_type='cluster', cov_kwds={'groups': df['firm']})
# make month 13 as the benchmark, also remove multilinearity
ols3.summary()
#ols3.bse
betaols3 = np.round(ols3.params.to_numpy(),2) # save estimated parameters
seols3 = ols3.bse.to_numpy() # save clustered standard errors
params, = np.shape(betaols3) # save number of estimated parameters
nobs3 = np.round(int(ols3.nobs),0)

seols3 = pd.Series(np.round(seols3,2)) 
seols3 = '(' + seols3.map(str) +  ')'
## Get output in order
order = [2,5,0]
output3 = pd.DataFrame(np.column_stack([betaols3,seols3])).reindex(order)

## Row and column names
rownames = pd.concat([pd.Series(['Treatment group(gamma)','When a firm is treated (delta)','Constant','Observations']),pd.Series([' ',' ',' '])],axis = 1).stack() # Note this stacks an empty list to make room for standard errors
colnames = ['Estimates (clustered standard errors)']

## Append se, # Observations, row and column names
output3 = pd.DataFrame(output3.stack().append(pd.Series(nobs3)))
output3.index = rownames
output3.columns = colnames

## Output directly to LaTeX
os.chdir(outputpath)
output1.to_latex('Q3c.tex')
with open("Q3c_full.tex", "w") as f: f.write(ols3.summary().as_latex())


# Q3
# (d)
output1
output2
output3
output_all = pd.concat([output1, output2, output3], axis=1)
colnames = [('Estimates','(clustered s.d.)','(a)'),('Estimates','(clustered s.d.)','(b)'),('Estimates','(clustered s.d.)','(c)')] # three rows of column names
output_all.columns = pd.MultiIndex.from_tuples(colnames)
os.chdir(outputpath)
output_all.to_latex('Q3d.tex')























