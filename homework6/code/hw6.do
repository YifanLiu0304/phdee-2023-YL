
* Homework6
* Yifan Liu


* Start by clearing everything

	clear all // Note that in Stata, tabs don't mean anything, so I use them to organize nested parts of code to keep things looking clean.
	set more off // Prevents you from having to click more to see more output

* Set up your working directories

	* local datapath = "C:\Users\dbrewer30\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2023-DB\sample_code\output" // Typically, where you keep the data and where you want the outputs to go will be different.  In this sample code, this is not the case so I don't specify a data path.
	local outputpath = "/Users/yifanliu/Documents/GitHub/phdee-2023-YL/homework6/output" 
	
	cd "`outputpath'"
	
	
* Load the dataset
import delimited "/Users/yifanliu/Documents/GitHub/phdee-2023-YL/homework6/data/instrumentalvehicles.csv"


* Q1 (a)
generate cutoff = 225
generate len_cut = length - cutoff
rdrobust mpg length, c(225) p(2) bwselect(mserd) covs(car)





* Q1 (b)
