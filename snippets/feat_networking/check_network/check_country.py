# ref : https://docs.micropython.org/en/latest/rp2/quickref.html

import network

# set your Wifi country code
network.country("NL")  # type: ignore # TODO : micropython.network -  esp8266 has no network.country() method
