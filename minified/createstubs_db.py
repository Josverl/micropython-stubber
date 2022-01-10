b='utf8'
a='{}/{}'
Z='_thread'
Y=IndexError
X=NameError
W=print
V=NotImplementedError
R='__init__'
P='version'
O=True
N=KeyError
M=ImportError
L='_'
K=open
J='.'
I=len
H=''
G=AttributeError
F=False
D='/'
C=None
A=OSError
import sys,gc as E,uos as os
from utime import sleep_us as c
from ujson import dumps as Q
__version__='1.5.1'
d=2
e=2
try:from machine import resetWDT as S
except M:
	def S():0
class Stubber:
	def __init__(B,path=C,firmware_id=C):
		F=firmware_id;C=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise V('MicroPython 1.13.0 cannot be stubbed')
		except G:pass
		B._report=[];B.info=_info();E.collect()
		if F:B._fwid=str(F).lower()
		else:B._fwid='{family}-{ver}-{port}'.format(**B.info).lower()
		B._start_free=E.mem_free()
		if C:
			if C.endswith(D):C=C[:-1]
		else:C=get_root()
		B.path='{}/stubs/{}'.format(C,B.flat_fwid).replace('//',D)
		try:T(C+D)
		except A:pass
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[]
	def get_obj_attributes(I,item_instance):
		B=item_instance;A=[];F=[]
		for C in dir(B):
			try:D=getattr(B,C);A.append((C,repr(D),repr(type(D)),D))
			except G as H:F.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(C,B,H))
		A=[B for B in A if not(B[0].startswith(L)and B[0]!=R)];E.collect();return A,F
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(C,module_name):
		B=module_name
		if B.startswith(L)and B!=Z:return F
		if B in C.problematic:return F
		if B in C.excluded:return F
		G='{}/{}.py'.format(C.path,B.replace(J,D));E.collect();H=E.mem_free();W('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(B,G,H))
		try:C.create_module_stub(B,G)
		except A:return F
		E.collect();return O
	def create_module_stub(F,module_name,file_name=C):
		G=file_name;B=module_name
		if B.startswith(L)and B!=Z:return
		if B in F.problematic:return
		if G is C:G=F.path+D+B.replace(J,L)+'.py'
		if D in B:B=B.replace(D,J)
		I=C
		try:I=__import__(B,C,C,'*')
		except M:return
		T(G)
		with K(G,'w')as O:P='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(B,F._fwid,F.info,__version__);O.write(P);O.write('from typing import Any\n\n');F.write_object_stub(O,I,B,H)
		F._report.append({'module':B,'file':G})
		if not B in['os','sys','logging','gc']:
			try:del I
			except (A,N):pass
			try:del sys.modules[B]
			except N:pass
		E.collect()
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		b='tuple';a='list';Z='dict';Y='{0}{1} = {2} # type: {3}\n';W='bound_method';V='Any';P=in_class;O=object_expr;J=fp;B=indent;E.collect()
		if O in L.problematic:return
		Q,d=L.get_obj_attributes(O)
		for (C,K,F,T) in Q:
			if C in['classmethod','staticmethod']:continue
			S();c(1)
			if F=="<class 'type'>"and I(B)<=e*4:D='\n'+B+'class '+C+':\n';D+=B+"    ''\n";J.write(D);L.write_object_stub(J,T,'{0}.{1}'.format(obj_name,C),B+'    ',P+1)
			elif'method'in F or'function'in F or C==R:
				M=V;U=H
				if P>0:
					U='self, '
					if C==R:M='None'
				if W in F or W in K:D='{}@classmethod\n'.format(B);D+='{}def {}(cls, *args) -> {}:\n'.format(B,C,M)
				else:D='{}def {}({}*args) -> {}:\n'.format(B,C,U,M)
				D+=B+'    ...\n\n';J.write(D)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				G=F[8:-2];D=H
				if G in['str','int','float','bool','bytearray','bytes']:D=Y.format(B,C,K,G)
				elif G in[Z,a,b]:f={Z:'{}',a:'[]',b:'()'};D=Y.format(B,C,f[G],G)
				else:
					if not G in['object','set','frozenset']:G=V
					D='{0}{1} : {2} ## {3} = {4}\n'.format(B,C,G,F,K)
				J.write(D)
			else:J.write("# all other, type = '{0}'\n".format(F));J.write(B+C+' # type: Any\n')
		del Q;del d
		try:del C,K,F,T
		except (A,N,X):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,L)
		return A
	def clean(E,path=C):
		B=path
		if B is C:B=E.path
		W('Clean/remove files in folder: {}'.format(B))
		try:F=os.listdir(B)
		except (A,G):return
		for H in F:
			D=a.format(B,H)
			try:os.remove(D)
			except A:
				try:E.clean(D);os.rmdir(D)
				except A:pass
	def report(C,filename='modules.json'):
		H='firmware';D=',\n';I=a.format(C.path,filename);E.collect()
		try:
			with K(I,'w')as B:
				B.write('{');B.write(Q({H:C.info})[1:-1]);B.write(D);B.write(Q({'stubber':{P:__version__},'stubtype':H})[1:-1]);B.write(D);B.write('"modules" :[\n');G=O
				for J in C._report:
					if G:G=F
					else:B.write(D)
					B.write(Q(J))
				B.write('\n]}')
			L=C._start_free-E.mem_free()
		except A:pass
