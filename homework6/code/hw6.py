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
# It should be a fuzzy RD.
# The fuzzy RD appears when the threshold merely discontinuously increase the probability of treatment.
# In this case, the vehicle equipped with the technology, which meet the length requirement (longer than 225 inches), are significantly less fuel-efficient (lower mpg).


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



# Q4: 
# Fit a second-order polynomial to the data on either side of the cutoff
x1 = df[df['length'] < cutoff]['length'] - cutoff
y1 = df[df['length'] < cutoff]['mpg']
p1 = np.polyfit(x1, y1, 2)

x2 = df[df['length'] >= cutoff]['length'] - cutoff
y2 = df[df['length'] >= cutoff]['mpg']
p2 = np.polyfit(x2, y2, 2)

# Generate a curve representing the estimated relationship between mpg and length - cutoff
x = np.linspace(df['length'].min() - cutoff, df['length'].max() - cutoff, 100)
y1_pred = np.polyval(p1, x)
y2_pred = np.polyval(p2, x)

# Plot the curve over a scatterplot of the data
fig, ax = plt.subplots()
ax.scatter(df['length'] - cutoff, df['mpg'], alpha=0.5)
ax.plot(x_left, y1_pred, 'blue', label='2nd-order polynomial (left)')
ax.plot(x_right, y2_pred, 'green', label='2nd-order polynomial (right)')
ax.axvline(0, color='red', linestyle='--')
ax.legend()
ax.set_xlabel('length - cutoff')
ax.set_ylabel('mpg')
plt.savefig('Q4.pdf',format='pdf')
plt.show()

# Estimate the impact of the policy on fuel efficiency around the cutoff
treatment_effect = y2_pred[0] - y1_pred[-1]
print('Treatment effect estimate:', treatment_effect)
# Treatment effect estimate: 2.91



# Q5:
# Fit a fifth-order polynomial to the data on either side of the cutoff
x1 = df[df['length'] < cutoff]['length'] - cutoff
y1 = df[df['length'] < cutoff]['mpg']
p1 = np.polyfit(x1, y1, 5)

x2 = df[df['length'] >= cutoff]['length'] - cutoff
y2 = df[df['length'] >= cutoff]['mpg']
p2 = np.polyfit(x2, y2, 5)

# Generate a curve representing the estimated relationship between mpg and length - cutoff
x = np.linspace(df['length'].min() - cutoff, df['length'].max() - cutoff, 100)
y1_pred = np.polyval(p1, x)
y2_pred = np.polyval(p2, x)

# Plot the curve over a scatterplot of the data
fig, ax = plt.subplots()
ax.scatter(df['length'] - cutoff, df['mpg'], alpha=0.5)
ax.plot(x_left, y1_pred, 'r', label='5th-order polynomial (left)')
ax.plot(x_right, y2_pred, 'g', label='5th-order polynomial (right)')
ax.axvline(0, color='k', linestyle='--')
ax.legend()
ax.set_xlabel('length - cutoff')
ax.set_ylabel('mpg')
plt.savefig('Q5.pdf',format='pdf')
plt.show()

# Estimate the impact of the policy on fuel efficiency around the cutoff
treatment_effect = y2_pred[0] - y1_pred[-1]
print('Treatment effect estimate:', treatment_effect)
# Treatment effect estimate: -5279.63


# Q6:
# add a column of ones named "one"
df = df.assign(one = pd.Series(1, index=df.index))
# (a) "weight" as the excluded instrument
# regress X on Z
# PWX = Z*inv(Z'*Z)*Z'*X
Z = df[['one','length-cutoff','car']]
X = df[['one','mpg','car']]
PWX = np.matrix (Z @ np.linalg.inv(Z.T @ Z)) @ np.matrix(Z.T) @ X
# regress y on the fitted value 
# beta_2sls = inv(PWX'*PWX)*PWX'*y
y = df['price']
beta = np.linalg.inv(PWX.T @ PWX) @ PWX.T @ y
beta
# The average treatment effect is 162.43.
# In other words, one unit increase of mpg is expected to increase the vehicle sale price by 162.43 units, holding all other variables constant.





















