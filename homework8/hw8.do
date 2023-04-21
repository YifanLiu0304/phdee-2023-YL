* Homework8
* Yifan Liu


* Start by clearing everything

	clear all // Note that in Stata, tabs don't mean anything, so I use them to organize nested parts of code to keep things looking clean.
	set more off // Prevents you from having to click more to see more output

* Set up your working directories

	* local datapath = "C:\Users\dbrewer30\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2023-DB\sample_code\output" // Typically, where you keep the data and where you want the outputs to go will be different.  In this sample code, this is not the case so I don't specify a data path.
	local outputpath = "/Users/yifanliu/Documents/GitHub/phdee-2023-YL/homework8" 
	
	cd "`outputpath'"
	
* Download and use plotplainblind scheme

	ssc install blindschemes, all
	set scheme plotplainblind, permanently
	ssc install did_multiplegt, replace
	ssc install sdid, replace
	ssc  install reghdfe, replace
	
* Load the dataset
    use recycling_hw.dta, replace


** Q1: a yearly plot of the recycling rate for NYC and the controls
egen avg_recyclingrate = mean(recyclingrate), by(year nyc nj ma)

twoway (line avg_recyclingrate year if nyc==1, sort) ///
       (line avg_recyclingrate year if nj==1, sort) ///
       (line avg_recyclingrate year if ma==1, sort), ///
        xtitle("Year") ytitle("Recycling Rate") ///
        legend(label(1 "NYC") label(2 "NJ") label(3 "MA"))
graph export "recycling_rate_plot.pdf", replace		


** Q2: TWFE regression
keep if year <= 2004
gen pause = (year >= 2002 & year <= 2004) & nyc == 1
reghdfe recyclingrate pause, absorb(nyc year) cluster(region)
** Q2: The average treatment effect of the recycling pause is -.0619874 with a standard error of .0058256.


** Q3: synthetic DID 
* Use the predict command to generate the synthetic DID weights
* predict sdid_w
gen state = "nyc"
replace state = "nj" if nj==1
replace state = "ma" if ma==1

duplicates report state year
duplicates drop state year, force
sdid avg_recyclingrate state year pause, vce(placebo) seed(123) graph
graph export "Q3.pdf", replace		
** Q3: The average treatment effect of the recycling pause is -.06310 with a standard error of .03792.

* sdid recyclingrate state year pause, vce(placebo) seed(123) graph
* did_multiplegt recyclingrate nyc year pause, robust_dynamic cluster(fips)


** Q4: event study
use recycling_hw.dta, replace
egen avg_recyclingrate = mean(recyclingrate), by(year nyc nj ma)
gen pause = (year >= 2002 & year <= 2004) & nyc == 1

tab year, gen(y)
forval year=1(1)12 {
	gen dy_`year'= (nyc * y`year')
}	

reghdfe recyclingrate dy_1-dy_4 dy_6-dy_12 incomepercapita nonwhite, absorb(region year) cluster(region)
* set the year of 2001 as the benchmark
* year of 2002 (dy_6) is   -.0673386 with a standard error of .0072786.
coefplot, keep(dy*)  vertical omitted baselevels
graph export "Q4.pdf", replace		


** Q5: synthetic control estimates 




















