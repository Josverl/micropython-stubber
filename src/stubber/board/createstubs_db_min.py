w='stubber'
v='{}/{}'
u='method'
t='function'
s='bool'
r='str'
q='float'
p='int'
o=NameError
n=sorted
m=MemoryError
l=NotImplementedError
c=',\n'
b='dict'
a='list'
Z='tuple'
Y='micropython'
X=str
W=repr
U='_'
T=KeyError
S=IndexError
R=dir
Q=ImportError
P='family'
O=True
N='.'
M=len
L='board'
K='port'
J=open
I=AttributeError
H=print
G='/'
F=False
E=None
D='version'
A=OSError
C=''
import gc as B,os,sys
from ujson import dumps as d
try:from machine import reset
except P:pass
try:from collections import OrderedDict as d
except P:from ucollections import OrderedDict as d
__version__='v1.16.0'
w=2
x=2
y=2
f=[N,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(C,path=E,firmware_id=E):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise l('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		C._report=[];C.info=_info();H('Port: {}'.format(C.info[K]));H('Board: {}'.format(C.info[L]));B.collect()
		if D:C._fwid=D.lower()
		elif C.info[P]==Y:C._fwid='{family}-{ver}-{port}-{board}'.format(**C.info)
		else:C._fwid='{family}-{ver}-{port}'.format(**C.info)
		C._start_free=B.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',G)
		try:g(path+G)
		except A:H('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;D=[];J=[]
		for A in R(H):
			if A.startswith(U)and not A in L.modules:continue
			try:
				E=getattr(H,A)
				try:F=W(type(E)).split("'")[1]
				except S:F=C
				if F in{p,q,r,s,Z,a,b}:G=1
				elif F in{t,u}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,W(E),W(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,K))
			except m as K:sleep(1);reset()
		D=n([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);B.collect();return D,J
	def add_modules(A,modules):A.modules=n(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(C,module_name):
		D=module_name
		if D in C.problematic:return F
		if D in C.excluded:return F
		H='{}/{}.py'.format(C.path,D.replace(N,G));B.collect();E=F
		try:E=C.create_module_stub(D,H)
		except A:return F
		B.collect();return E
	def create_module_stub(K,module_name,file_name=E):
		I=file_name;D=module_name
		if I is E:L=D.replace(N,U)+'.py';I=K.path+G+L
		else:L=I.split(G)[-1]
		if G in D:D=D.replace(G,N)
		M=E
		try:M=__import__(D,E,E,'*');R=B.mem_free();H('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(D,L,R))
		except Q:return F
		g(I)
		with J(I,'w')as P:S=X(K.info).replace('OrderedDict(',C).replace('})','}');V='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,K._fwid,S,__version__);P.write(V);P.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');K.write_object_stub(P,M,D,C)
		K._report.append('{{"module": "{}", "file": "{}"}}'.format(D,I.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del M
			except(A,T):pass
			try:del sys.modules[D]
			except T:pass
		B.collect();return O
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';Y='Incomplete';Q=in_class;P=object_expr;O='Exception';I=fp;E=indent;B.collect()
		if P in L.problematic:return
		R,N=L.get_obj_attributes(P)
		if N:H(N)
		for(F,K,G,S,f)in R:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if F[0].isdigit():continue
			if G=="<class 'type'>"and M(E)<=y*4:
				U=C;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				D='\n{}class {}({}):\n'.format(E,F,U)
				if V:D+=E+'    ...\n';I.write(D);return
				I.write(D);L.write_object_stub(I,S,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';I.write(D)
			elif any(A in G for A in[u,t,'closure']):
				W=Y;X=C
				if Q>0:X='self, '
				if c in G or c in K:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,X,W)
				D+=E+'    ...\n\n';I.write(D)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				J=G[8:-2];D=C
				if J in[r,p,q,s,'bytearray','bytes']:D=d.format(E,F,K,J)
				elif J in[b,a,Z]:e={b:'{}',a:'[]',Z:'()'};D=d.format(E,F,e[J],J)
				else:
					if J not in['object','set','frozenset']:J=Y
					D='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,J,G,K)
				I.write(D)
			else:I.write("# all other, type = '{0}'\n".format(G));I.write(E+F+' # type: Incomplete\n')
		del R;del N
		try:del F,K,G,S
		except(A,T,o):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,U)
		return A
	def clean(C,path=E):
		if path is E:path=C.path
		H('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);D=os.listdir(path)
		except(A,I):return
		for F in D:
			B=v.format(path,F)
			try:os.remove(B)
			except A:
				try:C.clean(B);os.rmdir(B)
				except A:pass
	def report(C,filename='modules.json'):
		H('Created stubs for {} modules on board {}\nPath: {}'.format(M(C._report),C._fwid,C.path));G=v.format(C.path,filename);B.collect()
		try:
			with J(G,'w')as D:
				C.write_json_header(D);E=O
				for I in C._report:C.write_json_node(D,I,E);E=F
				C.write_json_end(D)
			K=C._start_free-B.mem_free()
		except A:H('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(d({A:B.info})[1:-1]);f.write(c);f.write(d({w:{D:__version__},'stubtype':A})[1:-1]);f.write(c);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(c)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def g(path):
	B=D=0
	while B!=-1:
		B=path.find(G,D)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except A as E:
				if E.args[0]==x:
					try:os.mkdir(C)
					except A as F:H('failed to create folder {}'.format(C));raise F
		D=B+1
def V(s):
	A=' on '
	if not s:return C
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else C
def _info():
	n='ev3-pybricks';m='pycom';l='pycopy';k='unix';j='win32';g='GENERIC';d='arch';c='cpu';b='ver';W='with';G='mpy';F='build';A=e({P:sys.implementation.name,D:C,F:C,b:C,K:sys.platform,L:g,c:C,G:C,d:C})
	if A[K]=='pyb':A[K]='stm32'
	elif A[K]==j:A[K]='windows'
	elif A[K]=='linux':A[K]=k
	try:A[D]=N.join([X(A)for A in sys.implementation.version])
	except I:pass
	try:Z=sys.implementation._machine if'_machine'in R(sys.implementation)else os.uname().machine;A[L]=Z.strip();A[c]=Z.split(W)[1].strip();A[G]=sys.implementation._mpy if'_mpy'in R(sys.implementation)else sys.implementation.mpy if G in R(sys.implementation)else C
	except(I,S):pass
	B.collect()
	for J in[A+'/board_info.csv'for A in f]:
		if i(J):
			H=A[L].strip()
			if h(A,H,J):break
			if W in H:
				H=H.split(W)[0].strip()
				if h(A,H,J):break
			A[L]=g
	A[L]=A[L].replace(' ',U);B.collect()
	try:
		A[F]=V(os.uname()[3])
		if not A[F]:A[F]=V(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=V(sys.version.split(';')[1])
	except(I,S):pass
	if A[F]and M(A[F])>5:A[F]=C
	if A[D]==C and sys.platform not in(k,j):
		try:o=os.uname();A[D]=o.release
		except(S,I,TypeError):pass
	for(p,q,r)in[(l,l,'const'),(m,m,'FAT'),(n,'pybricks.hubs','EV3Brick')]:
		try:s=__import__(q,E,E,r);A[P]=p;del s;break
		except(Q,T):pass
	if A[P]==n:A['release']='2.0.0'
	if A[P]==Y:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if G in A and A[G]:
		O=int(A[G]);a=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][O>>10]
		if a:A[d]=a
		A[G]='v{}.{}'.format(O&255,O>>8&3)
	A[b]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def h(info,board_descr,filename):
	with J(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[L]=D;return O
	return F
def get_root():
	try:B=os.getcwd()
	except(A,I):B=N
	C=B
	for C in[B,'/sd','/flash',G,N]:
		try:D=os.stat(C);break
		except A:continue
	return C
def i(filename):
	try:
		if os.stat(filename)[0]>>14:return O
		return F
	except A:return F
def j():sys.exit(1)
def read_path():
	path=C
	if M(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:j()
	elif M(sys.argv)==2:j()
	return path
def k():
	try:A=bytes('abc',encoding='utf8');B=k.__module__;return F
	except(l,I):return O
def main():
	K='failed';G='modulelist.done';import machine as N
	try:C=J(G,'r+b');L=O
	except A:C=J(G,'w+b');L=F
	stubber=Stubber(path=read_path())
	if not L:stubber.clean()
	z(stubber);D={}
	try:
		with J(G)as C:
			for E in C.read().split('\n'):
				E=E.strip();B.collect()
				if M(E)>0:P,Q=E.split('=',1);D[P]=Q
	except(A,SyntaxError):pass
	B.collect();R=[A for A in stubber.modules if A not in D.keys()];B.collect()
	for H in R:
		I=F
		try:I=stubber.create_one_stub(H)
		except m:N.reset()
		B.collect();D[H]=X(stubber._report[-1]if I else K)
		with J(G,'a')as C:C.write('{}={}\n'.format(H,'ok'if I else K))
	if D:stubber._report=[A for(B,A)in D.items()if A!=K];stubber.report()
def z(stubber):
	E='/modulelist.txt';stubber.modules=[]
	for D in f:
		try:
			with J(D+E)as F:
				H('DEBUG: list of modules: '+D+E)
				for C in F.read().split('\n'):
					C=C.strip()
					if M(C)>0 and C[0]!='#':stubber.modules.append(C)
				B.collect();break
		except A:pass
	if not stubber.modules:stubber.modules=[Y]
	B.collect()
if __name__=='__main__'or k():
	try:A0=logging.getLogger(w);logging.basicConfig(level=logging.INFO)
	except o:pass
	if not i('no_auto_stubber.txt'):
		try:B.threshold(4*1024);B.enable()
		except BaseException:pass
		main()