y='pyb'
x='stubber'
w='{}/{}'
v='logging'
u='sys'
t='method'
s='function'
r='bool'
q='str'
p='float'
o='int'
n=NameError
m=sorted
l=NotImplementedError
d='pycom'
c=',\n'
b='dict'
a='list'
Z='tuple'
Y='micropython'
X=open
W=repr
U='cpu'
T='_'
S=len
R=KeyError
Q=IndexError
P=dir
O=print
N=ImportError
M='with'
L='family'
K=True
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
from ujson import dumps as e
try:from machine import reset
except N:pass
try:from collections import OrderedDict as f
except N:from ucollections import OrderedDict as f
__version__='v1.16.2'
z=2
A0=2
A1=[I,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise l('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();C.collect()
		if B:A._fwid=B.lower()
		elif A.info[L]==Y:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:g(path+G)
		except F:O('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		I=item_instance;D=[];J=[]
		for A in P(I):
			if A.startswith(T)and not A in L.modules:continue
			try:
				E=getattr(I,A)
				try:F=W(type(E)).split("'")[1]
				except Q:F=B
				if F in{o,p,q,r,Z,a,b}:G=1
				elif F in{s,t}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,W(E),W(type(E)),E,G))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,I,K))
			except MemoryError as K:sleep(1);reset()
		D=m([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);C.collect();return D,J
	def add_modules(A,modules):A.modules=m(set(A.modules)|set(modules))
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
		if H is E:O=D.replace(I,T)+'.py';H=J.path+G+O
		else:O=H.split(G)[-1]
		if G in D:D=D.replace(G,I)
		L=E
		try:L=__import__(D,E,E,'*');S=C.mem_free()
		except N:return A
		g(H)
		with X(H,'w')as M:P=str(J.info).replace('OrderedDict(',B).replace('})','}');Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,J._fwid,P,__version__);M.write(Q);M.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(M,L,D,B)
		J._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os',u,v,'gc'}:
			try:del L
			except(F,R):pass
			try:del sys.modules[D]
			except R:pass
		C.collect();return K
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';Y='Incomplete';P=in_class;N=object_expr;M='Exception';H=fp;D=indent;C.collect()
		if N in K.problematic:return
		Q,L=K.get_obj_attributes(N)
		if L:O(L)
		for(E,J,G,T,f)in Q:
			if E in['classmethod','staticmethod','BaseException',M]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and S(D)<=A0*4:
				U=B;V=E.endswith(M)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=M
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),D+'    ',P+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif any(A in G for A in[t,s,'closure']):
				W=Y;X=B
				if P>0:X='self, '
				if c in G or c in J:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,X,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[q,o,p,r,'bytearray','bytes']:A=d.format(D,E,J,I)
				elif I in[b,a,Z]:e={b:'{}',a:'[]',Z:'()'};A=d.format(D,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=Y
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,I,G,J)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+E+' # type: Incomplete\n')
		del Q;del L
		try:del E,J,G,T
		except(F,R,n):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,T)
		return A
	def clean(B,path=E):
		if path is E:path=B.path
		try:os.stat(path);C=os.listdir(path)
		except(F,H):return
		for D in C:
			A=w.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(B,filename='modules.json'):
		G=w.format(B.path,filename);C.collect()
		try:
			with X(G,'w')as D:
				B.write_json_header(D);E=K
				for H in B._report:B.write_json_node(D,H,E);E=A
				B.write_json_end(D)
			I=B._start_free-C.mem_free()
		except F:O('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(e({A:B.info})[1:-1]);f.write(c);f.write(e({x:{D:__version__},'stubtype':A})[1:-1]);f.write(c);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(c)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def g(path):
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
def V(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	e='ev3-pybricks';c='pycopy';b='unix';a='win32';Z='arch';X='ver';K='mpy';G='port';F='build';A=f({L:sys.implementation.name,D:B,F:B,X:B,G:sys.platform,J:'UNKNOWN',U:B,K:B,Z:B})
	if A[G].startswith(y):A[G]='stm32'
	elif A[G]==a:A[G]='windows'
	elif A[G]=='linux':A[G]=b
	try:A[D]=I.join([str(A)for A in sys.implementation.version]).rstrip(I)
	except H:pass
	try:T=sys.implementation._machine if'_machine'in P(sys.implementation)else os.uname().machine;A[J]=M.join(T.split(M)[:-1]).strip();A[U]=T.split(M)[-1].strip();A[K]=sys.implementation._mpy if'_mpy'in P(sys.implementation)else sys.implementation.mpy if K in P(sys.implementation)else B
	except(H,Q):pass
	C.collect();A2(A);C.collect()
	try:
		A[F]=V(os.uname()[3])
		if not A[F]:A[F]=V(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=V(sys.version.split(';')[1])
	except(H,Q):pass
	if A[F]and S(A[F])>5:A[F]=B
	if A[D]==B and sys.platform not in(b,a):
		try:g=os.uname();A[D]=g.release
		except(Q,H,TypeError):pass
	for(h,i,j)in[(c,c,'const'),(d,d,'FAT'),(e,'pybricks.hubs','EV3Brick')]:
		try:k=__import__(i,E,E,j);A[L]=h;del k;break
		except(N,R):pass
	if A[L]==e:A['release']='2.0.0'
	if A[L]==Y:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if K in A and A[K]:
		O=int(A[K]);W=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][O>>10]
		if W:A[Z]=W
		A[K]='v{}.{}'.format(O&255,O>>8&3)
	A[X]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def A2(info,desc=B):
	G='with ';D=info;E=A
	for F in[A+'/board_info.csv'for A in A1]:
		if i(F):
			B=desc or D[J].strip()
			if h(D,B,F):E=K;break
			if M in B:
				B=B.split(M)[0].strip()
				if h(D,B,F):E=K;break
	if not E:
		B=desc or D[J].strip()
		if G+D[U].upper()in B:B=B.split(G+D[U].upper())[0].strip()
		D[J]=B
	D[J]=D[J].replace(' ',T);C.collect()
def h(info,board_descr,filename):
	with X(filename,'r')as C:
		while 1:
			B=C.readline()
			if not B:break
			D,E=B.split(',')[0].strip(),B.split(',')[1].strip()
			if D==board_descr:info[J]=E;return K
	return A
def get_root():
	try:A=os.getcwd()
	except(F,H):A=I
	B=A
	for B in[A,'/sd','/flash',G,I]:
		try:C=os.stat(B);break
		except F:continue
	return B
def i(filename):
	try:
		if os.stat(filename)[0]>>14:return K
		return A
	except F:return A
def j():sys.exit(1)
def read_path():
	path=B
	if S(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:j()
	elif S(sys.argv)==2:j()
	return path
def k():
	try:B=bytes('abc',encoding='utf8');C=k.__module__;return A
	except(l,H):return K
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_asyncio','_boot_fat','_coap','_espnow','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','adcfft','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','aioespnow','ak8963','apa102','apa106','argparse','array','asyncio/__init__','asyncio/core','asyncio/event','asyncio/funcs','asyncio/lock','asyncio/stream','binascii','bluetooth','breakout_as7262','breakout_bh1745','breakout_bme280','breakout_bme68x','breakout_bmp280','breakout_dotmatrix','breakout_encoder','breakout_icp10125','breakout_ioexpander','breakout_ltr559','breakout_matrix11x7','breakout_mics6814','breakout_msa301','breakout_paa5100','breakout_pmw3901','breakout_potentiometer','breakout_rgbmatrix5x5','breakout_rtc','breakout_scd41','breakout_sgp30','breakout_trackball','breakout_vl53l5cx','btree','cmath','collections','crypto','cryptolib','curl','deflate','dht','display','display_driver_utils','ds18x20','encoder','errno','esp','esp32','espidf','espnow','ffi','flashbdev','framebuf','freesans20','fs_driver','functools','galactic','gc','gfx_pack','gsm','hashlib','heapq','hub75','ili9341','ili9XXX','imagetools','inisetup','interstate75','io','jpegdec','json','lcd160cr','lodepng',v,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip','machine','math','microWebSocket','microWebSrv','microWebTemplate',Y,'mip','mip/__init__','mip/__main__','motor','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pcf85063a','picoexplorer','picographics','picokeypad','picoscroll','picounicorn','picowireless','pimoroni','pimoroni_bus','pimoroni_i2c','plasma','platform',y,d,'pye','qrcode','queue','random','requests','requests/__init__','rp2','rtch','samd','select','servo','socket','ssd1306','ssh','ssl','stm','struct',u,'termios','time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib',D,'websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or k():
	try:A3=logging.getLogger(x);logging.basicConfig(level=logging.INFO)
	except n:pass
	if not i('no_auto_stubber.txt'):
		try:C.threshold(4*1024);C.enable()
		except BaseException:pass
		main()