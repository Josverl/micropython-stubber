A5='windows'
A4='No report file'
A3='Failed to create the report.'
A2='logging'
A1='method'
A0='function'
z='float'
y='int'
x='stubber'
w=KeyError
v=sorted
u=NotImplementedError
q='unix'
p='arch'
o='variant'
n=',\n'
m='dict'
l='list'
k='tuple'
j='micropython'
i=TypeError
h=repr
e='-preview'
d=len
c=getattr
b=print
Z='family'
X='board_id'
W='board'
V=IndexError
T=open
S=ImportError
Q='mpy'
U='*'
P=dir
N='build'
M='port'
L='.'
R=Exception
H=AttributeError
G='-'
O=True
F=OSError
J=None
A='version'
E='/'
C=''
B=False
import gc as K,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except S:pass
try:from collections import OrderedDict as r
except S:from ucollections import OrderedDict as r
try:import inspect as Y;a=O
except S:a=B
__version__='v1.26.5a0'
A6=2
A7=44
A8=2
AL=['lib','/lib','/sd/lib','/flash/lib',L]
class I:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=b
	@staticmethod
	def getLogger(name):return I()
	@classmethod
	def basicConfig(A,level):A.level=level
	def debug(A,msg):
		if A.level<=I.DEBUG:A.prnt('DEBUG :',msg)
	def info(A,msg):
		if A.level<=I.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=I.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=I.ERROR:A.prnt('ERROR :',msg)
