w='pyb'
v='stubber'
u='{}/{}'
t='logging'
s='sys'
r='method'
q='function'
p='bool'
o='str'
n='float'
m='int'
l=NameError
k=sorted
j=NotImplementedError
b='pycom'
a=',\n'
Z='dict'
Y='list'
X='tuple'
W='micropython'
V=open
U=repr
S='_'
R=len
Q=KeyError
P=IndexError
O=dir
N=print
M=ImportError
L=True
K='family'
J='board'
I='.'
H=AttributeError
A=False
G='/'
E=None
F=OSError
D='version'
B=''
import gc as C,os,sys
from ujson import dumps as c
try:from machine import reset
except M:pass
try:from collections import OrderedDict as d
except M:from ucollections import OrderedDict as d
__version__='v1.16.0'
x=2
y=2
z=[I,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise j('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();C.collect()
		if B:A._fwid=B.lower()
		elif A.info[K]==W:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:e(path+G)
		except F:N('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		I=item_instance;D=[];J=[]
		for A in O(I):
			if A.startswith(S)and not A in L.modules:continue
			try:
				E=getattr(I,A)
				try:F=U(type(E)).split("'")[1]
				except P:F=B
				if F in{m,n,o,p,X,Y,Z}:G=1
				elif F in{q,r}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,U(E),U(type(E)),E,G))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,I,K))
			except MemoryError as K:sleep(1);reset()
		D=k([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);C.collect();return D,J
	def add_modules(A,modules):A.modules=k(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(B,module_name):
		D=module_name
		if D in B.problematic:return A
		if D in B.excluded:return A
		H='{}/{}.py'.format(B.path,D.replace(I,G));C.collect();E=A
		try:E=B.create_module_stub(D,H)
		except F:return A
		C.collect();return E
	def create_module_stub(J,module_name,file_name=E):
		H=file_name;D=module_name
		if H is E:O=D.replace(I,S)+'.py';H=J.path+G+O
		else:O=H.split(G)[-1]
		if G in D:D=D.replace(G,I)
		K=E
		try:K=__import__(D,E,E,'*');T=C.mem_free()
		except M:return A
		e(H)
		with V(H,'w')as N:P=str(J.info).replace('OrderedDict(',B).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,J._fwid,P,__version__);N.write(R);N.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(N,K,D,B)
		J._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os',s,t,'gc'}:
			try:del K
			except(F,Q):pass
			try:del sys.modules[D]
			except Q:pass
		C.collect();return L
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Incomplete';P=in_class;O=object_expr;M='Exception';H=fp;D=indent;C.collect()
		if O in K.problematic:return
		S,L=K.get_obj_attributes(O)
		if L:N(L)
		for(E,J,G,T,f)in S:
			if E in['classmethod','staticmethod','BaseException',M]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and R(D)<=y*4:
				U=B;V=E.endswith(M)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=M
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),D+'    ',P+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif any(A in G for A in[r,q,'closure']):
				W=b;a=B
				if P>0:a='self, '
				if c in G or c in J:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,a,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[o,m,n,p,'bytearray','bytes']:A=d.format(D,E,J,I)
				elif I in[Z,Y,X]:e={Z:'{}',Y:'[]',X:'()'};A=d.format(D,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,I,G,J)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+E+' # type: Incomplete\n')
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
		except(F,H):return
		for D in C:
			A=u.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(B,filename='modules.json'):
		G=u.format(B.path,filename);C.collect()
		try:
			with V(G,'w')as D:
				B.write_json_header(D);E=L
				for H in B._report:B.write_json_node(D,H,E);E=A
				B.write_json_end(D)
			I=B._start_free-C.mem_free()
		except F:N('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(c({A:B.info})[1:-1]);f.write(a);f.write(c({v:{D:__version__},'stubtype':A})[1:-1]);f.write(a);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(a)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def e(path):
	A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except F as D:
				if D.args[0]==x:
					try:os.mkdir(B)
					except F as E:N('failed to create folder {}'.format(B));raise E
		C=A+1
def T(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	i='ev3-pybricks';h='pycopy';e='GENERIC';c='arch';a='cpu';Z='ver';V='with';G='mpy';F='build';A=d({K:sys.implementation.name,D:B,F:B,Z:B,'port':'stm32'if sys.platform.startswith(w)else sys.platform,J:e,a:B,G:B,c:B})
	try:A[D]=I.join([str(A)for A in sys.implementation.version])
	except H:pass
	try:X=sys.implementation._machine if'_machine'in O(sys.implementation)else os.uname().machine;A[J]=X.strip();A[a]=X.split(V)[1].strip();A[G]=sys.implementation._mpy if'_mpy'in O(sys.implementation)else sys.implementation.mpy if G in O(sys.implementation)else B
	except(H,P):pass
	C.collect()
	for N in[A+'/board_info.csv'for A in z]:
		if g(N):
			L=A[J].strip()
			if f(A,L,N):break
			if V in L:
				L=L.split(V)[0].strip()
				if f(A,L,N):break
			A[J]=e
	A[J]=A[J].replace(' ',S);C.collect()
	try:
		A[F]=T(os.uname()[3])
		if not A[F]:A[F]=T(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=T(sys.version.split(';')[1])
	except(H,P):pass
	if A[F]and R(A[F])>5:A[F]=B
	if A[D]==B and sys.platform not in('unix','win32'):
		try:j=os.uname();A[D]=j.release
		except(P,H,TypeError):pass
	for(k,l,m)in[(h,h,'const'),(b,b,'FAT'),(i,'pybricks.hubs','EV3Brick')]:
		try:n=__import__(l,E,E,m);A[K]=k;del n;break
		except(M,Q):pass
	if A[K]==i:A['release']='2.0.0'
	if A[K]==W:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if G in A and A[G]:
		U=int(A[G]);Y=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][U>>10]
		if Y:A[c]=Y
		A[G]='v{}.{}'.format(U&255,U>>8&3)
	A[Z]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def f(info,board_descr,filename):
	with V(filename,'r')as C:
		while 1:
			B=C.readline()
			if not B:break
			D,E=B.split(',')[0].strip(),B.split(',')[1].strip()
			if D==board_descr:info[J]=E;return L
	return A
def get_root():
	try:A=os.getcwd()
	except(F,H):A=I
	B=A
	for B in[A,'/sd','/flash',G,I]:
		try:C=os.stat(B);break
		except F:continue
	return B
def g(filename):
	try:
		if os.stat(filename)[0]>>14:return L
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
	except(j,H):return L
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_asyncio','_boot_fat','_coap','_espnow','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','apa102','apa106','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','cmath','collections','crypto','cryptolib','curl','deflate','dht','display','display_driver_utils','ds18x20','encoder','errno','esp','esp32','espidf','espnow','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','json','lcd160cr','lodepng',t,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','math','microWebSocket','microWebSrv','microWebTemplate',W,'mip','mip/__init__','motor','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pcf85063a','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform',w,b,'pye','qrcode','queue','random','requests','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','struct',s,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',D,'websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or i():
	try:A0=logging.getLogger(v);logging.basicConfig(level=logging.INFO)
	except l:pass
	if not g('no_auto_stubber.txt'):
		try:C.threshold(4*1024);C.enable()
		except BaseException:pass
		main()