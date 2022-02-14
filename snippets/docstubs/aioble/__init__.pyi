from .central import scan as scan
from .core import GattError as GattError, config as config, log_error as log_error, log_warn as log_warn, stop as stop
from .device import Device as Device, DeviceDisconnectedError as DeviceDisconnectedError
from .peripheral import advertise as advertise
from .server import BufferedCharacteristic as BufferedCharacteristic, Characteristic as Characteristic, Descriptor as Descriptor, Service as Service, register_services as register_services
from typing import Any

ADDR_PUBLIC: Any
ADDR_RANDOM: Any
