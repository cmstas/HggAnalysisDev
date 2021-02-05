python3 -m pip install --user virtualenv
python3 -m venv env
source env/bin/activate

pip install --upgrade pip

# For preselection
pip install uproot awkward
pip install pandas
pip install numba==0.50.1

# For MVAs
pip install tensorflow
pip install xgboost==1.2.1 # negative weights disallowed in xgboost 1.3
pip install scikit-learn
pip install tables
pip install matplotlib

mkdir -p Preselection/output/
mkdir -p MVAs/output/
mkdir -p SR_Optimization/output/
