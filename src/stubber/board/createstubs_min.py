A5='windows'
A4='No report file'
A3='Failed to create the report.'
A2='logging'
A1='method'
A0='function'
z='str'
y='float'
x='int'
w='stubber'
v=KeyError
u=sorted
t=NotImplementedError
p='unix'
o='arch'
n='variant'
m=',\n'
l='dict'
k='list'
j='tuple'
i='micropython'
h=TypeError
g=repr
f=getattr
b='-preview'
a=len
Z=print
X='family'
W='board_id'
V='board'
U=True
T=IndexError
S=open
R=Exception
Q=ImportError
P='mpy'
O=dir
N='build'
M='port'
L='.'
J=AttributeError
I='/'
E='-'
H=None
D=OSError
F=False
C='version'
A=''
import gc as G,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except Q:pass
try:from collections import OrderedDict as q
except Q:from ucollections import OrderedDict as q
try:import inspect as Y;c=U
except Q:c=F
__version__='v1.26.4'
A6=2
A7=44
A8=2
AL=['lib','/lib','/sd/lib','/flash/lib',L]
class K:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=Z
	@staticmethod
	def getLogger(name):return K()
	@classmethod
	def basicConfig(A,level):A.level=level
	def debug(A,msg):
		if A.level<=K.DEBUG:A.prnt('DEBUG :',msg)
	def info(A,msg):
		if A.level<=K.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=K.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=K.ERROR:A.prnt('ERROR :',msg)
