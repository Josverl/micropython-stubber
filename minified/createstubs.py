f='micropython'
e='esp32'
d='pycom'
c='pyb'
b='{}/{}'
a='logging'
Z='sys'
Y=IndexError
X=NameError
W=print
V=NotImplementedError
T='platform'
S='machine'
P=True
M='_'
O='version'
N=len
K=KeyError
J=ImportError
I='.'
H=AttributeError
G=''
F=False
B='/'
C=None
E=OSError
import sys,gc as D,uos as os
from utime import sleep_us as g
from ujson import dumps as L
__version__='1.7.2'
h=2
i=2
try:from machine import resetWDT as Q
except J:
	def Q():0
class Stubber:
	def __init__(A,path=C,firmware_id=C):
		F=firmware_id;C=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise V('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();D.collect()
		if F:A._fwid=str(F).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=D.mem_free()
		if C:
			if C.endswith(B):C=C[:-1]
		else:C=get_root()
		A.path='{}/stubs/{}'.format(C,A.flat_fwid).replace('//',B)
		try:R(C+B)
		except E:pass
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(I,item_instance):
		B=item_instance;A=[];F=[]
		for C in dir(B):
			try:E=getattr(B,C);A.append((C,repr(E),repr(type(E)),E))
			except H as G:F.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(C,B,G))
		A=[B for B in A if not B[0].startswith(M)];D.collect();return A,F
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		D.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:return F
		if A in C.excluded:return F
		G='{}/{}.py'.format(C.path,A.replace(I,B));D.collect();J=D.mem_free();W('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(A,G,J));H=F
		try:H=C.create_module_stub(A,G)
		except E:return F
		D.collect();return H
	def create_module_stub(H,module_name,file_name=C):
		L=file_name;A=module_name
		if A in H.problematic:return F
		if L is C:L=H.path+B+A.replace(I,M)+'.py'
		if B in A:A=A.replace(B,I)
		N=C
		try:N=__import__(A,C,C,'*')
		except J:return F
		R(L)
		with open(L,'w')as O:Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,H.info,__version__);O.write(Q);O.write('from typing import Any\n\n');H.write_object_stub(O,N,A,G)
		H._report.append({'module':A,'file':L})
		if not A in['os',Z,a,'gc']:
			try:del N
			except (E,K):pass
			try:del sys.modules[A]
			except K:pass
		D.collect();return P
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='tuple';c='list';b='dict';a='{0}{1} = {2} # type: {3}\n';Z='bound_method';Y='Any';P=in_class;O=object_expr;M='Exception';I=fp;A=indent;D.collect()
		if O in L.problematic:return
		R,e=L.get_obj_attributes(O)
		for (C,J,F,S) in R:
			if C in['classmethod','staticmethod','BaseException',M]:continue
			Q();g(1)
			if F=="<class 'type'>"and N(A)<=i*4:
				T=G;U=C.endswith(M)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if U:T=M
				B='\n{}class {}({}):\n'.format(A,C,T)
				if U:B+=A+'    ...\n'
				else:B+=A+'    def __init__(self, *argv, **kwargs) -> None:\n';B+=A+'        ...\n\n'
				I.write(B);L.write_object_stub(I,S,'{0}.{1}'.format(obj_name,C),A+'    ',P+1)
			elif'method'in F or'function'in F:
				V=Y;W=G
				if P>0:W='self, '
				if Z in F or Z in J:B='{}@classmethod\n'.format(A);B+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(A,C,V)
				else:B='{}def {}({}*args, **kwargs) -> {}:\n'.format(A,C,W,V)
				B+=A+'    ...\n\n';I.write(B)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				H=F[8:-2];B=G
				if H in['str','int','float','bool','bytearray','bytes']:B=a.format(A,C,J,H)
				elif H in[b,c,d]:f={b:'{}',c:'[]',d:'()'};B=a.format(A,C,f[H],H)
				else:
					if not H in['object','set','frozenset']:H=Y
					B='{0}{1} : {2} ## {3} = {4}\n'.format(A,C,H,F,J)
				I.write(B)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(A+C+' # type: Any\n')
		del R;del e
		try:del C,J,F,S
		except (E,K,X):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,M)
		return A
	def clean(D,path=C):
		A=path
		if A is C:A=D.path
		W('Clean/remove files in folder: {}'.format(A))
		try:F=os.listdir(A)
		except (E,H):return
		for G in F:
			B=b.format(A,G)
			try:os.remove(B)
			except E:
				try:D.clean(B);os.rmdir(B)
				except E:pass
	def report(B,filename='modules.json'):
		H='firmware';C=',\n';I=b.format(B.path,filename);D.collect()
		try:
			with open(I,'w')as A:
				A.write('{');A.write(L({H:B.info})[1:-1]);A.write(C);A.write(L({'stubber':{O:__version__},'stubtype':H})[1:-1]);A.write(C);A.write('"modules" :[\n');G=P
				for J in B._report:
					if G:G=F
					else:A.write(C)
					A.write(L(J))
				A.write('\n]}')
			K=B._start_free-D.mem_free()
		except E:pass
