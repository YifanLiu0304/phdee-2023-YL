# -*- coding: utf-8 -*-
"""
Homework 3

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

wdpath = r'C:\Users\enact\Dropbox (GaTech)\phdee-2023-YL\phdee-2023-YL\homework3'
outputpath = wdpath + '\output'
datapath = wdpath + '\data'

np.random.seed(123)

# Load the data set

df = pd.read_csv(datapath + "\kwh.csv")

### (e)
## log-transformed regression
## Using statsmodels
df['lnelectricity'] = np.log(df['electricity'])
df['lnsqft'] = np.log(df['sqft']) 
df['lntemp'] = np.log(df['temp']) 

ols = sm.OLS(df['lnelectricity'],sm.add_constant(df.drop(['electricity','sqft','temp','lnelectricity'],axis = 1))).fit()
betaols = ols.params.to_numpy() # save estimated parameters
params, = np.shape(betaols) # save number of estimated parameters
nobs = int(ols.nobs)
result1 = ols.params
result1

delta = np.exp(betaols[1])
gamma_lsqft = betaols[2]
gamma_ltemp = betaols[3]

# average marginal effects
ame_retrofit = sum(((delta - 1)*df['electricity']) / (delta**(df['retrofit'])))/nobs
ame_sqft = sum(gamma_lsqft*df['electricity']/df['sqft'])/nobs
ame_temp = sum(gamma_ltemp*df['electricity']/df['temp'])/nobs

# Bootstrap by hand and get confidence intervals -----------------------------
## Set values and initialize arrays to output to
breps = 1000 # number of bootstrap replications
olsbetablist = np.zeros((breps,params))

## Get an index of the data we will sample by sampling with replacement
bidx = np.random.choice(nobs,(nobs,breps)) # Generates random numbers on the interval [0,nobs3] and produces a nobs3 x breps sized array

## Sample with replacement to get the size of the sample on each iteration
for r in range(breps):
    ### Sample the data
    dfb = df.iloc[bidx[:,r]]
    ### Perform the estimation
    olsb = sm.OLS(dfb['lnelectricity'],sm.add_constant(dfb.drop(['electricity','sqft','temp','lnelectricity'],axis = 1))).fit()
    ### Output the result
    olsbetablist[r,:] = olsb.params.to_numpy()
    # ameb[r,:] = olsbetablist[r,:]*df['electricity']/df['temp']

########################### coefficient estimates
deltab = sum(np.exp(olsbetablist[:,1]))/nobs
gammab_lsqft = sum(olsbetablist[:,2])/nobs
gammab_ltemp = sum(olsbetablist[:,3])/nobs   
coef = np.array([deltab,gammab_lsqft,gammab_ltemp])
## Extract 2.5th and 97.5th percentile
retrofit_lb = np.percentile(np.exp(olsbetablist[:,1]),2.5,axis = 0,interpolation = 'lower')
retrofit_ub = np.percentile(np.exp(olsbetablist[:,1]),97.5,axis = 0,interpolation = 'higher')
sqft_lb = np.percentile(olsbetablist[:,2],2.5,axis = 0,interpolation = 'lower')
sqft_ub = np.percentile(olsbetablist[:,2],97.5,axis = 0,interpolation = 'higher')
temp_lb = np.percentile(olsbetablist[:,3],2.5,axis = 0,interpolation = 'lower')
temp_ub = np.percentile(olsbetablist[:,3],97.5,axis = 0,interpolation = 'higher')
coef_lb = np.array([retrofit_lb,sqft_lb,temp_lb])
coef_ub = np.array([retrofit_ub,sqft_ub,temp_ub])

############################# average marginal effects
ameb_retrofit = sum(((deltab - 1)*df['electricity']) / (deltab**(df['retrofit'])))/nobs  # Here I should not use the average deltab, gammab_lsqft, and gammab_ltemp. Instead, it should be incorporated in the loop.
ameb_sqft = sum(gammab_lsqft*df['electricity']/df['sqft'])/nobs
ameb_temp = sum(gammab_ltemp*df['electricity']/df['temp'])/nobs
ame = np.array([ameb_retrofit,ameb_sqft,ameb_temp])

## Extract 2.5th and 97.5th percentile for the average marginal effects
ameb_retrofit_lb = np.percentile(((deltab - 1)*df['electricity']) / (deltab**(df['retrofit'])),2.5,axis = 0,interpolation = 'lower')
ameb_retrofit_ub = np.percentile(((deltab - 1)*df['electricity']) / (deltab**(df['retrofit'])),97.5,axis = 0,interpolation = 'higher')
ameb_sqft_lb = np.percentile(gammab_lsqft*df['electricity']/df['sqft'],2.5,axis = 0,interpolation = 'lower')
ameb_sqft_ub = np.percentile(gammab_lsqft*df['electricity']/df['sqft'],97.5,axis = 0,interpolation = 'higher')
ameb_temp_lb = np.percentile(gammab_ltemp*df['electricity']/df['temp'],2.5,axis = 0,interpolation = 'lower')
ameb_temp_ub = np.percentile(gammab_ltemp*df['electricity']/df['temp'],97.5,axis = 0,interpolation = 'higher')
ameb_lb = np.array([ameb_retrofit_lb,ameb_sqft_lb,ameb_temp_lb])
ameb_ub = np.array([ameb_retrofit_ub,ameb_sqft_ub,ameb_temp_ub])

# Regression output table with CIs
## Format estimates and confidence intervals
coef = pd.Series(np.round(coef,2))
coef_lb = pd.Series(np.round(coef_lb,2)) # Round to two decimal places and get a Pandas Series version
coef_ub = pd.Series(np.round(coef_ub,2))
ci = '(' + coef_lb.map(str) + ', ' + coef_ub.map(str) + ')'


## Format average marginal effects and confidence intervals
ame = pd.Series(np.round(ame,2))
ame_lb = pd.Series(np.round(ameb_lb,2)) # Round to two decimal places and get a Pandas Series version
ame_ub = pd.Series(np.round(ameb_ub,2))
ame_ci = '(' + ame_lb.map(str) + ', ' + ame_ub.map(str) + ')'

null = np.array(['','',''])
null = pd.Series(null, index = ['retrofit','sqft','temp'])
coefficients = pd.concat([coef,ci],axis = 1).stack()
ame = pd.concat([ame,ame_ci],axis = 1).stack()
table = pd.concat([coefficients,ame],axis = 1)

## Add column and row labels.  Convert to dataframe (helps when you export it)
rownames = pd.concat([pd.Series(['retrofit (delta)','sqft (gamma1)','temp(gamma2)']),pd.Series([' ',' ',' '])],axis = 1).stack() # Note this stacks an empty list to make room for stdevs
colnames = [('Coefficient Estimates','(CI)'),('Average Marginal Effect Estimates','(CI)')] # three rows of column names

table = pd.DataFrame(table)
table.index = rownames
table.columns = pd.MultiIndex.from_tuples(colnames)

## Output directly to LaTeX
os.chdir(outputpath) # Output directly to LaTeX folder
table.to_latex('table_e.tex')


### (f)
# Plot average marginal effects with error bars -------------------------------------
ame2 = np.array([ameb_sqft,ameb_temp])
ameb2_lb = np.array([ameb_sqft_lb,ameb_temp_lb])
ameb2_ub = np.array([ameb_sqft_ub,ameb_temp_ub])
lowbar = np.array(ame2 - ameb2_lb)
highbar = np.array(ameb2_ub - ame2)
plt.errorbar(y = ame2, x = np.arange(2), yerr = [lowbar,highbar], fmt = 'o', capsize = 5)
plt.ylabel('Average marginal effects estimate')
plt.xticks(np.arange(2),['square fee of the home', 'outside temperature'])
plt.xlim((-0.5,1.5)) # Scales the figure more nicely
plt.axhline(linewidth=2, color='r')
plt.savefig('bar_f.pdf',format='pdf')
plt.show()



# whis1 =  np.array([0,0.05,0.5,0.95,1])
# plt.boxplot(gammab_lsqft*df['electricity']/df['sqft'])
# plt.xlabel('Average marginal effects of the square feet of the home')
# plt.savefig('graph_f1.pdf',format='pdf') 
# plt.boxplot(gammab_ltemp*df['electricity']/df['temp'])
# plt.xlabel('Average marginal effects of outdoor temperature')
# plt.savefig('graph_f2.pdf',format='pdf') 
# sns.boxplot(
    # data=[gammab_lsqft*df['electricity']/df['sqft'], gammab_ltemp*df['electricity']/df['temp']],
    # palette=[sns.xkcd_rgb["pale red"], sns.xkcd_rgb["medium green"]],
    # showmeans=True,
# )
# plt.savefig('graph_f3.pdf',format='pdf') 

