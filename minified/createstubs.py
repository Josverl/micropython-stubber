c='micropython'
b='esp32'
a='{}/{}'
Z='logging'
Y='sys'
X=IndexError
W=NameError
V=print
U=NotImplementedError
S='machine'
P=True
K='_'
O='version'
N=len
M=KeyError
L=ImportError
I=False
H='.'
F=AttributeError
G=''
B='/'
C=None
E=OSError
import sys,gc as D,uos as os
from utime import sleep_us as e
from ujson import dumps as J
__version__='1.5.4'
d=2
f=2
try:from machine import resetWDT as Q
except L:
	def Q():0
class Stubber:
	def __init__(A,path=C,firmware_id=C):
		G=firmware_id;C=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise U('MicroPython 1.13.0 cannot be stubbed')
		except F:pass
		A._report=[];A.info=_info();D.collect()
		if G:A._fwid=str(G).lower()
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
		B=item_instance;A=[];G=[]
		for C in dir(B):
			try:E=getattr(B,C);A.append((C,repr(E),repr(type(E)),E))
			except F as H:G.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(C,B,H))
		A=[B for B in A if not B[0].startswith(K)];D.collect();return A,G
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		D.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:return I
		if A in C.excluded:return I
		F='{}/{}.py'.format(C.path,A.replace(H,B));D.collect();G=D.mem_free();V('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(A,F,G))
		try:C.create_module_stub(A,F)
		except E:return I
		D.collect();return P
	def create_module_stub(F,module_name,file_name=C):
		I=file_name;A=module_name
		if A in F.problematic:return
		if I is C:I=F.path+B+A.replace(H,K)+'.py'
		if B in A:A=A.replace(B,H)
		J=C
		try:J=__import__(A,C,C,'*')
		except L:return
		R(I)
		with open(I,'w')as N:O='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,F._fwid,F.info,__version__);N.write(O);N.write('from typing import Any\n\n');F.write_object_stub(N,J,A,G)
		F._report.append({'module':A,'file':I})
		if not A in['os',Y,Z,'gc']:
			try:del J
			except (E,M):pass
			try:del sys.modules[A]
			except M:pass
		D.collect()
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='tuple';c='list';b='dict';a='{0}{1} = {2} # type: {3}\n';Z='bound_method';Y='Any';P=in_class;O=object_expr;L='Exception';I=fp;A=indent;D.collect()
		if O in K.problematic:return
		R,g=K.get_obj_attributes(O)
		for (C,J,F,S) in R:
			if C in['classmethod','staticmethod','BaseException',L]:continue
			Q();e(1)
			if F=="<class 'type'>"and N(A)<=f*4:
				T=G;U=C.endswith(L)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if U:T=L
				B='\n{}class {}({}):\n'.format(A,C,T);B+=A+"    ''\n"
				if not U:B+=A+'    def __init__(self, *argv, **kwargs) -> None:\n';B+=A+"        ''\n";B+=A+'        ...\n'
				I.write(B);K.write_object_stub(I,S,'{0}.{1}'.format(obj_name,C),A+'    ',P+1)
			elif'method'in F or'function'in F:
				V=Y;X=G
				if P>0:X='self, '
				if Z in F or Z in J:B='{}@classmethod\n'.format(A);B+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(A,C,V)
				else:B='{}def {}({}*args, **kwargs) -> {}:\n'.format(A,C,X,V)
				B+=A+'    ...\n\n';I.write(B)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				H=F[8:-2];B=G
				if H in['str','int','float','bool','bytearray','bytes']:B=a.format(A,C,J,H)
				elif H in[b,c,d]:h={b:'{}',c:'[]',d:'()'};B=a.format(A,C,h[H],H)
				else:
					if not H in['object','set','frozenset']:H=Y
					B='{0}{1} : {2} ## {3} = {4}\n'.format(A,C,H,F,J)
				I.write(B)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(A+C+' # type: Any\n')
		del R;del g
		try:del C,J,F,S
		except (E,M,W):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,K)
		return A
	def clean(D,path=C):
		A=path
		if A is C:A=D.path
		V('Clean/remove files in folder: {}'.format(A))
		try:G=os.listdir(A)
		except (E,F):return
		for H in G:
			B=a.format(A,H)
			try:os.remove(B)
			except E:
				try:D.clean(B);os.rmdir(B)
				except E:pass
	def report(B,filename='modules.json'):
		G='firmware';C=',\n';H=a.format(B.path,filename);D.collect()
		try:
			with open(H,'w')as A:
				A.write('{');A.write(J({G:B.info})[1:-1]);A.write(C);A.write(J({'stubber':{O:__version__},'stubtype':G})[1:-1]);A.write(C);A.write('"modules" :[\n');F=P
				for K in B._report:
					if F:F=I
					else:A.write(C)
					A.write(J(K))
				A.write('\n]}')
			L=B._start_free-D.mem_free()
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
				if G.args[0]==d:
					try:os.mkdir(D)
					except E as H:raise H
				else:raise G
		F=A+1
