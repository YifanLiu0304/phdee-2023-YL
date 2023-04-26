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
	ssc install reghdfe, replace
	ssc install synth, all
	
* Load the dataset
    use recycling_hw.dta, replace


** Q1: a yearly plot of the recycling rate for NYC and the controls
egen avg_recyclingrate = mean(recyclingrate), by(year nyc nj ma)

twoway (line avg_recyclingrate year if nyc==1, sort) ///
       (line avg_recyclingrate year if nj==1, sort) ///
       (line avg_recyclingrate year if ma==1, sort), ///
        xtitle("Year") ytitle("Recycling Rate") ///
        legend(label(1 "NYC") label(2 "NJ") label(3 "MA"))
graph export "Q1.pdf", replace		


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
gen state = "nyc"
replace state = "nj" if nj==1
replace state = "ma" if ma==1

* (a) The plot of raw outcomes for treated and control groups over time
egen avg_recyclingrate2 = mean(recyclingrate), by(year nyc)
twoway (line avg_recyclingrate2 year if nyc==1, sort) ///
       (line avg_recyclingrate2 year if nyc==0, sort), ///
        xtitle("Year") ytitle("Recycling Rate") ///
        legend(label(1 "Treatment") label(2 "Control")) 
graph export "Q5a.pdf", replace		

graph twoway (line recyclingrate year if stateregionid != "NYC", lc(gray)) ///
            (line recyclingrate year if stateregionid == "NYC", lc(black)), ///
			xtitle("Year") ytitle("Recycling Rate") ///
			xlabel(1997(2)2008) legend(label(1 "Controls") label(2 "NYC"))
graph export "Q5aa.pdf", replace		

* (b) The plot of raw outcomes for treated group and synthetic control group over time
* net install synth_runner, from(https://raw.github.com/bquistorff/synth_runner/master/) replace
encode state, gen(nstate)
encode region, gen(nregion)
egen average_nyc = mean(recyclingrate) if nyc ==1, by(year nyc)
* make average_nyc represent the outcome variable, also for MA and NJ
replace average_nyc = recyclingrate if average_nyc ==. 
drop if region == "Bronx" |region == "Queens"
sort state region year
egen stateregionid = concat(state region)
replace stateregionid = "NYC" if stateregionid == "nycBrooklyn"
encode stateregionid, gen(nstateregion)
tab nstateregion
rename average_nyc outcomes

tsset nstateregion year
synth outcomes incomepercapita(1997(1)2001) nonwhite(1997(1)2001) munipop2000 collegedegree2000 democratvoteshare2000, trunit(1) trperiod(2002) fig
graph export "Q5b.pdf", replace

synth_runner outcomes incomepercapita(1997(1)2001) nonwhite(1997(1)2001) munipop2000 collegedegree2000 democratvoteshare2000, trunit(1) trperiod(2002) gen_vars

effect_graphs , trlinediff(-1) effect_gname(effect) tc_gname(outcomes_synth)
single_treatment_graphs, trlinediff(-1) raw_gname(outcomes) effects_gname(effects) 
* (c) The plot of estimated synthetic control effects and placebo effects over time
* effect: a variable that contains the difference between the unit's outcome and its synthetic control for that time period.
graph twoway (line effect year if stateregionid != "NYC", lc(gray)) ///
            (line effect year if stateregionid == "NYC", lc(black)), ///
			xtitle("Year") ytitle("Recycling Rate") ///
			xlabel(1997(2)2008) legend(label(1 "Donors") label(2 "NYC")) ///
graph export "Q5c.pdf", replace


* (d) The plot of final synthetic control estimates over time
* depvar_synth: a variable that contains the unit's synthetic control outcome for that time period.
graph twoway (line outcomes_synth year if stateregionid != "NYC", lc(gray)) ///
            (line outcomes_synth year if stateregionid == "NYC", lc(black)), ///
			xtitle("Year") ytitle("Recycling Rate") ///
			xlabel(1997(2)2008) legend(label(1 "Donors") label(2 "NYC")) ///
graph export "Q5d.pdf", replace













