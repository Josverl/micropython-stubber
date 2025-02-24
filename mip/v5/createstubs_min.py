A0='windows'
z='No report file'
y='Failed to create the report.'
x='{}/{}'
w='logging'
v='sys'
u='method'
t='function'
s='bool'
r='str'
q='float'
p='int'
o='stubber'
n=Exception
m=KeyError
l=sorted
k=NotImplementedError
g='unix'
f=',\n'
e='dict'
d='list'
c='tuple'
b='micropython'
a=TypeError
Z=repr
W='-preview'
V=True
U='-'
T='board'
S=len
R=open
Q=print
P='family'
O=IndexError
N=ImportError
M=dir
L='port'
K='.'
I=AttributeError
H=False
G=None
E='/'
D=OSError
C='version'
B=''
import gc as F,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except N:pass
try:from collections import OrderedDict as h
except N:from ucollections import OrderedDict as h
__version__='v1.24.0'
A1=2
A2=44
A3=2
A7=['lib','/lib','/sd/lib','/flash/lib',K]
class J:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=Q
	@staticmethod
	def getLogger(name):return J()
	@classmethod
	def basicConfig(A,level):A.level=level
	def debug(A,msg):
		if A.level<=J.DEBUG:A.prnt('DEBUG :',msg)
	def info(A,msg):
		if A.level<=J.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=J.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=J.ERROR:A.prnt('ERROR :',msg)
