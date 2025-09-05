A3='windows'
A2='No report file'
A1='Failed to create the report.'
A0='logging'
z='method'
y='function'
x='bool'
w='str'
v='float'
u='int'
t='stubber'
s=Exception
r=KeyError
q=sorted
p=NotImplementedError
l='unix'
k='arch'
j='variant'
i=',\n'
h='dict'
g='list'
f='tuple'
e='micropython'
d=TypeError
c=repr
Z='-preview'
Y=True
X=len
W=open
V=print
U='family'
T='board_id'
S='board'
R=IndexError
Q=ImportError
P='mpy'
O=dir
N='build'
M='port'
L='.'
J=AttributeError
I=False
H=None
G='/'
E='-'
D=OSError
C='version'
A=''
import gc as F,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except Q:pass
try:from collections import OrderedDict as m
except Q:from ucollections import OrderedDict as m
__version__='v1.26.1'
A4=2
A5=44
A6=2
AJ=['lib','/lib','/sd/lib','/flash/lib',L]
class K:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=V
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
B=K.getLogger(t)
K.basicConfig(level=K.INFO)
class Stubber:
	def __init__(A,path=A,firmware_id=A):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise p('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		A.info=_info();B.info('Port: {}'.format(A.info[M]));B.info('Board: {}'.format(A.info[S]));B.info('Board_ID: {}'.format(A.info[T]));F.collect()
		if C:A._fwid=C.lower()
		elif A.info[U]==e:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(E)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=F.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:a(path+G)
		except D:B.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[];A._json_name=H;A._json_first=I
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for B in O(H):
			if B.startswith('__')and not B in L.modules:continue
			try:
				D=getattr(H,B)
				try:E=c(type(D)).split("'")[1]
				except R:E=A
				if E in{u,v,w,x,f,g,h}:G=1
				elif E in{y,z}:G=2
				elif E in'class':G=3
				else:G=4
				C.append((B,c(D),c(type(D)),D,G))
			except J as I:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(B,H,I))
			except MemoryError as I:V('MemoryError: {}'.format(I));sleep(1);reset()
		C=q([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return C,K
	def add_modules(A,modules):A.modules=q(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();F.collect()
		for C in A.modules:A.create_one_stub(C)
		A.report_end();B.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:B.warning('Skip module: {:<25}        : Known problematic'.format(A));return I
		if A in C.excluded:B.warning('Skip module: {:<25}        : Excluded'.format(A));return I
		H='{}/{}.pyi'.format(C.path,A.replace(L,G));F.collect();E=I
		try:E=C.create_module_stub(A,H)
		except D:return I
		F.collect();return E
	def create_module_stub(J,module_name,file_name=H):
		E=file_name;C=module_name
		if E is H:K=C.replace(L,'_')+'.pyi';E=J.path+G+K
		else:K=E.split(G)[-1]
		if G in C:C=C.replace(G,L)
		M=H
		try:M=__import__(C,H,H,'*');O=F.mem_free();B.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,K,O))
		except Q:return I
		a(E)
		with W(E,'w')as N:P=str(J.info).replace('OrderedDict(',A).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,J._fwid,P,__version__);N.write(R);N.write('from __future__ import annotations\nfrom typing import Any, Final, Generator\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(N,M,C,A)
		J.report_add(C,E)
		if C not in{'os','sys',A0,'gc'}:
			try:del M
			except(D,r):B.warning('could not del new_module')
		F.collect();return Y
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		Y=' at ...>';W='{0}{1}: {3} = {2}\n';V='bound_method';U='Incomplete';O=in_class;N='Exception';M=object_expr;K=' at ';J=fp;E=indent;F.collect()
		if M in L.problematic:B.warning('SKIPPING problematic module:{}'.format(M));return
		Z,P=L.get_obj_attributes(M)
		if P:B.error(P)
		for(C,H,I,a,c)in Z:
			if C in['classmethod','staticmethod','BaseException',N]:continue
			if C[0].isdigit():B.warning('NameError: invalid name {}'.format(C));continue
			if I=="<class 'type'>"and X(E)<=A6*4:
				Q=A;R=C.endswith(N)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=N
				D='\n{}class {}({}):\n'.format(E,C,Q)
				if R:D+=E+'    ...\n';J.write(D);continue
				J.write(D);L.write_object_stub(J,a,'{0}.{1}'.format(obj_name,C),E+'    ',O+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';J.write(D)
			elif any(A in I for A in[z,y,'closure']):
				S=U;T=A
				if O>0:T='self, '
				if V in I or V in H:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,C,S)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,C,T,S)
				D+=E+'    ...\n\n';J.write(D)
			elif I=="<class 'module'>":0
			elif I.startswith("<class '"):
				G=I[8:-2];D=A
				if G in(w,u,v,x,'bytearray','bytes'):
					if C.upper()==C:D='{0}{1}: Final[{3}] = {2}\n'.format(E,C,H,G)
					else:D=W.format(E,C,H,G)
				elif G in(h,g,f):b={h:'{}',g:'[]',f:'()'};D=W.format(E,C,b[G],G)
				elif G in('object','set','frozenset','Pin'):D='{0}{1}: {2} ## = {4}\n'.format(E,C,G,I,H)
				elif G=='generator':G='Generator';D='{0}def {1}(*args, **kwargs) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(E,C,G,I,H)
				else:
					G=U
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
		G='firmware';A._json_name='{}/{}'.format(A.path,filename);A._json_first=Y;a(A._json_name);B.info('Report file: {}'.format(A._json_name));F.collect()
		try:
			with W(A._json_name,'w')as E:E.write('{');E.write(dumps({G:A.info})[1:-1]);E.write(i);E.write(dumps({t:{C:__version__},'stubtype':G})[1:-1]);E.write(i);E.write('"modules" :[\n')
		except D as I:B.error(A1);A._json_name=H;raise I
	def report_add(A,module_name,stub_file):
		if not A._json_name:raise s(A2)
		try:
			with W(A._json_name,'a')as C:
				if not A._json_first:C.write(i)
				else:A._json_first=I
				E='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',G));C.write(E)
		except D:B.error(A1)
	def report_end(A):
		if not A._json_name:raise s(A2)
		with W(A._json_name,'a')as C:C.write('\n]}')
		B.info('Path: {}'.format(A.path))
