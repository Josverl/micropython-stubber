"""
Collect modules and python stubs from other projects
"""
import requests
import os

try:
    os.chdir('./runonpc')
except:
    pass

def download_file(url, folder = "./"):
    local_filename = folder + url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return local_filename

def download_files(repo, frozen_modules, savepath):
    if not os.path.exists(savepath):
        os.makedirs(savepath)

    for mod in frozen_modules:
        url = repo.format(mod)
        download_file(url, savepath  )


def make_stubfiles(modulepath):
    cmd = "python make_stub_files.py -c ./make_stub_files.cfg -u {}*.py".format(modulepath)
    os.system(cmd)



#Loboris frozen modules 
frozen_modules = ["README.md","ak8963.py","freesans20.py","functools.py","logging.py","microWebSocket.py","microWebSrv.py","microWebTemplate.py","mpu6500.py","mpu9250.py","pye.py","ssd1306.py","tpcalib.py","upip.py",
"upip_utarfile.py","upysh.py","urequests.py","writer.py"] 
repo = 'https://raw.githubusercontent.com/loboris/MicroPython_ESP32_psRAM_LoBo/master/MicroPython_BUILD/components/micropython/esp32/modules/{}'

modulepath = '../stubs/esp32_lobo_frozen/'

#download 
download_files(repo, frozen_modules, modulepath )
#now generate / update stubs 
make_stubfiles(modulepath)



# pyboard custom stub is included and doesn not need to be downloaded.
modulepath = '../stubs/pyb_common/'
    ## modules = ['pyb.py']
    ## url = 'https://raw.githubusercontent.com/dastultz/micropython-pyb/master/lib/{}'
    ## download_files(url, modules,  savepath )
#now generate / update stubs 
make_stubfiles(modulepath)


# step x : generate pyi files for the generated stubs

make_stubfiles('../stubs/esp32_LoBo_3_2_24/')

