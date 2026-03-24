'\nCreate stubs for (all) modules on a MicroPython board\n'
A5='windows'
A4='No report file'
A3='Failed to create the report.'
A2='logging'
A1='method'
A0='function'
z='stubber'
y=isinstance
x=KeyError
w=sorted
v=NotImplementedError
r='unix'
q='arch'
p='variant'
o=',\n'
n='dict'
m='list'
l='tuple'
k='micropython'
j=TypeError
i=repr
f='-preview'
e=len
d=str
c=getattr
a=print
Y='family'
X='board_id'
V='board'
U=IndexError
T=open
S=ImportError
Q='mpy'
W='*'
O=dir
N='build'
M='port'
L='.'
H=AttributeError
R=Exception
G='-'
P=True
D=OSError
J=None
A='version'
F='/'
C=''
B=False
import gc as K,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except S:pass
try:from collections import OrderedDict as s
except S:from ucollections import OrderedDict as s
try:import inspect as Z;b=P
except S:b=B
__version__='v1.26.5a0'
A6=2
A7=44
AB=2
AL=['lib','/lib','/sd/lib','/flash/lib',L]
class I:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=a
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
E=I.getLogger(z)
I.basicConfig(level=I.INFO)
class Stubber:
	'Generate stubs for modules in firmware'
	def __init__(A,path=C,firmware_id=C):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise v('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A.info=_info();E.info('Port: {}'.format(A.info[M]));E.info('Board: {}'.format(A.info[V]));E.info('Board_ID: {}'.format(A.info[X]));K.collect()
		if C:A._fwid=C.lower()
		elif A.info[Y]==k:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(G)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=K.mem_free()
		if path:
			if path.endswith(F):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',F)
		try:g(path+F)
		except D:E.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=J;A._json_first=B
	def load_exlusions(B):
		try:
			with T('modulelist_exclude.txt','r')as C:
				for F in C:
					A=F.strip()
					if A and A not in B.excluded:B.excluded.append(A);E.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except D:pass
	def get_obj_attributes(L,item_instance):
		'extract information of the objects members and attributes';G=item_instance;B=[];J=[]
		for A in O(G):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=c(G,A)
				try:E=i(type(D)).split("'")[1]
				except U:E=C
				if E in{'int','float','str','bool',l,m,n}:F=1
				elif E in{A0,A1}:F=2
				elif E in'class':F=3
				else:F=4
				B.append((A,i(D),i(type(D)),D,F))
			except H as I:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,G,I))
			except MemoryError as I:a('MemoryError: {}'.format(I));sleep(1);reset()
		B=w([A for A in B if not A[0].startswith('__')],key=lambda x:x[4]);K.collect();return B,J
	def add_modules(A,modules):'Add additional modules to be exported';A.modules=w(set(A.modules)|set(modules))
	def create_all_stubs(A):
		'Create stubs for all configured modules';E.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();K.collect()
		for B in A.modules:A.create_one_stub(B)
		A.report_end();E.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:E.warning('Skip module: {:<25}        : Known problematic'.format(A));return B
		if A in C.excluded:E.warning('Skip module: {:<25}        : Excluded'.format(A));return B
		H='{}/{}.pyi'.format(C.path,A.replace(L,F));K.collect();G=B
		try:G=C.create_module_stub(A,H)
		except D:return B
		K.collect();return G
	def create_module_stub(H,module_name,file_name=J):
		"Create a Stub of a single python module\n\n        Args:\n        - module_name (str): name of the module to document. This module will be imported.\n        - file_name (Optional[str]): the 'path/filename.pyi' to write to. If omitted will be created based on the module name.\n        ";G=file_name;A=module_name
		if G is J:I=A.replace(L,'_')+'.pyi';G=H.path+F+I
		else:I=G.split(F)[-1]
		if F in A:A=A.replace(F,L)
		M=J
		try:M=__import__(A,J,J,W);O=K.mem_free();E.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,I,O))
		except S:return B
		g(G)
		with T(G,'w')as N:Q=d(H.info).replace('OrderedDict(',C).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,Q,__version__);N.write(R);N.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n');H.write_object_stub(N,M,A,C)
		H.report_add(A,G)
		if A not in{'os','sys',A2,'gc'}:
			try:del M
			except(D,x):E.warning('could not del new_module')
		K.collect();return P
	def write_object_stub(k,fp,object_expr,obj_name,indent,in_class=0):
		'Write a module/object stub to an open file. Can be called recursive.';AA=' at ...>';A9='{0}{1}: {3} = {2}\n';A8='bound_method';A7='{}*args, **kwargs';A6='Incomplete';A5='    """{0}"""\n';A4='\\"\\"\\"';u='    ';t='Exception';o=object_expr;j=' at ';i=', ';h='self, ';g='\n';X=in_class;S=fp;D=indent;K.collect()
		if o in k.problematic:E.warning('SKIPPING problematic module:{}'.format(o));return
		AC,v=k.get_obj_attributes(o)
		if v:E.error(v)
		for(G,N,T,U,_)in AC:
			if G in['classmethod','staticmethod','BaseException',t]:continue
			if G[0].isdigit():E.warning('NameError: invalid name {}'.format(G));continue
			if T=="<class 'type'>"and e(D)<=AB*4:
				w=C;x=G.endswith(t)or G.endswith('Error')or G in['KeyboardInterrupt','StopIteration','SystemExit']
				if x:w=t
				H='\n{}class {}({}):\n'.format(D,G,w)
				if x:H+=D+'    ...\n';S.write(H);continue
				S.write(H)
				try:
					L=U.__doc__
					if L and y(L,d):
						L=L.strip().replace('"""',A4).replace(g,g+D+u)
						if L:S.write(D+A5.format(L))
				except R:pass
				k.write_object_stub(S,U,'{0}.{1}'.format(obj_name,G),D+u,X+1);H=D+'    def __init__(self, *argv, **kwargs) -> None:\n';H+=D+'        ...\n\n';S.write(H)
			elif any(A in T for A in[A1,A0,'closure']):
				p=A6;z=C
				if X>0:z=h
				f=B;q=B;A2=B
				if b:
					try:f=Z.iscoroutinefunction(U)
					except R:pass
					if not f:
						try:q=c(Z,'isasyncgenfunction',lambda _:B)(U)
						except R:pass
					if not f and not q:
						try:A2=Z.isgeneratorfunction(U)
						except R:pass
				V=J
				if b:
					try:
						r=Z.signature(U);A=[];I=B;Y=B
						for(M,s)in r.parameters.items():
							Q=c(s,'kind',J)
							if Q==0:I=P;A.append(M)
							elif Q==1:
								if I:A.append(F);I=B
								A.append(M)
							elif Q==2:
								if I:A.append(F);I=B
								Y=P;A.append(W+M)
							elif Q==3:
								if I:A.append(F);I=B
								if not Y:A.append(W);Y=P
								A.append(M)
							elif Q==4:
								if I:A.append(F);I=B
								A.append('**'+M)
							else:A.append(M)
						if I:A.append(F)
						if X>0 and A and A[0]not in(W,F):A=A[1:]
						if X>0:V=h+i.join(A)if A else'self'
						else:V=i.join(A)
					except R:pass
				if V is J:V=A7.format(z)
				if A8 in T or A8 in N:H='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,G,p)
				elif f:H='{}async def {}({}) -> {}:\n'.format(D,G,V,p)
				elif q:H='{}async def {}({}) -> AsyncGenerator:\n'.format(D,G,V)
				elif A2:H='{}def {}({}) -> Generator:\n'.format(D,G,V)
				else:H='{}def {}({}) -> {}:\n'.format(D,G,V,p)
				try:
					L=U.__doc__
					if L and y(L,d):
						L=L.strip().replace('"""',A4).replace(g,g+D+u)
						if L:H+=D+A5.format(L)
				except R:pass
				H+=D+'    ...\n\n';S.write(H)
			elif T=="<class 'module'>":0
			elif T.startswith("<class '"):
				O=T[8:-2];H=C
				if O in('str','int','float','bool','bytearray','bytes'):
					if G.upper()==G:H='{0}{1}: Final[{3}] = {2}\n'.format(D,G,N,O)
					else:H=A9.format(D,G,N,O)
				elif O in(n,m,l):AD={n:'{}',m:'[]',l:'()'};H=A9.format(D,G,AD[O],O)
				elif O in('object','set','frozenset','Pin'):H='{0}{1}: {2} ## = {4}\n'.format(D,G,O,T,N)
				elif O=='generator':
					AE=h if X>0 else C;a=J;A3=B
					if b:
						try:A3=Z.iscoroutinefunction(U)
						except R:pass
						try:
							r=Z.signature(U);A=[];I=B;Y=B
							for(M,s)in r.parameters.items():
								Q=c(s,'kind',J)
								if Q==0:I=P;A.append(M)
								elif Q==1:
									if I:A.append(F);I=B
									A.append(M)
								elif Q==2:
									if I:A.append(F);I=B
									Y=P;A.append(W+M)
								elif Q==3:
									if I:A.append(F);I=B
									if not Y:A.append(W);Y=P
									A.append(M)
								elif Q==4:
									if I:A.append(F);I=B
									A.append('**'+M)
								else:A.append(M)
							if I:A.append(F)
							if X>0 and A and A[0]not in(W,F):A=A[1:]
							if X>0:a=h+i.join(A)if A else'self'
							else:a=i.join(A)
						except R:pass
					if a is J:a=A7.format(AE)
					if A3:H='{0}async def {1}({2}) -> Incomplete:\n{0}    ...\n\n'.format(D,G,a)
					else:H='{0}def {1}({2}) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(D,G,a,O,N)
				else:
					O=A6
					if j in N:N=N.split(j)[0]+AA
					if j in N:N=N.split(j)[0]+AA
					H='{0}{1}: {2} ## {3} = {4}\n'.format(D,G,O,T,N)
				S.write(H)
			else:S.write("# all other, type = '{0}'\n".format(T));S.write(D+G+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		"Turn _fwid from 'v1.2.3' into '1_2_3' to be used in filename";A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(B,path=C):
		'Remove all files from the stub folder'
		if not path:path=B.path
		E.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except(D,H):return
		for F in C:
			A='{}/{}'.format(path,F)
			try:os.remove(A)
			except D:
				try:B.clean(A);os.rmdir(A)
				except D:pass
	def report_start(B,filename='modules.json'):
		'Start a report of the modules that have been stubbed\n        "create json with list of exported modules';F='firmware';B._json_name='{}/{}'.format(B.path,filename);B._json_first=P;g(B._json_name);E.info('Report file: {}'.format(B._json_name));K.collect()
		try:
			with T(B._json_name,'w')as C:C.write('{');C.write(dumps({F:B.info})[1:-1]);C.write(o);C.write(dumps({z:{A:__version__},'stubtype':F})[1:-1]);C.write(o);C.write('"modules" :[\n')
		except D as G:E.error(A3);B._json_name=J;raise G
	def report_add(A,module_name,stub_file):
		'Add a module to the report'
		if not A._json_name:raise R(A4)
		try:
			with T(A._json_name,'a')as C:
				if not A._json_first:C.write(o)
				else:A._json_first=B
				G='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',F));C.write(G)
		except D:E.error(A3)
	def report_end(A):
		if not A._json_name:raise R(A4)
		with T(A._json_name,'a')as B:B.write('\n]}')
		E.info('Path: {}'.format(A.path))
