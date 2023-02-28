"""
Homework 6

Created on Thu Feb 25 13:34:12 2023

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
from tabulate import tabulate

# Set working directories and seed

wdpath = '/Users/yifanliu/Documents/GitHub/phdee-2023-YL/homework6'
outputpath = wdpath + '/output'
datapath = wdpath + '/data'

np.random.seed(123)

# Load the data set

df = pd.read_csv(datapath + "/instrumentalvehicles.csv")
df.columns


# Q1: sharp or fuzzy RD
# It should be a sharp RD.
# The sharp RD ensures that the running variable completely determines the treatment, while the fuzzy RD appears when the threshold merely discontinuously increase the probability of treatment.
# In this case, the policy requires all vehicles longer than 225 inches must be equipped with the specific safety technology.

# Q2: scatter plot
# Define the value of the RD cutoff
cutoff = 225
# Create a new column 'length-cutoff' in the DataFrame
df['length-cutoff'] = df['length'] - cutoff
# Create a scatter plot with mpg on the y-axis and length-cutoff on the x-axis
plt.scatter(df['length-cutoff'], df['mpg'])
# Add a vertical line at the cutoff
plt.axvline(x=0, linestyle='--', color='red')
# Add axis labels and a title
plt.xlabel('Length - Cutoff')
plt.ylabel('MPG')
os.chdir(outputpath) # Output directly to LaTeX folder
plt.savefig('Q2.pdf',format='pdf')
# Show the plot
plt.show()



# Q3:
# Create a binary treatment indicator for values of 'length' greater than or equal to the cutoff
df['treatment'] = np.where(df['length'] >= cutoff, 1, 0)
# Define the degree of the polynomial
degree = 1
# Fit a first-order polynomial to both sides of the cutoff using the OLS method
# for the left and right sides separately
left_model = sm.OLS(df.query('`length` < @cutoff')['mpg'], 
                    sm.add_constant(df.query('`length` < @cutoff')['length-cutoff'])).fit()
right_model = sm.OLS(df.query('`length` >= @cutoff')['mpg'], 
                     sm.add_constant(df.query('`length` >= @cutoff')['length-cutoff'])).fit()

# Print the summary statistics for the regression models
print('Left model:\n', left_model.summary())
print('Right model:\n', right_model.summary())
## Output directly to LaTeX
os.chdir(outputpath) # Output directly to LaTeX folder
with open("Q3L.tex", "w") as f: f.write(left_model.summary().as_latex())
with open("Q3R.tex", "w") as f: f.write(right_model.summary().as_latex())

# Compute the first-stage treatment effect estimate
effect = right_model.params[1] - left_model.params[1]
print('First-stage treatment effect estimate: {:.4f}'.format(effect))
# First-stage treatment effect estimate: 0.0111


# Create a scatter plot with mpg on the y-axis and length-cutoff on the x-axis
plt.scatter(df['length-cutoff'], df['mpg'])
# Add a vertical line at the cutoff
plt.axvline(x=0, linestyle='--', color='red')
# Plot the fitted polynomials over the scatterplot
x_left = np.linspace(df.query('`length` < @cutoff')['length-cutoff'].min(), 0, 100)
y_left = left_model.predict(sm.add_constant(x_left))
plt.plot(x_left, y_left, color='blue', label='Left of cutoff')
x_right = np.linspace(0, df.query('`length` >= @cutoff')['length-cutoff'].max(), 100)
y_right = right_model.predict(sm.add_constant(x_right))
plt.plot(x_right, y_right, color='green', label='Right of cutoff')
# Add a legend, axis labels, and a title
plt.legend()
plt.xlabel('Length - Cutoff')
plt.ylabel('MPG')
plt.savefig('Q3.pdf',format='pdf')
plt.show()

y_right[0] - y_left[-1]

# Q4: second-order polynomial
plt.scatter(df['length-cutoff'], df['mpg'])
# Add a vertical line at the cutoff
plt.axvline(x=0, linestyle='--', color='red')
# Fit a second-order polynomial to the data on either side of the cutoff
x_left = df[df['length'] < cutoff]['length'] - cutoff
y_left = df[df['length'] < cutoff]['mpg']
model_left = sm.OLS(y_left, sm.add_constant(np.column_stack((x_left,x_left**2)))).fit()

x_right = df[df['length'] >= cutoff]['length'] - cutoff
y_right = df[df['length'] >= cutoff]['mpg']
model_right = sm.OLS(y_right, sm.add_constant(np.column_stack((x_right,x_right**2)))).fit()

# Generate a curve representing the estimated relationship between mpg and length - cutoff
x1 = np.linspace(df.query('`length` < @cutoff')['length-cutoff'].min(), 0, 100)
y_left = model_left.predict(sm.add_constant(np.column_stack((x1, x1**2))))
plt.plot(x1, y_left, color='blue', label='Left of cutoff')
x2 = np.linspace(0, df.query('`length` >= @cutoff')['length-cutoff'].max(), 100)
y_right = model_right.predict(sm.add_constant(np.column_stack((x2, x2**2))))
plt.plot(x2, y_right, color='green', label='Right of cutoff')

plt.legend()
plt.xlabel('Length - Cutoff')
plt.ylabel('MPG')
plt.savefig('Q4.pdf',format='pdf')
plt.show()

## Output directly to LaTeX
os.chdir(outputpath) # Output directly to LaTeX folder
with open("Q4L.tex", "w") as f: f.write(model_left.summary().as_latex())
with open("Q4R.tex", "w") as f: f.write(model_right.summary().as_latex())


# Estimate the impact of the policy on fuel efficiency around the cutoff
treatment_effect = y_right[0] - y_left[-1]
print('Treatment effect estimate:', treatment_effect)
model_left.summary()
model_right.summary()
# Treatment effect estimate: -8.05



# Q5: fifth-order polynomial
plt.scatter(df['length-cutoff'], df['mpg'])
# Add a vertical line at the cutoff
plt.axvline(x=0, linestyle='--', color='red')
# Fit a second-order polynomial to the data on either side of the cutoff
x_left = df[df['length'] < cutoff]['length'] - cutoff
y_left = df[df['length'] < cutoff]['mpg']
model_left = sm.OLS(y_left, sm.add_constant(np.column_stack((x_left,x_left**2,x_left**3,x_left**4,x_left**5)))).fit()

x_right = df[df['length'] >= cutoff]['length'] - cutoff
y_right = df[df['length'] >= cutoff]['mpg']
model_right = sm.OLS(y_right, sm.add_constant(np.column_stack((x_right,x_right**2,x_right**3,x_right**4,x_right**5)))).fit()

# Generate a curve representing the estimated relationship between mpg and length - cutoff
x1 = np.linspace(df.query('`length` < @cutoff')['length-cutoff'].min(), 0, 100)
y_left = model_left.predict(sm.add_constant(np.column_stack((x1, x1**2,x1**3,x1**4,x1**5))))
plt.plot(x1, y_left, color='blue', label='Left of cutoff')
x2 = np.linspace(0, df.query('`length` >= @cutoff')['length-cutoff'].max(), 100)
y_right = model_right.predict(sm.add_constant(np.column_stack((x2, x2**2,x2**3,x2**4,x2**5))))
plt.plot(x2, y_right, color='green', label='Right of cutoff')

plt.legend()
plt.xlabel('Length - Cutoff')
plt.ylabel('MPG')
plt.savefig('Q5.pdf',format='pdf')
plt.show()

## Output directly to LaTeX
os.chdir(outputpath) # Output directly to LaTeX folder
with open("Q5L.tex", "w") as f: f.write(model_left.summary().as_latex())
with open("Q5R.tex", "w") as f: f.write(model_right.summary().as_latex())

# Estimate the impact of the policy on fuel efficiency around the cutoff
treatment_effect = y_right[0] - y_right[-1]
print('Treatment effect estimate:', treatment_effect)
# Treatment effect estimate: -4.17


# Q6:
# add a column of ones named "one"
df = df.assign(one = pd.Series(1, index=df.index))
# (a) "weight" as the excluded instrument
# regress X on Z
# PWX = Z*inv(Z'*Z)*Z'*X
Z = df[['one','length-cutoff','car']] #set the discontinuity as a continuous variable
X = df[['one','mpg','car']]
PWX = np.matrix (Z @ np.linalg.inv(Z.T @ Z)) @ np.matrix(Z.T) @ X
# regress y on the fitted value 
# beta_2sls = inv(PWX'*PWX)*PWX'*y
y = df['price']
beta = np.linalg.inv(PWX.T @ PWX) @ PWX.T @ y
beta
# The average treatment effect is 162.43.
# In other words, one unit increase of mpg is expected to increase the vehicle sale price by 162.43 units, holding all other variables constant.

df['policy'] = 0
df['policy'][df['length']>225] = 1
# regress X on Z
# PWX = Z*inv(Z'*Z)*Z'*X
Z = df[['one','policy','car']] #set the discontinuity as a continuous variable
X = df[['one','mpg','car']]
PWX = np.matrix (Z @ np.linalg.inv(Z.T @ Z)) @ np.matrix(Z.T) @ X
# regress y on the fitted value 
# beta_2sls = inv(PWX'*PWX)*PWX'*y
y = df['price']
beta = np.linalg.inv(PWX.T @ PWX) @ PWX.T @ y
beta

















