python3 -m pip install --user virtualenv
python3 -m venv env
source env/bin/activate

pip install --upgrade pip
pip install uproot awkward
pip install pandas
pip install numba==0.50.1
pip install tensorflow
