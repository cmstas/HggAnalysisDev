conda pack -n analysisenv --arcroot analysisenv -f --format tar.gz --compress-level 9 -j 8 --exclude "*.pyc" --exclude "*.js.map" --exclude "*.a"
