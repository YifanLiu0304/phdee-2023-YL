* Homework4
* Yifan Liu


* Start by clearing everything

	clear all // Note that in Stata, tabs don't mean anything, so I use them to organize nested parts of code to keep things looking clean.
	set more off // Prevents you from having to click more to see more output

* Set up your working directories

	* local datapath = "C:\Users\dbrewer30\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2023-DB\sample_code\output" // Typically, where you keep the data and where you want the outputs to go will be different.  In this sample code, this is not the case so I don't specify a data path.
	local outputpath = "/Users/yifanliu/Documents/GitHub/phdee-2023-YL/homework4/output" 
	
	cd "`outputpath'"
	
* Download and use plotplainblind scheme

	ssc install blindschemes, all
	set scheme plotplainblind, permanently
	
	
* Load the dataset
import delimited "/Users/yifanliu/Documents/GitHub/phdee-2023-YL/homework4/data/fishbycatch.csv"
* Reshape the dataset
reshape long shrimp salmon bycatch, i(firm) j(month)

* (a)
* Generate the indicator variables for each firm
local i = 1
forvalues i = 1/50 {
    gen is_firm`i' = 0
    replace is_firm`i' = 1 if firm == `i'
}

local j = 1
forvalues j = 1/24 {
    gen is_month`j' = 0
    replace is_month`j' = 1 if month == `j'
}

gen post = 0 
replace post = 1 if month > 12
gen treat_post = treated * post

regress bycatch treat_post firmsize shrimp salmon is_firm1-is_month12 is_month14-is_month24, cluster(firm)
estimates store m1
esttab m1, label star(* 0.10 ** 0.05 *** 0.01)
eststo: estout using Q1a_Stata.tex, replace label

* (b)
* Store the group mean in a new variable
egen mean_bycatch = mean(bycatch), by (month)
* Demean the dependent variable
gen bycatch_demean = bycatch - mean_bycatch

* Demean the independent variables
foreach var in treat_post firmsize shrimp salmon {
  egen mean_`var' = mean(`var'), by (month)
  gen `var'_demean = `var' - mean_`var'
}

regress bycatch_demean treat_post_demean firmsize_demean shrimp_demean salmon_demean, cluster(firm)
estimates store m2
esttab m2, label star(* 0.10 ** 0.05 *** 0.01)
eststo: estout using Q1b_Stata.tex, replace label

* change the name of one of the regression coefficients
* rename m2 _b[treat_post_demean] treat_post
* view the renamed results
* estimates table m2


* (c)
esttab m1 m2, label star(* 0.10 ** 0.05 *** 0.01)
* eresults m1, varnames(treat_post firmsize shrimp. salmon Constant)







