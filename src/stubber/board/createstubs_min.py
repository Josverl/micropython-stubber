A1='windows'
A0='No report file'
z='Failed to create the report.'
y='{}/{}'
x='logging'
w='sys'
v='method'
u='function'
t='bool'
s='str'
r='float'
q='int'
p='stubber'
o=Exception
n=KeyError
m=sorted
l=NotImplementedError
h='pycom'
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
G='/'
E=OSError
D=None
C='version'
B=''
import gc as F,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except N:pass
try:from collections import OrderedDict as i
except N:from ucollections import OrderedDict as i
__version__='v1.24.0'
A2=2
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
A=J.getLogger(p)
J.basicConfig(level=J.INFO)
class Stubber:
	def __init__(B,path=D,firmware_id=D):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise l('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		B.info=_info();A.info('Port: {}'.format(B.info[L]));A.info('Board: {}'.format(B.info[T]));F.collect()
		if C:B._fwid=C.lower()
		elif B.info[P]==b:B._fwid='{family}-v{version}-{port}-{board}'.format(**B.info).rstrip(U)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=F.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',G)
		try:X(path+G)
		except E:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[];B._json_name=D;B._json_first=H
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for A in M(H):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=getattr(H,A)
				try:E=Z(type(D)).split("'")[1]
				except O:E=B
				if E in{q,r,s,t,c,d,e}:G=1
				elif E in{u,v}:G=2
				elif E in'class':G=3
				else:G=4
				C.append((A,Z(D),Z(type(D)),D,G))
			except I as J:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,J))
			except MemoryError as J:Q('MemoryError: {}'.format(J));sleep(1);reset()
		C=m([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return C,K
	def add_modules(A,modules):A.modules=m(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber {} on {}'.format(__version__,B._fwid));B.report_start();F.collect()
		for C in B.modules:B.create_one_stub(C)
		B.report_end();A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return H
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return H
		I='{}/{}.pyi'.format(C.path,B.replace(K,G));F.collect();D=H
		try:D=C.create_module_stub(B,I)
		except E:return H
		F.collect();return D
	def create_module_stub(J,module_name,file_name=D):
		I=file_name;C=module_name
		if I is D:L=C.replace(K,'_')+'.pyi';I=J.path+G+L
		else:L=I.split(G)[-1]
		if G in C:C=C.replace(G,K)
		M=D
		try:M=__import__(C,D,D,'*');P=F.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,L,P))
		except N:return H
		X(I)
		with R(I,'w')as O:Q=str(J.info).replace('OrderedDict(',B).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,J._fwid,Q,__version__);O.write(S);O.write('from __future__ import annotations\nfrom typing import Any, Generator\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(O,M,C,B)
		J.report_add(C,I)
		if C not in{'os',w,x,'gc'}:
			try:del M
			except(E,n):A.warning('could not del new_module')
		F.collect();return V
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		Z=' at ...>';Y='generator';X='{0}{1}: {3} = {2}\n';W='bound_method';V='Incomplete';O=in_class;N='Exception';M=object_expr;K=' at ';J=fp;E=indent;F.collect()
		if M in L.problematic:A.warning('SKIPPING problematic module:{}'.format(M));return
		a,P=L.get_obj_attributes(M)
		if P:A.error(P)
		for(C,H,I,b,g)in a:
			if C in['classmethod','staticmethod','BaseException',N]:continue
			if C[0].isdigit():A.warning('NameError: invalid name {}'.format(C));continue
			if I=="<class 'type'>"and S(E)<=A3*4:
				Q=B;R=C.endswith(N)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=N
				D='\n{}class {}({}):\n'.format(E,C,Q)
				if R:D+=E+'    ...\n';J.write(D);continue
				J.write(D);L.write_object_stub(J,b,'{0}.{1}'.format(obj_name,C),E+'    ',O+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';J.write(D)
			elif any(A in I for A in[v,u,'closure']):
				T=V;U=B
				if O>0:U='self, '
				if W in I or W in H:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,C,T)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,C,U,T)
				D+=E+'    ...\n\n';J.write(D)
			elif I=="<class 'module'>":0
			elif I.startswith("<class '"):
				G=I[8:-2];D=B
				if G in(s,q,r,t,'bytearray','bytes'):
					if C.upper()==C:D='{0}{1}: Final[{3}] = {2}\n'.format(E,C,H,G)
					else:D=X.format(E,C,H,G)
				elif G in(e,d,c):f={e:'{}',d:'[]',c:'()'};D=X.format(E,C,f[G],G)
				elif G in('object','set','frozenset','Pin',Y):
					if G==Y:G='Generator'
					D='{0}{1}: {2} ## = {4}\n'.format(E,C,G,I,H)
				else:
					G=V
					if K in H:H=H.split(K)[0]+Z
					if K in H:H=H.split(K)[0]+Z
					D='{0}{1}: {2} ## {3} = {4}\n'.format(E,C,G,I,H)
				J.write(D)
			else:J.write("# all other, type = '{0}'\n".format(I));J.write(E+C+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(C,path=D):
		if path is D:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);F=os.listdir(path)
		except(E,I):return
		for G in F:
			B=y.format(path,G)
			try:os.remove(B)
			except E:
				try:C.clean(B);os.rmdir(B)
				except E:pass
	def report_start(B,filename='modules.json'):
		H='firmware';B._json_name=y.format(B.path,filename);B._json_first=V;X(B._json_name);A.info('Report file: {}'.format(B._json_name));F.collect()
		try:
			with R(B._json_name,'w')as G:G.write('{');G.write(dumps({H:B.info})[1:-1]);G.write(f);G.write(dumps({p:{C:__version__},'stubtype':H})[1:-1]);G.write(f);G.write('"modules" :[\n')
		except E as I:A.error(z);B._json_name=D;raise I
	def report_add(B,module_name,stub_file):
		if not B._json_name:raise o(A0)
		try:
			with R(B._json_name,'a')as C:
				if not B._json_first:C.write(f)
				else:B._json_first=H
				D='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',G));C.write(D)
		except E:A.error(z)
	def report_end(B):
		if not B._json_name:raise o(A0)
		with R(B._json_name,'a')as C:C.write('\n]}')
		A.info('Path: {}'.format(B.path))
