
* Homework5
* Yifan Liu


* Start by clearing everything

	clear all // Note that in Stata, tabs don't mean anything, so I use them to organize nested parts of code to keep things looking clean.
	set more off // Prevents you from having to click more to see more output

* Set up your working directories

	* local datapath = "C:\Users\dbrewer30\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2023-DB\sample_code\output" // Typically, where you keep the data and where you want the outputs to go will be different.  In this sample code, this is not the case so I don't specify a data path.
	local outputpath = "/Users/yifanliu/Documents/GitHub/phdee-2023-YL/homework5/output" 
	
	cd "`outputpath'"
	
* Download and use plotplainblind scheme

	ssc install blindschemes, all
	set scheme plotplainblind, permanently
	
	
* Load the dataset
import delimited "/Users/yifanliu/Documents/GitHub/phdee-2023-YL/homework5/data/instrumentalvehicles.csv"


** Q1
ivregress liml price car (mpg = weight), vce(robust)
estimates store m1
outreg2 [m1] using Q1_Stata.tex, label 2aster tex(frag) dec(2) replace ctitle("Limited information maximum likelihood estimates")


** Q2
ivregress liml price car (mpg = weight), vce(robust)
weakivtest
* The effective F statistics is 78.362 at 5% confidence level.
* The 5% critical value is 37.418.
* Since F statistics is larger than the critical value, we can reject the null hypothesis that the instrument is weak. In other words, we can safely use the instrument in this case.