def _info():
	h=' on ';g='0.0.0';f='port';e='platform';d='nodename';a='name';U='mpy';T='unknown';R='-';Q='sysname';K='v';J='family';I='build';D='ver';B='release';V=sys.implementation.name;W=sys.platform;A={a:V,B:g,O:g,I:G,Q:T,d:T,S:T,J:V,e:W,f:W,D:G}
	try:A[B]=H.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[a]=sys.implementation.name;A[U]=sys.implementation.mpy
	except F:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[d]=E.nodename;A[B]=E.release;A[S]=E.machine
			if h in E.version:
				P=E.version.split(h)[0]
				if A[Q]=='esp8266':
					if R in P:Y=P.split(R)[0]
					else:Y=P
					A[O]=A[B]=Y.lstrip(K)
				try:A[I]=P.split(R)[1]
				except X:pass
		except (X,F,TypeError):pass
	try:from pycopy import const;A[J]='pycopy';del const
	except (L,M):pass
	if A[e]=='esp32_LoBo':A[J]='loboris';A[f]=b
	elif A[Q]=='ev3':
		A[J]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except L:pass
	if A[B]:A[D]=K+A[B].lstrip(K)
	if A[J]==c:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[D]=A[B][:-2]
		else:A[D]=A[B]
		if A[I]!=G and N(A[I])<4:A[D]+=R+A[I]
	if A[D][0]!=K:A[D]=K+A[D]
	if U in A:
		i=int(A[U]);Z=[C,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][i>>10]
		if Z:A['arch']=Z
	return A
def get_root():
	try:A=os.getcwd()
	except (E,F):A=H
	C=A
	for C in [A,'/sd','/flash',B,H]:
		try:D=os.stat(C);break
		except E as G:continue
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
def T():
	try:A=bytes('abc',encoding='utf8');B=T.__module__;return I
	except (U,F):return P
def main():A='apa106';stubber=Stubber(path=read_path());stubber.clean();stubber.modules=['_onewire','_thread','_rp2','_uasyncio','ak8963','apa102',A,'array','binascii','btree','builtins','cmath','collections','crypto','curl','dht','display','display_driver_utils','ds18x20','errno','esp',b,'espidf','flashbdev','framebuf','freesans20','fs_driver','functools','gc','gsm','hashlib','heapq','ili9XXX','imagetools','inisetup','io','json','lcd160cr','lodepng',Z,'lv_colors','lv_utils','lvgl','lwip',S,'math','microWebSocket','microWebSrv','microWebTemplate',c,'mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pyb','pycom','pye','queue','random','re','requests','rtch','select','socket','ssd1306','ssh','ssl','stm','struct',Y,'time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/robust','umqtt/simple','uos','uplatform','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib','websocket','websocket_helper','writer','xpt2046','ymodem','zlib','rp2',A];D.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or T():
	try:logging.basicConfig(level=logging.INFO)
	except W:pass
	main()