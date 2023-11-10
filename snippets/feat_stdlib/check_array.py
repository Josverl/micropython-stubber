import array

NUM_LEDS = 10

ar = array.array("I", [0 for _ in range(NUM_LEDS)])

x = ar[3] 
# type: ignore # TODO: __getitem__ not defined 
ar[3] = 0x12345678 
# type: ignore # TODO: __setitem__ not defined