D=I.getLogger(x)
I.basicConfig(level=I.INFO)
class Stubber:
	def __init__(A,path=C,firmware_id=C):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise u('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A.info=_info();D.info('Port: {}'.format(A.info[M]));D.info('Board: {}'.format(A.info[W]));D.info('Board_ID: {}'.format(A.info[X]));K.collect()
		if C:A._fwid=C.lower()
		elif A.info[Z]==j:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(G)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=K.mem_free()
		if path:
			if path.endswith(E):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',E)
		try:f(path+E)
		except F:D.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=J;A._json_first=B
	def load_exlusions(B):
		try:
			with T('modulelist_exclude.txt','r')as C:
				for E in C:
					A=E.strip()
					if A and A not in B.excluded:B.excluded.append(A);D.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except F:pass
	def get_obj_attributes(L,item_instance):
		G=item_instance;B=[];J=[]
		for A in P(G):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=c(G,A)
				try:E=h(type(D)).split("'")[1]
				except V:E=C
				if E in{y,z,'str','bool',k,l,m}:F=1
				elif E in{A0,A1}:F=2
				elif E in'class':F=3
				else:F=4
				B.append((A,h(D),h(type(D)),D,F))
			except H as I:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,G,I))
			except MemoryError as I:b('MemoryError: {}'.format(I));sleep(1);reset()
		B=v([A for A in B if not A[0].startswith('__')],key=lambda x:x[4]);K.collect();return B,J
	def add_modules(A,modules):A.modules=v(set(A.modules)|set(modules))
	def create_all_stubs(A):
		D.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();K.collect()
		for B in A.modules:A.create_one_stub(B)
		A.report_end();D.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:D.warning('Skip module: {:<25}        : Known problematic'.format(A));return B
		if A in C.excluded:D.warning('Skip module: {:<25}        : Excluded'.format(A));return B
		H='{}/{}.pyi'.format(C.path,A.replace(L,E));K.collect();G=B
		try:G=C.create_module_stub(A,H)
		except F:return B
		K.collect();return G
	def create_module_stub(H,module_name,file_name=J):
		G=file_name;A=module_name
		if G is J:I=A.replace(L,'_')+'.pyi';G=H.path+E+I
		else:I=G.split(E)[-1]
		if E in A:A=A.replace(E,L)
		M=J
		try:M=__import__(A,J,J,U);P=K.mem_free();D.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,I,P))
		except S:return B
		f(G)
		with T(G,'w')as N:Q=str(H.info).replace('OrderedDict(',C).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,Q,__version__);N.write(R);N.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n');H.write_object_stub(N,M,A,C)
		H.report_add(A,G)
		if A not in{'os','sys',A2,'gc'}:
			try:del M
			except(F,w):D.warning('could not del new_module')
		K.collect();return O
	def write_object_stub(h,fp,object_expr,obj_name,indent,in_class=0):
		A5=' at ...>';A4='{0}{1}: {3} = {2}\n';A3='bound_method';A2='{}*args, **kwargs';x='Incomplete';q='Exception';i=object_expr;g=' at ';f=', ';e='self, ';V=in_class;S=fp;H=indent;K.collect()
		if i in h.problematic:D.warning('SKIPPING problematic module:{}'.format(i));return
		A6,r=h.get_obj_attributes(i)
		if r:D.error(r)
		for(F,M,Q,W,_)in A6:
			if F in['classmethod','staticmethod','BaseException',q]:continue
			if F[0].isdigit():D.warning('NameError: invalid name {}'.format(F));continue
			if Q=="<class 'type'>"and d(H)<=A8*4:
				s=C;t=F.endswith(q)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if t:s=q
				G='\n{}class {}({}):\n'.format(H,F,s)
				if t:G+=H+'    ...\n';S.write(G);continue
				S.write(G);h.write_object_stub(S,W,'{0}.{1}'.format(obj_name,F),H+'    ',V+1);G=H+'    def __init__(self, *argv, **kwargs) -> None:\n';G+=H+'        ...\n\n';S.write(G)
			elif any(A in Q for A in[A1,A0,'closure']):
				j=x;u=C
				if V>0:u=e
				b=B;n=B;v=B
				if a:
					try:b=Y.iscoroutinefunction(W)
					except R:pass
					if not b:
						try:n=c(Y,'isasyncgenfunction',lambda _:B)(W)
						except R:pass
					if not b and not n:
						try:v=Y.isgeneratorfunction(W)
						except R:pass
				T=J
				if a:
					try:
						o=Y.signature(W);A=[];I=B;X=B
						for(L,p)in o.parameters.items():
							P=c(p,'kind',J)
							if P==0:I=O;A.append(L)
							elif P==1:
								if I:A.append(E);I=B
								A.append(L)
							elif P==2:
								if I:A.append(E);I=B
								X=O;A.append(U+L)
							elif P==3:
								if I:A.append(E);I=B
								if not X:A.append(U);X=O
								A.append(L)
							elif P==4:
								if I:A.append(E);I=B
								A.append('**'+L)
							else:A.append(L)
						if I:A.append(E)
						if V>0 and A and A[0]not in(U,E):A=A[1:]
						if V>0:T=e+f.join(A)if A else'self'
						else:T=f.join(A)
					except R:pass
				if T is J:T=A2.format(u)
				if A3 in Q or A3 in M:G='{}@classmethod\n'.format(H)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(H,F,j)
				elif b:G='{}async def {}({}) -> {}:\n'.format(H,F,T,j)
				elif n:G='{}async def {}({}) -> AsyncGenerator:\n'.format(H,F,T)
				elif v:G='{}def {}({}) -> Generator:\n'.format(H,F,T)
				else:G='{}def {}({}) -> {}:\n'.format(H,F,T,j)
				G+=H+'    ...\n\n';S.write(G)
			elif Q=="<class 'module'>":0
			elif Q.startswith("<class '"):
				N=Q[8:-2];G=C
				if N in('str',y,z,'bool','bytearray','bytes'):
					if F.upper()==F:G='{0}{1}: Final[{3}] = {2}\n'.format(H,F,M,N)
					else:G=A4.format(H,F,M,N)
				elif N in(m,l,k):A7={m:'{}',l:'[]',k:'()'};G=A4.format(H,F,A7[N],N)
				elif N in('object','set','frozenset','Pin'):G='{0}{1}: {2} ## = {4}\n'.format(H,F,N,Q,M)
				elif N=='generator':
					A9=e if V>0 else C;Z=J;w=B
					if a:
						try:w=Y.iscoroutinefunction(W)
						except R:pass
						try:
							o=Y.signature(W);A=[];I=B;X=B
							for(L,p)in o.parameters.items():
								P=c(p,'kind',J)
								if P==0:I=O;A.append(L)
								elif P==1:
									if I:A.append(E);I=B
									A.append(L)
								elif P==2:
									if I:A.append(E);I=B
									X=O;A.append(U+L)
								elif P==3:
									if I:A.append(E);I=B
									if not X:A.append(U);X=O
									A.append(L)
								elif P==4:
									if I:A.append(E);I=B
									A.append('**'+L)
								else:A.append(L)
							if I:A.append(E)
							if V>0 and A and A[0]not in(U,E):A=A[1:]
							if V>0:Z=e+f.join(A)if A else'self'
							else:Z=f.join(A)
						except R:pass
					if Z is J:Z=A2.format(A9)
					if w:G='{0}async def {1}({2}) -> Incomplete:\n{0}    ...\n\n'.format(H,F,Z)
					else:G='{0}def {1}({2}) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(H,F,Z,N,M)
				else:
					N=x
					if g in M:M=M.split(g)[0]+A5
					if g in M:M=M.split(g)[0]+A5
					G='{0}{1}: {2} ## {3} = {4}\n'.format(H,F,N,Q,M)
				S.write(G)
			else:S.write("# all other, type = '{0}'\n".format(Q));S.write(H+F+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(B,path=C):
		if not path:path=B.path
		D.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except(F,H):return
		for E in C:
			A='{}/{}'.format(path,E)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report_start(B,filename='modules.json'):
		E='firmware';B._json_name='{}/{}'.format(B.path,filename);B._json_first=O;f(B._json_name);D.info('Report file: {}'.format(B._json_name));K.collect()
		try:
			with T(B._json_name,'w')as C:C.write('{');C.write(dumps({E:B.info})[1:-1]);C.write(n);C.write(dumps({x:{A:__version__},'stubtype':E})[1:-1]);C.write(n);C.write('"modules" :[\n')
		except F as G:D.error(A3);B._json_name=J;raise G
	def report_add(A,module_name,stub_file):
		if not A._json_name:raise R(A4)
		try:
			with T(A._json_name,'a')as C:
				if not A._json_first:C.write(n)
				else:A._json_first=B
				G='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',E));C.write(G)
		except F:D.error(A3)
	def report_end(A):
		if not A._json_name:raise R(A4)
		with T(A._json_name,'a')as B:B.write('\n]}')
		D.info('Path: {}'.format(A.path))
