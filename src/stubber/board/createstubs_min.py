x='pyb'
w='{}/{}'
v='logging'
u='sys'
t='method'
s='function'
r='bool'
q='str'
p='float'
o='int'
n='stubber'
m=TypeError
l=KeyError
k=sorted
j=NotImplementedError
e='pycom'
d=',\n'
c='dict'
b='list'
a='tuple'
Z='_'
Y='micropython'
X=repr
W=print
U='-preview'
T=True
S='-'
R='board'
Q=IndexError
P='family'
O=len
N=ImportError
M=dir
K='port'
J='.'
I=False
H=AttributeError
G='/'
E=None
D=OSError
C='version'
B=''
import gc as F,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except N:pass
try:from collections import OrderedDict as f
except N:from ucollections import OrderedDict as f
__version__='v1.16.3'
y=2
z=2
A3=['lib','/lib','/sd/lib','/flash/lib',J]
class L:
	INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=W
	@staticmethod
	def getLogger(name):return L()
	@classmethod
	def basicConfig(A,level):A.level=level
	def info(A,msg):
		if A.level<=L.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=L.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=L.ERROR:A.prnt('ERROR :',msg)
A=L.getLogger(n)
L.basicConfig(level=L.INFO)
class Stubber:
	def __init__(B,path=E,firmware_id=E):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise j('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		B._report=[];B.info=_info();A.info('Port: {}'.format(B.info[K]));A.info('Board: {}'.format(B.info[R]));F.collect()
		if C:B._fwid=C.lower()
		elif B.info[P]==Y:B._fwid='{family}-v{version}-{port}-{board}'.format(**B.info).rstrip(S)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=F.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',G)
		try:g(path+G)
		except D:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[]
	def get_obj_attributes(L,item_instance):
		I=item_instance;C=[];K=[]
		for A in M(I):
			if A.startswith(Z)and not A in L.modules:continue
			try:
				D=getattr(I,A)
				try:E=X(type(D)).split("'")[1]
				except Q:E=B
				if E in{o,p,q,r,a,b,c}:G=1
				elif E in{s,t}:G=2
				elif E in'class':G=3
				else:G=4
				C.append((A,X(D),X(type(D)),D,G))
			except H as J:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,I,J))
			except MemoryError as J:W('MemoryError: {}'.format(J));sleep(1);reset()
		C=k([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return C,K
	def add_modules(A,modules):A.modules=k(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber v{} on {}'.format(__version__,B._fwid));F.collect()
		for C in B.modules:B.create_one_stub(C)
		A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return I
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return I
		H='{}/{}.py'.format(C.path,B.replace(J,G));F.collect();E=I
		try:E=C.create_module_stub(B,H)
		except D:return I
		F.collect();return E
	def create_module_stub(K,module_name,file_name=E):
		H=file_name;C=module_name
		if H is E:L=C.replace(J,Z)+'.py';H=K.path+G+L
		else:L=H.split(G)[-1]
		if G in C:C=C.replace(G,J)
		M=E
		try:M=__import__(C,E,E,'*');P=F.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,L,P))
		except N:return I
		g(H)
		with open(H,'w')as O:Q=str(K.info).replace('OrderedDict(',B).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,K._fwid,Q,__version__);O.write(R);O.write('from __future__ import annotations\nfrom typing import Any\nfrom _typeshed import Incomplete\n\n');K.write_object_stub(O,M,C,B)
		K._report.append('{{"module": "{}", "file": "{}"}}'.format(C,H.replace('\\',G)))
		if C not in{'os',u,v,'gc'}:
			try:del M
			except(D,l):A.warning('could not del new_module')
		F.collect();return T
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		W='{0}{1} = {2} # type: {3}\n';V='bound_method';U='Incomplete';N=in_class;M='Exception';L=object_expr;I=fp;D=indent;F.collect()
		if L in K.problematic:A.warning('SKIPPING problematic module:{}'.format(L));return
		X,P=K.get_obj_attributes(L)
		if P:A.error(P)
		for(E,J,G,Y,d)in X:
			if E in['classmethod','staticmethod','BaseException',M]:continue
			if E[0].isdigit():A.warning('NameError: invalid name {}'.format(E));continue
			if G=="<class 'type'>"and O(D)<=z*4:
				Q=B;R=E.endswith(M)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=M
				C='\n{}class {}({}):\n'.format(D,E,Q)
				if R:C+=D+'    ...\n';I.write(C);continue
				I.write(C);K.write_object_stub(I,Y,'{0}.{1}'.format(obj_name,E),D+'    ',N+1);C=D+'    def __init__(self, *argv, **kwargs) -> None:\n';C+=D+'        ...\n\n';I.write(C)
			elif any(A in G for A in[t,s,'closure']):
				S=U;T=B
				if N>0:T='self, '
				if V in G or V in J:C='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,S)
				else:C='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,T,S)
				C+=D+'    ...\n\n';I.write(C)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				H=G[8:-2];C=B
				if H in[q,o,p,r,'bytearray','bytes']:C=W.format(D,E,J,H)
				elif H in[c,b,a]:Z={c:'{}',b:'[]',a:'()'};C=W.format(D,E,Z[H],H)
				elif H in['object','set','frozenset','Pin','FileIO']:C='{0}{1} : {2} ## = {4}\n'.format(D,E,H,G,J)
				else:H=U;C='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,H,G,J)
				I.write(C)
			else:I.write("# all other, type = '{0}'\n".format(G));I.write(D+E+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,Z)
		return A
	def clean(C,path=E):
		if path is E:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);F=os.listdir(path)
		except(D,H):return
		for G in F:
			B=w.format(path,G)
			try:os.remove(B)
			except D:
				try:C.clean(B);os.rmdir(B)
				except D:pass
	def report(B,filename='modules.json'):
		A.info('Created stubs for {} modules on board {}\nPath: {}'.format(O(B._report),B._fwid,B.path));E=w.format(B.path,filename);A.info('Report file: {}'.format(E));F.collect()
		try:
			with open(E,'w')as C:
				B.write_json_header(C);G=T
				for H in B._report:B.write_json_node(C,H,G);G=I
				B.write_json_end(C)
			J=B._start_free-F.mem_free()
		except D:A.error('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(dumps({A:B.info})[1:-1]);f.write(d);f.write(dumps({n:{C:__version__},'stubtype':A})[1:-1]);f.write(d);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(d)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def g(path):
	B=E=0
	while B!=-1:
		B=path.find(G,E)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except D as F:
				if F.args[0]==y:
					try:os.mkdir(C)
					except D as H:A.error('failed to create folder {}'.format(C));raise H
		E=B+1
def V(s):
	C=' on '
	if not s:return B
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not S in s:return B
		A=s.split(S)[1];return A
	if not U in s:return B
	A=s.split(U)[1].split(J)[1];return A
def _info():
	Z='ev3-pybricks';X='pycopy';W='unix';T='win32';S='arch';O='cpu';L='ver';F='mpy';D='build';A=f({P:sys.implementation.name,C:B,D:B,L:B,K:sys.platform,R:'UNKNOWN',O:B,F:B,S:B})
	if A[K].startswith(x):A[K]='stm32'
	elif A[K]==T:A[K]='windows'
	elif A[K]=='linux':A[K]=W
	try:A[C]=A0(sys.implementation.version)
	except H:pass
	try:I=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[R]=I;A[O]=I.split('with')[-1].strip();A[F]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if F in M(sys.implementation)else B
	except(H,Q):pass
	A[R]=A1()
	try:
		if'uname'in M(os):
			A[D]=V(os.uname()[3])
			if not A[D]:A[D]=V(os.uname()[2])
		elif C in M(sys):A[D]=V(sys.version)
	except(H,Q,m):pass
	if A[C]==B and sys.platform not in(W,T):
		try:a=os.uname();A[C]=a.release
		except(Q,H,m):pass
	for(b,c,d)in[(X,X,'const'),(e,e,'FAT'),(Z,'pybricks.hubs','EV3Brick')]:
		try:g=__import__(c,E,E,d);A[P]=b;del g;break
		except(N,l):pass
	if A[P]==Z:A['release']='2.0.0'
	if A[P]==Y:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if F in A and A[F]:
		G=int(A[F]);J=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][G>>10]
		if J:A[S]=J
		A[F]='v{}.{}'.format(G&255,G>>8&3)
	if A[D]and not A[C].endswith(U):A[C]=A[C]+U
	A[L]=f"{A[C]}-{A[D]}"if A[D]else f"{A[C]}";return A
