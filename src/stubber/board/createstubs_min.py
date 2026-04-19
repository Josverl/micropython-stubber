'\nCreate stubs for (all) modules on a MicroPython board\n'
AA='windows'
A9='No report file'
A8='Failed to create the report.'
A7='logging'
A6='builtins'
A5='method'
A4='function'
A3='stubber'
A2='esp8266'
A1=isinstance
A0=KeyError
z=MemoryError
y=NotImplementedError
t='unix'
s='arch'
r='variant'
q=',\n'
p='dict'
o='list'
n='tuple'
m='__'
l='micropython'
k=TypeError
j=repr
b='-preview'
e=len
d=str
c=getattr
Z='family'
Y='board_id'
W='board'
V=IndexError
U=open
T=print
S=ImportError
Q='mpy'
X='*'
O='build'
N='.'
M=dir
I='port'
H=AttributeError
R=Exception
G='-'
P=True
E=OSError
J=None
A='version'
F='/'
C=''
B=False
import gc as K,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset as f
except S:
	def f():T('Reset called - exiting');sys.exit(0)
try:from collections import OrderedDict as u
except S:from ucollections import OrderedDict as u
v=A2,
AB=sys.platform in v
g=B
if not AB:
	try:import inspect as a;g=P
	except S:g=B
__version__='v1.28.2'
AC=2
AD=44
AE=2
AR=['lib','/lib','/sd/lib','/flash/lib',N]
class L:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=T
	@staticmethod
	def getLogger(name):return L()
	@classmethod
	def basicConfig(A,level):A.level=level
	def debug(A,msg):
		if A.level<=L.DEBUG:A.prnt('DEBUG :',msg)
	def info(A,msg):
		if A.level<=L.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=L.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=L.ERROR:A.prnt('ERROR :',msg)