def f(path):
	A=C=0
	while A!=-1:
		A=path.find(E,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except F as G:
				if G.args[0]in[A6,A7]:
					try:D.debug('Create folder {}'.format(B));os.mkdir(B)
					except F as H:D.error('failed to create folder {}'.format(B));raise H
		C=A+1
def g(s):
	B=' on '
	if not s:return C
	s=s.split(B,1)[0]if B in s else s
	if s.startswith('v'):
		if not G in s:return C
		A=s.split(G)[1];return A
	if not e in s:return C
	A=s.split(e)[1].split(L)[1];return A
def A9():
	try:B=sys.implementation[0]
	except i:B=sys.implementation.name
	D=r({Z:B,A:C,N:C,'ver':C,M:sys.platform,W:'UNKNOWN',X:C,o:C,'cpu':C,Q:C,p:C});return D
def AA(info):
	A=info
	if A[M].startswith('pyb'):A[M]='stm32'
	elif A[M]=='win32':A[M]=A5
	elif A[M]=='linux':A[M]=q
def AB(info):
	try:info[A]=AI(sys.implementation.version)
	except H:pass
def AC(info):
	A=info
	try:
		D=sys.implementation._machine if'_machine'in P(sys.implementation)else os.uname().machine;A[W]=D.strip();B=sys.implementation._build if'_build'in P(sys.implementation)else C
		if B:A[W]=B.split(G)[0];A[o]=B.split(G)[1]if G in B else C
		A[X]=B;A['cpu']=D.split('with')[-1].strip();A[Q]=sys.implementation._mpy if'_mpy'in P(sys.implementation)else sys.implementation.mpy if Q in P(sys.implementation)else C
	except(H,V):pass
	if not A[X]:AJ(A)
def AD(info):
	B=info
	try:
		if'uname'in P(os):
			B[N]=g(os.uname()[3])
			if not B[N]:B[N]=g(os.uname()[2])
		elif A in P(sys):B[N]=g(sys.version)
	except(H,V,i):pass
	if B[A]==C and sys.platform not in(q,'win32'):
		try:D=os.uname();B[A]=D.release
		except(V,H,i):pass
def AE(info):
	D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,J,J,G);A[Z]=E;del H;break
		except(S,w):pass
	if A[Z]==D:A['release']='2.0.0'
