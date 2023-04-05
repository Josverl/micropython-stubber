w='micropython'
v='esp32'
u='pycom'
t='nodename'
s='pyb'
r='{}/{}'
q='logging'
p='sys'
o='method'
n='function'
m='bool'
l='str'
k='float'
j='int'
i=NameError
h=sorted
g=NotImplementedError
b='platform'
a='machine'
A=',\n'
Z='_'
Y='dict'
X='list'
W='tuple'
V=IndexError
U=repr
T='-'
S='sysname'
R=True
Q='v'
P='build'
O='version'
N=len
M=KeyError
L=ImportError
K='.'
J=print
I=AttributeError
H=False
G=''
F='/'
D=None
C=OSError
B='release'
import gc as E,sys,uos as os
from ujson import dumps as c
try:from collections import OrderedDict
except L:from ucollections import OrderedDict
__version__='v1.12.2'
x=2
y=2
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise g('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();E.collect()
		if B:A._fwid=B.lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if path:
			if path.endswith(F):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',F)
		try:d(path+F)
		except C:J('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;A=[];J=[]
		for H in dir(F):
			try:
				B=getattr(F,H)
				try:C=U(type(B)).split("'")[1]
				except V:C=G
				if C in{j,k,l,m,W,X,Y}:D=1
				elif C in{n,o}:D=2
				elif C in'class':D=3
				else:D=4
				A.append((H,U(B),U(type(B)),B,D))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(H,F,K))
		A=h([A for A in A if not A[0].startswith(Z)],key=lambda x:x[4]);E.collect();return A,J
	def add_modules(A,modules):A.modules=h(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(A,module_name):
		B=module_name
		if B in A.problematic:return H
		if B in A.excluded:return H
		G='{}/{}.py'.format(A.path,B.replace(K,F));E.collect();D=H
		try:D=A.create_module_stub(B,G)
		except C:return H
		E.collect();return D
	def create_module_stub(I,module_name,file_name=D):
		B=file_name;A=module_name
		if B is D:B=I.path+F+A.replace(K,Z)+'.py'
		if F in A:A=A.replace(F,K)
		N=D
		try:N=__import__(A,D,D,'*');J('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,B,E.mem_free()))
		except L:return H
		d(B)
		with open(B,'w')as O:P='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,I._fwid,I.info,__version__);O.write(P);O.write('from typing import Any\n\n');I.write_object_stub(O,N,A,G)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(A,B.replace('\\',F)))
		if A not in{'os',p,q,'gc'}:
			try:del N
			except (C,M):pass
			try:del sys.modules[A]
			except M:pass
		E.collect();return R
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';R=in_class;Q=object_expr;P='Exception';H=fp;B=indent;E.collect()
		if Q in L.problematic:return
		S,O=L.get_obj_attributes(Q)
		if O:J(O)
		for (D,K,F,T,f) in S:
			if D in['classmethod','staticmethod','BaseException',P]:continue
			if F=="<class 'type'>"and N(B)<=y*4:
				U=G;V=D.endswith(P)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=P
				A='\n{}class {}({}):\n'.format(B,D,U)
				if V:A+=B+'    ...\n';H.write(A);return
				H.write(A);L.write_object_stub(H,T,'{0}.{1}'.format(obj_name,D),B+'    ',R+1);A=B+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=B+'        ...\n\n';H.write(A)
			elif o in F or n in F:
				Z=b;a=G
				if R>0:a='self, '
				if c in F or c in K:A='{}@classmethod\n'.format(B)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(B,D,Z)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(B,D,a,Z)
				A+=B+'    ...\n\n';H.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				I=F[8:-2];A=G
				if I in[l,j,k,m,'bytearray','bytes']:A=d.format(B,D,K,I)
				elif I in[Y,X,W]:e={Y:'{}',X:'[]',W:'()'};A=d.format(B,D,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(B,D,I,F,K)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(F));H.write(B+D+' # type: Any\n')
		del S;del O
		try:del D,K,F,T
		except (C,M,i):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,Z)
		return A
	def clean(B,path=D):
		if path is D:path=B.path
		J('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except (C,I):return
		for F in E:
			A=r.format(path,F)
			try:os.remove(A)
			except C:
				try:B.clean(A);os.rmdir(A)
				except C:pass
	def report(A,filename='modules.json'):
		J('Created stubs for {} modules on board {}\nPath: {}'.format(N(A._report),A._fwid,A.path));F=r.format(A.path,filename);E.collect()
		try:
			with open(F,'w')as B:
				A.write_json_header(B);D=R
				for G in A._report:A.write_json_node(B,G,D);D=H
				A.write_json_end(B)
			I=A._start_free-E.mem_free()
		except C:J('Failed to create the report.')
	def write_json_header(C,f):B='firmware';f.write('{');f.write(c({B:C.info})[1:-1]);f.write(A);f.write(c({'stubber':{O:__version__},'stubtype':B})[1:-1]);f.write(A);f.write('"modules" :[\n')
	def write_json_node(B,f,n,first):
		if not first:f.write(A)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def d(path):
	A=D=0
	while A!=-1:
		A=path.find(F,D)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except C as E:
				if E.args[0]==x:
					try:os.mkdir(B)
					except C as G:J('failed to create folder {}'.format(B));raise G
		D=A+1
def _info():
	Z='0.0.0';Y='port';X='name';J='mpy';H='unknown';E='family';C='ver';R=sys.implementation.name;U='stm32'if sys.platform.startswith(s)else sys.platform;A={X:R,B:Z,O:Z,P:G,S:H,t:H,a:H,E:R,b:U,Y:U,C:G}
	try:A[B]=K.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[X]=sys.implementation.name;A[J]=sys.implementation.mpy
	except I:pass
	if sys.platform not in('unix','win32'):
		try:z(A)
		except (V,I,TypeError):pass
	try:from pycopy import const as F;A[E]='pycopy';del F
	except (L,M):pass
	try:from pycom import FAT as F;A[E]=u;del F
	except (L,M):pass
	if A[b]=='esp32_LoBo':A[E]='loboris';A[Y]=v
	elif A[S]=='ev3':
		A[E]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except L:pass
	if A[B]:A[C]=Q+A[B].lstrip(Q)
	if A[E]==w:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[P]!=G and N(A[P])<4:A[C]+=T+A[P]
	if A[C][0]!=Q:A[C]=Q+A[C]
	if J in A:
		c=int(A[J]);W=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][c>>10]
		if W:A['arch']=W
	return A
def z(info):
	E=' on ';A=info;C=os.uname();A[S]=C[0];A[t]=C[1];A[B]=C[2];A[a]=C[4]
	if E in C[3]:
		D=C[3].split(E)[0]
		if A[S]=='esp8266':F=D.split(T)[0]if T in D else D;A[O]=A[B]=F.lstrip(Q)
		try:A[P]=D.split(T)[1]
		except V:pass
def get_root():
	try:A=os.getcwd()
	except (C,I):A=K
	B=A
	for B in [A,'/sd','/flash',F,K]:
		try:D=os.stat(B);break
		except C:continue
	return B
def A0(filename):
	try:os.stat(filename);return R
	except C:return H
def e():sys.exit(1)
def read_path():
	path=G
	if N(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:e()
	elif N(sys.argv)==2:e()
	return path
def f():
	try:A=bytes('abc',encoding='utf8');B=f.__module__;return H
	except (g,I):return R
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_boot_fat','_coap','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','ak8963','apa102','apa106','array','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','cmath','collections','crypto','cryptolib','curl','dht','display','display_driver_utils','ds18x20','encoder','errno','esp',v,'espidf','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','json','lcd160cr','lodepng',q,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip',a,'math','microWebSocket','microWebSrv','microWebTemplate',w,'mip','motor','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pcf85063a','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma',b,s,u,'pye','qrcode','queue','random','requests','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','struct',p,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',O,'websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or f():
	try:logging.basicConfig(level=logging.INFO)
	except i:pass
	if not A0('no_auto_stubber.txt'):main()