A=J.getLogger(o)
J.basicConfig(level=J.INFO)
class Stubber:
	def __init__(B,path=B,firmware_id=B):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise k('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		B.info=_info();A.info('Port: {}'.format(B.info[L]));A.info('Board: {}'.format(B.info[T]));F.collect()
		if C:B._fwid=C.lower()
		elif B.info[P]==b:B._fwid='{family}-v{version}-{port}-{board}'.format(**B.info).rstrip(U)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=F.mem_free()
		if path:
			if path.endswith(E):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',E)
		try:X(path+E)
		except D:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[];B._json_name=G;B._json_first=H
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for A in M(H):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=getattr(H,A)
				try:E=Z(type(D)).split("'")[1]
				except O:E=B
				if E in{p,q,r,s,c,d,e}:G=1
				elif E in{t,u}:G=2
				elif E in'class':G=3
				else:G=4
				C.append((A,Z(D),Z(type(D)),D,G))
			except I as J:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,J))
			except MemoryError as J:Q('MemoryError: {}'.format(J));sleep(1);reset()
		C=l([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return C,K
	def add_modules(A,modules):A.modules=l(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber {} on {}'.format(__version__,B._fwid));B.report_start();F.collect()
		for C in B.modules:B.create_one_stub(C)
		B.report_end();A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return H
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return H
		I='{}/{}.pyi'.format(C.path,B.replace(K,E));F.collect();G=H
		try:G=C.create_module_stub(B,I)
		except D:return H
		F.collect();return G
	def create_module_stub(J,module_name,file_name=G):
		I=file_name;C=module_name
		if I is G:L=C.replace(K,'_')+'.pyi';I=J.path+E+L
		else:L=I.split(E)[-1]
		if E in C:C=C.replace(E,K)
		M=G
		try:M=__import__(C,G,G,'*');P=F.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,L,P))
		except N:return H
		X(I)
		with R(I,'w')as O:Q=str(J.info).replace('OrderedDict(',B).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,J._fwid,Q,__version__);O.write(S);O.write('from __future__ import annotations\nfrom typing import Any, Final, Generator\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(O,M,C,B)
		J.report_add(C,I)
		if C not in{'os',v,w,'gc'}:
			try:del M
			except(D,m):A.warning('could not del new_module')
		F.collect();return V
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		Y=' at ...>';X='{0}{1}: {3} = {2}\n';W='bound_method';V='Incomplete';O=in_class;N='Exception';M=object_expr;K=' at ';J=fp;E=indent;F.collect()
		if M in L.problematic:A.warning('SKIPPING problematic module:{}'.format(M));return
		Z,P=L.get_obj_attributes(M)
		if P:A.error(P)
		for(C,H,I,a,f)in Z:
			if C in['classmethod','staticmethod','BaseException',N]:continue
			if C[0].isdigit():A.warning('NameError: invalid name {}'.format(C));continue
			if I=="<class 'type'>"and S(E)<=A3*4:
				Q=B;R=C.endswith(N)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=N
				D='\n{}class {}({}):\n'.format(E,C,Q)
				if R:D+=E+'    ...\n';J.write(D);continue
				J.write(D);L.write_object_stub(J,a,'{0}.{1}'.format(obj_name,C),E+'    ',O+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';J.write(D)
			elif any(A in I for A in[u,t,'closure']):
				T=V;U=B
				if O>0:U='self, '
				if W in I or W in H:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,C,T)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,C,U,T)
				D+=E+'    ...\n\n';J.write(D)
			elif I=="<class 'module'>":0
			elif I.startswith("<class '"):
				G=I[8:-2];D=B
				if G in(r,p,q,s,'bytearray','bytes'):
					if C.upper()==C:D='{0}{1}: Final[{3}] = {2}\n'.format(E,C,H,G)
					else:D=X.format(E,C,H,G)
				elif G in(e,d,c):b={e:'{}',d:'[]',c:'()'};D=X.format(E,C,b[G],G)
				elif G in('object','set','frozenset','Pin'):D='{0}{1}: {2} ## = {4}\n'.format(E,C,G,I,H)
				elif G=='generator':G='Generator';D='{0}def {1}(*args, **kwargs) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(E,C,G,I,H)
				else:
					G=V
					if K in H:H=H.split(K)[0]+Y
					if K in H:H=H.split(K)[0]+Y
					D='{0}{1}: {2} ## {3} = {4}\n'.format(E,C,G,I,H)
				J.write(D)
			else:J.write("# all other, type = '{0}'\n".format(I));J.write(E+C+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(C,path=B):
		if not path:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except(D,I):return
		for F in E:
			B=x.format(path,F)
			try:os.remove(B)
			except D:
				try:C.clean(B);os.rmdir(B)
				except D:pass
	def report_start(B,filename='modules.json'):
		H='firmware';B._json_name=x.format(B.path,filename);B._json_first=V;X(B._json_name);A.info('Report file: {}'.format(B._json_name));F.collect()
		try:
			with R(B._json_name,'w')as E:E.write('{');E.write(dumps({H:B.info})[1:-1]);E.write(f);E.write(dumps({o:{C:__version__},'stubtype':H})[1:-1]);E.write(f);E.write('"modules" :[\n')
		except D as I:A.error(y);B._json_name=G;raise I
	def report_add(B,module_name,stub_file):
		if not B._json_name:raise n(z)
		try:
			with R(B._json_name,'a')as C:
				if not B._json_first:C.write(f)
				else:B._json_first=H
				F='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',E));C.write(F)
		except D:A.error(y)
	def report_end(B):
		if not B._json_name:raise n(z)
		with R(B._json_name,'a')as C:C.write('\n]}')
		A.info('Path: {}'.format(B.path))
def X(path):
	B=F=0
	while B!=-1:
		B=path.find(E,F)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except D as G:
				if G.args[0]in[A1,A2]:
					try:A.debug('Create folder {}'.format(C));os.mkdir(C)
					except D as H:A.error('failed to create folder {}'.format(C));raise H
		F=B+1
def Y(s):
	C=' on '
	if not s:return B
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not U in s:return B
		A=s.split(U)[1];return A
	if not W in s:return B
	A=s.split(W)[1].split(K)[1];return A