B=K.getLogger(w)
K.basicConfig(level=K.INFO)
class Stubber:
	def __init__(A,path=A,firmware_id=A):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise t('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		A.info=_info();B.info('Port: {}'.format(A.info[M]));B.info('Board: {}'.format(A.info[V]));B.info('Board_ID: {}'.format(A.info[W]));G.collect()
		if C:A._fwid=C.lower()
		elif A.info[X]==i:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(E)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=G.mem_free()
		if path:
			if path.endswith(I):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',I)
		try:d(path+I)
		except D:B.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=H;A._json_first=F
	def load_exlusions(C):
		try:
			with S('modulelist_exclude.txt','r')as E:
				for F in E:
					A=F.strip()
					if A and A not in C.excluded:C.excluded.append(A);B.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except D:pass
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for B in O(H):
			if B.startswith('__')and not B in L.modules:continue
			try:
				D=f(H,B)
				try:E=g(type(D)).split("'")[1]
				except T:E=A
				if E in{x,y,z,'bool',j,k,l}:F=1
				elif E in{A0,A1}:F=2
				elif E in'class':F=3
				else:F=4
				C.append((B,g(D),g(type(D)),D,F))
			except J as I:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(B,H,I))
			except MemoryError as I:Z('MemoryError: {}'.format(I));sleep(1);reset()
		C=u([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);G.collect();return C,K
	def add_modules(A,modules):A.modules=u(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();G.collect()
		for C in A.modules:A.create_one_stub(C)
		A.report_end();B.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:B.warning('Skip module: {:<25}        : Known problematic'.format(A));return F
		if A in C.excluded:B.warning('Skip module: {:<25}        : Excluded'.format(A));return F
		H='{}/{}.pyi'.format(C.path,A.replace(L,I));G.collect();E=F
		try:E=C.create_module_stub(A,H)
		except D:return F
		G.collect();return E
	def create_module_stub(J,module_name,file_name=H):
		E=file_name;C=module_name
		if E is H:K=C.replace(L,'_')+'.pyi';E=J.path+I+K
		else:K=E.split(I)[-1]
		if I in C:C=C.replace(I,L)
		M=H
		try:M=__import__(C,H,H,'*');O=G.mem_free();B.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,K,O))
		except Q:return F
		d(E)
		with S(E,'w')as N:P=str(J.info).replace('OrderedDict(',A).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,J._fwid,P,__version__);N.write(R);N.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(N,M,C,A)
		J.report_add(C,E)
		if C not in{'os','sys',A2,'gc'}:
			try:del M
			except(D,v):B.warning('could not del new_module')
		G.collect();return U
	def write_object_stub(T,fp,object_expr,obj_name,indent,in_class=0):
		r=' at ...>';q='{0}{1}: {3} = {2}\n';p='bound_method';o='self';n='self, ';m='Incomplete';Z='Exception';U=object_expr;S=' at ';P=in_class;M=fp;E=indent;G.collect()
		if U in T.problematic:B.warning('SKIPPING problematic module:{}'.format(U));return
		s,b=T.get_obj_attributes(U)
		if b:B.error(b)
		for(C,J,K,O,w)in s:
			if C in['classmethod','staticmethod','BaseException',Z]:continue
			if C[0].isdigit():B.warning('NameError: invalid name {}'.format(C));continue
			if K=="<class 'type'>"and a(E)<=A8*4:
				d=A;e=C.endswith(Z)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if e:d=Z
				D='\n{}class {}({}):\n'.format(E,C,d)
				if e:D+=E+'    ...\n';M.write(D);continue
				M.write(D);T.write_object_stub(M,O,'{0}.{1}'.format(obj_name,C),E+'    ',P+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';M.write(D)
			elif any(A in K for A in[A1,A0,'closure']):
				V=m;g=A
				if P>0:g=n
				Q=F;W=F;h=F
				if c:
					try:Q=Y.iscoroutinefunction(O)
					except R:pass
					if not Q:
						try:W=f(Y,'isasyncgenfunction',lambda _:F)(O)
						except R:pass
					if not Q and not W:
						try:h=Y.isgeneratorfunction(O)
						except R:pass
				N=H
				if c:
					try:
						t=Y.signature(O);L=[]
						for(X,u)in t.parameters.items():
							i=f(u,'kind',H)
							if i==2:L.append('*'+X)
							elif i==4:L.append('**'+X)
							else:L.append(X)
						if P>0 and L and L[0]in(o,'cls'):L=L[1:]
						if P>0:N=n+', '.join(L)if L else o
						else:N=', '.join(L)
					except R:pass
				if N is H:N='{}*args, **kwargs'.format(g)
				if p in K or p in J:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,C,V)
				elif Q:D='{}async def {}({}) -> {}:\n'.format(E,C,N,V)
				elif W:D='{}async def {}({}) -> AsyncGenerator:\n'.format(E,C,N)
				elif h:D='{}def {}({}) -> Generator:\n'.format(E,C,N)
				else:D='{}def {}({}) -> {}:\n'.format(E,C,N,V)
				D+=E+'    ...\n\n';M.write(D)
			elif K=="<class 'module'>":0
			elif K.startswith("<class '"):
				I=K[8:-2];D=A
				if I in(z,x,y,'bool','bytearray','bytes'):
					if C.upper()==C:D='{0}{1}: Final[{3}] = {2}\n'.format(E,C,J,I)
					else:D=q.format(E,C,J,I)
				elif I in(l,k,j):v={l:'{}',k:'[]',j:'()'};D=q.format(E,C,v[I],I)
				elif I in('object','set','frozenset','Pin'):D='{0}{1}: {2} ## = {4}\n'.format(E,C,I,K,J)
				elif I=='generator':I='Generator';D='{0}def {1}(*args, **kwargs) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(E,C,I,K,J)
				else:
					I=m
					if S in J:J=J.split(S)[0]+r
					if S in J:J=J.split(S)[0]+r
					D='{0}{1}: {2} ## {3} = {4}\n'.format(E,C,I,K,J)
				M.write(D)
			else:M.write("# all other, type = '{0}'\n".format(K));M.write(E+C+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(C,path=A):
		if not path:path=C.path
		B.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except(D,J):return
		for F in E:
			A='{}/{}'.format(path,F)
			try:os.remove(A)
			except D:
				try:C.clean(A);os.rmdir(A)
				except D:pass
	def report_start(A,filename='modules.json'):
		F='firmware';A._json_name='{}/{}'.format(A.path,filename);A._json_first=U;d(A._json_name);B.info('Report file: {}'.format(A._json_name));G.collect()
		try:
			with S(A._json_name,'w')as E:E.write('{');E.write(dumps({F:A.info})[1:-1]);E.write(m);E.write(dumps({w:{C:__version__},'stubtype':F})[1:-1]);E.write(m);E.write('"modules" :[\n')
		except D as I:B.error(A3);A._json_name=H;raise I
	def report_add(A,module_name,stub_file):
		if not A._json_name:raise R(A4)
		try:
			with S(A._json_name,'a')as C:
				if not A._json_first:C.write(m)
				else:A._json_first=F
				E='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',I));C.write(E)
		except D:B.error(A3)
	def report_end(A):
		if not A._json_name:raise R(A4)
		with S(A._json_name,'a')as C:C.write('\n]}')
		B.info('Path: {}'.format(A.path))
def d(path):
	A=E=0
	while A!=-1:
		A=path.find(I,E)
		if A!=-1:
			C=path[0]if A==0 else path[:A]
			try:H=os.stat(C)
			except D as F:
				if F.args[0]in[A6,A7]:
					try:B.debug('Create folder {}'.format(C));os.mkdir(C)
					except D as G:B.error('failed to create folder {}'.format(C));raise G
		E=A+1
def e(s):
	C=' on '
	if not s:return A
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not E in s:return A
		B=s.split(E)[1];return B
	if not b in s:return A
	B=s.split(b)[1].split(L)[1];return B
def A9():
	try:B=sys.implementation[0]
	except h:B=sys.implementation.name
	D=q({X:B,C:A,N:A,'ver':A,M:sys.platform,V:'UNKNOWN',W:A,n:A,'cpu':A,P:A,o:A});return D
def AA(info):
	A=info
	if A[M].startswith('pyb'):A[M]='stm32'
	elif A[M]=='win32':A[M]=A5
	elif A[M]=='linux':A[M]=p
