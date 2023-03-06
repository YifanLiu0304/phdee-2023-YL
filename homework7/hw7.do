* Homework7
* Yifan Liu


* Start by clearing everything

	clear all // Note that in Stata, tabs don't mean anything, so I use them to organize nested parts of code to keep things looking clean.
	set more off // Prevents you from having to click more to see more output

* Set up your working directories

	* local datapath = "C:\Users\dbrewer30\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2023-DB\sample_code\output" // Typically, where you keep the data and where you want the outputs to go will be different.  In this sample code, this is not the case so I don't specify a data path.
	local outputpath = "/Users/yifanliu/Documents/GitHub/phdee-2023-YL/homework7" 
	
	cd "`outputpath'"
	
* Download and use plotplainblind scheme

	ssc install blindschemes, all
	set scheme plotplainblind, permanently
	
	
* Load the dataset
    use electric_matching.dta
	
** Q1 
* Generate a log outcome variable and a binary treatment variable that is equal to one if March 1, 2020 and after
gen logmw = log(mw)
gen treatment = 0
replace treatment = 1 if date >= 21975

*(a) 
encode zone, generate(zonen)
reg logmw i.zonen i.month i.dow i.hour treatment temp pcp, vce(robust)
* The coefficient estimate of treatment is -.0654671 with a heteroskedasticity-robust standard error of .0013594.

* (b)
drop if month == 1
drop if month == 2
teffects nnmatch (logmw temp pcp) (treatment), nneighbor(1) ematch(zonen dow hour month) vce(robust) dmvariables
* The coefficient estimate of treatment is -.0702609 with a heteroskedasticity-robust standard error of .0010031.

* (c)
* In order to deal with possible selection bias in the quasi-experiment, (a) adds covariates that explain the initial difference regardless of the pandemic, while (b) employs matching to find similar control groups for the treatment observations. 
* The issues with these approaches are that they did not control for history threat to internal validity. It might end up matching a pair of observations in different years. The variance in the outcome variable (electricity consumption) might come from variance in years instead of the pandemic. In other words, the true treatment effect can be obscured by events other than pandemic that happened during the period. 


** Q2
* add an indicator for year of sample
* (a)
use electric_matching.dta, replace
gen logmw = log(mw)
gen treatment = 0
replace treatment = 1 if date >= 21975
encode zone, generate(zonen)
reg logmw i.zonen i.month i.dow i.hour i.year treatment temp pcp, vce(robust)
* The coefficient estimate of treatment is .0250788  with a heteroskedasticity-robust standard error of .0027001.
* (b)
* This adds an indicator for year of sample, aiming to control for the variance in different years. This can help address the history threat to internal validity. In this way, the true treatment effect won't be obscured too much by events other than pandemic that happened during the period. 

** Q3
gen year2020 = 0
replace year2020 = 1 if year == 2020
keep if year == 2020 | year ==2019
teffects nnmatch (logmw temp pcp) (year2020), nneighbor(1) ematch(zonen dow hour month) gen(logmw_hat)  vce(robust) dmvariables



   










