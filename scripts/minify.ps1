# Minify normal version
stubber minify -xc
# Minify low_mem version
stubber minify -s board/createstubs_mem.py -o minified -xc
# Minify low_mem _ restartable version
stubber minify -s board/createstubs_db.py -o minified -xc
