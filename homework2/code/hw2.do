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
		esttab nonretrofit retrofit diff, cells("mean(pattern(1 1 0) fmt(3)) sd(pattern(1 1 0)) b(star pattern(0 0 1) fmt(3)) t(pattern(0 0 1) par fmt(3))") label
	
	* Generate the LaTeX table using esttab in this case
	
		esttab nonretrofit retrofit diff using summarystats.tex, tex cells(mean(fmt(2) label(Mean)) sd(fmt(2) par label(Std. Dev.))) replace label
	
	
********************************************************************************
* twoway scatter plot

    twoway scatter electricity sqft, ytitle("electricity consumption") xtitle("square feet")
	
	
********************************************************************************
* Fit linear regression model

	reg yvar x1 x2 // this is the basic regression.  It calculates standard errors assuming homoskedasticity by default.
	
	* If we want to bootstrap, we can ask Stata to bootstrap for us:

		reg yvar x1 x2, vce(bootstrap, reps(1000))
	
	* If we need to bootstrap ourselves (to incorporate two steps in the estimation for example), we can draw bootstrap samples and repeatedly estimate our regression:
	
		mat betas = J(1000,3,.) // pre-allocate a matrix for the outcomes of our 1000 regressions
	
		forvalues i = 1/1000 {
			preserve // preserves the data as it was in the memory at this point
				bsample // samples with replacement up to the number of observations
				
				reg yvar x1 x2
				
				mat betas[`i',1] = _b[x1] // save both
				mat betas[`i',2] = _b[x2]
				mat betas[`i',3] = _b[_cons]
			restore // restores the data as you preserved it originally
		}
		
	* You can just use the 25th and 975th largest estimates (2.5 and 97.5 percentiles) as the confidence interval, take the standard deviation of all the estimates as the standard error, or calculate the full covariance matrix of the boostrap estimates.  You can look at the "betas" by typing "mat list betas"
	
	* What I will do is get the full covariance matrix.
	
	* You can write a program to get Stata to replace the covariance matrix with the bootstrapped covariance matrix.  Doing this will let you use postestimation commands like outreg2 that make creating tables really easy.
	
		capture program drop bootstrapsample
		program define bootstrapsample, eclass
			tempname betas betas1 betas2 betas3
			mat `betas' = J(1000,3,.)
			forvalues i = 1/1000 {
				preserve
					bsample 
					quietly: reg yvar x1 x2
					
					mat `betas'[`i',1] = _b[x1] // save both
					mat `betas'[`i',2] = _b[x2]
					mat `betas'[`i',3] = _b[_cons]
					di `i' // lets you know the progress
				restore
			}
			svmat `betas', name(temp)
				corr temp1 temp2 temp3, cov // get the covariance matrix
				mat A = r(C) // save covariance matrix
				drop temp1 temp2 temp3
				
			reg yvar x1 x2 // rerun the regression
			ereturn repost V = A // post the new covariance matrix as the covariance matrix V that Stata uses
		end
		
		bootstrapsample // runs the program we wrote
		estimates store bootreg
		
	* Write a table using outreg2
	
		outreg2 [bootreg] using sampleoutput_stata.tex, label 2aster tex(frag) dec(2) replace ctitle("Ordinary least squares")
		
* Plot coefficients using coefplot
	
	coefplot, vertical yline(0) rename(_cons = "Constant") ytitle("Coefficient estimate")
	
	graph export samplebars_stata.pdf, replace
	



























