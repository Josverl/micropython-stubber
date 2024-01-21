y='with'
x='pyb'
w='stubber'
v='{}/{}'
u='logging'
t='sys'
s='method'
r='function'
q='bool'
p='str'
o='float'
n='int'
m=TypeError
l=NameError
k=sorted
j=NotImplementedError
d='pycom'
c='-'
b=',\n'
a='dict'
Z='list'
Y='tuple'
X='micropython'
W=open
V=repr
T='cpu'
S='_'
R=len
Q=KeyError
P=IndexError
O=print
N=ImportError
M='family'
L=dir
K=True
J='.'
I=AttributeError
H='board'
A=False
G='/'
E=None
F=OSError
C='version'
B=''
import gc as D,os,sys
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except N:pass
try:from collections import OrderedDict as e
except N:from ucollections import OrderedDict as e
__version__='v1.16.2'
z=2
A0=2
A1=[J,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise j('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();D.collect()
		if B:A._fwid=B.lower()
		elif A.info[M]==X:A._fwid='{family}-v{version}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=D.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:f(path+G)
		except F:O('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(M,item_instance):
		H=item_instance;C=[];J=[]
		for A in L(H):
			if A.startswith(S)and not A in M.modules:continue
			try:
				E=getattr(H,A)
				try:F=V(type(E)).split("'")[1]
				except P:F=B
				if F in{n,o,p,q,Y,Z,a}:G=1
				elif F in{r,s}:G=2
				elif F in'class':G=3
				else:G=4
				C.append((A,V(E),V(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,K))
			except MemoryError as K:sleep(1);reset()
		C=k([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);D.collect();return C,J
	def add_modules(A,modules):A.modules=k(set(A.modules)|set(modules))
	def create_all_stubs(A):
		D.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(B,module_name):
		C=module_name
		if C in B.problematic:return A
		if C in B.excluded:return A
		H='{}/{}.py'.format(B.path,C.replace(J,G));D.collect();E=A
		try:E=B.create_module_stub(C,H)
		except F:return A
		D.collect();return E
	def create_module_stub(I,module_name,file_name=E):
		H=file_name;C=module_name
		if H is E:O=C.replace(J,S)+'.py';H=I.path+G+O
		else:O=H.split(G)[-1]
		if G in C:C=C.replace(G,J)
		L=E
		try:L=__import__(C,E,E,'*');T=D.mem_free()
		except N:return A
		f(H)
		with W(H,'w')as M:P=str(I.info).replace('OrderedDict(',B).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,I._fwid,P,__version__);M.write(R);M.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(M,L,C,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(C,H.replace('\\',G)))
		if C not in{'os',t,u,'gc'}:
			try:del L
			except(F,Q):pass
			try:del sys.modules[C]
			except Q:pass
		D.collect();return K
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Incomplete';P=in_class;N=object_expr;M='Exception';H=fp;C=indent;D.collect()
		if N in K.problematic:return
		S,L=K.get_obj_attributes(N)
		if L:O(L)
		for(E,J,G,T,f)in S:
			if E in['classmethod','staticmethod','BaseException',M]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and R(C)<=A0*4:
				U=B;V=E.endswith(M)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=M
				A='\n{}class {}({}):\n'.format(C,E,U)
				if V:A+=C+'    ...\n';H.write(A);return
				H.write(A);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),C+'    ',P+1);A=C+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=C+'        ...\n\n';H.write(A)
			elif any(A in G for A in[s,r,'closure']):
				W=b;X=B
				if P>0:X='self, '
				if c in G or c in J:A='{}@classmethod\n'.format(C)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(C,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(C,E,X,W)
				A+=C+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[p,n,o,q,'bytearray','bytes']:A=d.format(C,E,J,I)
				elif I in[a,Z,Y]:e={a:'{}',Z:'[]',Y:'()'};A=d.format(C,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(C,E,I,G,J)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(C+E+' # type: Incomplete\n')
		del S;del L
		try:del E,J,G,T
		except(F,Q,l):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,S)
		return A
	def clean(B,path=E):
		if path is E:path=B.path
		try:os.stat(path);C=os.listdir(path)
		except(F,I):return
		for D in C:
			A=v.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(B,filename='modules.json'):
		G=v.format(B.path,filename);D.collect()
		try:
			with W(G,'w')as C:
				B.write_json_header(C);E=K
				for H in B._report:B.write_json_node(C,H,E);E=A
				B.write_json_end(C)
			I=B._start_free-D.mem_free()
		except F:O('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(dumps({A:B.info})[1:-1]);f.write(b);f.write(dumps({w:{C:__version__},'stubtype':A})[1:-1]);f.write(b);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(b)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def f(path):
	A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except F as D:
				if D.args[0]==z:
					try:os.mkdir(B)
					except F as E:O('failed to create folder {}'.format(B));raise E
		C=A+1
def U(s):
	A=' on '
	if not s:return B
	s=s.split(A,1)[0]if A in s else s;s=s.split('; ',1)[1]if'; 'in s else s;C=s.split(c)[1]if s.startswith('v')else s.split(c,1)[-1].split(J)[1];return C
def _info():
	b='-preview';a='ev3-pybricks';Z='pycopy';Y='unix';W='win32';V='arch';S='ver';J='mpy';G='port';F='build';A=e({M:sys.implementation.name,C:B,F:B,S:B,G:sys.platform,H:'UNKNOWN',T:B,J:B,V:B})
	if A[G].startswith(x):A[G]='stm32'
	elif A[G]==W:A[G]='windows'
	elif A[G]=='linux':A[G]=Y
	try:A[C]=A2(sys.implementation.version)
	except I:pass
	try:O=sys.implementation._machine if'_machine'in L(sys.implementation)else os.uname().machine;A[H]=O;A[T]=O.split(y)[-1].strip();A[J]=sys.implementation._mpy if'_mpy'in L(sys.implementation)else sys.implementation.mpy if J in L(sys.implementation)else B
	except(I,P):pass
	D.collect();A3(A);D.collect()
	try:
		if'uname'in L(os):
			A[F]=U(os.uname()[3])
			if not A[F]:A[F]=U(os.uname()[2])
		elif C in L(sys):A[F]=U(sys.version)
	except(I,P,m):pass
	if A[C]==B and sys.platform not in(Y,W):
		try:c=os.uname();A[C]=c.release
		except(P,I,m):pass
	for(f,g,h)in[(Z,Z,'const'),(d,d,'FAT'),(a,'pybricks.hubs','EV3Brick')]:
		try:i=__import__(g,E,E,h);A[M]=f;del i;break
		except(N,Q):pass
	if A[M]==a:A['release']='2.0.0'
	if A[M]==X:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if J in A and A[J]:
		K=int(A[J]);R=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][K>>10]
		if R:A[V]=R
		A[J]='v{}.{}'.format(K&255,K>>8&3)
	if A[F]and not A[C].endswith(b):A[C]=A[C]+b
	A[S]=f"{A[C]}-{A[F]}"if A[F]else f"{A[C]}";return A
def A2(version):
	A=version;B=J.join([str(A)for A in A[:3]])
	if R(A)>3 and A[3]:B+=c+A[3]
	return B
def A3(info,desc=B):
	L='with ';C=info;F=A
	for G in[A+'/board_info.csv'for A in A1]:
		if g(G):
			E=desc or C[H].strip();I=E.rfind(' with')
			if I!=-1:J=E[:I].strip()
			else:J=B
			if A4(C,E,G,J):F=K;break
	if not F:
		E=desc or C[H].strip()
		if L+C[T].upper()in E:E=E.split(L+C[T].upper())[0].strip()
		C[H]=E
	C[H]=C[H].replace(' ',S);D.collect()
def A4(info,descr,filename,short_descr):
	D=short_descr;C=info;E=B
	with W(filename,'r')as J:
		while 1:
			F=J.readline()
			if not F:break
			I,G=F.split(',')[0].strip(),F.split(',')[1].strip()
			if I==descr:C[H]=G;return K
			elif D and I==D:
				if y in D:C[H]=G;return K
				E=G
	if E:C[H]=E;return K
	return A
def get_root():
	try:A=os.getcwd()
	except(F,I):A=J
	B=A
	for B in[A,'/sd','/flash',G,J]:
		try:C=os.stat(B);break
		except F:continue
	return B
def g(filename):
	try:
		if os.stat(filename)[0]>>14:return K
		return A
	except F:return A
def h():sys.exit(1)
def read_path():
	path=B
	if R(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:h()
	elif R(sys.argv)==2:h()
	return path
def i():
	try:B=bytes('abc',encoding='utf8');C=i.__module__;return A
	except(j,I):return K
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_asyncio','_boot_fat','_coap','_espnow','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','cmath','collections','crypto','cryptolib','curl','deflate','dht','display','display_driver_utils','ds18x20','encoder','errno','esp','esp32','espidf','espnow','ffi','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','json','lcd160cr','lodepng',u,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','math','microWebSocket','microWebSrv','microWebTemplate',X,'mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pcf85063a','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform',x,d,'pye','qrcode','queue','random','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','struct',t,'termios','time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',C,'websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];D.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or i():
	try:A5=logging.getLogger(w);logging.basicConfig(level=logging.INFO)
	except l:pass
	if not g('no_auto_stubber.txt'):
		try:D.threshold(4*1024);D.enable()
		except BaseException:pass
		main()