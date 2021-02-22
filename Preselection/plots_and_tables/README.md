# Plotter code

---

One plotter to rule them all  
One plotter to find them  
One plotter to collect them all  
And in the output, plot them  

---

Use this plotter both in script mode and in jupyter notebook mode

### Requirements
* yahist
* mplhep

### Instructions

1. Initialize an instance of the `Plotter` class from `plots_and_tables/plotter.py`
    * Required arguments
        * `input` : Input DataFrame `pkl` or `hdf5` file, or an actual pandas `DataFrame` (useful in Jupyter notebook mode)
        * `plot_options` : A `json` file (or an equivalent `dict`) that contains the options for the plotter (More details below)
        * `branches` : A list of branches to plot
        * `debug` : Boolean that prints debug messages
    * In addition, an input `json` file (or an equivalent `dict`) corresponding to the `pkl` or `hdf5` file containing DataFrame details is also required

2. `run()` the instance to get plots

### Plotter `json` file contents
* Every main entry in the `json` file has the following format
    `{branch name : {bin type : <bin type>, bins : <bins>, processes : [List of physics processes involved for this plot], <other optional parameters>}}`
* A json file can have multiple such entries 

* Mandatory parameters
    * `bin type` : `linspace` or `list`. `linspace` means equally spaced bins, `list` means list of bin left edges
    * `bins` : array of 3 numbers (in case of `linspace`) or the bin left edges (in case of `list`). The three numbers for `linspace` are in the order [start point, end point, number of bins]

    * `processes` : List of physics processes that need to be plotted. Example list : [`GJets`, `VH`, `DiGamma`,`signal`, `Data`] (**Note the way Data is written with a capital D**)

* Optional parameters
    * `signal_scaling` : `float` - scales the signal by the factor provided by the `float`. This number is also written in the legend as (signal x scale factor)
    * `yaxis` : `linear` (default) or `log`
    * `title` : Branch name will be used by default
    * `cms_label` : `bool` that specifies whether 'CMS Preliminary' and '137.2 fb^-1' lumi should be drawn on the plot 
    * `xlabel` : X axis label. In the absence of x axis label, the title will be used
    * `ylim` : List of two numbers specifying the y axis limits. This will be fine-tuned further to accommodate the legend if required
    * `ratio_log` : Log ratio plot
    * `ratio_ylim` : Sets y limits for the ratio plots
    * `output_name` : string containing the output name
    * `stack`:`1` or `0` (default 1) Enables or disables stacking
    * `normalize`:`unit_area` - Normalizes the plots to unit area for shape comparisons. **NOTE : This disables stacking!**

### Sample test 
* Download `HggUnitTest.pkl`, `plot_options_test.json` and `HggUnitTest.json` from [here](http://uaf-10.t2.ucsd.edu/~bsathian/HHggTauTau_plotting/)
* Run `plotter.py`

### Known issues
* Axis rescaling to accommodate legend does not work if a data histogram is not present

### More features 
* Ability to provide custom colors
* Draw the dotted line at 1 for the ratio

