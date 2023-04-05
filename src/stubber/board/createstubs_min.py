v='pyb'
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
A=',\n'
a='dict'
Z='list'
Y='tuple'
X='micropython'
W=open
V=repr
T='_'
S=KeyError
R=dir
Q=True
P='family'
O=len
N=IndexError
M=ImportError
L='.'
K='board'
J=print
I=False
G='/'
H=AttributeError
F=None
E='version'
D=OSError
B=''
import gc as C,sys,uos as os
from ujson import dumps as c
try:from machine import reset
except M:pass
try:from collections import OrderedDict as d
except M:from ucollections import OrderedDict as d
__version__='v1.12.2'
w=2
x=2
class Stubber:
	def __init__(A,path=F,firmware_id=F):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise j('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();C.collect()
		if B:A._fwid=B.lower()
		elif A.info[P]==X:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:e(path+G)
		except D:J('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		G=item_instance;A=[];J=[]
		for I in R(G):
			try:
				D=getattr(G,I)
				try:E=V(type(D)).split("'")[1]
				except N:E=B
				if E in{m,n,o,p,Y,Z,a}:F=1
				elif E in{q,r}:F=2
				elif E in'class':F=3
				else:F=4
				A.append((I,V(D),V(type(D)),D,F))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(I,G,K))
		A=k([A for A in A if not A[0].startswith(T)],key=lambda x:x[4]);C.collect();return A,J
	def add_modules(A,modules):A.modules=k(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(A,module_name):
		B=module_name
		if B in A.problematic:return I
		if B in A.excluded:return I
		F='{}/{}.py'.format(A.path,B.replace(L,G));C.collect();E=I
		try:E=A.create_module_stub(B,F)
		except D:return I
		C.collect();return E
	def create_module_stub(H,module_name,file_name=F):
		E=file_name;A=module_name
		if C.mem_free()<8500:
			try:from machine import reset;reset()
			except M:pass
		if E is F:E=H.path+G+A.replace(L,T)+'.py'
		if G in A:A=A.replace(G,L)
		K=F
		try:K=__import__(A,F,F,'*');J('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,E,C.mem_free()))
		except M:return I
		e(E)
		with W(E,'w')as N:O='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,H.info,__version__);N.write(O);N.write('from typing import Any\n\n');H.write_object_stub(N,K,A,B)
		H._report.append('{{"module": "{}", "file": "{}"}}'.format(A,E.replace('\\',G)))
		if A not in{'os',s,t,'gc'}:
			try:del K
			except (D,S):pass
			try:del sys.modules[A]
			except S:pass
		C.collect();return Q
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';Q=in_class;P=object_expr;N='Exception';H=fp;E=indent;C.collect()
		if P in L.problematic:return
		R,M=L.get_obj_attributes(P)
		if M:J(M)
		for (F,K,G,T,f) in R:
			if F in['classmethod','staticmethod','BaseException',N]:continue
			if G=="<class 'type'>"and O(E)<=x*4:
				U=B;V=F.endswith(N)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=N
				A='\n{}class {}({}):\n'.format(E,F,U)
				if V:A+=E+'    ...\n';H.write(A);return
				H.write(A);L.write_object_stub(H,T,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);A=E+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=E+'        ...\n\n';H.write(A)
			elif r in G or q in G:
				W=b;X=B
				if Q>0:X='self, '
				if c in G or c in K:A='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,X,W)
				A+=E+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[o,m,n,p,'bytearray','bytes']:A=d.format(E,F,K,I)
				elif I in[a,Z,Y]:e={a:'{}',Z:'[]',Y:'()'};A=d.format(E,F,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,I,G,K)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(E+F+' # type: Any\n')
		del R;del M
		try:del F,K,G,T
		except (D,S,l):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,T)
		return A
	def clean(B,path=F):
		if path is F:path=B.path
		J('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except (D,H):return
		for E in C:
			A=u.format(path,E)
			try:os.remove(A)
			except D:
				try:B.clean(A);os.rmdir(A)
				except D:pass
	def report(A,filename='modules.json'):
		J('Created stubs for {} modules on board {}\nPath: {}'.format(O(A._report),A._fwid,A.path));F=u.format(A.path,filename);C.collect()
		try:
			with W(F,'w')as B:
				A.write_json_header(B);E=Q
				for G in A._report:A.write_json_node(B,G,E);E=I
				A.write_json_end(B)
			H=A._start_free-C.mem_free()
		except D:J('Failed to create the report.')
	def write_json_header(C,f):B='firmware';f.write('{');f.write(c({B:C.info})[1:-1]);f.write(A);f.write(c({'stubber':{E:__version__},'stubtype':B})[1:-1]);f.write(A);f.write('"modules" :[\n')
	def write_json_node(B,f,n,first):
		if not first:f.write(A)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def e(path):
	A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except D as E:
				if E.args[0]==w:
					try:os.mkdir(B)
					except D as F:J('failed to create folder {}'.format(B));raise F
		C=A+1
def U(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	j='ev3-pybricks';i='pycopy';h='GENERIC';e='arch';c='cpu';a='ver';W='with';I='mpy';G='build';A=d({P:sys.implementation.name,E:B,G:B,a:B,'port':'stm32'if sys.platform.startswith(v)else sys.platform,K:h,c:B,I:B,e:B})
	try:A[E]=L.join([str(A)for A in sys.implementation.version])
	except H:pass
	try:Y=sys.implementation._machine if'_machine'in R(sys.implementation)else os.uname().machine;A[K]=Y.strip();A[c]=Y.split(W)[1].strip();A[I]=sys.implementation._mpy if'_mpy'in R(sys.implementation)else sys.implementation.mpy if I in R(sys.implementation)else B
	except (H,N):pass
	C.collect()
	try:
		for Q in ['board_info.csv','lib/board_info.csv']:
			if g(Q):
				J=A[K].strip()
				if f(A,J,Q):break
				if W in J:
					J=J.split(W)[0].strip()
					if f(A,J,Q):break
				A[K]=h
	except (H,N,D):pass
	A[K]=A[K].replace(' ',T);C.collect()
	try:
		A[G]=U(os.uname()[3])
		if not A[G]:A[G]=U(os.uname()[2])
		if not A[G]and';'in sys.version:A[G]=U(sys.version.split(';')[1])
	except (H,N):pass
	if A[G]and O(A[G])>5:A[G]=B
	if A[E]==B and sys.platform not in('unix','win32'):
		try:k=os.uname();A[E]=k.release
		except (N,H,TypeError):pass
	for (l,m,n) in [(i,i,'const'),(b,b,'FAT'),(j,'pybricks.hubs','EV3Brick')]:
		try:o=__import__(m,F,F,n);A[P]=l;del o;break
		except (M,S):pass
	if A[P]==j:A['release']='2.0.0'
	if A[P]==X:
		if A[E]and A[E].endswith('.0')and A[E]>='1.10.0'and A[E]<='1.20.0':A[E]=A[E][:-2]
	if I in A and A[I]:
		V=int(A[I]);Z=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][V>>10]
		if Z:A[e]=Z
		A[I]='v{}.{}'.format(V&255,V>>8&3)
	A[a]=f"v{A[E]}-{A[G]}"if A[G]else f"v{A[E]}";return A
def f(info,board_descr,filename):
	with W(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[K]=D;return Q
	return I
def get_root():
	try:A=os.getcwd()
	except (D,H):A=L
	B=A
	for B in [A,'/sd','/flash',G,L]:
		try:C=os.stat(B);break
		except D:continue
	return B
def g(filename):
	try:os.stat(filename);return Q
	except D:return I
def h():sys.exit(1)
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
	except (j,H):return Q
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_boot_fat','_coap','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','ak8963','apa102','apa106','array','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','cmath','collections','crypto','cryptolib','curl','dht','display','display_driver_utils','ds18x20','encoder','errno','esp','esp32','espidf','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','json','lcd160cr','lodepng',t,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','math','microWebSocket','microWebSrv','microWebTemplate',X,'mip','motor','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pcf85063a','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform',v,b,'pye','qrcode','queue','random','requests','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','struct',s,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',E,'websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or i():
	try:logging.basicConfig(level=logging.INFO)
	except l:pass
	if not g('no_auto_stubber.txt'):main()