x='with'
w='stubber'
v='{}/{}'
u='method'
t='function'
s='bool'
r='str'
q='float'
p='int'
o=TypeError
n=NameError
m=sorted
l=MemoryError
k=NotImplementedError
d='-'
c=',\n'
b='dict'
a='list'
Z='tuple'
Y='micropython'
X=str
W=repr
U='cpu'
T='_'
S=KeyError
R=IndexError
Q=ImportError
P='family'
O=print
N=len
M=dir
L='.'
K=open
J=True
I=AttributeError
H='board'
G='/'
F=None
E=False
A=OSError
D='version'
C=''
import gc as B,os,sys
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except Q:pass
try:from collections import OrderedDict as e
except Q:from ucollections import OrderedDict as e
__version__='v1.16.2'
y=2
z=2
f=[L,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(C,path=F,firmware_id=F):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise k('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		C._report=[];C.info=_info();B.collect()
		if D:C._fwid=D.lower()
		elif C.info[P]==Y:C._fwid='{family}-v{version}-{port}-{board}'.format(**C.info)
		else:C._fwid='{family}-v{version}-{port}'.format(**C.info)
		C._start_free=B.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',G)
		try:g(path+G)
		except A:O('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;D=[];J=[]
		for A in M(H):
			if A.startswith(T)and not A in L.modules:continue
			try:
				E=getattr(H,A)
				try:F=W(type(E)).split("'")[1]
				except R:F=C
				if F in{p,q,r,s,Z,a,b}:G=1
				elif F in{t,u}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,W(E),W(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,K))
			except l as K:sleep(1);reset()
		D=m([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);B.collect();return D,J
	def add_modules(A,modules):A.modules=m(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(C,module_name):
		D=module_name
		if D in C.problematic:return E
		if D in C.excluded:return E
		H='{}/{}.py'.format(C.path,D.replace(L,G));B.collect();F=E
		try:F=C.create_module_stub(D,H)
		except A:return E
		B.collect();return F
	def create_module_stub(I,module_name,file_name=F):
		H=file_name;D=module_name
		if H is F:O=D.replace(L,T)+'.py';H=I.path+G+O
		else:O=H.split(G)[-1]
		if G in D:D=D.replace(G,L)
		M=F
		try:M=__import__(D,F,F,'*');U=B.mem_free()
		except Q:return E
		g(H)
		with K(H,'w')as N:P=X(I.info).replace('OrderedDict(',C).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,I._fwid,P,__version__);N.write(R);N.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(N,M,D,C)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del M
			except(A,S):pass
			try:del sys.modules[D]
			except S:pass
		B.collect();return J
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';Y='Incomplete';Q=in_class;P=object_expr;M='Exception';H=fp;E=indent;B.collect()
		if P in K.problematic:return
		R,L=K.get_obj_attributes(P)
		if L:O(L)
		for(F,J,G,T,f)in R:
			if F in['classmethod','staticmethod','BaseException',M]:continue
			if F[0].isdigit():continue
			if G=="<class 'type'>"and N(E)<=z*4:
				U=C;V=F.endswith(M)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=M
				D='\n{}class {}({}):\n'.format(E,F,U)
				if V:D+=E+'    ...\n';H.write(D);return
				H.write(D);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';H.write(D)
			elif any(A in G for A in[u,t,'closure']):
				W=Y;X=C
				if Q>0:X='self, '
				if c in G or c in J:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,X,W)
				D+=E+'    ...\n\n';H.write(D)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];D=C
				if I in[r,p,q,s,'bytearray','bytes']:D=d.format(E,F,J,I)
				elif I in[b,a,Z]:e={b:'{}',a:'[]',Z:'()'};D=d.format(E,F,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=Y
					D='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,I,G,J)
				H.write(D)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(E+F+' # type: Incomplete\n')
		del R;del L
		try:del F,J,G,T
		except(A,S,n):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,T)
		return A
	def clean(C,path=F):
		if path is F:path=C.path
		try:os.stat(path);D=os.listdir(path)
		except(A,I):return
		for E in D:
			B=v.format(path,E)
			try:os.remove(B)
			except A:
				try:C.clean(B);os.rmdir(B)
				except A:pass
	def report(C,filename='modules.json'):
		G=v.format(C.path,filename);B.collect()
		try:
			with K(G,'w')as D:
				C.write_json_header(D);F=J
				for H in C._report:C.write_json_node(D,H,F);F=E
				C.write_json_end(D)
			I=C._start_free-B.mem_free()
		except A:O('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(dumps({A:B.info})[1:-1]);f.write(c);f.write(dumps({w:{D:__version__},'stubtype':A})[1:-1]);f.write(c);f.write('"modules" :[\n')
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
			try:H=os.stat(C)
			except A as E:
				if E.args[0]==y:
					try:os.mkdir(C)
					except A as F:O('failed to create folder {}'.format(C));raise F
		D=B+1
def V(s):
	A=' on '
	if not s:return C
	s=s.split(A,1)[0]if A in s else s;s=s.split('; ',1)[1]if'; 'in s else s;B=s.split(d)[1]if s.startswith('v')else s.split(d,1)[-1].split(L)[1];return B
def _info():
	c='-preview';b='ev3-pybricks';a='pycom';Z='pycopy';X='unix';W='win32';T='arch';O='ver';J='mpy';G='port';E='build';A=e({P:sys.implementation.name,D:C,E:C,O:C,G:sys.platform,H:'UNKNOWN',U:C,J:C,T:C})
	if A[G].startswith('pyb'):A[G]='stm32'
	elif A[G]==W:A[G]='windows'
	elif A[G]=='linux':A[G]=X
	try:A[D]=A0(sys.implementation.version)
	except I:pass
	try:L=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[H]=L;A[U]=L.split(x)[-1].strip();A[J]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if J in M(sys.implementation)else C
	except(I,R):pass
	B.collect();A1(A);B.collect()
	try:
		if'uname'in M(os):
			A[E]=V(os.uname()[3])
			if not A[E]:A[E]=V(os.uname()[2])
		elif D in M(sys):A[E]=V(sys.version)
	except(I,R,o):pass
	if A[D]==C and sys.platform not in(X,W):
		try:d=os.uname();A[D]=d.release
		except(R,I,o):pass
	for(f,g,h)in[(Z,Z,'const'),(a,a,'FAT'),(b,'pybricks.hubs','EV3Brick')]:
		try:i=__import__(g,F,F,h);A[P]=f;del i;break
		except(Q,S):pass
	if A[P]==b:A['release']='2.0.0'
	if A[P]==Y:
		A[D]
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if J in A and A[J]:
		K=int(A[J]);N=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][K>>10]
		if N:A[T]=N
		A[J]='v{}.{}'.format(K&255,K>>8&3)
	if A[E]and not A[D].endswith(c):A[D]=A[D]+c
	A[O]=f"{A[D]}-{A[E]}"if A[E]else f"{A[D]}";return A
def A0(version):
	A=version;B=L.join([X(A)for A in A[:3]])
	if N(A)>3 and A[3]:B+=d+A[3]
	return B
def A1(info,desc=C):
	L='with ';A=info;F=E
	for G in[A+'/board_info.csv'for A in f]:
		if h(G):
			D=desc or A[H].strip();I=D.rfind(' with')
			if I!=-1:K=D[:I].strip()
			else:K=C
			if A2(A,D,G,K):F=J;break
	if not F:
		D=desc or A[H].strip()
		if L+A[U].upper()in D:D=D.split(L+A[U].upper())[0].strip()
		A[H]=D
	A[H]=A[H].replace(' ',T);B.collect()
def A2(info,descr,filename,short_descr):
	B=short_descr;A=info;D=C
	with K(filename,'r')as L:
		while 1:
			F=L.readline()
			if not F:break
			I,G=F.split(',')[0].strip(),F.split(',')[1].strip()
			if I==descr:A[H]=G;return J
			elif B and I==B:
				if x in B:A[H]=G;return J
				D=G
	if D:A[H]=D;return J
	return E
def get_root():
	try:B=os.getcwd()
	except(A,I):B=L
	C=B
	for C in[B,'/sd','/flash',G,L]:
		try:D=os.stat(C);break
		except A:continue
	return C
def h(filename):
	try:
		if os.stat(filename)[0]>>14:return J
		return E
	except A:return E
def i():sys.exit(1)
def read_path():
	path=C
	if N(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:i()
	elif N(sys.argv)==2:i()
	return path
def j():
	try:A=bytes('abc',encoding='utf8');B=j.__module__;return E
	except(k,I):return J
def main():
	L='failed';G='modulelist.done';import machine as O
	try:C=K(G,'r+b');M=J
	except A:C=K(G,'w+b');M=E
	stubber=Stubber(path=read_path())
	if not M:stubber.clean()
	A3(stubber);D={}
	try:
		with K(G)as C:
			for F in C.read().split('\n'):
				F=F.strip();B.collect()
				if N(F)>0:P,Q=F.split('=',1);D[P]=Q
	except(A,SyntaxError):pass
	B.collect();R=[A for A in stubber.modules if A not in D.keys()];B.collect()
	for H in R:
		I=E
		try:I=stubber.create_one_stub(H)
		except l:O.reset()
		B.collect();D[H]=X(stubber._report[-1]if I else L)
		with K(G,'a')as C:C.write('{}={}\n'.format(H,'ok'if I else L))
	if D:stubber._report=[A for(B,A)in D.items()if A!=L];stubber.report()
def A3(stubber):
	E='/modulelist.txt';stubber.modules=[]
	for D in f:
		try:
			with K(D+E)as F:
				O('DEBUG: list of modules: '+D+E)
				for C in F.read().split('\n'):
					C=C.strip()
					if N(C)>0 and C[0]!='#':stubber.modules.append(C)
				B.collect();break
		except A:pass
	if not stubber.modules:stubber.modules=[Y];_log.warn('Could not find modulelist.txt, using default modules')
	B.collect()
if __name__=='__main__'or j():
	try:A4=logging.getLogger(w);logging.basicConfig(level=logging.INFO)
	except n:pass
	if not h('no_auto_stubber.txt'):
		try:B.threshold(4*1024);B.enable()
		except BaseException:pass
		main()