D=L.getLogger(A3)
L.basicConfig(level=L.INFO)
class Stubber:
	'Generate stubs for modules in firmware'
	def __init__(A,path=C,firmware_id=C):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise y('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A.info=_info();D.info('Port: {}'.format(A.info[I]));D.info('Board: {}'.format(A.info[W]));D.info('Board_ID: {}'.format(A.info[Y]));A._is_low_mem_port=A.info[I]in v;A._capture_docstrings=not A._is_low_mem_port;A._use_inspect=g and not A._is_low_mem_port
		if A._is_low_mem_port:D.info('Low-memory mode: disabling inspect and docstrings')
		K.collect()
		if C:A._fwid=C.lower()
		elif A.info[Z]==l:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(G)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=K.mem_free()
		if path:
			if path.endswith(F):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',F)
		try:h(path+F)
		except E:D.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=J;A._json_first=B
	def load_exlusions(B):
		try:
			with U('modulelist_exclude.txt','r')as C:
				for F in C:
					A=F.strip()
					if A and A not in B.excluded:B.excluded.append(A);D.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except E:pass
	def get_obj_attributes(L,item_instance):
		'extract information of the objects members and attributes';G=item_instance;B=[];J=[]
		for A in M(G):
			if A.startswith(m)and not A in L.modules:continue
			try:
				D=c(G,A)
				try:E=j(type(D)).split("'")[1]
				except V:E=C
				if E in{'int','float','str','bool',n,o,p}:F=1
				elif E in{A4,A5}:F=2
				elif E in'class':F=3
				else:F=4
				B.append((A,j(D),j(type(D)),D,F))
			except H as I:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,G,I))
			except z as I:T('MemoryError: {}'.format(I));sleep(1);f()
		B=sorted([A for A in B if not A[0].startswith(m)],key=lambda x:x[4]);K.collect();return B,J
	def add_modules(A,modules):'Add additional modules to be exported';A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		'Create stubs for all configured modules';D.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();K.collect()
		for B in A.modules:A.create_one_stub(B)
		A.report_end();D.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:D.warning('Skip module: {:<25}        : Known problematic'.format(A));return B
		if A in C.excluded:D.warning('Skip module: {:<25}        : Excluded'.format(A));return B
		H='{}/{}.pyi'.format(C.path,A.replace(N,F));K.collect();G=B
		try:G=C.create_module_stub(A,H)
		except E:return B
		K.collect();return G
	def create_module_stub(G,module_name,file_name=J):
		"Create a Stub of a single python module\n\n        Args:\n        - module_name (str): name of the module to document. This module will be imported.\n        - file_name (Optional[str]): the 'path/filename.pyi' to write to. If omitted will be created based on the module name.\n        ";H=file_name;A=module_name
		if H is J:M=A.replace(N,'_')+'.pyi';H=G.path+F+M
		else:M=H.split(F)[-1]
		if F in A:A=A.replace(F,N)
		I=J
		try:I=__import__(A,J,J,X);O=K.mem_free();D.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,M,O))
		except S:return B
		h(H)
		with U(H,'w')as L:
			Q=d(G.info).replace('OrderedDict(',C).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,G._fwid,Q,__version__);L.write(R);L.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n')
			if G._is_low_mem_port and A in{A6,'uasyncio.__init__'}:D.warning('Low-memory mode: using shallow stub strategy.');G.write_shallow_stub(L,I)
			else:
				try:G.write_object_stub(L,I,A,C)
				except z:
					if not G._is_low_mem_port:raise
					K.collect();D.warning('Low-memory mode: MemoryError while stubbing {}, resetting'.format(A));f()
		G.report_add(A,H)
		if A not in{'os','sys',A7,'gc'}:
			try:del I
			except(E,A0):D.warning('could not del new_module')
		K.collect();return P
	def write_shallow_stub(B,fp,module_obj):
		fp.write('# Low-memory mode: shallow stub with names only\n')
		for A in M(module_obj):
			if A.startswith(m)and not A in B.modules:continue
			if not A or A[0].isdigit():continue
			fp.write('{}: Incomplete\n'.format(A))
	def write_object_stub(V,fp,object_expr,obj_name,indent,in_class=0):
		'Write a module/object stub to an open file. Can be called recursive.';A9=' at ...>';A8='{0}{1}: {3} = {2}\n';A7='bound_method';A6='{}*args, **kwargs';A3='Incomplete';A2='    """{0}"""\n';A0='\\"\\"\\"';t='    ';s='Exception';k=object_expr;j=' at ';i=', ';h='self, ';g='\n';Y=in_class;S=fp;E=indent;K.collect()
		if k in V.problematic:D.warning('SKIPPING problematic module:{}'.format(k));return
		AA,u=V.get_obj_attributes(k)
		if u:D.error(u)
		for(G,N,T,U,_)in AA:
			if G in['classmethod','staticmethod','BaseException',s]:continue
			if G[0].isdigit():D.warning('NameError: invalid name {}'.format(G));continue
			if T=="<class 'type'>"and e(E)<=AE*4:
				v=C;w=G.endswith(s)or G.endswith('Error')or G in['KeyboardInterrupt','StopIteration','SystemExit']
				if w:v=s
				H='\n{}class {}({}):\n'.format(E,G,v)
				if w:H+=E+'    ...\n';S.write(H);continue
				S.write(H)
				if V._capture_docstrings:
					try:
						L=U.__doc__
						if L and A1(L,d):
							L=L.strip().replace('"""',A0).replace(g,g+E+t)
							if L:S.write(E+A2.format(L))
					except R:pass
				V.write_object_stub(S,U,'{0}.{1}'.format(obj_name,G),E+t,Y+1);H=E+'    def __init__(self, *argv, **kwargs) -> None:\n';H+=E+'        ...\n\n';S.write(H)
			elif any(A in T for A in[A5,A4,'closure']):
				l=A3;x=C
				if Y>0:x=h
				f=B;m=B;y=B
				if V._use_inspect:
					try:f=a.iscoroutinefunction(U)
					except R:pass
					if not f:
						try:m=c(a,'isasyncgenfunction',lambda _:B)(U)
						except R:pass
					if not f and not m:
						try:y=a.isgeneratorfunction(U)
						except R:pass
				W=J
				if V._use_inspect:
					try:
						q=a.signature(U);A=[];I=B;Z=B
						for(M,r)in q.parameters.items():
							Q=c(r,'kind',J)
							if Q==0:I=P;A.append(M)
							elif Q==1:
								if I:A.append(F);I=B
								A.append(M)
							elif Q==2:
								if I:A.append(F);I=B
								Z=P;A.append(X+M)
							elif Q==3:
								if I:A.append(F);I=B
								if not Z:A.append(X);Z=P
								A.append(M)
							elif Q==4:
								if I:A.append(F);I=B
								A.append('**'+M)
							else:A.append(M)
						if I:A.append(F)
						if Y>0 and A and A[0]not in(X,F):A=A[1:]
						if Y>0:W=h+i.join(A)if A else'self'
						else:W=i.join(A)
					except R:pass
				if W is J:W=A6.format(x)
				if A7 in T or A7 in N:H='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,G,l)
				elif f:H='{}async def {}({}) -> {}:\n'.format(E,G,W,l)
				elif m:H='{}async def {}({}) -> AsyncGenerator:\n'.format(E,G,W)
				elif y:H='{}def {}({}) -> Generator:\n'.format(E,G,W)
				else:H='{}def {}({}) -> {}:\n'.format(E,G,W,l)
				if V._capture_docstrings:
					try:
						L=U.__doc__
						if L and A1(L,d):
							L=L.strip().replace('"""',A0).replace(g,g+E+t)
							if L:H+=E+A2.format(L)
					except R:pass
				H+=E+'    ...\n\n';S.write(H)
			elif T=="<class 'module'>":0
			elif T.startswith("<class '"):
				O=T[8:-2];H=C
				if O in('str','int','float','bool','bytearray','bytes'):
					if G.upper()==G:H='{0}{1}: Final[{3}] = {2}\n'.format(E,G,N,O)
					else:H=A8.format(E,G,N,O)
				elif O in(p,o,n):AB={p:'{}',o:'[]',n:'()'};H=A8.format(E,G,AB[O],O)
				elif O in('object','set','frozenset','Pin'):H='{0}{1}: {2} ## = {4}\n'.format(E,G,O,T,N)
				elif O=='generator':
					AC=h if Y>0 else C;b=J;z=B
					if V._use_inspect:
						try:z=a.iscoroutinefunction(U)
						except R:pass
						try:
							q=a.signature(U);A=[];I=B;Z=B
							for(M,r)in q.parameters.items():
								Q=c(r,'kind',J)
								if Q==0:I=P;A.append(M)
								elif Q==1:
									if I:A.append(F);I=B
									A.append(M)
								elif Q==2:
									if I:A.append(F);I=B
									Z=P;A.append(X+M)
								elif Q==3:
									if I:A.append(F);I=B
									if not Z:A.append(X);Z=P
									A.append(M)
								elif Q==4:
									if I:A.append(F);I=B
									A.append('**'+M)
								else:A.append(M)
							if I:A.append(F)
							if Y>0 and A and A[0]not in(X,F):A=A[1:]
							if Y>0:b=h+i.join(A)if A else'self'
							else:b=i.join(A)
						except R:pass
					if b is J:b=A6.format(AC)
					if z:H='{0}async def {1}({2}) -> Incomplete:\n{0}    ...\n\n'.format(E,G,b)
					else:H='{0}def {1}({2}) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(E,G,b,O,N)
				else:
					O=A3
					if j in N:N=N.split(j)[0]+A9
					if j in N:N=N.split(j)[0]+A9
					H='{0}{1}: {2} ## {3} = {4}\n'.format(E,G,O,T,N)
				S.write(H)
			else:S.write("# all other, type = '{0}'\n".format(T));S.write(E+G+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		"Turn _fwid from 'v1.2.3' into '1_2_3' to be used in filename";A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(B,path=C):
		'Remove all files from the stub folder'
		if not path:path=B.path
		D.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except(E,H):return
		for F in C:
			A='{}/{}'.format(path,F)
			try:os.remove(A)
			except E:
				try:B.clean(A);os.rmdir(A)
				except E:pass
	def report_start(B,filename='modules.json'):
		'Start a report of the modules that have been stubbed\n        "create json with list of exported modules';F='firmware';B._json_name='{}/{}'.format(B.path,filename);B._json_first=P;h(B._json_name);D.info('Report file: {}'.format(B._json_name));K.collect()
		try:
			with U(B._json_name,'w')as C:C.write('{');C.write(dumps({F:B.info})[1:-1]);C.write(q);C.write(dumps({A3:{A:__version__},'stubtype':F})[1:-1]);C.write(q);C.write('"modules" :[\n')
		except E as G:D.error(A8);B._json_name=J;raise G
	def report_add(A,module_name,stub_file):
		'Add a module to the report'
		if not A._json_name:raise R(A9)
		try:
			with U(A._json_name,'a')as C:
				if not A._json_first:C.write(q)
				else:A._json_first=B
				G='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',F));C.write(G)
		except E:D.error(A8)
	def report_end(A):
		if not A._json_name:raise R(A9)
		with U(A._json_name,'a')as B:B.write('\n]}')
		D.info('Path: {}'.format(A.path))
