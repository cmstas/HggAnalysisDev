python3 -m pip install --user virtualenv
python3 -m venv env
source env/bin/activate

pip install --upgrade pip

# For preselection
pip install xrootd==5.1.1
pip install uproot awkward
pip install pandas
pip install numba==0.50.1
pip install mplhep
pip install vector

# For plotting
pip install yahist

# For MVAs
pip install pyarrow
pip install tensorflow
pip install xgboost==1.2.1 # negative weights disallowed in xgboost 1.3
pip install scikit-learn
pip install tables
pip install matplotlib

# For SR Optimization
pip install zfit
pip install tensorflow


mkdir -p Preselection/output/
mkdir -p MVAs/output/
mkdir -p SR_Optimization/output/
