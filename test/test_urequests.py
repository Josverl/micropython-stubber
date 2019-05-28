# LoBo Frozem Modules
# urequests 
#
import urequests
response = urequests.get("https://apithingspeak.com/update?api_key=MY_WRITE_API_KEY&field1=SOME_VALUE")
response.close()


