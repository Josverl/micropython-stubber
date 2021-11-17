f='esp32'
e='{}/{}'
d='logging'
c='sys'
b='upip'
a=IndexError
Z=NameError
Y=print
X=NotImplementedError
S='machine'
R=True
Q='_thread'
P='__init__'
N='version'
M=len
L=KeyError
K=ImportError
J='.'
I='_'
G=False
H=''
F=AttributeError
E='/'
D=None
C=OSError
import sys,gc as B,uos as os
from utime import sleep_us as g
from ujson import dumps as O
__version__='1.4.3'
T=2
h=2
try:from machine import resetWDT as U
except K:
	def U():0
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		G=firmware_id;D=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise X('MicroPython 1.13.0 cannot be stubbed')
		except F:pass
		A._report=[];A.info=_info();B.collect()
		if G:A._fwid=str(G).lower()
		else:A._fwid='{family}-{port}-{ver}'.format(**A.info).lower()
		A._start_free=B.mem_free()
		if D:
			if D.endswith(E):D=D[:-1]
		else:D=get_root()
		A.path='{}/stubs/{}'.format(D,A.flat_fwid).replace('//',E)
		try:V(D+E)
		except C:pass
		A.problematic=[b,'upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(K,item_instance):
		J="Couldn't get attribute '{}' from object '{}', Err: {}";A=item_instance;C=[];E=[]
		try:
			for D in dir(A):
				try:G=getattr(A,D);C.append((D,repr(G),repr(type(G)),G))
				except F as H:E.append(J.format(D,A,H))
		except F as H:E.append(J.format(D,A,H))
		C=[A for A in C if not(A[0].startswith(I)and A[0]!=P)];B.collect();return C,E
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(D,module_name):
		A=module_name
		if A.startswith(I)and A!=Q:return G
		if A in D.problematic:return G
		if A in D.excluded:return G
		F='{}/{}.py'.format(D.path,A.replace(J,E));B.collect();H=B.mem_free();Y('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(A,F,H))
		try:D.create_module_stub(A,F)
		except C:return G
		B.collect();return R
	def create_module_stub(F,module_name,file_name=D):
		G=file_name;A=module_name
		if A.startswith(I)and A!=Q:return
		if A in F.problematic:return
		if G is D:G=F.path+E+A.replace(J,I)+'.py'
		if E in A:A=A.replace(E,J)
		M=D
		try:M=__import__(A,D,D,'*')
		except K:return
		V(G)
		with open(G,'w')as N:O='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,F._fwid,F.info,__version__);N.write(O);N.write('from typing import Any\n\n');F.write_object_stub(N,M,A,H)
		F._report.append({'module':A,'file':G})
		if not A in['os',c,d,'gc']:
			try:del M
			except (C,L):pass
			try:del sys.modules[A]
			except L:pass
		B.collect()
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		b='tuple';a='list';Y='dict';X='{0}{1} = {2} # type: {3}\n';W='bound_method';V='Any';Q=in_class;O=object_expr;I=fp;A=indent;B.collect()
		if O in K.problematic:return
		R,c=K.get_obj_attributes(O)
		for (D,J,F,S) in R:
			if D in['classmethod','staticmethod']:continue
			U();g(1)
			if F=="<class 'type'>"and M(A)<=h*4:E='\n'+A+'class '+D+':\n';E+=A+"    ''\n";I.write(E);K.write_object_stub(I,S,'{0}.{1}'.format(obj_name,D),A+'    ',Q+1)
			elif'method'in F or'function'in F or D==P:
				N=V;T=H
				if Q>0:
					T='self, '
					if D==P:N='None'
				if W in F or W in J:E='{}@classmethod\n'.format(A);E+='{}def {}(cls, *args) -> {}:\n'.format(A,D,N)
				else:E='{}def {}({}*args) -> {}:\n'.format(A,D,T,N)
				E+=A+'    ...\n\n';I.write(E)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				G=F[8:-2];E=H
				if G in['str','int','float','bool','bytearray','bytes']:E=X.format(A,D,J,G)
				elif G in[Y,a,b]:d={Y:'{}',a:'[]',b:'()'};E=X.format(A,D,d[G],G)
				else:
					if not G in['object','set','frozenset']:G=V
					E='{0}{1} : {2} ## {3} = {4}\n'.format(A,D,G,F,J)
				I.write(E)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(A+D+' # type: Any\n')
		del R;del c
		try:del D,J,F,S
		except (C,L,Z):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,I)
		return A
	def clean(E,path=D):
		A=path
		if A is D:A=E.path
		Y('Clean/remove files in folder: {}'.format(A))
		try:G=os.listdir(A)
		except (C,F):return
		for H in G:
			B=e.format(A,H)
			try:os.remove(B)
			except C:
				try:E.clean(B);os.rmdir(B)
				except C:pass
	def report(D,filename='modules.json'):
		E=',\n';H=e.format(D.path,filename);B.collect()
		try:
			with open(H,'w')as A:
				A.write('{');A.write(O({'firmware':D.info})[1:-1]);A.write(E);A.write(O({'stubber':{N:__version__}})[1:-1]);A.write(E);A.write('"modules" :[\n');F=R
				for I in D._report:
					if F:F=G
					else:A.write(E)
					A.write(O(I))
				A.write('\n]}')
			J=D._start_free-B.mem_free()
		except C:pass
def V(path):
	B=path;A=F=0
	while A!=-1:
		A=B.find(E,F)
		if A!=-1:
			if A==0:D=B[0]
			else:D=B[0:A]
			try:I=os.stat(D)
			except C as G:
				if G.args[0]==T:
					try:os.mkdir(D)
					except C as H:raise H
				else:raise G
		F=A+1
def _info():
	h='loboris';g=' on ';e='0.0.0';d='port';c='platform';b='nodename';Z='name';U='v';T='mpy';R='unknown';Q='-';P='sysname';I='ver';G='family';E='build';B='release';V=sys.implementation.name;W=sys.platform;A={Z:V,B:e,N:e,E:H,P:R,b:R,S:R,G:V,c:W,d:W,I:H}
	try:A[B]=J.join([str(A)for A in sys.implementation.version]);A[N]=A[B];A[Z]=sys.implementation.name;A[T]=sys.implementation.mpy
	except F:pass
	if sys.platform not in('unix','win32'):
		try:
			C=os.uname();A[P]=C.sysname;A[b]=C.nodename;A[B]=C.release;A[S]=C.machine
			if g in C.version:
				O=C.version.split(g)[0]
				if A[P]=='esp8266':
					if Q in O:X=O.split(Q)[0]
					else:X=O
					A[N]=A[B]=X.lstrip(U)
				try:A[E]=O.split(Q)[1]
				except a:pass
		except (a,F,TypeError):pass
	try:from pycopy import const;A[G]='pycopy';del const
	except (K,L):pass
	if A[c]=='esp32_LoBo':A[G]=h;A[d]=f
	elif A[P]=='ev3':
		A[G]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except K:pass
	if A[B]:A[I]=U+A[B].lstrip(U)
	if A[G]!=h:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[I]=A[B][:-2]
		else:A[I]=A[B]
		if A[E]!=H and M(A[E])<4:A[I]+=Q+A[E]
	if T in A:
		i=int(A[T]);Y=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][i>>10]
		if Y:A['arch']=Y
	return A