def A0(version):
	A=version;B=J.join([str(A)for A in A[:3]])
	if O(A)>3 and A[3]:B+=S+A[3]
	return B
def A1():
	try:from boardname import BOARDNAME as C;A.info('Found BOARDNAME: {}'.format(C))
	except N:A.warning('BOARDNAME not found');C=B
	return C
def get_root():
	try:A=os.getcwd()
	except(D,H):A=J
	B=A
	for B in[A,'/sd','/flash',G,J]:
		try:C=os.stat(B);break
		except D:continue
	return B
def A2(filename):
	try:
		if os.stat(filename)[0]>>14:return T
		return I
	except D:return I
def h():W("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if O(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:h()
	elif O(sys.argv)==2:h()
	return path
def i():
	try:A=bytes('abc',encoding='utf8');B=i.__module__;return I
	except(j,H):return T
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_asyncio','_boot_fat','_coap','_espnow','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','cmath','collections','crypto','cryptolib','curl','deflate','dht','display','display_driver_utils','ds18x20','encoder','errno','esp','esp32','espidf','espnow','ffi','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','json','lcd160cr','lodepng',v,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','math','microWebSocket','microWebSrv','microWebTemplate',Y,'mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pcf85063a','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform',x,e,'pye','qrcode','queue','random','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','struct',u,'termios','time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',C,'websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];F.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or i():
	if not A2('no_auto_stubber.txt'):
		try:F.threshold(4*1024);F.enable()
		except BaseException:pass
		main()