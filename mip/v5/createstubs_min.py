'\nCreate stubs for (all) modules on a MicroPython board\n'
AB='windows'
AA='No report file'
A9='Failed to create the report.'
A8='logging'
A7='builtins'
A6='method'
A5='function'
A4='stubber'
A3='esp8266'
A2=ValueError
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
a='-preview'
f=str
e=getattr
Z='family'
X='board_id'
W=IndexError
V=open
U=print
T='board'
c=len
S=ImportError
Q='mpy'
Y='*'
O='build'
N='.'
M=dir
I='port'
H=AttributeError
R=Exception
E='-'
P=True
D=OSError
A='version'
J=None
G='/'
C=''
B=False
import gc as K,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset as d
except S:
	def d():U('Reset called - exiting');sys.exit(0)
try:from collections import OrderedDict as u
except S:from ucollections import OrderedDict as u
v=A3,
AC=sys.platform in v
g=B
if not AC:
	try:import inspect as b;g=P
	except S:g=B
__version__='v1.29.0'
AD=2
AE=44
AI=2
AS=['lib','/lib','/sd/lib','/flash/lib',N]
class L:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=U
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
F=L.getLogger(A4)
L.basicConfig(level=L.INFO)
class Stubber:
	'Generate stubs for modules in firmware'
	def __init__(A,path=C,firmware_id=C):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise y('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A.info=_info();F.info('Port: {}'.format(A.info[I]));F.info('Board: {}'.format(A.info[T]));F.info('Board_ID: {}'.format(A.info[X]));A._is_low_mem_port=A.info[I]in v;A._capture_docstrings=not A._is_low_mem_port;A._use_inspect=g and not A._is_low_mem_port
		if A._is_low_mem_port:F.info('Low-memory mode: disabling inspect and docstrings')
		K.collect()
		if C:A._fwid=C.lower()
		elif A.info[Z]==l:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(E)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=K.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:h(path+G)
		except D:F.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=J;A._json_first=B
	def load_exlusions(B):
		try:
			with V('modulelist_exclude.txt','r')as C:
				for E in C:
					A=E.strip()
					if A and A not in B.excluded:B.excluded.append(A);F.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except D:pass
	def get_obj_attributes(L,item_instance):
		'extract information of the objects members and attributes';G=item_instance;B=[];J=[]
		for A in M(G):
			if A.startswith(m)and not A in L.modules:continue
			try:
				D=e(G,A)
				try:E=j(type(D)).split("'")[1]
				except W:E=C
				if E in{'int','float','str','bool',n,o,p}:F=1
				elif E in{A5,A6}:F=2
				elif E in'class':F=3
				else:F=4
				B.append((A,j(D),j(type(D)),D,F))
			except H as I:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,G,I))
			except z as I:U('MemoryError: {}'.format(I));sleep(1);d()
		B=sorted([A for A in B if not A[0].startswith(m)],key=lambda x:x[4]);K.collect();return B,J
	def add_modules(A,modules):'Add additional modules to be exported';A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		'Create stubs for all configured modules';F.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();K.collect()
		for B in A.modules:A.create_one_stub(B)
		A.report_end();F.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:F.warning('Skip module: {:<25}        : Known problematic'.format(A));return B
		if A in C.excluded:F.warning('Skip module: {:<25}        : Excluded'.format(A));return B
		H='{}/{}.pyi'.format(C.path,A.replace(N,G));K.collect();E=B
		try:E=C.create_module_stub(A,H)
		except D:return B
		K.collect();return E
	def create_module_stub(E,module_name,file_name=J):
		"Create a Stub of a single python module\n\n        Args:\n        - module_name (str): name of the module to document. This module will be imported.\n        - file_name (Optional[str]): the 'path/filename.pyi' to write to. If omitted will be created based on the module name.\n        ";H=file_name;A=module_name
		if H is J:M=A.replace(N,'_')+'.pyi';H=E.path+G+M
		else:M=H.split(G)[-1]
		if G in A:A=A.replace(G,N)
		I=J
		try:I=__import__(A,J,J,Y);O=K.mem_free();F.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,M,O))
		except S:return B
		h(H)
		with V(H,'w')as L:
			Q=f(E.info).replace('OrderedDict(',C).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,E._fwid,Q,__version__);L.write(R);L.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n')
			if E._is_low_mem_port and A in{A7,'uasyncio.__init__'}:F.warning('Low-memory mode: using shallow stub strategy.');E.write_shallow_stub(L,I)
			else:
				try:E.write_object_stub(L,I,A,C)
				except z:
					if not E._is_low_mem_port:raise
					K.collect();F.warning('Low-memory mode: MemoryError while stubbing {}, resetting'.format(A));d()
		E.report_add(A,H)
		if A not in{'os','sys',A8,'gc'}:
			try:del I
			except(D,A0):F.warning('could not del new_module')
		K.collect();return P
	def write_shallow_stub(B,fp,module_obj):
		fp.write('# Low-memory mode: shallow stub with names only\n')
		for A in M(module_obj):
			if A.startswith(m)and not A in B.modules:continue
			if not A or A[0].isdigit():continue
			fp.write('{}: Incomplete\n'.format(A))
	def write_object_stub(X,fp,object_expr,obj_name,indent,in_class=0):
		'Write a module/object stub to an open file. Can be called recursive.';AH=' at ...>';AG='{0}{1}: {3} = {2}\n';AF='{}# inspect: arity={}\n';AE='{}def {}({}) -> {}:\n';AD='bound_method';AC='{}*args, **kwargs';AB='inspect returned arity-only parameters';AA='Incomplete';A9='    """{0}"""\n';A8='\\"\\"\\"';x='self';w='    ';v='Exception';m=object_expr;l=' at ';k=', ';j='kind';i='self, ';h='\n';Z=in_class;S=fp;D=indent;K.collect()
		if m in X.problematic:F.warning('SKIPPING problematic module:{}'.format(m));return
		AJ,y=X.get_obj_attributes(m)
		if y:F.error(y)
		for(H,N,T,U,_)in AJ:
			if H in['classmethod','staticmethod','BaseException',v]:continue
			if H[0].isdigit():F.warning('NameError: invalid name {}'.format(H));continue
			if T=="<class 'type'>"and c(D)<=AI*4:
				z=C;A0=H.endswith(v)or H.endswith('Error')or H in['KeyboardInterrupt','StopIteration','SystemExit']
				if A0:z=v
				E='\n{}class {}({}):\n'.format(D,H,z)
				if A0:E+=D+'    ...\n';S.write(E);continue
				S.write(E)
				if X._capture_docstrings:
					try:
						L=U.__doc__
						if L and A1(L,f):
							L=L.strip().replace('"""',A8).replace(h,h+D+w)
							if L:S.write(D+A9.format(L))
					except R:pass
				X.write_object_stub(S,U,'{0}.{1}'.format(obj_name,H),D+w,Z+1);E=D+'    def __init__(self, *argv, **kwargs) -> None:\n';E+=D+'        ...\n\n';S.write(E)
			elif any(A in T for A in[A6,A5,'closure']):
				q=AA;A3=C
				if Z>0:A3=i
				g=B;r=B;A4=B
				if X._use_inspect:
					try:g=b.iscoroutinefunction(U)
					except R:pass
					if not g:
						try:r=e(b,'isasyncgenfunction',lambda _:B)(U)
						except R:pass
					if not g and not r:
						try:A4=b.isgeneratorfunction(U)
						except R:pass
				V=J;s=J
				if X._use_inspect:
					try:
						W=b.signature(U)
						if W.parameters and not all(hasattr(A,j)for A in W.parameters.values()):s=c(W.parameters);raise A2(AB)
						A=[];I=B;a=B
						for(M,t)in W.parameters.items():
							Q=e(t,j,J)
							if Q==0:I=P;A.append(M)
							elif Q==1:
								if I:A.append(G);I=B
								A.append(M)
							elif Q==2:
								if I:A.append(G);I=B
								a=P;A.append(Y+M)
							elif Q==3:
								if I:A.append(G);I=B
								if not a:A.append(Y);a=P
								A.append(M)
							elif Q==4:
								if I:A.append(G);I=B
								A.append('**'+M)
							else:A.append(M)
						if I:A.append(G)
						if Z>0 and A and A[0]not in(Y,G):A=A[1:]
						if Z>0:V=i+k.join(A)if A else x
						else:V=k.join(A)
					except R:pass
				if V is J:V=AC.format(A3)
				if AD in T or AD in N:E='{}@classmethod\n'.format(D)+AE.format(D,H,V.replace(x,'cls',1),q)
				elif g:E='{}async def {}({}) -> {}:\n'.format(D,H,V,q)
				elif r:E='{}async def {}({}) -> AsyncGenerator:\n'.format(D,H,V)
				elif A4:E='{}def {}({}) -> Generator:\n'.format(D,H,V)
				else:E=AE.format(D,H,V,q)
				if s is not J:E=AF.format(D,s)+E
				if X._capture_docstrings:
					try:
						L=U.__doc__
						if L and A1(L,f):
							L=L.strip().replace('"""',A8).replace(h,h+D+w)
							if L:E+=D+A9.format(L)
					except R:pass
				E+=D+'    ...\n\n';S.write(E)
			elif T=="<class 'module'>":0
			elif T.startswith("<class '"):
				O=T[8:-2];E=C
				if O in('str','int','float','bool','bytearray','bytes'):
					if H.upper()==H:E='{0}{1}: Final[{3}] = {2}\n'.format(D,H,N,O)
					else:E=AG.format(D,H,N,O)
				elif O in(p,o,n):AK={p:'{}',o:'[]',n:'()'};E=AG.format(D,H,AK[O],O)
				elif O in('object','set','frozenset','Pin'):E='{0}{1}: {2} ## = {4}\n'.format(D,H,O,T,N)
				elif O=='generator':
					AL=i if Z>0 else C;d=J;u=J;A7=B
					if X._use_inspect:
						try:A7=b.iscoroutinefunction(U)
						except R:pass
						try:
							W=b.signature(U)
							if W.parameters and not all(hasattr(A,j)for A in W.parameters.values()):u=c(W.parameters);raise A2(AB)
							A=[];I=B;a=B
							for(M,t)in W.parameters.items():
								Q=e(t,j,J)
								if Q==0:I=P;A.append(M)
								elif Q==1:
									if I:A.append(G);I=B
									A.append(M)
								elif Q==2:
									if I:A.append(G);I=B
									a=P;A.append(Y+M)
								elif Q==3:
									if I:A.append(G);I=B
									if not a:A.append(Y);a=P
									A.append(M)
								elif Q==4:
									if I:A.append(G);I=B
									A.append('**'+M)
								else:A.append(M)
							if I:A.append(G)
							if Z>0 and A and A[0]not in(Y,G):A=A[1:]
							if Z>0:d=i+k.join(A)if A else x
							else:d=k.join(A)
						except R:pass
					if d is J:d=AC.format(AL)
					if A7:E='{0}async def {1}({2}) -> Incomplete:\n{0}    ...\n\n'.format(D,H,d)
					else:E='{0}def {1}({2}) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(D,H,d,O,N)
					if u is not J:E=AF.format(D,u)+E
				else:
					O=AA
					if l in N:N=N.split(l)[0]+AH
					if l in N:N=N.split(l)[0]+AH
					E='{0}{1}: {2} ## {3} = {4}\n'.format(D,H,O,T,N)
				S.write(E)
			else:S.write("# all other, type = '{0}'\n".format(T));S.write(D+H+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		"Turn _fwid from 'v1.2.3' into '1_2_3' to be used in filename";A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(B,path=C):
		'Remove all files from the stub folder'
		if not path:path=B.path
		F.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except(D,H):return
		for E in C:
			A='{}/{}'.format(path,E)
			try:os.remove(A)
			except D:
				try:B.clean(A);os.rmdir(A)
				except D:pass
	def report_start(B,filename='modules.json'):
		'Start a report of the modules that have been stubbed\n        "create json with list of exported modules';E='firmware';B._json_name='{}/{}'.format(B.path,filename);B._json_first=P;h(B._json_name);F.info('Report file: {}'.format(B._json_name));K.collect()
		try:
			with V(B._json_name,'w')as C:C.write('{');C.write(dumps({E:B.info})[1:-1]);C.write(q);C.write(dumps({A4:{A:__version__},'stubtype':E})[1:-1]);C.write(q);C.write('"modules" :[\n')
		except D as G:F.error(A9);B._json_name=J;raise G
	def report_add(A,module_name,stub_file):
		'Add a module to the report'
		if not A._json_name:raise R(AA)
		try:
			with V(A._json_name,'a')as C:
				if not A._json_first:C.write(q)
				else:A._json_first=B
				E='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',G));C.write(E)
		except D:F.error(A9)
	def report_end(A):
		if not A._json_name:raise R(AA)
		with V(A._json_name,'a')as B:B.write('\n]}')
		F.info('Path: {}'.format(A.path))