def R(path):
	C=path;A=F=0
	while A!=-1:
		A=C.find(B,F)
		if A!=-1:
			if A==0:D=C[0]
			else:D=C[0:A]
			try:I=os.stat(D)
			except E as G:
				if G.args[0]==h:
					try:os.mkdir(D)
					except E as H:raise H
				else:raise G
		F=A+1
def _info():
	k=' on ';j='0.0.0';i='port';h='nodename';g='name';W='mpy';V='unknown';R='-';Q='sysname';M='v';L='build';F='family';D='ver';B='release';X=sys.implementation.name;Z=sys.platform if not sys.platform.startswith(c)else'stm32';A={g:X,B:j,O:j,L:G,Q:V,h:V,S:V,F:X,T:Z,i:Z,D:G}
	try:A[B]=I.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[g]=sys.implementation.name;A[W]=sys.implementation.mpy
	except H:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[h]=E.nodename;A[B]=E.release;A[S]=E.machine
			if k in E.version:
				P=E.version.split(k)[0]
				if A[Q]=='esp8266':
					if R in P:a=P.split(R)[0]
					else:a=P
					A[O]=A[B]=a.lstrip(M)
				try:A[L]=P.split(R)[1]
				except Y:pass
		except (Y,H,TypeError):pass
	try:from pycopy import const as U;A[F]='pycopy';del U
	except (J,K):pass
	try:from pycom import FAT as U;A[F]=d;del U
	except (J,K):pass
	if A[T]=='esp32_LoBo':A[F]='loboris';A[i]=e
	elif A[Q]=='ev3':
		A[F]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except J:pass
	if A[B]:A[D]=M+A[B].lstrip(M)
	if A[F]==f:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[D]=A[B][:-2]
		else:A[D]=A[B]
		if A[L]!=G and N(A[L])<4:A[D]+=R+A[L]
	if A[D][0]!=M:A[D]=M+A[D]
	if W in A:
		l=int(A[W]);b=[C,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][l>>10]
		if b:A['arch']=b
	return A
def get_root():
	try:A=os.getcwd()
	except (E,H):A=I
	C=A
	for C in [A,'/sd','/flash',B,I]:
		try:D=os.stat(C);break
		except E as F:continue
	return C
def A():sys.exit(1)
def read_path():
	B=G
	if N(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):B=sys.argv[2]
		else:A()
	elif N(sys.argv)==2:A()
	return B
def U():
	try:A=bytes('abc',encoding='utf8');B=U.__module__;return F
	except (V,H):return P
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['_OTA','_coap','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/server','ak8963','apa102','apa106','array','binascii','btree','cmath','crypto','curl','dht','display','display_driver_utils','ds18x20','errno','esp',e,'espidf','flashbdev','framebuf','freesans20','fs_driver','functools','gc','gsm','hashlib','heapq','ili9341','ili9XXX','imagetools','inisetup','json','lcd160cr','lodepng',a,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip',S,'math','microWebSocket','microWebSrv','microWebTemplate',f,'mpu6500','mpu9250','neopixel','network','ntptime','onewire','os',T,c,d,'pye','queue','random','requests','rp2','rtch','select','socket','ssd1306','ssh','ssl','stm','struct',Z,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib','websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];D.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or U():
	try:logging.basicConfig(level=logging.INFO)
	except X:pass
	main()