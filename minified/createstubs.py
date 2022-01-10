f='micropython'
e='esp32'
d='{}/{}'
c='logging'
b='sys'
a='upip'
Z=IndexError
Y=NameError
X=print
W=NotImplementedError
S='machine'
R=True
Q='_thread'
P='__init__'
O='version'
N=len
M=KeyError
L=ImportError
J='_'
I='.'
G=False
H=''
F=AttributeError
E='/'
D=None
C=OSError
import sys,gc as B,uos as os
from utime import sleep_us as g
from ujson import dumps as K
__version__='1.5.1'
h=2
i=2
try:from machine import resetWDT as T
except L:
	def T():0
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		G=firmware_id;D=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise W('MicroPython 1.13.0 cannot be stubbed')
		except F:pass
		A._report=[];A.info=_info();B.collect()
		if G:A._fwid=str(G).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=B.mem_free()
		if D:
			if D.endswith(E):D=D[:-1]
		else:D=get_root()
		A.path='{}/stubs/{}'.format(D,A.flat_fwid).replace('//',E)
		try:U(D+E)
		except C:pass
		A.problematic=[a,'upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(I,item_instance):
		C=item_instance;A=[];G=[]
		for D in dir(C):
			try:E=getattr(C,D);A.append((D,repr(E),repr(type(E)),E))
			except F as H:G.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(D,C,H))
		A=[B for B in A if not(B[0].startswith(J)and B[0]!=P)];B.collect();return A,G
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(D,module_name):
		A=module_name
		if A.startswith(J)and A!=Q:return G
		if A in D.problematic:return G
		if A in D.excluded:return G
		F='{}/{}.py'.format(D.path,A.replace(I,E));B.collect();H=B.mem_free();X('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(A,F,H))
		try:D.create_module_stub(A,F)
		except C:return G
		B.collect();return R
	def create_module_stub(F,module_name,file_name=D):
		G=file_name;A=module_name
		if A.startswith(J)and A!=Q:return
		if A in F.problematic:return
		if G is D:G=F.path+E+A.replace(I,J)+'.py'
		if E in A:A=A.replace(E,I)
		K=D
		try:K=__import__(A,D,D,'*')
		except L:return
		U(G)
		with open(G,'w')as N:O='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,F._fwid,F.info,__version__);N.write(O);N.write('from typing import Any\n\n');F.write_object_stub(N,K,A,H)
		F._report.append({'module':A,'file':G})
		if not A in['os',b,c,'gc']:
			try:del K
			except (C,M):pass
			try:del sys.modules[A]
			except M:pass
		B.collect()
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		b='tuple';a='list';Z='dict';X='{0}{1} = {2} # type: {3}\n';W='bound_method';V='Any';Q=in_class;O=object_expr;I=fp;A=indent;B.collect()
		if O in K.problematic:return
		R,c=K.get_obj_attributes(O)
		for (D,J,F,S) in R:
			if D in['classmethod','staticmethod']:continue
			T();g(1)
			if F=="<class 'type'>"and N(A)<=i*4:E='\n'+A+'class '+D+':\n';E+=A+"    ''\n";I.write(E);K.write_object_stub(I,S,'{0}.{1}'.format(obj_name,D),A+'    ',Q+1)
			elif'method'in F or'function'in F or D==P:
				L=V;U=H
				if Q>0:
					U='self, '
					if D==P:L='None'
				if W in F or W in J:E='{}@classmethod\n'.format(A);E+='{}def {}(cls, *args) -> {}:\n'.format(A,D,L)
				else:E='{}def {}({}*args) -> {}:\n'.format(A,D,U,L)
				E+=A+'    ...\n\n';I.write(E)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				G=F[8:-2];E=H
				if G in['str','int','float','bool','bytearray','bytes']:E=X.format(A,D,J,G)
				elif G in[Z,a,b]:d={Z:'{}',a:'[]',b:'()'};E=X.format(A,D,d[G],G)
				else:
					if not G in['object','set','frozenset']:G=V
					E='{0}{1} : {2} ## {3} = {4}\n'.format(A,D,G,F,J)
				I.write(E)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(A+D+' # type: Any\n')
		del R;del c
		try:del D,J,F,S
		except (C,M,Y):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,J)
		return A
	def clean(E,path=D):
		A=path
		if A is D:A=E.path
		X('Clean/remove files in folder: {}'.format(A))
		try:G=os.listdir(A)
		except (C,F):return
		for H in G:
			B=d.format(A,H)
			try:os.remove(B)
			except C:
				try:E.clean(B);os.rmdir(B)
				except C:pass
	def report(D,filename='modules.json'):
		H='firmware';E=',\n';I=d.format(D.path,filename);B.collect()
		try:
			with open(I,'w')as A:
				A.write('{');A.write(K({H:D.info})[1:-1]);A.write(E);A.write(K({'stubber':{O:__version__},'stubtype':H})[1:-1]);A.write(E);A.write('"modules" :[\n');F=R
				for J in D._report:
					if F:F=G
					else:A.write(E)
					A.write(K(J))
				A.write('\n]}')
			L=D._start_free-B.mem_free()
		except C:pass
