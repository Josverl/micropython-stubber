
pip install -U micropython-stdlib-minimal --target ./typings --no-user
# pip install micropython-esp32-stubs --target ./typings --no-user

$PyPi = $False

if ($PyPi) {
    pip install -U micropython-stm32-stubs --target .snippets/stm32/typings --no-user
    pip install -U micropython-esp32-stubs --target .snippets/esp32/typings --no-user
    pip install -U micropython-esp8266-stubs --target .snippets/esp8266/typings --no-user
    pip install -U micropython-rp2-stubs --target .snippets/rp2/typings --no-user
} else {
    pip install -U C:\develop\MyPython\micropython-stubber\repos\micropython-stubs\publish\micropython-v1_19_1-stm32-stubs --target .snippets/stm32/typings --no-user
    pip install -U C:\develop\MyPython\micropython-stubber\repos\micropython-stubs\publish\micropython-v1_19_1-esp32-stubs --target .snippets/esp32/typings --no-user
    pip install -U C:\develop\MyPython\micropython-stubber\repos\micropython-stubs\publish\micropython-v1_19_1-esp8266-stubs --target .snippets/esp8266/typings --no-user
    pip install -U C:\develop\MyPython\micropython-stubber\repos\micropython-stubs\publish\micropython-v1_19_1-rp2-stubs --target .snippets/rp2/typings --no-user
}

if (0){
    pip install -U C:\develop\MyPython\micropython-stubber\repos\micropython-stubs\publish\m\micropython-stdlib-minimal --target ./typings --no-user
    pip install -U C:\develop\MyPython\micropython-stubber\repos\micropython-stubs\publish\m\micropython-stdlib-minimal --target .snippets/stm32/typings --no-user
    pip install -U C:\develop\MyPython\micropython-stubber\repos\micropython-stubs\publish\m\micropython-stdlib-minimal --target .snippets/esp32/typings --no-user
    pip install -U C:\develop\MyPython\micropython-stubber\repos\micropython-stubs\publish\m\micropython-stdlib-minimal --target .snippets/esp8266/typings --no-user
    pip install -U C:\develop\MyPython\micropython-stubber\repos\micropython-stubs\publish\m\micropython-stdlib-minimal --target .snippets/rp2/typings --no-user


}



