
mpremote mip install github:josverl/micropython-stubber

mpremote mip install github:josverl/micropython-stubber/mip/full.json@board_stubber

mpremote mip install github:josverl/micropython-stubber/mip/minified.json@board_stubber

mpremote mip install github:josverl/micropython-stubber/mip/mpy_v5.json@board_stubber


mpremote mip --target /lib install github:josverl/micropython-stubber/mip/mpy_v6.json@board_stubber 

mpremote mip --target /lib install http://localhost:8000/mip/mpy_v6.json@board_stubber 
mpremote mip --target /lib install http://localhost:8000/mip/mpy_v5.json@board_stubber 


# just a single file from http
mpremote mip --target /lib install http://localhost:8000/mip/v6/createstubs.py

# a package on http with http content 
mpremote mip --target /lib install http://localhost:8000/mip/http.json

# file:// urls or paths do not work :-( 
mpremote mip --target /lib install file://./mip/http.json