def AB(info):
	try:info[C]=AI(sys.implementation.version)
	except J:pass
def AC(info):
	B=info
	try:
		D=sys.implementation._machine if'_machine'in O(sys.implementation)else os.uname().machine;B[V]=D.strip();C=sys.implementation._build if'_build'in O(sys.implementation)else A
		if C:B[V]=C.split(E)[0];B[n]=C.split(E)[1]if E in C else A
		B[W]=C;B['cpu']=D.split('with')[-1].strip();B[P]=sys.implementation._mpy if'_mpy'in O(sys.implementation)else sys.implementation.mpy if P in O(sys.implementation)else A
	except(J,T):pass
	if not B[W]:AJ(B)
def AD(info):
	B=info
	try:
		if'uname'in O(os):
			B[N]=e(os.uname()[3])
			if not B[N]:B[N]=e(os.uname()[2])
		elif C in O(sys):B[N]=e(sys.version)
	except(J,T,h):pass
	if B[C]==A and sys.platform not in(p,'win32'):
		try:D=os.uname();B[C]=D.release
		except(T,J,h):pass
def AE(info):
	D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:I=__import__(F,H,H,G);A[X]=E;del I;break
		except(Q,v):pass
	if A[X]==D:A['release']='2.0.0'
def AF(info):
	A=info
	if A[X]==i:
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
def AG(info):
	A=info
	if P in A and A[P]:
		B=int(A[P])
		try:
			C=[H,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[o]=C
		except T:A[o]='unknown'
		A[P]='v{}.{}'.format(B&255,B>>8&3)
def AH(info):
	A=info
	if A[N]and not A[C].endswith(b):A[C]=A[C]+b
	A['ver']=f"{A[C]}-{A[N]}"if A[N]else f"{A[C]}"
def _info():A=A9();AA(A);AB(A);AC(A);AD(A);AE(A);AF(A);AG(A);AH(A);return A
def AI(version):
	A=version;B=L.join([str(A)for A in A[:3]])
	if a(A)>3 and A[3]:B+=E+A[3]
	return B
def AJ(info):
	D=info
	try:from boardname import BOARD_ID as C;B.info('Found BOARD_ID: {}'.format(C))
	except Q:B.warning('BOARD_ID not found');C=A
	D[W]=C;D[V]=C.split(E)[0]if E in C else C;D[n]==C.split(E)[1]if E in C else A
def get_root():
	try:A=os.getcwd()
	except(D,J):A=L
	B=A
	for B in['/remote','/sd','/flash',I,A,L]:
		try:C=os.stat(B);break
		except D:continue
	return B
def AK(filename):
	try:
		if os.stat(filename)[0]>>14:return U
		return F
	except D:return F
def r():Z("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=A
	if a(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):path=sys.argv[2]
		else:r()
	elif a(sys.argv)==2:r()
	return path
def s():
	try:A=bytes('abc',encoding='utf8');B=s.__module__;return F
	except(t,J):return U
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_asyncio','_boot_fat','_espnow','_onewire','_pyscript','_rp2','_thread','_uasyncio','abc','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','alif','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','base64','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','builtins','cc3200','cmath','collections','collections/__init__','collections/defaultdict','copy','crypto','cryptolib','curl','datetime','deflate','dht','display','display_driver_utils','ds18x20','embed','encoder','errno','esp','esp32','esp8266','espidf','espnow','ffi','flashbdev','fnmatch','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','gzip','hashlib','heapq','hmac','html/__init__','hub75','ili9341','ili9XXX','imagetools','inisetup','inspect','interstate75','io','itertools','jpegdec','js','jsffi','json','lcd160cr','locale','lodepng',A2,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','marshal','math','microWebSocket','microWebSrv','microWebTemplate',i,'mimxrt','mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','nrf','ntptime','onewire','openamp','operator','os','os/__init__','os/path','pathlib','pcf85063a','pic16bit','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform','powerpc','pyb','pye','pyscript','pyscript/__init__','pyscript/fs','qemu','qrcode','random','renesas','renesas-ra','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stat','stm','stm32','string','struct','sys','tarfile/__init__','tarfile/write','termios','time','tls','tpcalib','types','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','unittest/__init__',p,'uos','uplatform','urandom','ure','urequests','urllib/urequest','usb/device','usb/device/cdc','usb/device/hid','usb/device/keyboard','usb/device/midi','usb/device/mouse','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uu','uwebsocket','uzlib',C,'vfs','webassembly','websocket','websocket_helper',A5,'wipy','writer','xpt2046','ymodem','zephyr','zlib','zsensor'];G.collect();stubber.create_all_stubs()
if __name__=='__main__'or s():
	if not AK('no_auto_stubber.txt'):
		Z(f"createstubs.py: {__version__}")
		try:G.threshold(4096);G.enable()
		except BaseException:pass
		main()