def _info():
	Z='ev3-pybricks';X='pycom';V='pycopy';U='win32';S='arch';R='cpu';Q='ver';E='mpy';D='build'
	try:J=sys.implementation[0]
	except a:J=sys.implementation.name
	A=h({P:J,C:B,D:B,Q:B,L:sys.platform,T:'UNKNOWN',R:B,E:B,S:B})
	if A[L].startswith('pyb'):A[L]='stm32'
	elif A[L]==U:A[L]=A0
	elif A[L]=='linux':A[L]=g
	try:A[C]=A4(sys.implementation.version)
	except I:pass
	try:K=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[T]=K;A[R]=K.split('with')[-1].strip();A[E]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if E in M(sys.implementation)else B
	except(I,O):pass
	A[T]=A5()
	try:
		if'uname'in M(os):
			A[D]=Y(os.uname()[3])
			if not A[D]:A[D]=Y(os.uname()[2])
		elif C in M(sys):A[D]=Y(sys.version)
	except(I,O,a):pass
	if A[C]==B and sys.platform not in(g,U):
		try:c=os.uname();A[C]=c.release
		except(O,I,a):pass
	for(d,e,f)in[(V,V,'const'),(X,X,'FAT'),(Z,'pybricks.hubs','EV3Brick')]:
		try:i=__import__(e,G,G,f);A[P]=d;del i;break
		except(N,m):pass
	if A[P]==Z:A['release']='2.0.0'
	if A[P]==b:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if E in A and A[E]:
		F=int(A[E])
		try:H=[G,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][F>>10]
		except O:H='unknown'
		if H:A[S]=H
		A[E]='v{}.{}'.format(F&255,F>>8&3)
	if A[D]and not A[C].endswith(W):A[C]=A[C]+W
	A[Q]=f"{A[C]}-{A[D]}"if A[D]else f"{A[C]}";return A
def A4(version):
	A=version;B=K.join([str(A)for A in A[:3]])
	if S(A)>3 and A[3]:B+=U+A[3]
	return B
def A5():
	try:from boardname import BOARDNAME as C;A.info('Found BOARDNAME: {}'.format(C))
	except N:A.warning('BOARDNAME not found');C=B
	return C
def get_root():
	try:A=os.getcwd()
	except(D,I):A=K
	B=A
	for B in['/remote','/sd','/flash',E,A,K]:
		try:C=os.stat(B);break
		except D:continue
	return B
def A6(filename):
	try:
		if os.stat(filename)[0]>>14:return V
		return H
	except D:return H
def i():Q("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if S(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:i()
	elif S(sys.argv)==2:i()
	return path
def j():
	try:A=bytes('abc',encoding='utf8');B=j.__module__;return H
	except(k,I):return V
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_asyncio','_boot_fat','_espnow','_onewire','_rp2','_thread','_uasyncio','abc','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','base64','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','builtins','cc3200','cmath','collections','collections/__init__','collections/defaultdict','copy','crypto','cryptolib','curl','datetime','deflate','dht','display','display_driver_utils','ds18x20','embed','encoder','errno','esp','esp32','esp8266','espidf','espnow','ffi','flashbdev','fnmatch','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','gzip','hashlib','heapq','hmac','html/__init__','hub75','ili9341','ili9XXX','imagetools','inisetup','inspect','interstate75','io','itertools','jpegdec','js','jsffi','json','lcd160cr','locale','lodepng',w,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','marshal','math','microWebSocket','microWebSrv','microWebTemplate',b,'mimxrt','mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','nrf','ntptime','onewire','openamp','operator','os','os/__init__','os/path','pathlib','pcf85063a','pic16bit','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform','powerpc','pyb','pye','pyscript','pyscript/__init__','pyscript/fs','qemu','qrcode','random','renesas','renesas-ra','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stat','stm','stm32','string','struct',v,'tarfile/__init__','tarfile/write','termios','time','tls','tpcalib','types','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','unittest/__init__',g,'uos','uplatform','urandom','ure','urequests','urllib/urequest','usb/device','usb/device/cdc','usb/device/hid','usb/device/keyboard','usb/device/midi','usb/device/mouse','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uu','uwebsocket','uzlib',C,'vfs','webassembly','websocket','websocket_helper',A0,'wipy','writer','xpt2046','ymodem','zephyr','zlib'];F.collect();stubber.create_all_stubs()
if __name__=='__main__'or j():
	if not A6('no_auto_stubber.txt'):
		Q(f"createstubs.py: {__version__}")
		try:F.threshold(4096);F.enable()
		except BaseException:pass
		main()