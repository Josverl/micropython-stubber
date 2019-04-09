def get_root():
    # Determine the root folder of the device 
    import os, errno
    try:
        r = "/flash"
        _ = os.stat(r)
    except OSError as e:
        if e.args[0] == errno.ENOENT:
            r = os.getcwd()
    finally:
        return r


r = []
u = os.uname()
r.append( { 'sysname': u.sysname, 'nodename': u.nodename , 'release': u.release , 'version': u.version, 'machine': u.machine } )
