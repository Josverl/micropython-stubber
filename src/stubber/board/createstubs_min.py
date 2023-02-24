v='micropython'
u='esp32'
t='pycom'
s='nodename'
r='pyb'
q='{}/{}'
p='logging'
o='sys'
n='method'
m='function'
l='bool'
k='str'
j='float'
i='int'
h=NameError
g=sorted
f=NotImplementedError
b='platform'
a='machine'
Z='_'
Y='dict'
X='list'
W='tuple'
V=IndexError
U=repr
T='-'
S='sysname'
R=True
Q=ImportError
P='v'
O='build'
N='version'
M=len
L=KeyError
K='.'
J=AttributeError
I=False
H=print
G=''
F='/'
D=None
C=OSError
B='release'
import gc as E,sys,uos as os
from ujson import dumps as c
__version__='1.11.2'
w=2
x=2
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise f('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		A._report=[];A.info=_info();E.collect()
		if B:A._fwid=B.lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if path:
			if path.endswith(F):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',F)
		try:d(path+F)
		except C:H('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;A=[];I=[]
		for H in dir(F):
			try:
				B=getattr(F,H)
				try:C=U(type(B)).split("'")[1]
				except V:C=G
				if C in{i,j,k,l,W,X,Y}:D=1
				elif C in{m,n}:D=2
				elif C in'class':D=3
				else:D=4
				A.append((H,U(B),U(type(B)),B,D))
			except J as K:I.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(H,F,K))
		A=g([B for B in A if not B[0].startswith(Z)],key=lambda x:x[4]);E.collect();return A,I
	def add_modules(A,modules):A.modules=g(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(B,module_name):
		A=module_name
		if A in B.problematic:return I
		if A in B.excluded:return I
		D='{}/{}.py'.format(B.path,A.replace(K,F));E.collect();J=E.mem_free();H('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,D,J));G=I
		try:G=B.create_module_stub(A,D)
		except C:return I
		E.collect();return G
	def create_module_stub(B,module_name,file_name=D):
		J=file_name;A=module_name
		if J is D:J=B.path+F+A.replace(K,Z)+'.py'
		if F in A:A=A.replace(F,K)
		M=D
		try:M=__import__(A,D,D,'*')
		except Q:H('{}Skip module: {:<25} {:<79}'.format('\x1b[1A',A,'Module not found.'));return I
		d(J)
		with open(J,'w')as N:O='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,B._fwid,B.info,__version__);N.write(O);N.write('from typing import Any\n\n');B.write_object_stub(N,M,A,G)
		B._report.append('{{"module": "{}", "file": "{}"}}'.format(A,J.replace('\\',F)))
		if A not in{'os',o,p,'gc'}:
			try:del M
			except (C,L):pass
			try:del sys.modules[A]
			except L:pass
		E.collect();return R
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';R=in_class;Q=object_expr;P='Exception';I=fp;B=indent;E.collect()
		if Q in N.problematic:return
		S,O=N.get_obj_attributes(Q)
		if O:H(O)
		for (D,K,F,T,f) in S:
			if D in['classmethod','staticmethod','BaseException',P]:continue
			if F=="<class 'type'>"and M(B)<=x*4:
				U=G;V=D.endswith(P)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=P
				A='\n{}class {}({}):\n'.format(B,D,U)
				if V:A+=B+'    ...\n';I.write(A);return
				I.write(A);N.write_object_stub(I,T,'{0}.{1}'.format(obj_name,D),B+'    ',R+1);A=B+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=B+'        ...\n\n';I.write(A)
			elif n in F or m in F:
				Z=b;a=G
				if R>0:a='self, '
				if c in F or c in K:A='{}@classmethod\n'.format(B)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(B,D,Z)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(B,D,a,Z)
				A+=B+'    ...\n\n';I.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				J=F[8:-2];A=G
				if J in[k,i,j,l,'bytearray','bytes']:A=d.format(B,D,K,J)
				elif J in[Y,X,W]:e={Y:'{}',X:'[]',W:'()'};A=d.format(B,D,e[J],J)
				else:
					if J not in['object','set','frozenset']:J=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(B,D,J,F,K)
				I.write(A)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(B+D+' # type: Any\n')
		del S;del O
		try:del D,K,F,T
		except (C,L,h):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,Z)
		return A
	def clean(B,path=D):
		if path is D:path=B.path
		H('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except (C,J):return
		for F in E:
			A=q.format(path,F)
			try:os.remove(A)
			except C:
				try:B.clean(A);os.rmdir(A)
				except C:pass
	def report(A,filename='modules.json'):
		H('Created stubs for {} modules on board {}\nPath: {}'.format(M(A._report),A._fwid,A.path));B=q.format(A.path,filename);E.collect()
		try:
			with open(B,'w')as D:A.write_json_node(D)
			F=A._start_free-E.mem_free()
		except C:H('Failed to create the report.')
	def write_json_node(B,f):
		D='firmware';A=',\n';f.write('{');f.write(c({D:B.info})[1:-1]);f.write(A);f.write(c({'stubber':{N:__version__},'stubtype':D})[1:-1]);f.write(A);f.write('"modules" :[\n');C=R
		for E in B._report:
			if C:C=I
			else:f.write(A)
			f.write(E)
		f.write('\n]}')
def d(path):
	A=D=0
	while A!=-1:
		A=path.find(F,D)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except C as E:
				if E.args[0]==w:
					try:os.mkdir(B)
					except C as G:H('failed to create folder {}'.format(B));raise G
		D=A+1
def _info():
	Z='0.0.0';Y='port';X='name';I='mpy';H='unknown';E='family';C='ver';R=sys.implementation.name;U='stm32'if sys.platform.startswith(r)else sys.platform;A={X:R,B:Z,N:Z,O:G,S:H,s:H,a:H,E:R,b:U,Y:U,C:G}
	try:A[B]=K.join([str(A)for A in sys.implementation.version]);A[N]=A[B];A[X]=sys.implementation.name;A[I]=sys.implementation.mpy
	except J:pass
	if sys.platform not in('unix','win32'):
		try:y(A)
		except (V,J,TypeError):pass
	try:from pycopy import const as F;A[E]='pycopy';del F
	except (Q,L):pass
	try:from pycom import FAT as F;A[E]=t;del F
	except (Q,L):pass
	if A[b]=='esp32_LoBo':A[E]='loboris';A[Y]=u
	elif A[S]=='ev3':
		A[E]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except Q:pass
	if A[B]:A[C]=P+A[B].lstrip(P)
	if A[E]==v:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[O]!=G and M(A[O])<4:A[C]+=T+A[O]
	if A[C][0]!=P:A[C]=P+A[C]
	if I in A:
		c=int(A[I]);W=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][c>>10]
		if W:A['arch']=W
	return A
def y(info):
	E=' on ';A=info;C=os.uname();A[S]=C[0];A[s]=C[1];A[B]=C[2];A[a]=C[4]
	if E in C[3]:
		D=C[3].split(E)[0]
		if A[S]=='esp8266':F=D.split(T)[0]if T in D else D;A[N]=A[B]=F.lstrip(P)
		try:A[O]=D.split(T)[1]
		except V:pass
def get_root():
	try:A=os.getcwd()
	except (C,J):A=K
	B=A
	for B in [A,'/sd','/flash',F,K]:
		try:D=os.stat(B);break
		except C:continue
	return B
def z(filename):
	try:os.stat(filename);return R
	except C:return I
def A():sys.exit(1)
def read_path():
	path=G
	if M(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):path=sys.argv[2]
		else:A()
	elif M(sys.argv)==2:A()
	return path
def e():
	try:A=bytes('abc',encoding='utf8');B=e.__module__;return I
	except (f,J):return R
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_boot_fat','_coap','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','ak8963','apa102','apa106','array','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','cmath','collections','crypto','cryptolib','curl','dht','display','display_driver_utils','ds18x20','encoder','errno','esp',u,'espidf','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','json','lcd160cr','lodepng',p,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip',a,'math','microWebSocket','microWebSrv','microWebTemplate',v,'mip','motor','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pcf85063a','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma',b,r,t,'pye','qrcode','queue','random','requests','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','struct',o,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',N,'websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or e():
	try:logging.basicConfig(level=logging.INFO)
	except h:pass
	if not z('no_auto_stubber.txt'):main()