# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 15:41:03 2023

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

wdpath = r'C:\Users\enact\Dropbox (GaTech)\phdee-2023-YL\phdee-2023-YL\homework2'
outputpath = wdpath + '\output'
datapath = wdpath + '\data'

np.random.seed(202301221)

# Load the data set

data = pd.read_csv(datapath + "\kwh.csv")

### Q1
# Generate a table of means and standard deviations for the observed variables (there are faster ways to do this that are less general)
## Generate means
means_c = data.loc[data["retrofit"] == 0][['electricity','sqft','temp']].mean()
means_t = data.loc[data["retrofit"] == 1][['electricity','sqft','temp']].mean()

## Generate standard deviations
stdev_c = data.loc[data["retrofit"] == 0][['electricity','sqft','temp']].std()
stdev_t = data.loc[data["retrofit"] == 1][['electricity','sqft','temp']].std()

## Generate p value for t-test
diff = stats.ttest_ind(data.loc[data["retrofit"] == 0][['electricity','sqft','temp']],data.loc[data["retrofit"] == 1][['electricity','sqft','temp']])
pvalue = diff[1]
p = pd.Series(pvalue, index = ['electricity','sqft','temp'])

## Set the row and column names
rownames = pd.concat([pd.Series(['electricity','sqft','temp']),pd.Series([' ',' ',' '])],axis = 1).stack() # Note this stacks an empty list to make room for stdevs
colnames = [('Mean','(s.d.)','control group'),('Mean ','(s.d.)','treatment group'),('P-value ','of t-test','between two groups')] # three rows of column names

## Format means and std devs to display to two decimal places
means_c = means_c.map('{:.2f}'.format)
means_t = means_t.map('{:.2f}'.format)
stdev_c = stdev_c.map('({:.2f})'.format)
stdev_t = stdev_t.map('({:.2f})'.format)

## Align std deviations under means and add observations
null = np.array(['','',''])
null = pd.Series(null, index = ['electricity','sqft','temp'])
colc = pd.concat([means_c,stdev_c],axis = 1).stack()
colt = pd.concat([means_t,stdev_t],axis = 1).stack()
p_null = pd.concat([p,null],axis = 1).stack()
table = pd.concat([colc,colt,p_null],axis = 1)

## Add column and row labels.  Convert to dataframe (helps when you export it)
table = pd.DataFrame(table)
table.index = rownames
table.columns = pd.MultiIndex.from_tuples(colnames)

## Output to LaTeX folder
os.chdir(outputpath) # Output directly to LaTeX folder

table.to_latex('table.tex') # Note you would have to stitch together multiple series into a dataframe to have multiple columns

### Q2
# Plot a histogram of the outcome variable -----------------------------------
sns.displot(data = data,x= 'electricity', hue = 'retrofit', kind='kde',legend = True)
plt.xlabel('The electricity use')
plt.savefig('samplehist.pdf',format='pdf') # I suggest saving to .pdf for highest quality
plt.show()


### Q3

















# Fit a linear regression model to the data ----------------------------------
## Using statsmodels
ols = sm.OLS(data['Outcome'],sm.add_constant(data.drop('Outcome',axis = 1))).fit()
betaols = ols.params.to_numpy() # save estimated parameters
params, = np.shape(betaols) # save number of estimated parameters
nobs3 = int(ols.nobs)

# Bootstrap by hand and get confidence intervals -----------------------------
## Set values and initialize arrays to output to
breps = 1000 # number of bootstrap replications
olsbetablist = np.zeros((breps,params))

## Get an index of the data we will sample by sampling with replacement
bidx = np.random.choice(nobs3,(nobs3,breps)) # Generates random numbers on the interval [0,nobs3] and produces a nobs3 x breps sized array

## Sample with replacement to get the size of the sample on each iteration
for r in range(breps):
    ### Sample the data
    datab = data.iloc[bidx[:,r]]
    
    ### Perform the estimation
    olsb = sm.OLS(datab['Outcome'],sm.add_constant(datab.drop('Outcome',axis = 1))).fit()
    
    ### Output the result
    olsbetablist[r,:] = olsb.params.to_numpy()
    
## Extract 2.5th and 97.5th percentile
lb = np.percentile(olsbetablist,2.5,axis = 0,interpolation = 'lower')
ub = np.percentile(olsbetablist,97.5,axis = 0,interpolation = 'higher')

# Regression output table with CIs
## Format estimates and confidence intervals
betaols = np.round(betaols,2)

lbP = pd.Series(np.round(lb,2)) # Round to two decimal places and get a Pandas Series version
ubP = pd.Series(np.round(ub,2))
ci = '(' + lbP.map(str) + ', ' + ubP.map(str) + ')'

## Get output in order
order = [1,2,0]
output = pd.DataFrame(np.column_stack([betaols,ci])).reindex(order)

## Row and column names
rownames = pd.concat([pd.Series(['Variable 1','Variable 2','Constant','Observations']),pd.Series([' ',' ',' '])],axis = 1).stack() # Note this stacks an empty list to make room for CIs
colnames = ['Estimates']

## Append CIs, # Observations, row and column names
output = pd.DataFrame(output.stack().append(pd.Series(nobs3)))
output.index = rownames
output.columns = colnames

## Output directly to LaTeX
output.to_latex('sampleoutput.tex')


