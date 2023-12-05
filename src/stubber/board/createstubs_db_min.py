w='{}/{}'
v='method'
u='function'
t='bool'
s='str'
r='float'
q='int'
p='port'
o=NameError
n=sorted
m=MemoryError
l=NotImplementedError
c=',\n'
b='dict'
a='list'
Z='tuple'
Y='micropython'
X='stubber'
W=str
V=repr
T='_'
S=KeyError
R=IndexError
Q=dir
P=ImportError
O='family'
N=True
M='.'
L=len
K='board'
J=open
I=AttributeError
H=print
G='/'
A=False
F='version'
E=None
D=OSError
C=''
import gc as B,os,sys
from ujson import dumps as d
try:from machine import reset
except P:pass
try:from collections import OrderedDict as e
except P:from ucollections import OrderedDict as e
__version__='v1.15.1'
x=2
y=2
f=[M,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise l('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A.log=E;A.log=logging.getLogger(X);A._report=[];A.info=_info();H('Port: {}'.format(A.info[p]));H('Board: {}'.format(A.info[K]));B.collect()
		if C:A._fwid=C.lower()
		elif A.info[O]==Y:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=B.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:g(path+G)
		except D:H('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;D=[];J=[]
		for A in Q(H):
			if A.startswith(T)and not A in L.modules:continue
			try:
				E=getattr(H,A)
				try:F=V(type(E)).split("'")[1]
				except R:F=C
				if F in{q,r,s,t,Z,a,b}:G=1
				elif F in{u,v}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,V(E),V(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,K))
			except m as K:sleep(1);reset()
		D=n([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);B.collect();return D,J
	def add_modules(A,modules):A.modules=n(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(C,module_name):
		E=module_name
		if E in C.problematic:return A
		if E in C.excluded:return A
		H='{}/{}.py'.format(C.path,E.replace(M,G));B.collect();F=A
		try:F=C.create_module_stub(E,H)
		except D:return A
		B.collect();return F
	def create_module_stub(K,module_name,file_name=E):
		I=file_name;F=module_name
		if I is E:L=F.replace(M,T)+'.py';I=K.path+G+L
		else:L=I.split(G)[-1]
		if G in F:F=F.replace(G,M)
		O=E
		try:O=__import__(F,E,E,'*');R=B.mem_free();H('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(F,L,R))
		except P:return A
		g(I)
		with J(I,'w')as Q:U=W(K.info).replace('OrderedDict(',C).replace('})','}');V='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(F,K._fwid,U,__version__);Q.write(V);Q.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');K.write_object_stub(Q,O,F,C)
		K._report.append('{{"module": "{}", "file": "{}"}}'.format(F,I.replace('\\',G)))
		if F not in{'os','sys','logging','gc'}:
			try:del O
			except (D,S):pass
			try:del sys.modules[F]
			except S:pass
		B.collect();return N
	def write_object_stub(M,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';Y='Incomplete';Q=in_class;P=object_expr;O='Exception';I=fp;E=indent;B.collect()
		if P in M.problematic:return
		R,N=M.get_obj_attributes(P)
		if N:H(N)
		for (F,K,G,T,f) in R:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if F[0].isdigit():continue
			if G=="<class 'type'>"and L(E)<=y*4:
				U=C;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(E,F,U)
				if V:A+=E+'    ...\n';I.write(A);return
				I.write(A);M.write_object_stub(I,T,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);A=E+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=E+'        ...\n\n';I.write(A)
			elif any((A in G for A in[v,u,'closure'])):
				W=Y;X=C
				if Q>0:X='self, '
				if c in G or c in K:A='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,X,W)
				A+=E+'    ...\n\n';I.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				J=G[8:-2];A=C
				if J in[s,q,r,t,'bytearray','bytes']:A=d.format(E,F,K,J)
				elif J in[b,a,Z]:e={b:'{}',a:'[]',Z:'()'};A=d.format(E,F,e[J],J)
				else:
					if J not in['object','set','frozenset']:J=Y
					A='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,J,G,K)
				I.write(A)
			else:I.write("# all other, type = '{0}'\n".format(G));I.write(E+F+' # type: Incomplete\n')
		del R;del N
		try:del F,K,G,T
		except (D,S,o):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,T)
		return A
	def clean(B,path=E):
		if path is E:path=B.path
		H('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except (D,I):return
		for F in C:
			A=w.format(path,F)
			try:os.remove(A)
			except D:
				try:B.clean(A);os.rmdir(A)
				except D:pass
	def report(C,filename='modules.json'):
		H('Created stubs for {} modules on board {}\nPath: {}'.format(L(C._report),C._fwid,C.path));G=w.format(C.path,filename);B.collect()
		try:
			with J(G,'w')as E:
				C.write_json_header(E);F=N
				for I in C._report:C.write_json_node(E,I,F);F=A
				C.write_json_end(E)
			K=C._start_free-B.mem_free()
		except D:H('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(d({A:B.info})[1:-1]);f.write(c);f.write(d({X:{F:__version__},'stubtype':A})[1:-1]);f.write(c);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(c)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def g(path):
	A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except D as E:
				if E.args[0]==x:
					try:os.mkdir(B)
					except D as F:H('failed to create folder {}'.format(B));raise F
		C=A+1
def U(s):
	A=' on '
	if not s:return C
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else C
def _info():
	k='ev3-pybricks';j='pycom';g='pycopy';d='GENERIC';c='arch';b='cpu';a='ver';V='with';G='mpy';D='build';A=e({O:sys.implementation.name,F:C,D:C,a:C,p:'stm32'if sys.platform.startswith('pyb')else sys.platform,K:d,b:C,G:C,c:C})
	try:A[F]=M.join([W(A)for A in sys.implementation.version])
	except I:pass
	try:X=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[K]=X.strip();A[b]=X.split(V)[1].strip();A[G]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if G in Q(sys.implementation)else C
	except (I,R):pass
	B.collect()
	for J in [A+'/board_info.csv'for A in f]:
		if i(J):
			H=A[K].strip()
			if h(A,H,J):break
			if V in H:
				H=H.split(V)[0].strip()
				if h(A,H,J):break
			A[K]=d
	A[K]=A[K].replace(' ',T);B.collect()
	try:
		A[D]=U(os.uname()[3])
		if not A[D]:A[D]=U(os.uname()[2])
		if not A[D]and';'in sys.version:A[D]=U(sys.version.split(';')[1])
	except (I,R):pass
	if A[D]and L(A[D])>5:A[D]=C
	if A[F]==C and sys.platform not in('unix','win32'):
		try:l=os.uname();A[F]=l.release
		except (R,I,TypeError):pass
	for (m,n,o) in [(g,g,'const'),(j,j,'FAT'),(k,'pybricks.hubs','EV3Brick')]:
		try:q=__import__(n,E,E,o);A[O]=m;del q;break
		except (P,S):pass
	if A[O]==k:A['release']='2.0.0'
	if A[O]==Y:
		if A[F]and A[F].endswith('.0')and A[F]>='1.10.0'and A[F]<='1.19.9':A[F]=A[F][:-2]
	if G in A and A[G]:
		N=int(A[G]);Z=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][N>>10]
		if Z:A[c]=Z
		A[G]='v{}.{}'.format(N&255,N>>8&3)
	A[a]=f"v{A[F]}-{A[D]}"if A[D]else f"v{A[F]}";return A
def h(info,board_descr,filename):
	with J(filename,'r')as C:
		while 1:
			B=C.readline()
			if not B:break
			D,E=B.split(',')[0].strip(),B.split(',')[1].strip()
			if D==board_descr:info[K]=E;return N
	return A
def get_root():
	try:A=os.getcwd()
	except (D,I):A=M
	B=A
	for B in [A,'/sd','/flash',G,M]:
		try:C=os.stat(B);break
		except D:continue
	return B
def i(filename):
	try:
		if os.stat(filename)[0]>>14:return N
		return A
	except D:return A
def j():sys.exit(1)
def read_path():
	path=C
	if L(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:j()
	elif L(sys.argv)==2:j()
	return path
def k():
	try:B=bytes('abc',encoding='utf8');C=k.__module__;return A
	except (l,I):return N
def main():
	K='failed';G='modulelist.done';import machine as O
	try:C=J(G,'r+b');M=N;_log.info('Opened existing db')
	except D:C=J(G,'w+b');_log.info('created new db');M=A
	stubber=Stubber(path=read_path())
	if not M:stubber.clean()
	z(stubber);E={}
	try:
		with J(G)as C:
			for F in C.read().split('\n'):
				F=F.strip();B.collect()
				if L(F)>0:P,Q=F.split('=',1);E[P]=Q
	except (D,SyntaxError):pass
	B.collect();R=[A for A in stubber.modules if A not in E.keys()];B.collect()
	for H in R:
		I=A
		try:I=stubber.create_one_stub(H)
		except m:O.reset()
		B.collect();E[H]=W(stubber._report[-1]if I else K)
		with J(G,'a')as C:C.write('{}={}\n'.format(H,'ok'if I else K))
	if E:stubber._report=[A for(B,A)in E.items()if A!=K];stubber.report()
def z(stubber):
	E='/modulelist.txt';stubber.modules=[]
	for C in f:
		try:
			with J(C+E)as F:
				H('DEBUG: list of modules: '+C+E)
				for A in F.read().split('\n'):
					A=A.strip()
					if L(A)>0 and A[0]!='#':stubber.modules.append(A)
				B.collect();break
		except D:pass
	if not stubber.modules:stubber.modules=[Y];_log.warn('Could not find modulelist.txt, using default modules')
	B.collect()
if __name__=='__main__'or k():
	try:A0=logging.getLogger(X);logging.basicConfig(level=logging.INFO)
	except o:pass
	if not i('no_auto_stubber.txt'):
		try:B.threshold(4*1024);B.enable()
		except BaseException:pass
		main()