def h(path):
	'Create nested folders if needed';A=C=0
	while A!=-1:
		A=path.find(F,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except E as G:
				if G.args[0]in[AC,AD]:
					try:D.debug('Create folder {}'.format(B));os.mkdir(B)
					except E as H:D.error('failed to create folder {}'.format(B));raise H
		C=A+1
def i(s):
	B=' on '
	if not s:return C
	s=s.split(B,1)[0]if B in s else s
	if s.startswith('v'):
		if not G in s:return C
		A=s.split(G)[1];return A
	if not b in s:return C
	A=s.split(b)[1].split(N)[1];return A
def AF():
	'Get basic system implementation details.'
	try:B=sys.implementation[0]
	except k:B=sys.implementation.name
	D=u({Z:B,A:C,O:C,'ver':C,I:sys.platform,W:'UNKNOWN',Y:C,r:C,'cpu':C,Q:C,s:C});return D
def AG(info):
	'Normalize port names to be consistent with the repo.';A=info
	if A[I].startswith('pyb'):A[I]='stm32'
	elif A[I]=='win32':A[I]=AA
	elif A[I]=='linux':A[I]=t
def AH(info):
	'Extract version information from sys.implementation.'
	try:info[A]=AO(sys.implementation.version)
	except H:pass
def AI(info):
	'Extract board, CPU, and machine details.';A=info
	try:
		D=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[W]=D.strip();B=sys.implementation._build if'_build'in M(sys.implementation)else C
		if B:A[W]=B.split(G)[0];A[r]=B.split(G)[1]if G in B else C
		A[Y]=B;A['cpu']=D.split('with')[-1].strip();A[Q]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if Q in M(sys.implementation)else C
	except(H,V):pass
	if not A[Y]:AP(A)
def AJ(info):
	'Extract build information from various system sources.';B=info
	try:
		if'uname'in M(os):
			B[O]=i(os.uname()[3])
			if not B[O]:B[O]=i(os.uname()[2])
		elif A in M(sys):B[O]=i(sys.version)
	except(H,V,k):pass
	if B[A]==C and sys.platform not in(t,'win32'):
		try:D=os.uname();B[A]=D.release
		except(V,H,k):pass
def AK(info):
	'Detect special firmware families (pycopy, pycom, ev3-pybricks).';D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,J,J,G);A[Z]=E;del H;break
		except(S,A0):pass
	if A[Z]==D:A['release']='2.0.0'
