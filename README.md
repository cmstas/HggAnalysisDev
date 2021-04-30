# HggAnalysisDev
Repository for developing H->gg analyses, starting from (skimmed) nanoAOD inputs.
Will contain machinery for the standard tasks in developing an H->gg analysis:
* Looping over nanoAOD and making yield tables + data/MC plots
* MVA training: MVA input file prep, tools for BDT/DNN training, writing output to an ntuple for SR optimization
* Signal region optimization: optimize cut(s) on MVA(s) to maximize expected sensitivity to some observable

## Set-up
* For first time setup, run `source setup.sh` to create a virtual environment for python3 and install all necessary packages.
* After the first time, you can activate your virtual environment with `source env/bin/activate`

## Development
* Keep track of to-do's, problems, and planned developments in the Issues tab
* For major revisions/additions, make a pull request
* For minor changes/bug fixes, commit directly to `main`
* Try to somewhat loosely adhere to [PEP 8 style guidlines](https://www.python.org/dev/peps/pep-0008/) (or at least make your code readable and add comments)
  * If you want adhere to PEP8, use `flake8` to check if your code adheres to it, and `black` to auto-format your code to adhere to PEP8 

## Tutorial
* A tutorial for new users is available [here](https://cmstas.github.io/HggAnalysisDev/) (in progress).