def h(path):
	'Create nested folders if needed';A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except D as E:
				if E.args[0]in[AD,AE]:
					try:F.debug('Create folder {}'.format(B));os.mkdir(B)
					except D as H:F.error('failed to create folder {}'.format(B));raise H
		C=A+1
def i(s):
	B=' on '
	if not s:return C
	s=s.split(B,1)[0]if B in s else s
	if s.startswith('v'):
		if not E in s:return C
		A=s.split(E)[1];return A
	if not a in s:return C
	A=s.split(a)[1].split(N)[1];return A
def AF():
	'Get basic system implementation details.'
	try:B=sys.implementation[0]
	except k:B=sys.implementation.name
	D=u({Z:B,A:C,O:C,'ver':C,I:sys.platform,T:'UNKNOWN',X:C,r:C,'cpu':C,Q:C,s:C});return D
def AG(info):
	'Normalize port names to be consistent with the repo.';A=info
	if A[I].startswith('pyb'):A[I]='stm32'
	elif A[I]=='win32':A[I]=AB
	elif A[I]=='linux':A[I]=t
def AH(info):
	'Extract version information from sys.implementation.'
	try:info[A]=AP(sys.implementation.version)
	except H:pass
def AJ(info):
	'Extract board, CPU, and machine details.';A=info
	try:
		D=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[T]=D.strip();B=sys.implementation._build if'_build'in M(sys.implementation)else C
		if B:A[T]=B.split(E)[0];A[r]=B.split(E)[1]if E in B else C
		A[X]=B;A['cpu']=D.split('with')[-1].strip();A[Q]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if Q in M(sys.implementation)else C
	except(H,W):pass
	if not A[X]:AQ(A)
