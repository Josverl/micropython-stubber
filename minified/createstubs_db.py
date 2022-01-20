a='utf8'
Z='{}/{}'
Y=IndexError
X=NameError
W=print
V=NotImplementedError
R='__init__'
P='version'
O=True
L='_'
N=KeyError
M=ImportError
K=open
J='.'
I=len
H=AttributeError
G=''
F=False
B='/'
C=None
D=OSError
import sys,gc as E,uos as os
from utime import sleep_us as f
from ujson import dumps as Q
__version__='1.5.3'
b=2
g=2
try:from machine import resetWDT as S
except M:
	def S():0
class Stubber:
	def __init__(A,path=C,firmware_id=C):
		F=firmware_id;C=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise V('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();E.collect()
		if F:A._fwid=str(F).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if C:
			if C.endswith(B):C=C[:-1]
		else:C=get_root()
		A.path='{}/stubs/{}'.format(C,A.flat_fwid).replace('//',B)
		try:T(C+B)
		except D:pass
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(I,item_instance):
		B=item_instance;A=[];F=[]
		for C in dir(B):
			try:D=getattr(B,C);A.append((C,repr(D),repr(type(D)),D))
			except H as G:F.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(C,B,G))
		A=[B for B in A if not(B[0].startswith(L)and B[0]!=R)];E.collect();return A,F
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(C,module_name):
		A=module_name
		if A.startswith(L)and A!='_thread':return F
		if A in C.problematic:return F
		if A in C.excluded:return F
		G='{}/{}.py'.format(C.path,A.replace(J,B));E.collect();H=E.mem_free();W('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(A,G,H))
		try:C.create_module_stub(A,G)
		except D:return F
		E.collect();return O
	def create_module_stub(F,module_name,file_name=C):
		H=file_name;A=module_name
		if A in F.problematic:return
		if H is C:H=F.path+B+A.replace(J,L)+'.py'
		if B in A:A=A.replace(B,J)
		I=C
		try:I=__import__(A,C,C,'*')
		except M:return
		T(H)
		with K(H,'w')as O:P='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,F._fwid,F.info,__version__);O.write(P);O.write('from typing import Any\n\n');F.write_object_stub(O,I,A,G)
		F._report.append({'module':A,'file':H})
		if not A in['os','sys','logging','gc']:
			try:del I
			except (D,N):pass
			try:del sys.modules[A]
			except N:pass
		E.collect()
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		e='tuple';d='list';c='dict';b='{0}{1} = {2} # type: {3}\n';a='bound_method';Z='Any';Q=in_class;P=object_expr;O='Exception';J=fp;A=indent;E.collect()
		if P in L.problematic:return
		T,h=L.get_obj_attributes(P)
		for (C,K,F,U) in T:
			if C in['classmethod','staticmethod','BaseException',O]:continue
			S();f(1)
			if F=="<class 'type'>"and I(A)<=g*4:
				V=G;W=C.endswith(O)or C.endswith('Error')
				if W:V=O
				B='\n{}class {}({}):\n'.format(A,C,V);B+=A+"    ''\n"
				if not W:B+=A+'    def __init__(self, *argv, **kwargs) -> None:\n';B+=A+"        ''\n";B+=A+'        ...\n'
				J.write(B);L.write_object_stub(J,U,'{0}.{1}'.format(obj_name,C),A+'    ',Q+1)
			elif'method'in F or'function'in F or C==R:
				M=Z;Y=G
				if Q>0:
					Y='self, '
					if C==R:M='None'
				if a in F or a in K:B='{}@classmethod\n'.format(A);B+='{}def {}(cls, *args) -> {}:\n'.format(A,C,M)
				else:B='{}def {}({}*args) -> {}:\n'.format(A,C,Y,M)
				B+=A+'    ...\n\n';J.write(B)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				H=F[8:-2];B=G
				if H in['str','int','float','bool','bytearray','bytes']:B=b.format(A,C,K,H)
				elif H in[c,d,e]:i={c:'{}',d:'[]',e:'()'};B=b.format(A,C,i[H],H)
				else:
					if not H in['object','set','frozenset']:H=Z
					B='{0}{1} : {2} ## {3} = {4}\n'.format(A,C,H,F,K)
				J.write(B)
			else:J.write("# all other, type = '{0}'\n".format(F));J.write(A+C+' # type: Any\n')
		del T;del h
		try:del C,K,F,U
		except (D,N,X):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,L)
		return A
	def clean(E,path=C):
		A=path
		if A is C:A=E.path
		W('Clean/remove files in folder: {}'.format(A))
		try:F=os.listdir(A)
		except (D,H):return
		for G in F:
			B=Z.format(A,G)
			try:os.remove(B)
			except D:
				try:E.clean(B);os.rmdir(B)
				except D:pass
	def report(B,filename='modules.json'):
		H='firmware';C=',\n';I=Z.format(B.path,filename);E.collect()
		try:
			with K(I,'w')as A:
				A.write('{');A.write(Q({H:B.info})[1:-1]);A.write(C);A.write(Q({'stubber':{P:__version__},'stubtype':H})[1:-1]);A.write(C);A.write('"modules" :[\n');G=O
				for J in B._report:
					if G:G=F
					else:A.write(C)
					A.write(Q(J))
				A.write('\n]}')
			L=B._start_free-E.mem_free()
		except D:pass