def get_root():
	A='/flash'
	try:D=os.stat(A)
	except C as B:
		if B.args[0]==T:
			try:A=os.getcwd()
			except (C,F):A=J
		else:A=E
	return A
def A():sys.exit(1)
def read_path():
	B=H
	if M(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):B=sys.argv[2]
		else:A()
	elif M(sys.argv)==2:A()
	return B
def W():
	try:A=bytes('abc',encoding='utf8');B=W.__module__;return G
	except (X,F):return R
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['_onewire',Q,'_uasyncio','ak8963','apa102','apa106','array','binascii','btree','builtins','cmath','collections','crypto','curl','dht','display','display_driver_utils','ds18x20','errno','esp',f,'espidf','flashbdev','framebuf','freesans20','fs_driver','functools','gc','gsm','hashlib','heapq','ili9XXX','imagetools','inisetup','io','json','lcd160cr','lodepng',d,'lv_colors','lv_utils','lvgl','lwip',S,'math','microWebSocket','microWebSrv','microWebTemplate','micropython','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pyb','pycom','pye','queue','random','re','requests','rtch','select','socket','ssd1306','ssh','ssl','stm','struct',c,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/robust','umqtt/simple','uos',b,'upip_utarfile','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib','websocket','websocket_helper','writer','xpt2046','ymodem','zlib'];B.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or W():
	try:logging.basicConfig(level=logging.INFO)
	except Z:pass
	main()