def AL(info):
	'Process MicroPython-specific version formatting.';B=info
	if B[Z]==l:
		if B[A]and B[A].endswith('.0')and B[A]>='1.10.0'and B[A]<='1.19.9':B[A]=B[A][:-2]
def AM(info):
	'Process MPY architecture and version information.';A=info
	if Q in A and A[Q]:
		B=int(A[Q])
		try:
			C=[J,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[s]=C
		except V:A[s]='unknown'
		A[Q]='v{}.{}'.format(B&255,B>>8&3)
def AN(info):
	'Handle final version string formatting.';B=info
	if B[O]and not B[A].endswith(b):B[A]=B[A]+b
	B['ver']=f"{B[A]}-{B[O]}"if B[O]else f"{B[A]}"
def _info():'\n    Gather comprehensive system information for MicroPython stubbing.\n\n    Returns a dictionary containing family, version, port, board, and other\n    system details needed for stub generation.\n    ';A=AF();AG(A);AH(A);AI(A);AJ(A);AK(A);AL(A);AM(A);AN(A);return A
def AO(version):
	A=version;B=N.join([d(A)for A in A[:3]])
	if e(A)>3 and A[3]:B+=G+A[3]
	return B
def AP(info):
	'Read the board_id from the boardname.py file that may have been created upfront';B=info
	try:from boardname import BOARD_ID as A;D.info('Found BOARD_ID: {}'.format(A))
	except S:D.warning('BOARD_ID not found');A=C
	B[Y]=A;B[W]=A.split(G)[0]if G in A else A;B[r]==A.split(G)[1]if G in A else C
def get_root():
	'Determine the root folder of the device'
	try:A=os.getcwd()
	except(E,H):A=N
	B=A
	for B in['/remote','/sd','/flash',F,A,N]:
		try:C=os.stat(B);break
		except E:continue
	return B
def AQ(filename):
	try:
		if os.stat(filename)[0]>>14:return P
		return B
	except E:return B
def w():T("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	'get --path from cmdline. [unix/win]';path=C
	if e(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:w()
	elif e(sys.argv)==2:w()
	return path
def x():
	'runtime test to determine full or micropython'
	try:A=bytes('abc',encoding='utf8');C=x.__module__;return B
	except(y,H):return P
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_asyncio','_boot_fat','_espnow','_onewire','_pyscript','_rp2','_thread','_uasyncio','abc','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','alif','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','base64','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree',A6,'cc3200','cmath','collections','collections/__init__','collections/defaultdict','copy','crypto','cryptolib','curl','datetime','deflate','dht','display','display_driver_utils','ds18x20','embed','encoder','errno','esp','esp32',A2,'espidf','espnow','ffi','flashbdev','fnmatch','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','gzip','hashlib','heapq','hmac','html/__init__','hub75','ili9341','ili9XXX','imagetools','inisetup','inspect','interstate75','io','itertools','jpegdec','js','jsffi','json','lcd160cr','locale','lodepng',A7,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','marshal','math','microWebSocket','microWebSrv','microWebTemplate',l,'mimxrt','mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','nrf','ntptime','onewire','openamp','operator','os','os/__init__','os/path','pathlib','pcf85063a','pic16bit','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform','powerpc','pyb','pye','pyscript','pyscript/__init__','pyscript/fs','qemu','qrcode','random','renesas','renesas-ra','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stat','stm','stm32','string','struct','sys','tarfile/__init__','tarfile/write','termios','time','tls','tpcalib','types','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','unittest/__init__',t,'uos','uplatform','urandom','ure','urequests','urllib/urequest','usb/device','usb/device/cdc','usb/device/hid','usb/device/keyboard','usb/device/midi','usb/device/mouse','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uu','uwebsocket','uzlib',A,'vfs','webassembly','websocket','websocket_helper',AA,'wipy','writer','xpt2046','ymodem','zephyr','zlib','zsensor'];K.collect();stubber.create_all_stubs()
if __name__=='__main__'or x():
	if not AQ('no_auto_stubber.txt'):
		T(f"createstubs.py: {__version__}")
		try:K.threshold(4096);K.enable()
		except BaseException:pass
		main()