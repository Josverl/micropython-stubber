w='with'
v='stubber'
u='{}/{}'
t='method'
s='function'
r='bool'
q='str'
p='float'
o='int'
n=NameError
m=sorted
l=MemoryError
k=NotImplementedError
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
Q=dir
P=ImportError
O='family'
N=print
M=len
L='.'
K=open
J=True
I=AttributeError
H='board'
G='/'
F=None
E='version'
D=False
A=OSError
C=''
import gc as B,os,sys
from ujson import dumps as d
try:from machine import reset
except P:pass
try:from collections import OrderedDict as e
except P:from ucollections import OrderedDict as e
__version__='v1.16.2'
x=2
y=2
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
		elif C.info[O]==Y:C._fwid='{family}-{ver}-{port}-{board}'.format(**C.info)
		else:C._fwid='{family}-{ver}-{port}'.format(**C.info)
		C._start_free=B.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',G)
		try:g(path+G)
		except A:N('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;D=[];J=[]
		for A in Q(H):
			if A.startswith(T)and not A in L.modules:continue
			try:
				E=getattr(H,A)
				try:F=W(type(E)).split("'")[1]
				except R:F=C
				if F in{o,p,q,r,Z,a,b}:G=1
				elif F in{s,t}:G=2
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
		E=module_name
		if E in C.problematic:return D
		if E in C.excluded:return D
		H='{}/{}.py'.format(C.path,E.replace(L,G));B.collect();F=D
		try:F=C.create_module_stub(E,H)
		except A:return D
		B.collect();return F
	def create_module_stub(I,module_name,file_name=F):
		H=file_name;E=module_name
		if H is F:O=E.replace(L,T)+'.py';H=I.path+G+O
		else:O=H.split(G)[-1]
		if G in E:E=E.replace(G,L)
		M=F
		try:M=__import__(E,F,F,'*');U=B.mem_free()
		except P:return D
		g(H)
		with K(H,'w')as N:Q=X(I.info).replace('OrderedDict(',C).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(E,I._fwid,Q,__version__);N.write(R);N.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(N,M,E,C)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(E,H.replace('\\',G)))
		if E not in{'os','sys','logging','gc'}:
			try:del M
			except(A,S):pass
			try:del sys.modules[E]
			except S:pass
		B.collect();return J
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';Y='Incomplete';Q=in_class;P=object_expr;O='Exception';H=fp;E=indent;B.collect()
		if P in K.problematic:return
		R,L=K.get_obj_attributes(P)
		if L:N(L)
		for(F,J,G,T,f)in R:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if F[0].isdigit():continue
			if G=="<class 'type'>"and M(E)<=y*4:
				U=C;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				D='\n{}class {}({}):\n'.format(E,F,U)
				if V:D+=E+'    ...\n';H.write(D);return
				H.write(D);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';H.write(D)
			elif any(A in G for A in[t,s,'closure']):
				W=Y;X=C
				if Q>0:X='self, '
				if c in G or c in J:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,X,W)
				D+=E+'    ...\n\n';H.write(D)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];D=C
				if I in[q,o,p,r,'bytearray','bytes']:D=d.format(E,F,J,I)
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
			B=u.format(path,E)
			try:os.remove(B)
			except A:
				try:C.clean(B);os.rmdir(B)
				except A:pass
	def report(C,filename='modules.json'):
		G=u.format(C.path,filename);B.collect()
		try:
			with K(G,'w')as E:
				C.write_json_header(E);F=J
				for H in C._report:C.write_json_node(E,H,F);F=D
				C.write_json_end(E)
			I=C._start_free-B.mem_free()
		except A:N('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(d({A:B.info})[1:-1]);f.write(c);f.write(d({v:{E:__version__},'stubtype':A})[1:-1]);f.write(c);f.write('"modules" :[\n')
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
				if E.args[0]==x:
					try:os.mkdir(C)
					except A as F:N('failed to create folder {}'.format(C));raise F
		D=B+1
def V(s):
	A=' on '
	if not s:return C
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else C
def _info():
	f='ev3-pybricks';d='pycom';c='pycopy';b='unix';a='win32';Z='arch';W='ver';J='mpy';G='port';D='build';A=e({O:sys.implementation.name,E:C,D:C,W:C,G:sys.platform,H:'UNKNOWN',U:C,J:C,Z:C})
	if A[G].startswith('pyb'):A[G]='stm32'
	elif A[G]==a:A[G]='windows'
	elif A[G]=='linux':A[G]=b
	try:A[E]=L.join([X(A)for A in sys.implementation.version]).rstrip(L)
	except I:pass
	try:N=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[H]=N;A[U]=N.split(w)[-1].strip();A[J]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if J in Q(sys.implementation)else C
	except(I,R):pass
	B.collect();z(A);B.collect()
	try:
		A[D]=V(os.uname()[3])
		if not A[D]:A[D]=V(os.uname()[2])
		if not A[D]and';'in sys.version:A[D]=V(sys.version.split(';')[1])
	except(I,R):pass
	if A[D]and M(A[D])>5:A[D]=C
	if A[E]==C and sys.platform not in(b,a):
		try:g=os.uname();A[E]=g.release
		except(R,I,TypeError):pass
	for(h,i,j)in[(c,c,'const'),(d,d,'FAT'),(f,'pybricks.hubs','EV3Brick')]:
		try:k=__import__(i,F,F,j);A[O]=h;del k;break
		except(P,S):pass
	if A[O]==f:A['release']='2.0.0'
	if A[O]==Y:
		if A[E]and A[E].endswith('.0')and A[E]>='1.10.0'and A[E]<='1.19.9':A[E]=A[E][:-2]
	if J in A and A[J]:
		K=int(A[J]);T=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][K>>10]
		if T:A[Z]=T
		A[J]='v{}.{}'.format(K&255,K>>8&3)
	A[W]=f"v{A[E]}-{A[D]}"if A[D]else f"v{A[E]}";return A
def z(info,desc=C):
	L='with ';A=info;F=D
	for G in[A+'/board_info.csv'for A in f]:
		if h(G):
			E=desc or A[H].strip();I=E.rfind(' with')
			if I!=-1:K=E[:I].strip()
			else:K=C
			if A0(A,E,G,K):F=J;break
	if not F:
		E=desc or A[H].strip()
		if L+A[U].upper()in E:E=E.split(L+A[U].upper())[0].strip()
		A[H]=E
	A[H]=A[H].replace(' ',T);B.collect()
def A0(info,descr,filename,short_descr):
	B=short_descr;A=info;E=C
	with K(filename,'r')as L:
		while 1:
			F=L.readline()
			if not F:break
			I,G=F.split(',')[0].strip(),F.split(',')[1].strip()
			if I==descr:A[H]=G;return J
			elif B and I==B:
				if w in B:A[H]=G;return J
				E=G
	if E:A[H]=E;return J
	return D
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
		return D
	except A:return D
def i():sys.exit(1)
def read_path():
	path=C
	if M(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:i()
	elif M(sys.argv)==2:i()
	return path
def j():
	try:A=bytes('abc',encoding='utf8');B=j.__module__;return D
	except(k,I):return J
def main():
	L='failed';G='modulelist.done';import machine as O
	try:C=K(G,'r+b');N=J
	except A:C=K(G,'w+b');N=D
	stubber=Stubber(path=read_path())
	if not N:stubber.clean()
	A1(stubber);E={}
	try:
		with K(G)as C:
			for F in C.read().split('\n'):
				F=F.strip();B.collect()
				if M(F)>0:P,Q=F.split('=',1);E[P]=Q
	except(A,SyntaxError):pass
	B.collect();R=[A for A in stubber.modules if A not in E.keys()];B.collect()
	for H in R:
		I=D
		try:I=stubber.create_one_stub(H)
		except l:O.reset()
		B.collect();E[H]=X(stubber._report[-1]if I else L)
		with K(G,'a')as C:C.write('{}={}\n'.format(H,'ok'if I else L))
	if E:stubber._report=[A for(B,A)in E.items()if A!=L];stubber.report()
def A1(stubber):
	E='/modulelist.txt';stubber.modules=[]
	for D in f:
		try:
			with K(D+E)as F:
				N('DEBUG: list of modules: '+D+E)
				for C in F.read().split('\n'):
					C=C.strip()
					if M(C)>0 and C[0]!='#':stubber.modules.append(C)
				B.collect();break
		except A:pass
	if not stubber.modules:stubber.modules=[Y];_log.warn('Could not find modulelist.txt, using default modules')
	B.collect()
if __name__=='__main__'or j():
	try:A2=logging.getLogger(v);logging.basicConfig(level=logging.INFO)
	except n:pass
	if not h('no_auto_stubber.txt'):
		try:B.threshold(4*1024);B.enable()
		except BaseException:pass
		main()