def X(path):
	B=D=0
	while B!=-1:
		B=path.find(G,D)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except E as F:
				if F.args[0]==A2:
					try:A.debug('Create folder {}'.format(C));os.mkdir(C)
					except E as H:A.error('failed to create folder {}'.format(C));raise H
		D=B+1
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
	X='ev3-pybricks';V='pycopy';U='win32';S='arch';R='cpu';Q='ver';F='mpy';E='build'
	try:J=sys.implementation[0]
	except a:J=sys.implementation.name
	A=i({P:J,C:B,E:B,Q:B,L:sys.platform,T:'UNKNOWN',R:B,F:B,S:B})
	if A[L].startswith('pyb'):A[L]='stm32'
	elif A[L]==U:A[L]=A1
	elif A[L]=='linux':A[L]=g
	try:A[C]=A4(sys.implementation.version)
	except I:pass
	try:K=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[T]=K;A[R]=K.split('with')[-1].strip();A[F]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if F in M(sys.implementation)else B
	except(I,O):pass
	A[T]=A5()
	try:
		if'uname'in M(os):
			A[E]=Y(os.uname()[3])
			if not A[E]:A[E]=Y(os.uname()[2])
		elif C in M(sys):A[E]=Y(sys.version)
	except(I,O,a):pass
	if A[C]==B and sys.platform not in(g,U):
		try:Z=os.uname();A[C]=Z.release
		except(O,I,a):pass
	for(c,d,e)in[(V,V,'const'),(h,h,'FAT'),(X,'pybricks.hubs','EV3Brick')]:
		try:f=__import__(d,D,D,e);A[P]=c;del f;break
		except(N,n):pass
	if A[P]==X:A['release']='2.0.0'
	if A[P]==b:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if F in A and A[F]:
		G=int(A[F])
		try:H=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][G>>10]
		except O:H='unknown'
		if H:A[S]=H
		A[F]='v{}.{}'.format(G&255,G>>8&3)
	if A[E]and not A[C].endswith(W):A[C]=A[C]+W
	A[Q]=f"{A[C]}-{A[E]}"if A[E]else f"{A[C]}";return A
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
	except(E,I):A=K
	B=A
	for B in['/remote','/sd','/flash',G,A,K]:
		try:C=os.stat(B);break
		except E:continue
	return B
def A6(filename):
	try:
		if os.stat(filename)[0]>>14:return V
		return H
	except E:return H
def j():Q("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if S(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:j()
	elif S(sys.argv)==2:j()
	return path
def k():
	try:A=bytes('abc',encoding='utf8');B=k.__module__;return H
	except(l,I):return V
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_asyncio','_boot_fat','_coap','_espnow','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','builtins','cc3200','cmath','collections','crypto','cryptolib','curl','deflate','dht','display','display_driver_utils','ds18x20','embed','encoder','errno','esp','esp32','esp8266','espidf','espnow','ffi','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','js','jsffi','json','lcd160cr','lodepng',x,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','marshal','math','microWebSocket','microWebSrv','microWebTemplate',b,'mimxrt','mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','nrf','ntptime','onewire','openamp','os','pcf85063a','pic16bit','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform','powerpc','pyb',h,'pye','qemu','qrcode','queue','random','renesas','renesas-ra','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','stm32','struct',w,'termios','time','tls','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple',g,'uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','usb/device','usb/device/cdc','usb/device/hid','usb/device/keyboard','usb/device/midi','usb/device/mouse','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',C,'vfs','webassembly','websocket','websocket_helper',A1,'wipy','writer','xpt2046','ymodem','zephyr','zlib'];F.collect();stubber.create_all_stubs()
if __name__=='__main__'or k():
	if not A6('no_auto_stubber.txt'):
		Q(f"createstubs.py: {__version__}")
		try:F.threshold(4096);F.enable()
		except BaseException:pass
		main()