def g(path):
	'Create nested folders if needed';A=C=0
	while A!=-1:
		A=path.find(F,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except D as G:
				if G.args[0]in[A6,A7]:
					try:E.debug('Create folder {}'.format(B));os.mkdir(B)
					except D as H:E.error('failed to create folder {}'.format(B));raise H
		C=A+1
def h(s):
	B=' on '
	if not s:return C
	s=s.split(B,1)[0]if B in s else s
	if s.startswith('v'):
		if not G in s:return C
		A=s.split(G)[1];return A
	if not f in s:return C
	A=s.split(f)[1].split(L)[1];return A
def A8():
	'Get basic system implementation details.'
	try:B=sys.implementation[0]
	except j:B=sys.implementation.name
	D=s({Y:B,A:C,N:C,'ver':C,M:sys.platform,V:'UNKNOWN',X:C,p:C,'cpu':C,Q:C,q:C});return D
def A9(info):
	'Normalize port names to be consistent with the repo.';A=info
	if A[M].startswith('pyb'):A[M]='stm32'
	elif A[M]=='win32':A[M]=A5
	elif A[M]=='linux':A[M]=r
def AA(info):
	'Extract version information from sys.implementation.'
	try:info[A]=AI(sys.implementation.version)
	except H:pass
def AC(info):
	'Extract board, CPU, and machine details.';A=info
	try:
		D=sys.implementation._machine if'_machine'in O(sys.implementation)else os.uname().machine;A[V]=D.strip();B=sys.implementation._build if'_build'in O(sys.implementation)else C
		if B:A[V]=B.split(G)[0];A[p]=B.split(G)[1]if G in B else C
		A[X]=B;A['cpu']=D.split('with')[-1].strip();A[Q]=sys.implementation._mpy if'_mpy'in O(sys.implementation)else sys.implementation.mpy if Q in O(sys.implementation)else C
	except(H,U):pass
	if not A[X]:AJ(A)
def AD(info):
	'Extract build information from various system sources.';B=info
	try:
		if'uname'in O(os):
			B[N]=h(os.uname()[3])
			if not B[N]:B[N]=h(os.uname()[2])
		elif A in O(sys):B[N]=h(sys.version)
	except(H,U,j):pass
	if B[A]==C and sys.platform not in(r,'win32'):
		try:D=os.uname();B[A]=D.release
		except(U,H,j):pass
def AE(info):
	'Detect special firmware families (pycopy, pycom, ev3-pybricks).';D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,J,J,G);A[Y]=E;del H;break
		except(S,x):pass
	if A[Y]==D:A['release']='2.0.0'
