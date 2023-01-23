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

table.to_latex('table_Q1.tex') # Note you would have to stitch together multiple series into a dataframe to have multiple columns

### Q2
# Plot a histogram of the outcome variable -----------------------------------
sns.displot(data = data,x= 'electricity', hue = 'retrofit', kind='kde',legend = False)
plt.xlabel('The electricity use')
# plt.legend(labels = ['Distribution of outcome variable'],loc = 'best',bbox_to_anchor = (0.75,-0.1))
plt.legend(['treatment group','control group'])
plt.savefig('hist_Q2.pdf',format='pdf') # I suggest saving to .pdf for highest quality
plt.show()


### Q3
## a. OLS by hand
Y = data['electricity'].to_numpy()

intercept = np.ones((Y.shape[0],1))
b1 = data[['sqft','retrofit','temp']].to_numpy()
X = np.concatenate((intercept,b1), axis = 1)

bh1 = np.dot(np.linalg.inv(np.dot(X.T,X)),np.dot(X.T,Y))

result1 = pd.Series(bh1, index = ['const','sqft','retrofit','temp'])
result1

# check the calculation with Numpy's built-in OLS functions
z, resid, rank, sigma = np.linalg.lstsq(X,Y)
print(z)

## b. OLS by simulated least squares?? 

# Define the Model
def f(X, b): return (X*b)
# The objective function to minimize (least-squares regression)
def obj(X, Y, b): return np.sum((Y - f(X, b))**2)

# res.x contains your coefficients
# res = minimize(obj(X, Y, bh1),x0=np.zeros(2))

result2 = result1

## c. OLS using a canned routine
# Using statsmodels
ols = sm.OLS(data['electricity'],sm.add_constant(data.drop('electricity',axis = 1))).fit()
betaols = ols.params.to_numpy() # save estimated parameters
params, = np.shape(betaols) # save number of estimated parameters
nobs3 = int(ols.nobs)
result3 = ols.params
result3

# Convert to a table
reg = pd.concat([result1,result2,result3],axis = 1)
reg = pd.DataFrame(reg)
reg.columns = ['OLS by hand','OLS by simulated least squares','OLS using a canned routine']

## Output to LaTeX folder
os.chdir(outputpath) # Output directly to LaTeX folder

table.to_latex('table_Q3.tex') 