def AF(info):
	B=info
	if B[Z]==j:
		if B[A]and B[A].endswith('.0')and B[A]>='1.10.0'and B[A]<='1.19.9':B[A]=B[A][:-2]
def AG(info):
	A=info
	if Q in A and A[Q]:
		B=int(A[Q])
		try:
			C=[J,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[p]=C
		except V:A[p]='unknown'
		A[Q]='v{}.{}'.format(B&255,B>>8&3)
def AH(info):
	B=info
	if B[N]and not B[A].endswith(e):B[A]=B[A]+e
	B['ver']=f"{B[A]}-{B[N]}"if B[N]else f"{B[A]}"
def _info():A=A9();AA(A);AB(A);AC(A);AD(A);AE(A);AF(A);AG(A);AH(A);return A
def AI(version):
	A=version;B=L.join([str(A)for A in A[:3]])
	if d(A)>3 and A[3]:B+=G+A[3]
	return B
def AJ(info):
	B=info
	try:from boardname import BOARD_ID as A;D.info('Found BOARD_ID: {}'.format(A))
	except S:D.warning('BOARD_ID not found');A=C
	B[X]=A;B[W]=A.split(G)[0]if G in A else A;B[o]==A.split(G)[1]if G in A else C
def get_root():
	try:A=os.getcwd()
	except(F,H):A=L
	B=A
	for B in['/remote','/sd','/flash',E,A,L]:
		try:C=os.stat(B);break
		except F:continue
	return B
def AK(filename):
	try:
		if os.stat(filename)[0]>>14:return O
		return B
	except F:return B
def s():b("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=C
	if d(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:s()
	elif d(sys.argv)==2:s()
	return path
def t():
	try:A=bytes('abc',encoding='utf8');C=t.__module__;return B
	except(u,H):return O
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_asyncio','_boot_fat','_espnow','_onewire','_pyscript','_rp2','_thread','_uasyncio','abc','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','alif','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','base64','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','builtins','cc3200','cmath','collections','collections/__init__','collections/defaultdict','copy','crypto','cryptolib','curl','datetime','deflate','dht','display','display_driver_utils','ds18x20','embed','encoder','errno','esp','esp32','esp8266','espidf','espnow','ffi','flashbdev','fnmatch','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','gzip','hashlib','heapq','hmac','html/__init__','hub75','ili9341','ili9XXX','imagetools','inisetup','inspect','interstate75','io','itertools','jpegdec','js','jsffi','json','lcd160cr','locale','lodepng',A2,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','marshal','math','microWebSocket','microWebSrv','microWebTemplate',j,'mimxrt','mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','nrf','ntptime','onewire','openamp','operator','os','os/__init__','os/path','pathlib','pcf85063a','pic16bit','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform','powerpc','pyb','pye','pyscript','pyscript/__init__','pyscript/fs','qemu','qrcode','random','renesas','renesas-ra','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stat','stm','stm32','string','struct','sys','tarfile/__init__','tarfile/write','termios','time','tls','tpcalib','types','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','unittest/__init__',q,'uos','uplatform','urandom','ure','urequests','urllib/urequest','usb/device','usb/device/cdc','usb/device/hid','usb/device/keyboard','usb/device/midi','usb/device/mouse','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uu','uwebsocket','uzlib',A,'vfs','webassembly','websocket','websocket_helper',A5,'wipy','writer','xpt2046','ymodem','zephyr','zlib','zsensor'];K.collect();stubber.create_all_stubs()
if __name__=='__main__'or t():
	if not AK('no_auto_stubber.txt'):
		b(f"createstubs.py: {__version__}")
		try:K.threshold(4096);K.enable()
		except BaseException:pass
		main()