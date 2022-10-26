p='micropython'
o='esp32'
n='pycom'
m='pyb'
l='{}/{}'
k='logging'
j='sys'
i='method'
h='function'
g='bool'
f='str'
e='float'
d='int'
c=NameError
b=sorted
a=NotImplementedError
W='platform'
V='machine'
U='_'
T='dict'
R='list'
Q='tuple'
S=IndexError
P=repr
O='version'
M=True
N=ImportError
L=len
K=KeyError
J='.'
I=AttributeError
F=False
H=''
G=print
B='/'
D=None
C=OSError
import gc as E,sys,uos as os
from ujson import dumps as X
__version__='1.9.11'
q=2
r=2
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise a('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();E.collect()
		if D:A._fwid=str(D).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if path:
			if path.endswith(B):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',B)
		try:Y(path+B)
		except C:G('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;A=[];J=[]
		for G in dir(F):
			try:
				B=getattr(F,G)
				try:C=P(type(B)).split("'")[1]
				except S:C=H
				if C in(d,e,f,g,Q,R,T):D=1
				elif C in(h,i):D=2
				elif C in'class':D=3
				else:D=4
				A.append((G,P(B),P(type(B)),B,D))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(G,F,K))
		A=b([B for B in A if not B[0].startswith(U)],key=lambda x:x[4]);E.collect();return A,J
	def add_modules(A,modules):A.modules=b(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(D,module_name):
		A=module_name
		if A in D.problematic:return F
		if A in D.excluded:return F
		H='{}/{}.py'.format(D.path,A.replace(J,B));E.collect();K=E.mem_free();G('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,H,K));I=F
		try:I=D.create_module_stub(A,H)
		except C:return F
		E.collect();return I
	def create_module_stub(I,module_name,file_name=D):
		L=file_name;A=module_name
		if A in I.problematic:return F
		if L is D:L=I.path+B+A.replace(J,U)+'.py'
		if B in A:A=A.replace(B,J)
		O=D
		try:O=__import__(A,D,D,'*')
		except N:G('{}Skip module: {:<25} {:<79}'.format('\x1b[1A',A,'Module not found.'));return F
		Y(L)
		with open(L,'w')as P:Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,I._fwid,I.info,__version__);P.write(Q);P.write('from typing import Any\n\n');I.write_object_stub(P,O,A,H)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(A,L.replace('\\',B)))
		if not A in['os',j,k,'gc']:
			try:del O
			except (C,K):pass
			try:del sys.modules[A]
			except K:pass
		E.collect();return M
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		k='{0}{1} = {2} # type: {3}\n';j='bound_method';b='Any';U=in_class;S=object_expr;P='Exception';I=fp;B=indent;E.collect()
		if S in N.problematic:return
		V,O=N.get_obj_attributes(S)
		if O:G(O)
		for (D,M,F,W,m) in V:
			if D in['classmethod','staticmethod','BaseException',P]:continue
			if F=="<class 'type'>"and L(B)<=r*4:
				X=H;Y=D.endswith(P)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if Y:X=P
				A='\n{}class {}({}):\n'.format(B,D,X)
				if Y:A+=B+'    ...\n';I.write(A);return
				I.write(A);N.write_object_stub(I,W,'{0}.{1}'.format(obj_name,D),B+'    ',U+1);A=B+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=B+'        ...\n\n';I.write(A)
			elif i in F or h in F:
				Z=b;a=H
				if U>0:a='self, '
				if j in F or j in M:A='{}@classmethod\n'.format(B);A+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(B,D,Z)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(B,D,a,Z)
				A+=B+'    ...\n\n';I.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				J=F[8:-2];A=H
				if J in[f,d,e,g,'bytearray','bytes']:A=k.format(B,D,M,J)
				elif J in[T,R,Q]:l={T:'{}',R:'[]',Q:'()'};A=k.format(B,D,l[J],J)
				else:
					if not J in['object','set','frozenset']:J=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(B,D,J,F,M)
				I.write(A)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(B+D+' # type: Any\n')
		del V;del O
		try:del D,M,F,W
		except (C,K,c):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,U)
		return A
	def clean(B,path=D):
		if path is D:path=B.path
		G('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except (C,I):return
		for F in E:
			A=l.format(path,F)
			try:os.remove(A)
			except C:
				try:B.clean(A);os.rmdir(A)
				except C:pass
	def report(B,filename='modules.json'):
		I='firmware';D=',\n';G('Created stubs for {} modules on board {}\nPath: {}'.format(L(B._report),B._fwid,B.path));J=l.format(B.path,filename);E.collect()
		try:
			with open(J,'w')as A:
				A.write('{');A.write(X({I:B.info})[1:-1]);A.write(D);A.write(X({'stubber':{O:__version__},'stubtype':I})[1:-1]);A.write(D);A.write('"modules" :[\n');H=M
				for K in B._report:
					if H:H=F
					else:A.write(D)
					A.write(K)
				A.write('\n]}')
			N=B._start_free-E.mem_free()
		except C:G('Failed to create the report.')
def Y(path):
	H='failed to create folder {}';A=E=0
	while A!=-1:
		A=path.find(B,E)
		if A!=-1:
			if A==0:D=path[0]
			else:D=path[0:A]
			try:J=os.stat(D)
			except C as F:
				if F.args[0]==q:
					try:os.mkdir(D)
					except C as I:G(H.format(D));raise I
				else:G(H.format(D));raise F
		E=A+1
def _info():
	g=' on ';f='0.0.0';e='port';d='nodename';c='name';X='mpy';U='unknown';R='-';Q='sysname';M='v';G='build';F='family';C='ver';B='release';Y=sys.implementation.name;Z=sys.platform if not sys.platform.startswith(m)else'stm32';A={c:Y,B:f,O:f,G:H,Q:U,d:U,V:U,F:Y,W:Z,e:Z,C:H}
	try:A[B]=J.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[c]=sys.implementation.name;A[X]=sys.implementation.mpy
	except I:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E[0];A[d]=E[1];A[B]=E[2];A[V]=E[4]
			if g in E[3]:
				P=E[3].split(g)[0]
				if A[Q]=='esp8266':
					if R in P:a=P.split(R)[0]
					else:a=P
					A[O]=A[B]=a.lstrip(M)
				try:A[G]=P.split(R)[1]
				except S:pass
		except (S,I,TypeError):pass
	try:from pycopy import const as T;A[F]='pycopy';del T
	except (N,K):pass
	try:from pycom import FAT as T;A[F]=n;del T
	except (N,K):pass
	if A[W]=='esp32_LoBo':A[F]='loboris';A[e]=o
	elif A[Q]=='ev3':
		A[F]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except N:pass
	if A[B]:A[C]=M+A[B].lstrip(M)
	if A[F]==p:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[G]!=H and L(A[G])<4:A[C]+=R+A[G]
	if A[C][0]!=M:A[C]=M+A[C]
	if X in A:
		h=int(A[X]);b=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][h>>10]
		if b:A['arch']=b
	return A