def a(path):
	A=E=0
	while A!=-1:
		A=path.find(G,E)
		if A!=-1:
			C=path[0]if A==0 else path[:A]
			try:I=os.stat(C)
			except D as F:
				if F.args[0]in[A4,A5]:
					try:B.debug('Create folder {}'.format(C));os.mkdir(C)
					except D as H:B.error('failed to create folder {}'.format(C));raise H
		E=A+1
def b(s):
	C=' on '
	if not s:return A
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not E in s:return A
		B=s.split(E)[1];return B
	if not Z in s:return A
	B=s.split(Z)[1].split(L)[1];return B
def A7():
	try:B=sys.implementation[0]
	except d:B=sys.implementation.name
	D=m({U:B,C:A,N:A,'ver':A,M:sys.platform,S:'UNKNOWN',T:A,j:A,'cpu':A,P:A,k:A});return D
def A8(info):
	A=info
	if A[M].startswith('pyb'):A[M]='stm32'
	elif A[M]=='win32':A[M]=A3
	elif A[M]=='linux':A[M]=l
def A9(info):
	try:info[C]=AG(sys.implementation.version)
	except J:pass
def AA(info):
	B=info
	try:
		D=sys.implementation._machine if'_machine'in O(sys.implementation)else os.uname().machine;B[S]=D.strip();C=sys.implementation._build if'_build'in O(sys.implementation)else A
		if C:B[S]=C.split(E)[0];B[j]=C.split(E)[1]if E in C else A
		B[T]=C;B['cpu']=D.split('with')[-1].strip();B[P]=sys.implementation._mpy if'_mpy'in O(sys.implementation)else sys.implementation.mpy if P in O(sys.implementation)else A
	except(J,R):pass
	if not B[T]:AH(B)