def T(path):
	C=path;A=F=0
	while A!=-1:
		A=C.find(B,F)
		if A!=-1:
			if A==0:E=C[0]
			else:E=C[0:A]
			try:I=os.stat(E)
			except D as G:
				if G.args[0]==b:
					try:os.mkdir(E)
					except D as H:raise H
				else:raise G
		F=A+1
def _info():
	f=' on ';e='0.0.0';d='port';c='platform';b='machine';a='nodename';Z='name';T='mpy';S='unknown';R='-';Q='sysname';L='v';K='family';F='build';D='ver';B='release';U=sys.implementation.name;V=sys.platform;A={Z:U,B:e,P:e,F:G,Q:S,a:S,b:S,K:U,c:V,d:V,D:G}
	try:A[B]=J.join([str(A)for A in sys.implementation.version]);A[P]=A[B];A[Z]=sys.implementation.name;A[T]=sys.implementation.mpy
	except H:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[a]=E.nodename;A[B]=E.release;A[b]=E.machine
			if f in E.version:
				O=E.version.split(f)[0]
				if A[Q]=='esp8266':
					if R in O:W=O.split(R)[0]
					else:W=O
					A[P]=A[B]=W.lstrip(L)
				try:A[F]=O.split(R)[1]
				except Y:pass
		except (Y,H,TypeError):pass
	try:from pycopy import const;A[K]='pycopy';del const
	except (M,N):pass
	if A[c]=='esp32_LoBo':A[K]='loboris';A[d]='esp32'
	elif A[Q]=='ev3':
		A[K]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except M:pass
	if A[B]:A[D]=L+A[B].lstrip(L)
	if A[K]=='micropython':
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[D]=A[B][:-2]
		else:A[D]=A[B]
		if A[F]!=G and I(A[F])<4:A[D]+=R+A[F]
	if A[D][0]!=L:A[D]=L+A[D]
	if T in A:
		g=int(A[T]);X=[C,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][g>>10]
		if X:A['arch']=X
	return A
def get_root():
	try:A=os.getcwd()
	except (D,H):A=J
	C=A
	for C in [A,'/sd','/flash',B,J]:
		try:E=os.stat(C);break
		except D as F:continue
	return C
def A():sys.exit(1)
def read_path():
	B=G
	if I(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):B=sys.argv[2]
		else:A()
	elif I(sys.argv)==2:A()
	return B
def U():
	try:A=bytes('abc',encoding=a);B=U.__module__;return F
	except (V,H):return O
def c():
	M=b'todo';L='.db';G='modulelist';import machine as N,btree
	try:C=K(G+L,'r+b');E=O
	except D:C=K(G+L,'w+b');E=F
	stubber=Stubber(path=read_path())
	if not E:stubber.clean()
	A=btree.open(C)
	if not E or I(list(A.keys()))==0:
		for P in K(G+'.txt'):
			B=P.strip()
			if I(B)and B[0]!='#':A[B]=M
		A.flush()
	for B in A.keys():
		if A[B]!=M:continue
		H=F
		try:H=stubber.create_one_stub(B.decode(a))
		except MemoryError:A.close();C.close();N.reset()
		if H:J='good, I guess'
		else:J=b'skipped'
		A[B]=J;A.flush()
	A.close();C.close()
if __name__=='__main__'or U():
	try:logging.basicConfig(level=logging.INFO)
	except X:pass
	c()