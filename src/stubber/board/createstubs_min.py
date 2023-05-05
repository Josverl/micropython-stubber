w='pyb'
v='{}/{}'
u='logging'
t='sys'
s='method'
r='function'
q='bool'
p='str'
o='float'
n='int'
m='port'
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
T=KeyError
S=IndexError
R=dir
Q=ImportError
P=True
O='_'
N='family'
M=len
L='.'
K='board'
J=print
I=AttributeError
H=False
G='/'
E=None
F=OSError
D='version'
B=''
import gc as C,sys,uos as os
from ujson import dumps as c
try:from machine import reset
except Q:pass
try:from collections import OrderedDict as d
except Q:from ucollections import OrderedDict as d
__version__='v1.13.4'
x=2
y=2
z=[L,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise j('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();J('Port: {}'.format(A.info[m]));J('Board: {}'.format(A.info[K]));C.collect()
		if B:A._fwid=B.lower()
		elif A.info[N]==X:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:e(path+G)
		except F:J('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;A=[];J=[]
		for D in R(H):
			if D.startswith(O):continue
			try:
				E=getattr(H,D)
				try:F=V(type(E)).split("'")[1]
				except S:F=B
				if F in{n,o,p,q,Y,Z,a}:G=1
				elif F in{r,s}:G=2
				elif F in'class':G=3
				else:G=4
				A.append((D,V(E),V(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(D,H,K))
			except MemoryError as K:sleep(1);reset()
		A=k([A for A in A if not A[0].startswith(O)],key=lambda x:x[4]);C.collect();return A,J
	def add_modules(A,modules):A.modules=k(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(A,module_name):
		B=module_name
		if B in A.problematic:return H
		if B in A.excluded:return H
		E='{}/{}.py'.format(A.path,B.replace(L,G));C.collect();D=H
		try:D=A.create_module_stub(B,E)
		except F:return H
		C.collect();return D
	def create_module_stub(I,module_name,file_name=E):
		D=file_name;A=module_name
		if D is E:K=A.replace(L,O)+'.py';D=I.path+G+K
		else:K=D.split(G)[-1]
		if G in A:A=A.replace(G,L)
		M=E
		try:M=__import__(A,E,E,'*');R=C.mem_free();J('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,K,R))
		except Q:return H
		e(D)
		with W(D,'w')as N:S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,I._fwid,I.info,__version__);N.write(S);N.write('from typing import Any\n\n');I.write_object_stub(N,M,A,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(A,D.replace('\\',G)))
		if A not in{'os',t,u,'gc'}:
			try:del M
			except (F,T):pass
			try:del sys.modules[A]
			except T:pass
		C.collect();return P
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';Q=in_class;P=object_expr;O='Exception';H=fp;D=indent;C.collect()
		if P in L.problematic:return
		R,N=L.get_obj_attributes(P)
		if N:J(N)
		for (E,K,G,S,f) in R:
			if E in['classmethod','staticmethod','BaseException',O]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and M(D)<=y*4:
				U=B;V=E.endswith(O)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);L.write_object_stub(H,S,'{0}.{1}'.format(obj_name,E),D+'    ',Q+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif s in G or r in G:
				W=b;X=B
				if Q>0:X='self, '
				if c in G or c in K:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,X,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[p,n,o,q,'bytearray','bytes']:A=d.format(D,E,K,I)
				elif I in[a,Z,Y]:e={a:'{}',Z:'[]',Y:'()'};A=d.format(D,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,I,G,K)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+E+' # type: Any\n')
		del R;del N
		try:del E,K,G,S
		except (F,T,l):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,O)
		return A
	def clean(B,path=E):
		if path is E:path=B.path
		J('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except (F,I):return
		for D in C:
			A=v.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(A,filename='modules.json'):
		J('Created stubs for {} modules on board {}\nPath: {}'.format(M(A._report),A._fwid,A.path));E=v.format(A.path,filename);C.collect()
		try:
			with W(E,'w')as B:
				A.write_json_header(B);D=P
				for G in A._report:A.write_json_node(B,G,D);D=H
				A.write_json_end(B)
			I=A._start_free-C.mem_free()
		except F:J('Failed to create the report.')
	def write_json_header(C,f):B='firmware';f.write('{');f.write(c({B:C.info})[1:-1]);f.write(A);f.write(c({'stubber':{D:__version__},'stubtype':B})[1:-1]);f.write(A);f.write('"modules" :[\n')
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
			except F as D:
				if D.args[0]==x:
					try:os.mkdir(B)
					except F as E:J('failed to create folder {}'.format(B));raise E
		C=A+1
def U(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	i='ev3-pybricks';h='pycopy';e='GENERIC';c='arch';a='cpu';Z='ver';V='with';G='mpy';F='build';A=d({N:sys.implementation.name,D:B,F:B,Z:B,m:'stm32'if sys.platform.startswith(w)else sys.platform,K:e,a:B,G:B,c:B})
	try:A[D]=L.join([str(A)for A in sys.implementation.version])
	except I:pass
	try:W=sys.implementation._machine if'_machine'in R(sys.implementation)else os.uname().machine;A[K]=W.strip();A[a]=W.split(V)[1].strip();A[G]=sys.implementation._mpy if'_mpy'in R(sys.implementation)else sys.implementation.mpy if G in R(sys.implementation)else B
	except (I,S):pass
	C.collect()
	for J in [A+'/board_info.csv'for A in z]:
		if g(J):
			H=A[K].strip()
			if f(A,H,J):break
			if V in H:
				H=H.split(V)[0].strip()
				if f(A,H,J):break
			A[K]=e
	A[K]=A[K].replace(' ',O);C.collect()
	try:
		A[F]=U(os.uname()[3])
		if not A[F]:A[F]=U(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=U(sys.version.split(';')[1])
	except (I,S):pass
	if A[F]and M(A[F])>5:A[F]=B
	if A[D]==B and sys.platform not in('unix','win32'):
		try:j=os.uname();A[D]=j.release
		except (S,I,TypeError):pass
	for (k,l,n) in [(h,h,'const'),(b,b,'FAT'),(i,'pybricks.hubs','EV3Brick')]:
		try:o=__import__(l,E,E,n);A[N]=k;del o;break
		except (Q,T):pass
	if A[N]==i:A['release']='2.0.0'
	if A[N]==X:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if G in A and A[G]:
		P=int(A[G]);Y=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][P>>10]
		if Y:A[c]=Y
		A[G]='v{}.{}'.format(P&255,P>>8&3)
	A[Z]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def f(info,board_descr,filename):
	with W(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[K]=D;return P
	return H
def get_root():
	try:A=os.getcwd()
	except (F,I):A=L
	B=A
	for B in [A,'/sd','/flash',G,L]:
		try:C=os.stat(B);break
		except F:continue
	return B
def g(filename):
	try:
		if os.stat(filename)[0]>>14:return P
		return H
	except F:return H
def h():sys.exit(1)
def read_path():
	path=B
	if M(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:h()
	elif M(sys.argv)==2:h()
	return path
def i():
	try:A=bytes('abc',encoding='utf8');B=i.__module__;return H
	except (j,I):return P
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_boot_fat','_coap','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','ak8963','apa102','apa106','array','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','cmath','collections','crypto','cryptolib','curl','dht','display','display_driver_utils','ds18x20','encoder','errno','esp','esp32','espidf','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','json','lcd160cr','lodepng',u,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','math','microWebSocket','microWebSrv','microWebTemplate',X,'mip','motor','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pcf85063a','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform',w,b,'pye','qrcode','queue','random','requests','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','struct',t,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',D,'websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or i():
	try:logging.basicConfig(level=logging.INFO)
	except l:pass
	if not g('no_auto_stubber.txt'):
		try:C.threshold(4*1024);C.enable()
		except BaseException:pass
		main()