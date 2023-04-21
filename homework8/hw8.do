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
	
	
* Load the dataset
    use recycling_hw.dta


** Q1: a yearly plot of the recycling rate for NYC and the controls
egen avg_recyclingrate = mean(recyclingrate), by(year nyc nj ma)

twoway (line avg_recyclingrate year if nyc==1, sort) ///
       (line avg_recyclingrate year if nj==1, sort) ///
       (line avg_recyclingrate year if ma==1, sort), ///
        xtitle("Year") ytitle("Recycling Rate") ///
        legend(label(1 "NYC") label(2 "NJ") label(3 "MA"))

** Q2: TWFE regression



** Q3: synthetic DID




** Q4: event study




** Q5: synthetic control estimates 






