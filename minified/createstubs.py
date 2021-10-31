f='{}/{}'
e='__init__'
d='sys'
c='logging'
b='esp32'
a=NameError
Z=print
Y=staticmethod
X=IndexError
W=NotImplementedError
R=True
Q=False
P='version'
N='machine'
O='_thread'
M=len
K='_'
J=KeyError
I=ImportError
H=''
G=AttributeError
F='.'
E='/'
C=OSError
B=None
import sys,gc as D,uos as os
from utime import sleep_us as g
from ujson import dumps as L
S='1.4.1'
T=2
h=2
try:from machine import resetWDT as U
except I:
	def U():0
class Stubber:
	def __init__(A,path=B,firmware_id=B):
		F=firmware_id;B=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise W('MicroPython 1.13.0 cannot be stubbed')
		except G:pass
		A._report=[];A.info=A._info()
		if F:A._fwid=str(F).lower()
		else:A._fwid='{family}-{port}-{ver}'.format(**A.info).lower()
		A._start_free=D.mem_free()
		if B:
			if B.endswith(E):B=B[:-1]
		else:B=A.get_root()
		A.path='{}/stubs/{}'.format(B,A.flat_fwid).replace('//',E)
		try:A.ensure_folder(B+E)
		except C:pass
		A.problematic=['upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=['_onewire',O,'_uasyncio','ak8963','apa102','apa106','array','binascii','btree','builtins','cmath','collections','crypto','curl','dht','display','display_driver_utils','ds18x20','errno','esp',b,'espidf','flashbdev','framebuf','freesans20','fs_driver','functools','gc','gsm','hashlib','heapq','ili9XXX','imagetools','inisetup','io','json','lcd160cr','lodepng',c,'lv_colors','lv_utils','lvgl','lwip',N,'math','microWebSocket','microWebSrv','microWebTemplate','micropython','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pyb','pycom','pye','queue','random','re','requests','rtch','select','socket','ssd1306','ssh','ssl','stm','struct',d,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/robust','umqtt/simple','uos','upip','upip_utarfile','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib','websocket','websocket_helper','writer','xpt2046','ymodem','zlib'];A.include_nested=D.mem_free()>3200
	@Y
	def _info():
		a='loboris';Z='0.0.0';Y='port';W='platform';V='nodename';U='name';Q='mpy';O='unknown';M='sysname';L='build';K='ver';E='family';C='release';R=sys.implementation.name;S=sys.platform;A={U:R,C:Z,P:Z,L:H,M:O,V:O,N:O,E:R,W:S,Y:S,K:H}
		try:A[C]=F.join([str(A)for A in sys.implementation.version]);A[P]=A[C];A[U]=sys.implementation.name;A[Q]=sys.implementation.mpy
		except G:pass
		if sys.platform not in('unix','win32'):
			try:
				D=os.uname();A[M]=D.sysname;A[V]=D.nodename;A[C]=D.release;A[N]=D.machine
				if' on 'in D.version:
					c=D.version.split('on ')[0]
					try:A[L]=c.split('-')[1]
					except X:pass
			except (X,G,TypeError):pass
		try:from pycopy import const;A[E]='pycopy';del const
		except (I,J):pass
		if A[W]=='esp32_LoBo':A[E]=a;A[Y]=b
		elif A[M]=='ev3':
			A[E]='ev3-pybricks';A[C]='1.0.0'
			try:from pybricks.hubs import EV3Brick;A[C]='2.0.0'
			except I:pass
		if A[C]:A[K]='v'+A[C]
		if A[E]!=a:
			if A[C]and A[C]>='1.10.0'and A[C].endswith('.0'):A[K]=A[C][:-2]
			else:A[K]=A[C]
			if A[L]!=H:A[K]+='-'+A[L]
		if Q in A:
			d=int(A[Q]);T=[B,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][d>>10]
			if T:A['arch']=T
		return A
	def get_obj_attributes(L,obj):
		J="Couldn't get attribute '{}' from object '{}', Err: {}";C=obj;E=[];F=[];A=B
		try:
			for A in dir(C):
				try:H=getattr(C,A);E.append((A,repr(H),repr(type(H)),H))
				except G as I:F.append(J.format(A,C,I))
		except G as I:F.append(J.format(A,C,I))
		E=[A for A in E if not(A[0].startswith(K)and A[0]!=e)];D.collect();return E,F
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		A.modules=[B for B in A.modules if E in B]+[B for B in A.modules if E not in B];D.collect()
		for B in A.modules:
			if A.include_nested:A.include_nested=D.mem_free()>3200
			if B.startswith(K)and B!=O:continue
			if B in A.problematic:continue
			if B in A.excluded:continue
			G='{}/{}.py'.format(A.path,B.replace(F,E));D.collect();H=D.mem_free();Z('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(B,G,H))
			try:A.create_module_stub(B,G)
			except C:pass
			D.collect()
	def create_module_stub(G,module_name,file_name=B):
		L=file_name;A=module_name
		if A.startswith(K)and A!=O:return
		if A in G.problematic:return
		if L is B:L=G.path+E+A.replace(F,K)+'.py'
		if E in A:
			A=A.replace(E,F)
			if not G.include_nested:return
		T=Q;N=B
		try:N=__import__(A,B,B,'*')
		except I:
			T=R
			if not F in A:return
		if T and F in A:
			U=A.split(F)
			for V in range(1,M(U)):
				W=F.join(U[0:V])
				try:X=__import__(W);del X
				except (I,J):pass
			try:N=__import__(A,B,B,'*')
			except I:return
		G.ensure_folder(L)
		with open(L,'w')as P:Y='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,G._fwid,G.info,S);P.write(Y);P.write('from typing import Any\n\n');G.write_object_stub(P,N,A,H);G._report.append({'module':A,'file':L})
		if not A in['os',d,c,'gc']:
			try:del N
			except (C,J):pass
			try:del sys.modules[A]
			except J:pass
			D.collect()
	def write_object_stub(I,fp,object_expr,obj_name,indent,in_class=0):
		X='tuple';W='list';V='dict';T='{0}{1} = {2} # type: {3}\n';S='Any';N=object_expr;G=fp;A=indent
		if N in I.problematic:return
		O,Y=I.get_obj_attributes(N)
		for (D,P,E,Q) in O:
			U();g(1);K=["<class 'function'>","<class 'bound_method'>"]
			if E=="<class 'type'>"and M(A)<=h*4:B='\n'+A+'class '+D+':\n';B+=A+"    ''\n";G.write(B);I.write_object_stub(G,Q,'{0}.{1}'.format(obj_name,D),A+'    ',in_class+1)
			elif E in K:
				L=S;R=H
				if E==K[0]:
					R='self, '
					if D==e:L='None'
				if E==K[1]:B='{}@classmethod\n'.format(A);B+='{}def {}(cls) -> {}:\n'.format(A,D,L)
				else:B='{}def {}({}*args) -> {}:\n'.format(A,D,R,L)
				B+=A+'    ...\n\n';G.write(B)
			elif E.startswith("<class '"):
				F=E[8:-2];B=H
				if F in['str','int','float','bool','bytearray','bytes']:B=T.format(A,D,P,F)
				elif F in[V,W,X]:Z={V:'{}',W:'[]',X:'()'};B=T.format(A,D,Z[F],F)
				else:
					if not F in['object','set','frozenset']:F=S
					B='{0}{1}: {2}\n'.format(A,D,F)
				G.write(B)
			else:G.write("# all other, type = '{0}'\n".format(E));G.write(A+D+' = Any\n')
		del O;del Y
		try:del D,P,E,Q
		except (C,J,a):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,K)
		return A
	def clean(E,path=B):
		A=path
		if A is B:A=E.path
		Z('Clean/remove files in folder: {}'.format(A))
		try:F=os.listdir(A)
		except (C,G):return
		for H in F:
			D=f.format(A,H)
			try:os.remove(D)
			except C:
				try:E.clean(D);os.rmdir(D)
				except C:pass
	def report(B,filename='modules.json'):
		E=',\n';G=f.format(B.path,filename);D.collect()
		try:
			with open(G,'w')as A:
				A.write('{');A.write(L({'firmware':B.info})[1:-1]);A.write(E);A.write(L({'stubber':{P:S}})[1:-1]);A.write(E);A.write('"modules" :[\n');F=R
				for H in B._report:
					if F:F=Q
					else:A.write(E)
					A.write(L(H))
				A.write('\n]}')
			I=B._start_free-D.mem_free()
		except C:pass
	def ensure_folder(I,path):
		B=path;A=F=0
		while A!=-1:
			A=B.find(E,F)
			if A!=-1:
				if A==0:D=B[0]
				else:D=B[0:A]
				try:J=os.stat(D)
				except C as G:
					if G.args[0]==T:
						try:os.mkdir(D)
						except C as H:raise H
					else:raise G
			F=A+1
	@Y
	def get_root():
		try:A='/flash';D=os.stat(A)
		except C as B:
			if B.args[0]==T:
				try:A=os.getcwd()
				except (C,G):A=F
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
def V():
	try:A=bytes('abc',encoding='utf8');B=V.__module__;return Q
	except (W,G):return R
def main():
	try:logging.basicConfig(level=logging.INFO)
	except a:pass
	stubber=Stubber(path=read_path());stubber.clean();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or V():main()