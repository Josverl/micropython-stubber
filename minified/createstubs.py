o='micropython'
n='esp32'
m='pycom'
l='pyb'
k='{}/{}'
j='logging'
i='sys'
h='method'
g='function'
f='bool'
e='str'
d='float'
c='int'
b=NameError
a=sorted
Z=NotImplementedError
W='platform'
V='machine'
U='_'
T='dict'
R='list'
Q='tuple'
S=IndexError
P=repr
O='version'
L=True
N=len
M=ImportError
J=KeyError
I='.'
H=AttributeError
F=False
G=''
B='/'
D=None
C=OSError
import gc as E,sys,uos as os
from ujson import dumps as K
__version__='1.9.11'
p=2
q=2
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		F=firmware_id;D=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise Z('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();E.collect()
		if F:A._fwid=str(F).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if D:
			if D.endswith(B):D=D[:-1]
		else:D=get_root()
		A.path='{}/stubs/{}'.format(D,A.flat_fwid).replace('//',B)
		try:X(D+B)
		except C:pass
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;A=[];J=[]
		for I in dir(F):
			try:
				B=getattr(F,I)
				try:C=P(type(B)).split("'")[1]
				except S:C=G
				if C in(c,d,e,f,Q,R,T):D=1
				elif C in(g,h):D=2
				elif C in'class':D=3
				else:D=4
				A.append((I,P(B),P(type(B)),B,D))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(I,F,K))
		A=a([B for B in A if not B[0].startswith(U)],key=lambda x:x[4]);E.collect();return A,J
	def add_modules(A,modules):A.modules=a(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(A,module_name):
		D=module_name
		if D in A.problematic:return F
		if D in A.excluded:return F
		H='{}/{}.py'.format(A.path,D.replace(I,B));E.collect();J=E.mem_free();G=F
		try:G=A.create_module_stub(D,H)
		except C:return F
		E.collect();return G
	def create_module_stub(H,module_name,file_name=D):
		K=file_name;A=module_name
		if A in H.problematic:return F
		if K is D:K=H.path+B+A.replace(I,U)+'.py'
		if B in A:A=A.replace(B,I)
		N=D
		try:N=__import__(A,D,D,'*')
		except M:return F
		X(K)
		with open(K,'w')as O:P='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,H.info,__version__);O.write(P);O.write('from typing import Any\n\n');H.write_object_stub(O,N,A,G)
		H._report.append({'module':A,'file':K})
		if not A in['os',i,j,'gc']:
			try:del N
			except (C,J):pass
			try:del sys.modules[A]
			except J:pass
		E.collect();return L
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		i='{0}{1} = {2} # type: {3}\n';a='bound_method';Z='Any';P=in_class;O=object_expr;M='Exception';H=fp;B=indent;E.collect()
		if O in L.problematic:return
		S,j=L.get_obj_attributes(O)
		for (D,K,F,U,l) in S:
			if D in['classmethod','staticmethod','BaseException',M]:continue
			if F=="<class 'type'>"and N(B)<=q*4:
				V=G;W=D.endswith(M)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if W:V=M
				A='\n{}class {}({}):\n'.format(B,D,V)
				if W:A+=B+'    ...\n';H.write(A);return
				H.write(A);L.write_object_stub(H,U,'{0}.{1}'.format(obj_name,D),B+'    ',P+1);A=B+'    def __init__(self, *argv, **kwargs) -> None: ##\n';A+=B+'        ...\n\n';H.write(A)
			elif h in F or g in F:
				X=Z;Y=G
				if P>0:Y='self, '
				if a in F or a in K:A='{}@classmethod\n'.format(B);A+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(B,D,X)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(B,D,Y,X)
				A+=B+'    ...\n\n';H.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				I=F[8:-2];A=G
				if I in[e,c,d,f,'bytearray','bytes']:A=i.format(B,D,K,I)
				elif I in[T,R,Q]:k={T:'{}',R:'[]',Q:'()'};A=i.format(B,D,k[I],I)
				else:
					if not I in['object','set','frozenset']:I=Z
					A='{0}{1} : {2} ## {3} = {4}\n'.format(B,D,I,F,K)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(F));H.write(B+D+' # type: Any\n')
		del S;del j
		try:del D,K,F,U
		except (C,J,b):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,U)
		return A
	def clean(E,path=D):
		A=path
		if A is D:A=E.path
		print('Clean/remove files in folder: {}'.format(A))
		try:F=os.listdir(A)
		except (C,H):return
		for G in F:
			B=k.format(A,G)
			try:os.remove(B)
			except C:
				try:E.clean(B);os.rmdir(B)
				except C:pass
	def report(B,filename='modules.json'):
		H='firmware';D=',\n';I=k.format(B.path,filename);E.collect()
		try:
			with open(I,'w')as A:
				A.write('{');A.write(K({H:B.info})[1:-1]);A.write(D);A.write(K({'stubber':{O:__version__},'stubtype':H})[1:-1]);A.write(D);A.write('"modules" :[\n');G=L
				for J in B._report:
					if G:G=F
					else:A.write(D)
					A.write(K(J))
				A.write('\n]}')
			M=B._start_free-E.mem_free()
		except C:pass
