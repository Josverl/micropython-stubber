# FIXME: seperate script to work-around poetry install not making the commands executable / findable on CI 

# Minify normal version
python src/stubber/process.py minify -xc
# Minify low_mem version
python src/stubber/process.py minify -s board/createstubs_mem.py -o minified -xc
# Minify low_mem _ restartable version
python src/stubber/process.py minify -s board/createstubs_db.py -o minified -xc