def U(path):
	B=path;A=F=0
	while A!=-1:
		A=B.find(E,F)
		if A!=-1:
			if A==0:D=B[0]
			else:D=B[0:A]
			try:I=os.stat(D)
			except C as G:
				if G.args[0]==h:
					try:os.mkdir(D)
					except C as H:raise H
				else:raise G
		F=A+1
def _info():
	h=' on ';g='0.0.0';d='port';c='platform';b='nodename';a='name';U='mpy';T='unknown';R='-';Q='sysname';K='v';J='family';G='build';C='ver';B='release';V=sys.implementation.name;W=sys.platform;A={a:V,B:g,O:g,G:H,Q:T,b:T,S:T,J:V,c:W,d:W,C:H}
	try:A[B]=I.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[a]=sys.implementation.name;A[U]=sys.implementation.mpy
	except F:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[b]=E.nodename;A[B]=E.release;A[S]=E.machine
			if h in E.version:
				P=E.version.split(h)[0]
				if A[Q]=='esp8266':
					if R in P:X=P.split(R)[0]
					else:X=P
					A[O]=A[B]=X.lstrip(K)
				try:A[G]=P.split(R)[1]
				except Z:pass
		except (Z,F,TypeError):pass
	try:from pycopy import const;A[J]='pycopy';del const
	except (L,M):pass
	if A[c]=='esp32_LoBo':A[J]='loboris';A[d]=e
	elif A[Q]=='ev3':
		A[J]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except L:pass
	if A[B]:A[C]=K+A[B].lstrip(K)
	if A[J]==f:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[G]!=H and N(A[G])<4:A[C]+=R+A[G]
	if A[C][0]!=K:A[C]=K+A[C]
	if U in A:
		i=int(A[U]);Y=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][i>>10]
		if Y:A['arch']=Y
	return A
def get_root():
	try:A=os.getcwd()
	except (C,F):A=I
	for B in [A,'/sd','/flash',E,I]:
		try:D=os.stat(B);break
		except C as G:continue
	return B
def A():sys.exit(1)
def read_path():
	B=H
	if N(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):B=sys.argv[2]
		else:A()
	elif N(sys.argv)==2:A()
	return B
def V():
	try:A=bytes('abc',encoding='utf8');B=V.__module__;return G
	except (W,F):return R
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['_onewire',Q,'_uasyncio','ak8963','apa102','apa106','array','binascii','btree','builtins','cmath','collections','crypto','curl','dht','display','display_driver_utils','ds18x20','errno','esp',e,'espidf','flashbdev','framebuf','freesans20','fs_driver','functools','gc','gsm','hashlib','heapq','ili9XXX','imagetools','inisetup','io','json','lcd160cr','lodepng',c,'lv_colors','lv_utils','lvgl','lwip',S,'math','microWebSocket','microWebSrv','microWebTemplate',f,'mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pyb','pycom','pye','queue','random','re','requests','rtch','select','socket','ssd1306','ssh','ssl','stm','struct',b,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/robust','umqtt/simple','uos',a,'upip_utarfile','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib','websocket','websocket_helper','writer','xpt2046','ymodem','zlib'];B.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or V():
	try:logging.basicConfig(level=logging.INFO)
	except Y:pass
	main()