def X(path):
	D=path;A=F=0
	while A!=-1:
		A=D.find(B,F)
		if A!=-1:
			if A==0:E=D[0]
			else:E=D[0:A]
			try:I=os.stat(E)
			except C as G:
				if G.args[0]==p:
					try:os.mkdir(E)
					except C as H:raise H
				else:raise G
		F=A+1
def _info():
	g=' on ';f='0.0.0';e='port';d='nodename';c='name';X='mpy';U='unknown';R='-';Q='sysname';L='v';K='build';F='family';C='ver';B='release';Y=sys.implementation.name;Z=sys.platform if not sys.platform.startswith(l)else'stm32';A={c:Y,B:f,O:f,K:G,Q:U,d:U,V:U,F:Y,W:Z,e:Z,C:G}
	try:A[B]=I.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[c]=sys.implementation.name;A[X]=sys.implementation.mpy
	except H:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[d]=E.nodename;A[B]=E.release;A[V]=E.machine
			if g in E.version:
				P=E.version.split(g)[0]
				if A[Q]=='esp8266':
					if R in P:a=P.split(R)[0]
					else:a=P
					A[O]=A[B]=a.lstrip(L)
				try:A[K]=P.split(R)[1]
				except S:pass
		except (S,H,TypeError):pass
	try:from pycopy import const as T;A[F]='pycopy';del T
	except (M,J):pass
	try:from pycom import FAT as T;A[F]=m;del T
	except (M,J):pass
	if A[W]=='esp32_LoBo':A[F]='loboris';A[e]=n
	elif A[Q]=='ev3':
		A[F]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except M:pass
	if A[B]:A[C]=L+A[B].lstrip(L)
	if A[F]==o:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[K]!=G and N(A[K])<4:A[C]+=R+A[K]
	if A[C][0]!=L:A[C]=L+A[C]
	if X in A:
		h=int(A[X]);b=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][h>>10]
		if b:A['arch']=b
	return A
def get_root():
	try:A=os.getcwd()
	except (C,H):A=I
	D=A
	for D in [A,'/sd','/flash',B,I]:
		try:E=os.stat(D);break
		except C:continue
	return D
def r(filename):
	try:os.stat(filename);return L
	except C:return F
def A():sys.exit(1)
def read_path():
	B=G
	if N(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):B=sys.argv[2]
		else:A()
	elif N(sys.argv)==2:A()
	return B
def Y():
	try:A=bytes('abc',encoding='utf8');B=Y.__module__;return F
	except (Z,H):return L
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['_OTA','_coap','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/server','ak8963','apa102','apa106','array','binascii','btree','cmath','crypto','curl','dht','display','display_driver_utils','ds18x20','errno','esp',n,'espidf','flashbdev','framebuf','freesans20','fs_driver','functools','gc','gsm','hashlib','heapq','ili9341','ili9XXX','imagetools','inisetup','json','lcd160cr','lodepng',j,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip',V,'math','microWebSocket','microWebSrv','microWebTemplate',o,'mpu6500','mpu9250','neopixel','network','ntptime','onewire','os',W,l,m,'pye','queue','random','requests','rp2','rtch','select','socket','ssd1306','ssh','ssl','stm','struct',i,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib','websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or Y():
	try:logging.basicConfig(level=logging.INFO)
	except b:pass
	if not r('no_auto_stubber.txt'):main()