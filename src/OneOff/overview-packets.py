from stubber.publish.candidates import *

from stubber.publish.package import package_name

# # latest
# for c in frozen_candidates(boards="GENERIC", versions="auto"):
#     print(f"{package_name( **c) :50} | {c['port']:10}{c['board']:30} == {c['version']}")

matrix = {}
# for c in (frozen_candidates(boards="GENERIC", versions="auto")):
for c in frozen_candidates(boards="auto", versions="auto"):
    name = package_name(**c)
    if name not in matrix:
        matrix[name] = [c["version"]]
    else:
        matrix[name].append(c["version"])

for k, v in matrix.items():
    print(f"{k:50} | {str(v):>60}")


# print(tabulate(matrix, headers="keys"))
# print(tabulate(matrix, headers="keys", tablefmt="fancy_grid"))

# latest
for c in frozen_candidates():
    print(f"{package_name( **c) :50} | {c['port']:10}{c['board']:30} == {c['version']}")

"""
micropython-esp32-stubs                            | esp32     GENERIC                        == latest
micropython-esp32-lilygo_ttgo_lora32-stubs         | esp32     LILYGO_TTGO_LORA32             == latest
micropython-esp32-lolin_c3_mini-stubs              | esp32     LOLIN_C3_MINI                  == latest
micropython-esp32-lolin_s2_mini-stubs              | esp32     LOLIN_S2_MINI                  == latest
micropython-esp32-lolin_s2_pico-stubs              | esp32     LOLIN_S2_PICO                  == latest
micropython-esp32-m5stack_atom-stubs               | esp32     M5STACK_ATOM                   == latest
micropython-esp32-um_feathers2-stubs               | esp32     UM_FEATHERS2                   == latest
micropython-esp32-um_feathers2neo-stubs            | esp32     UM_FEATHERS2NEO                == latest
micropython-esp32-um_feathers3-stubs               | esp32     UM_FEATHERS3                   == latest
micropython-esp32-um_pros3-stubs                   | esp32     UM_PROS3                       == latest
micropython-esp32-um_tinypico-stubs                | esp32     UM_TINYPICO                    == latest
micropython-esp32-um_tinys2-stubs                  | esp32     UM_TINYS2                      == latest
micropython-esp32-um_tinys3-stubs                  | esp32     UM_TINYS3                      == latest
micropython-esp8266-stubs                          | esp8266   GENERIC                        == latest
micropython-mimxrt-stubs                           | mimxrt    GENERIC                        == latest
micropython-nrf-stubs                              | nrf       GENERIC                        == latest
micropython-nrf-arduino_nano_33_ble_sense-stubs    | nrf       arduino_nano_33_ble_sense      == latest
micropython-rp2-stubs                              | rp2       GENERIC                        == latest
micropython-rp2-arduino_nano_rp2040_connect-stubs  | rp2       ARDUINO_NANO_RP2040_CONNECT    == latest
micropython-rp2-pico_w-stubs                       | rp2       PICO_W                         == latest
micropython-samd-stubs                             | samd      GENERIC                        == latest
micropython-stm32-stubs                            | stm32     GENERIC                        == latest
micropython-stm32-arduino_portenta_h7-stubs        | stm32     ARDUINO_PORTENTA_H7            == latest
micropython-stm32-garatronic_pybstick26_f411-stubs | stm32     GARATRONIC_PYBSTICK26_F411     == latest
micropython-stm32-lego_hub_no6-stubs               | stm32     LEGO_HUB_NO6                   == latest
micropython-stm32-lego_hub_no7-stubs               | stm32     LEGO_HUB_NO7                   == latest
micropython-stm32-pybd_sf2-stubs                   | stm32     PYBD_SF2                       == latest
"""
