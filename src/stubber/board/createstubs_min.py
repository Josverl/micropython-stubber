A2='windows'
A1='No report file'
A0='Failed to create the report.'
z='{}/{}'
y='logging'
x='sys'
w='method'
v='function'
u='bool'
t='str'
s='float'
r='int'
q='stubber'
p=Exception
o=KeyError
n=sorted
m=NotImplementedError
i='unix'
h='variant'
g=',\n'
f='dict'
e='list'
d='tuple'
c='micropython'
b=TypeError
a=repr
X='-preview'
W=True
V=len
U=open
T=print
S='family'
R='board_id'
Q='board'
P=IndexError
O=ImportError
N=dir
M='port'
L='.'
J=AttributeError
I=False
H=None
G='/'
E='-'
D=OSError
C='version'
B=''
import gc as F,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except O:pass
try:from collections import OrderedDict as j
except O:from ucollections import OrderedDict as j
__version__='v1.25.0'
A3=2
A4=44
A5=2
A9=['lib','/lib','/sd/lib','/flash/lib',L]
class K:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=T
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
A=K.getLogger(q)
K.basicConfig(level=K.INFO)
class Stubber:
	def __init__(B,path=B,firmware_id=B):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise m('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		B.info=_info();A.info('Port: {}'.format(B.info[M]));A.info('Board: {}'.format(B.info[Q]));A.info('Board_ID: {}'.format(B.info[R]));F.collect()
		if C:B._fwid=C.lower()
		elif B.info[S]==c:B._fwid='{family}-v{version}-{port}-{board_id}'.format(**B.info).rstrip(E)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=F.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',G)
		try:Y(path+G)
		except D:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[];B._json_name=H;B._json_first=I
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for A in N(H):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=getattr(H,A)
				try:E=a(type(D)).split("'")[1]
				except P:E=B
				if E in{r,s,t,u,d,e,f}:G=1
				elif E in{v,w}:G=2
				elif E in'class':G=3
				else:G=4
				C.append((A,a(D),a(type(D)),D,G))
			except J as I:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,I))
			except MemoryError as I:T('MemoryError: {}'.format(I));sleep(1);reset()
		C=n([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return C,K
	def add_modules(A,modules):A.modules=n(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber {} on {}'.format(__version__,B._fwid));B.report_start();F.collect()
		for C in B.modules:B.create_one_stub(C)
		B.report_end();A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return I
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return I
		H='{}/{}.pyi'.format(C.path,B.replace(L,G));F.collect();E=I
		try:E=C.create_module_stub(B,H)
		except D:return I
		F.collect();return E
	def create_module_stub(J,module_name,file_name=H):
		E=file_name;C=module_name
		if E is H:K=C.replace(L,'_')+'.pyi';E=J.path+G+K
		else:K=E.split(G)[-1]
		if G in C:C=C.replace(G,L)
		M=H
		try:M=__import__(C,H,H,'*');P=F.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,K,P))
		except O:return I
		Y(E)
		with U(E,'w')as N:Q=str(J.info).replace('OrderedDict(',B).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,J._fwid,Q,__version__);N.write(R);N.write('from __future__ import annotations\nfrom typing import Any, Final, Generator\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(N,M,C,B)
		J.report_add(C,E)
		if C not in{'os',x,y,'gc'}:
			try:del M
			except(D,o):A.warning('could not del new_module')
		F.collect();return W
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		Y=' at ...>';X='{0}{1}: {3} = {2}\n';W='bound_method';U='Incomplete';O=in_class;N='Exception';M=object_expr;K=' at ';J=fp;E=indent;F.collect()
		if M in L.problematic:A.warning('SKIPPING problematic module:{}'.format(M));return
		Z,P=L.get_obj_attributes(M)
		if P:A.error(P)
		for(C,H,I,a,c)in Z:
			if C in['classmethod','staticmethod','BaseException',N]:continue
			if C[0].isdigit():A.warning('NameError: invalid name {}'.format(C));continue
			if I=="<class 'type'>"and V(E)<=A5*4:
				Q=B;R=C.endswith(N)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=N
				D='\n{}class {}({}):\n'.format(E,C,Q)
				if R:D+=E+'    ...\n';J.write(D);continue
				J.write(D);L.write_object_stub(J,a,'{0}.{1}'.format(obj_name,C),E+'    ',O+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';J.write(D)
			elif any(A in I for A in[w,v,'closure']):
				S=U;T=B
				if O>0:T='self, '
				if W in I or W in H:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,C,S)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,C,T,S)
				D+=E+'    ...\n\n';J.write(D)
			elif I=="<class 'module'>":0
			elif I.startswith("<class '"):
				G=I[8:-2];D=B
				if G in(t,r,s,u,'bytearray','bytes'):
					if C.upper()==C:D='{0}{1}: Final[{3}] = {2}\n'.format(E,C,H,G)
					else:D=X.format(E,C,H,G)
				elif G in(f,e,d):b={f:'{}',e:'[]',d:'()'};D=X.format(E,C,b[G],G)
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
	def clean(C,path=B):
		if not path:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except(D,J):return
		for F in E:
			B=z.format(path,F)
			try:os.remove(B)
			except D:
				try:C.clean(B);os.rmdir(B)
				except D:pass
	def report_start(B,filename='modules.json'):
		G='firmware';B._json_name=z.format(B.path,filename);B._json_first=W;Y(B._json_name);A.info('Report file: {}'.format(B._json_name));F.collect()
		try:
			with U(B._json_name,'w')as E:E.write('{');E.write(dumps({G:B.info})[1:-1]);E.write(g);E.write(dumps({q:{C:__version__},'stubtype':G})[1:-1]);E.write(g);E.write('"modules" :[\n')
		except D as I:A.error(A0);B._json_name=H;raise I
	def report_add(B,module_name,stub_file):
		if not B._json_name:raise p(A1)
		try:
			with U(B._json_name,'a')as C:
				if not B._json_first:C.write(g)
				else:B._json_first=I
				E='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',G));C.write(E)
		except D:A.error(A0)
	def report_end(B):
		if not B._json_name:raise p(A1)
		with U(B._json_name,'a')as C:C.write('\n]}')
		A.info('Path: {}'.format(B.path))
