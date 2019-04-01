lobo = [ ##Loboris
            '_thread', 'ak8963', 'array', 'binascii', 'btree', 'builtins',
            'cmath', 'collections', 'curl', 'display', 'errno', 'framebuf',
            'freesans20', 'functools', 'gc', 'gsm', 'hashlib', 'heapq', 'io',
            'json', 'logging', 'machine', 'math', 'microWebSocket', 'microWebSrv',
            'microWebTemplate', 'micropython', 'mpu6500', 'mpu9250', 'network', 'os',
            'pye', 'random', 're', 'requests', 'select', 'socket', 'ssd1306', 'ssh',
            'ssl', 'struct', 'sys', 'time', 'tpcalib', 'ubinascii', 'ucollections',
            'uctypes', 'uerrno', 'uhashlib', 'uheapq', 'uio', 'ujson', 'uos', 'upip',
            'upip_utarfile', 'upysh', 'urandom', 'ure', 'urequests', 'uselect', 'usocket',
            'ussl', 'ustruct', 'utime', 'utimeq', 'uzlib', 'websocket', 'writer', 'ymodem', 'zlib']

mpy = [ #standard ESP32 micropython        
        'framebuf',          'socket'            'upip',
        '_boot',             'gc',                'ssl',               'upip_utarfile',
        '_onewire',          'hashlib',           'struct',            'upysh',
        '_thread',           'heapq',             'sys',               'urandom',
        '_webrepl',          'inisetup',          'time',              'ure',
        'apa106',            'io',                'ubinascii',         'urequests',
        'array',             'json',              'ucollections',      'uselect',
        'binascii',          'machine',           'ucryptolib',        'usocket',
        'btree',             'math',              'uctypes',           'ussl',
        'builtins',          'micropython',       'uerrno',            'ustruct',
        'cmath',             'neopixel',          'uhashlib',          'utime',
        'collections',       'network',           'uhashlib',          'utimeq',
        'dht',               'ntptime',           'uheapq',            'uwebsocket',
        'ds18x20',           'onewire',           'uio',               'uzlib',
        'errno',             'os',                'ujson',             'webrepl',
        'esp',               'random',            'umqtt/robust',      'webrepl_setup',
        'esp32',             're',                'umqtt/simple',      'websocket_helper',
        'flashbdev',         'select',            'uos',               'zlib'
        ]

print( "mpy  modules :", len(mpy) ) 
print( "lobo modules :", len(lobo )) 

shared = set(mpy) & set(lobo) 
print( "Shared modules :", len(shared )) 

mpy_only = set(mpy) - set(lobo) 
print( "mpy only modules :", len(mpy_only)) 

lobo_only = set(lobo) - set(mpy) 
print( "lobo only modules :", len(lobo_only)) 

print( "mpy  modules :", len(mpy ),  "=", len(mpy_only)+ len(shared)) 
print( "lobo modules :", len(lobo ), "=", len(lobo_only)+ len(shared)) 

print("\nshared = ",end='')
print (sorted(shared))

print("\nmpy_only = ",end='')
print (sorted(mpy_only))

print("\nlobo_only = ",end='')
print (sorted(lobo_only))


print("\nall = ",end='')
print (sorted(set(mpy) | set(lobo)))


## result is : 

shared = ['_thread', 'array', 'binascii', 'btree', 'builtins', 'cmath', 'collections', 'errno', 'framebuf', 
            'gc', 'hashlib', 'heapq', 'io', 'json', 'machine', 'math', 'micropython', 'network', 'os', 'random', 
            're', 'select', 'ssl', 'struct', 'sys', 'time', 'ubinascii', 'ucollections', 'uctypes', 'uerrno', 
            'uhashlib', 'uheapq', 'uio', 'ujson', 'uos', 'upip_utarfile', 'upysh', 'urandom', 'ure', 'urequests', 
            'uselect', 'usocket', 'ussl', 'ustruct', 'utime', 'utimeq', 'uzlib', 'zlib']

mpy_only = ['_boot', '_onewire', '_webrepl', 'apa106', 'dht', 'ds18x20', 'esp', 'esp32', 'flashbdev', 'inisetup', 
            'neopixel', 'ntptime', 'onewire', 'socketupip', 'ucryptolib', 'umqtt/robust', 'umqtt/simple', 'uwebsocket', 
            'webrepl', 'webrepl_setup', 'websocket_helper']

lobo_only = ['ak8963', 'curl', 'display', 'freesans20', 'functools', 'gsm', 'logging', 'microWebSocket', 'microWebSrv', 
            'microWebTemplate', 'mpu6500', 'mpu9250', 'pye', 'requests', 'socket', 'ssd1306', 'ssh', 'tpcalib', 'upip', 
            'websocket', 'writer', 'ymodem']

all = ['_boot', '_onewire', '_thread', '_webrepl', 'ak8963', 'apa106', 'array', 'binascii', 'btree', 'builtins', 'cmath', 
        'collections', 'curl', 'dht', 'display', 'ds18x20', 'errno', 'esp', 'esp32', 'flashbdev', 'framebuf', 'freesans20', 
        'functools', 'gc', 'gsm', 'hashlib', 'heapq', 'inisetup', 'io', 'json', 'logging', 'machine', 'math', 'microWebSocket',
        'microWebSrv', 'microWebTemplate', 'micropython', 'mpu6500', 'mpu9250', 'neopixel', 'network', 'ntptime', 'onewire', 'os', 
        'pye', 'random', 're', 'requests', 'select', 'socket', 'socketupip', 'ssd1306', 'ssh', 'ssl', 'struct', 'sys', 'time', 'tpcalib', 
        'ubinascii', 'ucollections', 'ucryptolib', 'uctypes', 'uerrno', 'uhashlib', 'uheapq', 'uio', 'ujson', 'umqtt/robust', 'umqtt/simple', 
        'uos', 'upip', 'upip_utarfile', 'upysh', 'urandom', 'ure', 'urequests', 'uselect', 'usocket', 'ussl', 'ustruct', 'utime', 'utimeq', 
        'uwebsocket', 'uzlib', 'webrepl', 'webrepl_setup', 'websocket', 'websocket_helper', 'writer', 'ymodem', 'zlib']            

