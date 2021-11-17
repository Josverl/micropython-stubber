# Minify normal version
python process.py minify
# Minify low_mem version
python .\process.py -s board\createstubs_mem.py -o minified\createstubs_mem.py minify
# Minify low_mem _ restartable version
# python .\process.py -s board\createstubs_mem_db.py -o minified\createstubs_mem_db.py minify