def Y(path):
	B=E=0
	while B!=-1:
		B=path.find(G,E)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except D as F:
				if F.args[0]in[A3,A4]:
					try:A.debug('Create folder {}'.format(C));os.mkdir(C)
					except D as H:A.error('failed to create folder {}'.format(C));raise H
		E=B+1
def Z(s):
	C=' on '
	if not s:return B
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not E in s:return B
		A=s.split(E)[1];return A
	if not X in s:return B
	A=s.split(X)[1].split(L)[1];return A
def _info():
	e='ev3-pybricks';d='pycom';a='pycopy';Y='win32';W='arch';V='cpu';U='ver';F='mpy';D='build'
	try:L=sys.implementation[0]
	except b:L=sys.implementation.name
	A=j({S:L,C:B,D:B,U:B,M:sys.platform,Q:'UNKNOWN',R:B,h:B,V:B,F:B,W:B})
	if A[M].startswith('pyb'):A[M]='stm32'
	elif A[M]==Y:A[M]=A2
	elif A[M]=='linux':A[M]=i
	try:A[C]=A6(sys.implementation.version)
	except J:pass
	try:
		T=sys.implementation._machine if'_machine'in N(sys.implementation)else os.uname().machine;A[Q]=T.strip();G=sys.implementation._build if'_build'in N(sys.implementation)else B
		if G:A[Q]=G.split(E)[0];A[h]=G.split(E)[1]if E in G else B
		A[R]=G;A[V]=T.split('with')[-1].strip();A[F]=sys.implementation._mpy if'_mpy'in N(sys.implementation)else sys.implementation.mpy if F in N(sys.implementation)else B
	except(J,P):pass
	if not A[R]:A7(A)
	try:
		if'uname'in N(os):
			A[D]=Z(os.uname()[3])
			if not A[D]:A[D]=Z(os.uname()[2])
		elif C in N(sys):A[D]=Z(sys.version)
	except(J,P,b):pass
	if A[C]==B and sys.platform not in(i,Y):
		try:f=os.uname();A[C]=f.release
		except(P,J,b):pass
	for(g,k,l)in[(a,a,'const'),(d,d,'FAT'),(e,'pybricks.hubs','EV3Brick')]:
		try:m=__import__(k,H,H,l);A[S]=g;del m;break
		except(O,o):pass
	if A[S]==e:A['release']='2.0.0'
	if A[S]==c:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if F in A and A[F]:
		I=int(A[F])
		try:K=[H,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][I>>10]
		except P:K='unknown'
		if K:A[W]=K
		A[F]='v{}.{}'.format(I&255,I>>8&3)
	if A[D]and not A[C].endswith(X):A[C]=A[C]+X
	A[U]=f"{A[C]}-{A[D]}"if A[D]else f"{A[C]}";return A