def T(path):
	C=path;B=F=0
	while B!=-1:
		B=C.find(D,F)
		if B!=-1:
			if B==0:E=C[0]
			else:E=C[0:B]
			try:I=os.stat(E)
			except A as G:
				if G.args[0]==d:
					try:os.mkdir(E)
					except A as H:raise H
				else:raise G
		F=B+1
def _info():
	f=' on ';e='0.0.0';d='port';c='platform';b='machine';a='nodename';Z='name';T='mpy';S='unknown';R='-';Q='sysname';L='v';K='family';F='build';D='ver';B='release';U=sys.implementation.name;V=sys.platform;A={Z:U,B:e,P:e,F:H,Q:S,a:S,b:S,K:U,c:V,d:V,D:H}
	try:A[B]=J.join([str(A)for A in sys.implementation.version]);A[P]=A[B];A[Z]=sys.implementation.name;A[T]=sys.implementation.mpy
	except G:pass
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
		except (Y,G,TypeError):pass
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
		if A[F]!=H and I(A[F])<4:A[D]+=R+A[F]
	if A[D][0]!=L:A[D]=L+A[D]
	if T in A:
		g=int(A[T]);X=[C,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][g>>10]
		if X:A['arch']=X
	return A
def get_root():
	try:B=os.getcwd()
	except (A,G):B=J
	for C in [B,'/sd','/flash',D,J]:
		try:E=os.stat(C);break
		except A as F:continue
	return C
def B():sys.exit(1)
def read_path():
	A=H
	if I(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):A=sys.argv[2]
		else:B()
	elif I(sys.argv)==2:B()
	return A
def U():
	try:A=bytes('abc',encoding=b);B=U.__module__;return F
	except (V,G):return O
def f():
	M=b'todo';L='.db';G='modulelist';import machine as N,btree
	try:D=K(G+L,'r+b');E=O
	except A:D=K(G+L,'w+b');E=F
	stubber=Stubber(path=read_path())
	if not E:stubber.clean()
	B=btree.open(D)
	if not E or I(list(B.keys()))==0:
		for P in K(G+'.txt'):
			C=P.strip()
			if I(C)and C[0]!='#':B[C]=M
		B.flush()
	for C in B.keys():
		if B[C]!=M:continue
		H=F
		try:H=stubber.create_one_stub(C.decode(b))
		except MemoryError:B.close();D.close();N.reset()
		if H:J='good, I guess'
		else:J=b'skipped'
		B[C]=J;B.flush()
	B.close();D.close()
if __name__=='__main__'or U():
	try:logging.basicConfig(level=logging.INFO)
	except X:pass
	f()