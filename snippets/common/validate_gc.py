# type: ignore
# BUG : https://github.com/Josverl/micropython-stubber/issues/270

# ref: https://learn.adafruit.com/Memory-saving-tips-for-CircuitPython/ram-saving-tips

import gc

# add other imports

gc.collect()
start_mem = gc.mem_free()
print(f"Point 1 Available memory: {start_mem} bytes")

# add code here to be measured for memory use

gc.collect()
end_mem = gc.mem_free()

print(f"Point 2 Available memory: {end_mem} bytes")
print(f"Code section 1-2 used {start_mem - end_mem} bytes")

# https://docs.micropython.org/en/latest/reference/constrained.html#the-heap
gc.collect()
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())


# https://docs.micropython.org/en/latest/reference/constrained.html#reporting

# import gc
import micropython

gc.collect()
micropython.mem_info()
print("-----------------------------")
print(f"Initial free: {gc.mem_free()} allocated: {gc.mem_alloc()}")


def func():
    a = bytearray(10000)


gc.collect()
print(f"Func definition: {gc.mem_free()} allocated: {gc.mem_alloc()}")
func()
print(f"Func run free: {gc.mem_free()} allocated: {gc.mem_alloc()}")
gc.collect()
print(f"Garbage collect free: {gc.mem_free()} allocated: {gc.mem_alloc()}")
print("-----------------------------")
micropython.mem_info(1)