def A6(version):
	A=version;B=L.join([str(A)for A in A[:3]])
	if V(A)>3 and A[3]:B+=E+A[3]
	return B
def A7(info):
	D=info
	try:from boardname import BOARD_ID as C;A.info('Found BOARD_ID: {}'.format(C))
	except O:A.warning('BOARD_ID not found');C=B
	D[R]=C;D[Q]=C.split(E)[0]if E in C else C;D[h]==C.split(E)[1]if E in C else B
def get_root():
	try:A=os.getcwd()
	except(D,J):A=L
	B=A
	for B in['/remote','/sd','/flash',G,A,L]:
		try:C=os.stat(B);break
		except D:continue
	return B
def A8(filename):
	try:
		if os.stat(filename)[0]>>14:return W
		return I
	except D:return I
def k():T("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if V(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:k()
	elif V(sys.argv)==2:k()
	return path
def l():
	try:A=bytes('abc',encoding='utf8');B=l.__module__;return I
	except(m,J):return W
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_asyncio','_boot_fat','_espnow','_onewire','_rp2','_thread','_uasyncio','abc','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','base64','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','builtins','cc3200','cmath','collections','collections/__init__','collections/defaultdict','copy','crypto','cryptolib','curl','datetime','deflate','dht','display','display_driver_utils','ds18x20','embed','encoder','errno','esp','esp32','esp8266','espidf','espnow','ffi','flashbdev','fnmatch','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','gzip','hashlib','heapq','hmac','html/__init__','hub75','ili9341','ili9XXX','imagetools','inisetup','inspect','interstate75','io','itertools','jpegdec','js','jsffi','json','lcd160cr','locale','lodepng',y,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','marshal','math','microWebSocket','microWebSrv','microWebTemplate',c,'mimxrt','mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','nrf','ntptime','onewire','openamp','operator','os','os/__init__','os/path','pathlib','pcf85063a','pic16bit','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform','powerpc','pyb','pye','pyscript','pyscript/__init__','pyscript/fs','qemu','qrcode','random','renesas','renesas-ra','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stat','stm','stm32','string','struct',x,'tarfile/__init__','tarfile/write','termios','time','tls','tpcalib','types','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','unittest/__init__',i,'uos','uplatform','urandom','ure','urequests','urllib/urequest','usb/device','usb/device/cdc','usb/device/hid','usb/device/keyboard','usb/device/midi','usb/device/mouse','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uu','uwebsocket','uzlib',C,'vfs','webassembly','websocket','websocket_helper',A2,'wipy','writer','xpt2046','ymodem','zephyr','zlib'];F.collect();stubber.create_all_stubs()
if __name__=='__main__'or l():
	if not A8('no_auto_stubber.txt'):
		T(f"createstubs.py: {__version__}")
		try:F.threshold(4096);F.enable()
		except BaseException:pass
		main()