def AB(info):
	B=info
	try:
		if'uname'in O(os):
			B[N]=b(os.uname()[3])
			if not B[N]:B[N]=b(os.uname()[2])
		elif C in O(sys):B[N]=b(sys.version)
	except(J,R,d):pass
	if B[C]==A and sys.platform not in(l,'win32'):
		try:D=os.uname();B[C]=D.release
		except(R,J,d):pass
def AC(info):
	D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:I=__import__(F,H,H,G);A[U]=E;del I;break
		except(Q,r):pass
	if A[U]==D:A['release']='2.0.0'
def AD(info):
	A=info
	if A[U]==e:
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
def AE(info):
	A=info
	if P in A and A[P]:
		B=int(A[P])
		try:
			C=[H,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[k]=C
		except R:A[k]='unknown'
		A[P]='v{}.{}'.format(B&255,B>>8&3)
def AF(info):
	A=info
	if A[N]and not A[C].endswith(Z):A[C]=A[C]+Z
	A['ver']=f"{A[C]}-{A[N]}"if A[N]else f"{A[C]}"
def _info():A=A7();A8(A);A9(A);AA(A);AB(A);AC(A);AD(A);AE(A);AF(A);return A
def AG(version):
	A=version;B=L.join([str(A)for A in A[:3]])
	if X(A)>3 and A[3]:B+=E+A[3]
	return B
def AH(info):
	D=info
	try:from boardname import BOARD_ID as C;B.info('Found BOARD_ID: {}'.format(C))
	except Q:B.warning('BOARD_ID not found');C=A
	D[T]=C;D[S]=C.split(E)[0]if E in C else C;D[j]==C.split(E)[1]if E in C else A
def get_root():
	try:A=os.getcwd()
	except(D,J):A=L
	B=A
	for B in['/remote','/sd','/flash',G,A,L]:
		try:C=os.stat(B);break
		except D:continue
	return B
def AI(filename):
	try:
		if os.stat(filename)[0]>>14:return Y
		return I
	except D:return I
def n():V("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=A
	if X(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):path=sys.argv[2]
		else:n()
	elif X(sys.argv)==2:n()
	return path
def o():
	try:A=bytes('abc',encoding='utf8');B=o.__module__;return I
	except(p,J):return Y
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_asyncio','_boot_fat','_espnow','_onewire','_rp2','_thread','_uasyncio','abc','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','base64','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','builtins','cc3200','cmath','collections','collections/__init__','collections/defaultdict','copy','crypto','cryptolib','curl','datetime','deflate','dht','display','display_driver_utils','ds18x20','embed','encoder','errno','esp','esp32','esp8266','espidf','espnow','ffi','flashbdev','fnmatch','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','gzip','hashlib','heapq','hmac','html/__init__','hub75','ili9341','ili9XXX','imagetools','inisetup','inspect','interstate75','io','itertools','jpegdec','js','jsffi','json','lcd160cr','locale','lodepng',A0,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','marshal','math','microWebSocket','microWebSrv','microWebTemplate',e,'mimxrt','mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','nrf','ntptime','onewire','openamp','operator','os','os/__init__','os/path','pathlib','pcf85063a','pic16bit','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform','powerpc','pyb','pye','pyscript','pyscript/__init__','pyscript/fs','qemu','qrcode','random','renesas','renesas-ra','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stat','stm','stm32','string','struct','sys','tarfile/__init__','tarfile/write','termios','time','tls','tpcalib','types','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','unittest/__init__',l,'uos','uplatform','urandom','ure','urequests','urllib/urequest','usb/device','usb/device/cdc','usb/device/hid','usb/device/keyboard','usb/device/midi','usb/device/mouse','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uu','uwebsocket','uzlib',C,'vfs','webassembly','websocket','websocket_helper',A3,'wipy','writer','xpt2046','ymodem','zephyr','zlib','zsensor'];F.collect();stubber.create_all_stubs()
if __name__=='__main__'or o():
	if not AI('no_auto_stubber.txt'):
		V(f"createstubs.py: {__version__}")
		try:F.threshold(4096);F.enable()
		except BaseException:pass
		main()