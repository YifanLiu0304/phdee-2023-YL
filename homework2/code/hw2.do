* Homework2
* Yifan Liu


* Start by clearing everything

	clear all // Note that in Stata, tabs don't mean anything, so I use them to organize nested parts of code to keep things looking clean.
	set more off // Prevents you from having to click more to see more output

* Set up your working directories

	* local datapath = "C:\Users\dbrewer30\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2023-DB\sample_code\output" // Typically, where you keep the data and where you want the outputs to go will be different.  In this sample code, this is not the case so I don't specify a data path.
	local outputpath = "C:\Users\yliu3494\Dropbox (GaTech)\phdee-2023-YL\phdee-2023-YL\homework2\output" 
	
	cd "`outputpath'"
	
* Download and use plotplainblind scheme

	ssc install blindschemes, all
	set scheme plotplainblind, permanently
	
* ON IAC VLAB server, you will need to ucomment this line and run this:

    sysdir set PERSONAL \\iac.nas.gatech.edu\yliu3494

	
* Load the dataset
import delimited "C:\Users\yliu3494\Dropbox (GaTech)\phdee-2023-YL\phdee-2023-YL\homework2\data\kwh.csv", clear

********************************************************************************
* Create summary statistics table

	* Generate estimates of mean, std dev, and t-test
	
		eststo nonretrofit: quietly estpost summarize electricity sqft temp if retrofit == 0
		eststo retrofit: quietly estpost summarize electricity sqft temp if retrofit == 1
		eststo diff: quietly estpost ttest electricity sqft temp, by(retrofit) unequal
		*esttab nonretrofit retrofit diff, cells("mean(pattern(1 1 0) fmt(3)) sd(pattern(1 1 0)) b(star pattern(0 0 1) fmt(3)) t(pattern(0 0 1) par fmt(3))") label
	
	* Generate the LaTeX table using esttab in this case
	
		esttab nonretrofit retrofit diff using stata_Q1.tex, tex cells("mean(pattern(1 1 0) fmt(2)) p(star pattern(0 0 1) fmt(3))" sd(pattern(1 1 0))) label nonumbers mtitles("Control" "Treatment" "Difference")
	
	
********************************************************************************
* twoway scatter plot

    twoway scatter electricity sqft, ytitle("electricity consumption (kWh)") xtitle("square feet of the home")
	graph export stata_Q2.pdf, replace
	
	
********************************************************************************
* Fit linear regression model

	reg electricity sqft retrofit temp // this is the basic regression.  It calculates standard errors assuming homoskedasticity by default.
	
	* If we want to bootstrap, we can ask Stata to bootstrap for us:

	reg electricity sqft retrofit temp, vce(bootstrap, reps(1000))
	
	
	* robust heteroskedasticity
	reg electricity sqft retrofit temp, vce(robust)
	estimates store robust
		
		
	* Write a table using outreg2
	
	outreg2 [robust] using stata_Q3.tex, label 2aster tex(frag) dec(2) replace ctitle("Ordinary least squares")
		



























