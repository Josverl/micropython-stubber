# Minify normal version
python process.py minify -xc
# Minify low_mem version
python process.py minify -s board/createstubs_mem.py -o minified -xc
# Minify low_mem _ restartable version
python process.py minify -s board/createstubs_db.py -o minified -xc
