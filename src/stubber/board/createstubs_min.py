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
X=print
V='-preview'
U=True
T='-'
S='board'
R=IndexError
Q=repr
P='family'
O=len
N=ImportError
M=dir
L='port'
K='.'
J=False
I=AttributeError
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
A3=['lib','/lib','/sd/lib','/flash/lib',K]
class H:
	DEBUG=10;TRACE=15;INFO=20;WARNING=30;ERROR=40;CRITICAL=50;level=INFO;prnt=X
	@staticmethod
	def getLogger(name):return H()
	@classmethod
	def basicConfig(A,level):A.level=level
	def trace(A,msg):
		if A.level<=H.TRACE:A.prnt('TRACE :',msg)
	def debug(A,msg):
		if A.level<=H.DEBUG:A.prnt('DEBUG :',msg)
	def info(A,msg):
		if A.level<=H.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=H.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=H.ERROR:A.prnt('ERROR :',msg)
	def critical(A,msg):
		if A.level<=H.CRITICAL:A.prnt('CRIT  :',msg)
A=H.getLogger(n)
H.basicConfig(level=H.INFO)
class Stubber:
	def __init__(B,path=E,firmware_id=E):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise j('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		B._report=[];B.info=_info();A.info('Port: {}'.format(B.info[L]));A.info('Board: {}'.format(B.info[S]));F.collect()
		if C:B._fwid=C.lower()
		elif B.info[P]==Y:B._fwid='{family}-v{version}-{port}-{board}'.format(**B.info).rstrip(T)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=F.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',G);A.debug(B.path)
		try:g(path+G)
		except D:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[]
	def get_obj_attributes(N,item_instance):
		D=item_instance;G=[];L=[];A.debug('get attributes {} {}'.format(Q(D),D))
		for C in M(D):
			if C.startswith(Z)and not C in N.modules:continue
			A.debug('get attribute {}'.format(C))
			try:
				E=getattr(D,C);A.debug('attribute {}:{}'.format(C,E))
				try:H=Q(type(E)).split("'")[1]
				except R:H=B
				if H in{o,p,q,r,a,b,c}:J=1
				elif H in{s,t}:J=2
				elif H in'class':J=3
				else:J=4
				G.append((C,Q(E),Q(type(E)),E,J))
			except I as K:L.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(C,D,K))
			except MemoryError as K:X('MemoryError: {}'.format(K));sleep(1);reset()
		G=k([A for A in G if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return G,L
	def add_modules(A,modules):A.modules=k(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber v{} on {}'.format(__version__,B._fwid));F.collect()
		for C in B.modules:B.create_one_stub(C)
		A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return J
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return J
		H='{}/{}.py'.format(C.path,B.replace(K,G));F.collect();E=J
		try:E=C.create_module_stub(B,H)
		except D:return J
		F.collect();return E
	def create_module_stub(I,module_name,file_name=E):
		H=file_name;C=module_name
		if H is E:L=C.replace(K,Z)+'.py';H=I.path+G+L
		else:L=H.split(G)[-1]
		if G in C:C=C.replace(G,K)
		M=E
		try:M=__import__(C,E,E,'*');P=F.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,L,P))
		except N:A.trace('Skip module: {:<25} {:<79}'.format(C,'Module not found.'));return J
		g(H)
		with open(H,'w')as O:Q=str(I.info).replace('OrderedDict(',B).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,I._fwid,Q,__version__);O.write(R);O.write('from __future__ import annotations\nfrom typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(O,M,C,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(C,H.replace('\\',G)))
		if C not in{'os',u,v,'gc'}:
			try:del M
			except(D,l):A.warning('could not del new_module')
		F.collect();return U
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		W='{0}{1} = {2} # type: {3}\n';V='bound_method';U='Incomplete';N=in_class;M='Exception';L=object_expr;I=fp;E=indent;F.collect()
		if L in K.problematic:A.warning('SKIPPING problematic module:{}'.format(L));return
		X,P=K.get_obj_attributes(L)
		if P:A.error(P)
		for(C,J,G,Y,d)in X:
			if C in['classmethod','staticmethod','BaseException',M]:continue
			if C[0].isdigit():A.warning('NameError: invalid name {}'.format(C));continue
			if G=="<class 'type'>"and O(E)<=z*4:
				A.trace('{0}class {1}:'.format(E,C));Q=B;R=C.endswith(M)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=M
				D='\n{}class {}({}):\n'.format(E,C,Q)
				if R:D+=E+'    ...\n';I.write(D);continue
				I.write(D);A.debug('# recursion over class {0}'.format(C));K.write_object_stub(I,Y,'{0}.{1}'.format(obj_name,C),E+'    ',N+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';I.write(D)
			elif any(A in G for A in[t,s,'closure']):
				A.debug("# def {1} function/method/closure, type = '{0}'".format(G,C));S=U;T=B
				if N>0:T='self, '
				if V in G or V in J:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,C,S)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,C,T,S)
				D+=E+'    ...\n\n';I.write(D);A.debug('\n'+D)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				H=G[8:-2];D=B
				if H in[q,o,p,r,'bytearray','bytes']:D=W.format(E,C,J,H)
				elif H in[c,b,a]:Z={c:'{}',b:'[]',a:'()'};D=W.format(E,C,Z[H],H)
				elif H in['object','set','frozenset','Pin','FileIO']:D='{0}{1} : {2} ## = {4}\n'.format(E,C,H,G,J)
				else:H=U;D='{0}{1} : {2} ## {3} = {4}\n'.format(E,C,H,G,J)
				I.write(D);A.debug('\n'+D)
			else:A.debug("# all other, type = '{0}'".format(G));I.write("# all other, type = '{0}'\n".format(G));I.write(E+C+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,Z)
		return A
	def clean(C,path=E):
		if path is E:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);F=os.listdir(path)
		except(D,I):return
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
				B.write_json_header(C);G=U
				for H in B._report:B.write_json_node(C,H,G);G=J
				B.write_json_end(C)
			I=B._start_free-F.mem_free();A.trace('Memory used: {0} Kb'.format(I//1024))
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
def W(s):
	C=' on '
	if not s:return B
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not T in s:return B
		A=s.split(T)[1];return A
	if not V in s:return B
	A=s.split(V)[1].split(K)[1];return A
def _info():
	Z='ev3-pybricks';X='pycopy';U='unix';T='win32';Q='arch';O='cpu';K='ver';F='mpy';D='build';A=f({P:sys.implementation.name,C:B,D:B,K:B,L:sys.platform,S:'UNKNOWN',O:B,F:B,Q:B})
	if A[L].startswith(x):A[L]='stm32'
	elif A[L]==T:A[L]='windows'
	elif A[L]=='linux':A[L]=U
	try:A[C]=A0(sys.implementation.version)
	except I:pass
	try:H=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[S]=H;A[O]=H.split('with')[-1].strip();A[F]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if F in M(sys.implementation)else B
	except(I,R):pass
	A[S]=A1()
	try:
		if'uname'in M(os):
			A[D]=W(os.uname()[3])
			if not A[D]:A[D]=W(os.uname()[2])
		elif C in M(sys):A[D]=W(sys.version)
	except(I,R,m):pass
	if A[C]==B and sys.platform not in(U,T):
		try:a=os.uname();A[C]=a.release
		except(R,I,m):pass
	for(b,c,d)in[(X,X,'const'),(e,e,'FAT'),(Z,'pybricks.hubs','EV3Brick')]:
		try:g=__import__(c,E,E,d);A[P]=b;del g;break
		except(N,l):pass
	if A[P]==Z:A['release']='2.0.0'
	if A[P]==Y:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if F in A and A[F]:
		G=int(A[F]);J=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][G>>10]
		if J:A[Q]=J
		A[F]='v{}.{}'.format(G&255,G>>8&3)
	if A[D]and not A[C].endswith(V):A[C]=A[C]+V
	A[K]=f"{A[C]}-{A[D]}"if A[D]else f"{A[C]}";return A
def A0(version):
	A=version;B=K.join([str(A)for A in A[:3]])
	if O(A)>3 and A[3]:B+=T+A[3]
	return B
def A1():
	try:from boardname import BOARDNAME as C;A.info('Found BOARDNAME: {}'.format(C))
	except N:A.warning('BOARDNAME not found');C=B
	return C
def get_root():
	try:A=os.getcwd()
	except(D,I):A=K
	B=A
	for B in[A,'/sd','/flash',G,K]:
		try:C=os.stat(B);break
		except D:continue
	return B
def A2(filename):
	try:
		if os.stat(filename)[0]>>14:return U
		return J
	except D:return J
def h():X("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if O(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:h()
	elif O(sys.argv)==2:h()
	return path
def i():
	try:A=bytes('abc',encoding='utf8');B=i.__module__;return J
	except(j,I):return U
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_asyncio','_boot_fat','_coap','_espnow','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','cmath','collections','crypto','cryptolib','curl','deflate','dht','display','display_driver_utils','ds18x20','encoder','errno','esp','esp32','espidf','espnow','ffi','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','json','lcd160cr','lodepng',v,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','math','microWebSocket','microWebSrv','microWebTemplate',Y,'mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pcf85063a','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform',x,e,'pye','qrcode','queue','random','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','struct',u,'termios','time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',C,'websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];F.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or i():
	if not A2('no_auto_stubber.txt'):
		try:F.threshold(4*1024);F.enable()
		except BaseException:pass
		main()