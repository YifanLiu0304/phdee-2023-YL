* Homework3
* Yifan Liu


* Start by clearing everything

	clear all // Note that in Stata, tabs don't mean anything, so I use them to organize nested parts of code to keep things looking clean.
	set more off // Prevents you from having to click more to see more output

* Set up your working directories

	* local datapath = "C:\Users\dbrewer30\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2023-DB\sample_code\output" // Typically, where you keep the data and where you want the outputs to go will be different.  In this sample code, this is not the case so I don't specify a data path.
	local outputpath = "C:\Users\yliu3494\Dropbox (GaTech)\phdee-2023-YL\phdee-2023-YL\homework2\output" 
	
	cd "`outputpath'"

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

* Fit linear regression model

    generate lnelectricity = ln(electricity)
	generate lnsqft = ln(sqft)
	generate lntemp = ln(temp)

	reg lnelectricity retrofit lnsqft lntemp  // this is the basic regression.  It calculates standard errors assuming homoskedasticity by default.
	margins, dydx(retrofit lnsqft)
	
	* If we want to bootstrap, we can ask Stata to bootstrap for us:

	reg lnelectricity retrofit lnsqft lntemp , vce(bootstrap, reps(1000))
	margins, dydx(retrofit lnsqft)

********************************************************************************
* Generate the results table

    