def get_root():
	try:A=os.getcwd()
	except (C,I):A=J
	D=A
	for D in [A,'/sd','/flash',B,J]:
		try:E=os.stat(D);break
		except C:continue
	return D
def s(filename):
	try:os.stat(filename);return M
	except C:return F
def A():sys.exit(1)
def read_path():
	path=H
	if L(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):path=sys.argv[2]
		else:A()
	elif L(sys.argv)==2:A()
	return path
def Z():
	try:A=bytes('abc',encoding='utf8');B=Z.__module__;return F
	except (a,I):return M
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['WM8960','_OTA','_boot_fat','_coap','_flash_control_OTA','_main_pybytes','_mqtt','_mqtt_core','_msg_handl','_onewire','_periodical_pin','_pybytes','_pybytes_ca','_pybytes_config','_pybytes_config_reader','_pybytes_connection','_pybytes_constants','_pybytes_debug','_pybytes_library','_pybytes_machine_learning','_pybytes_main','_pybytes_protocol','_pybytes_pyconfig','_pybytes_pymesh_config','_rp2','_terminal','_thread','_uasyncio','_urequest','aioble/__init__','aioble/central','aioble/client','aioble/core','aioble/device','aioble/l2cap','aioble/peripheral','aioble/security','aioble/server','ak8963','apa102','apa106','array','binascii','bluetooth','btree','cmath','crypto','cryptolib','curl','dht','display','display_driver_utils','ds18x20','errno','esp',o,'espidf','flashbdev','framebuf','freesans20','fs_driver','functools','gc','gsm','hashlib','heapq','ili9341','ili9XXX','imagetools','inisetup','json','lcd160cr','lodepng',k,'lsm6dsox','lv_colors','lv_utils','lvgl','lwip',V,'math','microWebSocket','microWebSrv','microWebTemplate',p,'mip','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os',W,m,n,'pye','queue','random','requests','rp2','rtch','select','socket','ssd1306','ssh','ssl','stm','struct',j,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','uasyncio/tasks','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/__init__','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib','websocket','websocket_helper','wipy','writer','xpt2046','ymodem','zephyr','zlib'];E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or Z():
	try:logging.basicConfig(level=logging.INFO)
	except c:pass
	if not s('no_auto_stubber.txt'):main()