def AF(info):
	'Process MicroPython-specific version formatting.';B=info
	if B[Y]==k:
		if B[A]and B[A].endswith('.0')and B[A]>='1.10.0'and B[A]<='1.19.9':B[A]=B[A][:-2]
def AG(info):
	'Process MPY architecture and version information.';A=info
	if Q in A and A[Q]:
		B=int(A[Q])
		try:
			C=[J,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[q]=C
		except U:A[q]='unknown'
		A[Q]='v{}.{}'.format(B&255,B>>8&3)
def AH(info):
	'Handle final version string formatting.';B=info
	if B[N]and not B[A].endswith(f):B[A]=B[A]+f
	B['ver']=f"{B[A]}-{B[N]}"if B[N]else f"{B[A]}"
def _info():'\n    Gather comprehensive system information for MicroPython stubbing.\n\n    Returns a dictionary containing family, version, port, board, and other\n    system details needed for stub generation.\n    ';A=A8();A9(A);AA(A);AC(A);AD(A);AE(A);AF(A);AG(A);AH(A);return A
def AI(version):
	A=version;B=L.join([d(A)for A in A[:3]])
	if e(A)>3 and A[3]:B+=G+A[3]
	return B
def AJ(info):
	'Read the board_id from the boardname.py file that may have been created upfront';B=info
	try:from boardname import BOARD_ID as A;E.info('Found BOARD_ID: {}'.format(A))
	except S:E.warning('BOARD_ID not found');A=C
	B[X]=A;B[V]=A.split(G)[0]if G in A else A;B[p]==A.split(G)[1]if G in A else C
def get_root():
	'Determine the root folder of the device'
	try:A=os.getcwd()
	except(D,H):A=L
	B=A
	for B in['/remote','/sd','/flash',F,A,L]:
		try:C=os.stat(B);break
		except D:continue
	return B
def AK(filename):
	try:
		if os.stat(filename)[0]>>14:return P
		return B
	except D:return B
def t():a("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	'get --path from cmdline. [unix/win]';path=C
	if e(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:t()
	elif e(sys.argv)==2:t()
	return path
def u():
	'runtime test to determine full or micropython'
	try:A=bytes('abc',encoding='utf8');C=u.__module__;return B
	except(v,H):return P
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_asyncio','_boot_fat','_espnow','_onewire','_pyscript','_rp2','_thread','_uasyncio','abc','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','alif','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','base64','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','builtins','cc3200','cmath','collections','collections/__init__','collections/defaultdict','copy','crypto','cryptolib','curl','datetime','deflate','dht','display','display_driver_utils','ds18x20','embed','encoder','errno','esp','esp32','esp8266','espidf','espnow','ffi','flashbdev','fnmatch','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','gzip','hashlib','heapq','hmac','html/__init__','hub75','ili9341','ili9XXX','imagetools','inisetup','inspect','interstate75','io','itertools','jpegdec','js','jsffi','json','lcd160cr','locale','lodepng',A2,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','marshal','math','microWebSocket','microWebSrv','microWebTemplate',k,'mimxrt','mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','nrf','ntptime','onewire','openamp','operator','os','os/__init__','os/path','pathlib','pcf85063a','pic16bit','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform','powerpc','pyb','pye','pyscript','pyscript/__init__','pyscript/fs','qemu','qrcode','random','renesas','renesas-ra','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stat','stm','stm32','string','struct','sys','tarfile/__init__','tarfile/write','termios','time','tls','tpcalib','types','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','unittest/__init__',r,'uos','uplatform','urandom','ure','urequests','urllib/urequest','usb/device','usb/device/cdc','usb/device/hid','usb/device/keyboard','usb/device/midi','usb/device/mouse','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uu','uwebsocket','uzlib',A,'vfs','webassembly','websocket','websocket_helper',A5,'wipy','writer','xpt2046','ymodem','zephyr','zlib','zsensor'];K.collect();stubber.create_all_stubs()
if __name__=='__main__'or u():
	if not AK('no_auto_stubber.txt'):
		a(f"createstubs.py: {__version__}")
		try:K.threshold(4096);K.enable()
		except BaseException:pass
		main()