def AK(info):
	'Extract build information from various system sources.';B=info
	try:
		if'uname'in M(os):
			B[O]=i(os.uname()[3])
			if not B[O]:B[O]=i(os.uname()[2])
		elif A in M(sys):B[O]=i(sys.version)
	except(H,W,k):pass
	if B[A]==C and sys.platform not in(t,'win32'):
		try:D=os.uname();B[A]=D.release
		except(W,H,k):pass
def AL(info):
	'Detect special firmware families (pycopy, pycom, ev3-pybricks).';D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,J,J,G);A[Z]=E;del H;break
		except(S,A0):pass
	if A[Z]==D:A['release']='2.0.0'
def AM(info):
	'Process MicroPython-specific version formatting.';B=info
	if B[Z]==l:
		if B[A]and B[A].endswith('.0')and B[A]>='1.10.0'and B[A]<='1.19.9':B[A]=B[A][:-2]
def AN(info):
	'Process MPY architecture and version information.';A=info
	if Q in A and A[Q]:
		B=int(A[Q])
		try:
			C=[J,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[s]=C
		except W:A[s]='unknown'
		A[Q]='v{}.{}'.format(B&255,B>>8&3)
def AO(info):
	'Handle final version string formatting.';B=info
	if B[O]and not B[A].endswith(a):B[A]=B[A]+a
	B['ver']=f"{B[A]}-{B[O]}"if B[O]else f"{B[A]}"
def _info():'\n    Gather comprehensive system information for MicroPython stubbing.\n\n    Returns a dictionary containing family, version, port, board, and other\n    system details needed for stub generation.\n    ';A=AF();AG(A);AH(A);AJ(A);AK(A);AL(A);AM(A);AN(A);AO(A);return A
def AP(version):
	A=version;B=N.join([f(A)for A in A[:3]])
	if c(A)>3 and A[3]:B+=E+A[3]
	return B
def AQ(info):
	'Read the board_id from the boardname.py file that may have been created upfront';B=info
	try:from boardname import BOARD_ID as A;F.info('Found BOARD_ID: {}'.format(A))
	except S:F.warning('BOARD_ID not found');A=C
	B[X]=A;B[T]=A.split(E)[0]if E in A else A;B[r]==A.split(E)[1]if E in A else C
def get_root():
	'Determine the root folder of the device'
	try:A=os.getcwd()
	except(D,H):A=N
	B=A
	for B in['/remote','/sd','/flash',G,A,N]:
		try:C=os.stat(B);break
		except D:continue
	return B
def AR(filename):
	try:
		if os.stat(filename)[0]>>14:return P
		return B
	except D:return B
def w():U("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	'get --path from cmdline. [unix/win]';path=C
	if c(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:w()
	elif c(sys.argv)==2:w()
	return path
def x():
	'runtime test to determine full or micropython'
	try:A=bytes('abc',encoding='utf8');C=x.__module__;return B
	except(y,H):return P
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_asyncio','_boot_fat','_espnow','_onewire','_pyscript','_rp2','_thread','_uasyncio','abc','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','alif','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','base64','binascii','ble','bluetooth',T,'breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree',A7,'cc3200','cmath','collections','collections/__init__','collections/defaultdict','copy','crypto','cryptolib','curl','datetime','deflate','dht','display','display_driver_utils','ds18x20','embed','encoder','errno','esp','esp32',A3,'espidf','espnow','ffi','flashbdev','fnmatch','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','gzip','hashlib','heapq','hmac','html/__init__','hub75','ili9341','ili9XXX','imagetools','inisetup','inspect','interstate75','io','itertools','jpegdec','js','jsffi','json','lcd160cr','locale','lodepng',A8,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','marshal','math','microWebSocket','microWebSrv','microWebTemplate',l,'mimxrt','mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','music','neopixel','network','nrf','ntptime','onewire','openamp','operator','os','os/__init__','os/path','pathlib','pcf85063a','pic16bit','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform','powerpc','pyb','pye','pyscript','pyscript/__init__','pyscript/fs','qemu','qrcode','random','renesas','renesas-ra','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stat','stm','stm32','string','struct','sys','tarfile/__init__','tarfile/write','termios','time','tls','tpcalib','types','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluepy','ubluetooth','ucollections','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','unittest/__init__',t,'uos','uplatform','urandom','ure','urequests','urllib/urequest','usb/device','usb/device/cdc','usb/device/hid','usb/device/keyboard','usb/device/midi','usb/device/mouse','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uu','uuid','uwebsocket','uzlib',A,'vfs','webassembly','websocket','websocket_helper',AB,'wipy','writer','xpt2046','ymodem','zephyr','zlib','zsensor'];K.collect();stubber.create_all_stubs()
if __name__=='__main__'or x():
	if not AR('no_auto_stubber.txt'):
		U(f"createstubs.py: {__version__}")
		try:K.threshold(4096);K.enable()
		except BaseException:pass
		main()