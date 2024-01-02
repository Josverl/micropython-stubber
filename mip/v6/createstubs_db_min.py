x='stubber'
w='{}/{}'
v='method'
u='function'
t='bool'
s='str'
r='float'
q='int'
p=NameError
o=sorted
n=MemoryError
m=NotImplementedError
d=',\n'
c='dict'
b='list'
a='tuple'
Z='micropython'
Y=str
X=repr
V='cpu'
U='_'
T=KeyError
S=IndexError
R=dir
Q=ImportError
P='with'
O='family'
N=print
M=len
L='.'
K='board'
J=True
I=open
H=AttributeError
G='/'
F=None
E='version'
D=False
A=OSError
C=''
import gc as B,os,sys
from ujson import dumps as e
try:from machine import reset
except Q:pass
try:from collections import OrderedDict as f
except Q:from ucollections import OrderedDict as f
__version__='v1.16.2'
y=2
z=2
g=[L,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(C,path=F,firmware_id=F):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise m('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		C._report=[];C.info=_info();B.collect()
		if D:C._fwid=D.lower()
		elif C.info[O]==Z:C._fwid='{family}-{ver}-{port}-{board}'.format(**C.info)
		else:C._fwid='{family}-{ver}-{port}'.format(**C.info)
		C._start_free=B.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',G)
		try:h(path+G)
		except A:N('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		I=item_instance;D=[];J=[]
		for A in R(I):
			if A.startswith(U)and not A in L.modules:continue
			try:
				E=getattr(I,A)
				try:F=X(type(E)).split("'")[1]
				except S:F=C
				if F in{q,r,s,t,a,b,c}:G=1
				elif F in{u,v}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,X(E),X(type(E)),E,G))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,I,K))
			except n as K:sleep(1);reset()
		D=o([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);B.collect();return D,J
	def add_modules(A,modules):A.modules=o(set(A.modules)|set(modules))
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
	def create_module_stub(K,module_name,file_name=F):
		H=file_name;E=module_name
		if H is F:O=E.replace(L,U)+'.py';H=K.path+G+O
		else:O=H.split(G)[-1]
		if G in E:E=E.replace(G,L)
		M=F
		try:M=__import__(E,F,F,'*');S=B.mem_free()
		except Q:return D
		h(H)
		with I(H,'w')as N:P=Y(K.info).replace('OrderedDict(',C).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(E,K._fwid,P,__version__);N.write(R);N.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');K.write_object_stub(N,M,E,C)
		K._report.append('{{"module": "{}", "file": "{}"}}'.format(E,H.replace('\\',G)))
		if E not in{'os','sys','logging','gc'}:
			try:del M
			except(A,T):pass
			try:del sys.modules[E]
			except T:pass
		B.collect();return J
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';Z='bound_method';Y='Incomplete';Q=in_class;P=object_expr;O='Exception';H=fp;E=indent;B.collect()
		if P in K.problematic:return
		R,L=K.get_obj_attributes(P)
		if L:N(L)
		for(F,J,G,S,f)in R:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if F[0].isdigit():continue
			if G=="<class 'type'>"and M(E)<=z*4:
				U=C;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				D='\n{}class {}({}):\n'.format(E,F,U)
				if V:D+=E+'    ...\n';H.write(D);return
				H.write(D);K.write_object_stub(H,S,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';H.write(D)
			elif any(A in G for A in[v,u,'closure']):
				W=Y;X=C
				if Q>0:X='self, '
				if Z in G or Z in J:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,X,W)
				D+=E+'    ...\n\n';H.write(D)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];D=C
				if I in[s,q,r,t,'bytearray','bytes']:D=d.format(E,F,J,I)
				elif I in[c,b,a]:e={c:'{}',b:'[]',a:'()'};D=d.format(E,F,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=Y
					D='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,I,G,J)
				H.write(D)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(E+F+' # type: Incomplete\n')
		del R;del L
		try:del F,J,G,S
		except(A,T,p):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,U)
		return A
	def clean(C,path=F):
		if path is F:path=C.path
		try:os.stat(path);D=os.listdir(path)
		except(A,H):return
		for E in D:
			B=w.format(path,E)
			try:os.remove(B)
			except A:
				try:C.clean(B);os.rmdir(B)
				except A:pass
	def report(C,filename='modules.json'):
		G=w.format(C.path,filename);B.collect()
		try:
			with I(G,'w')as E:
				C.write_json_header(E);F=J
				for H in C._report:C.write_json_node(E,H,F);F=D
				C.write_json_end(E)
			K=C._start_free-B.mem_free()
		except A:N('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(e({A:B.info})[1:-1]);f.write(d);f.write(e({x:{E:__version__},'stubtype':A})[1:-1]);f.write(d);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(d)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def h(path):
	B=D=0
	while B!=-1:
		B=path.find(G,D)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:H=os.stat(C)
			except A as E:
				if E.args[0]==y:
					try:os.mkdir(C)
					except A as F:N('failed to create folder {}'.format(C));raise F
		D=B+1
def W(s):
	A=' on '
	if not s:return C
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else C
def _info():
	g='ev3-pybricks';e='pycom';d='pycopy';c='unix';b='win32';a='arch';X='ver';I='mpy';G='port';D='build';A=f({O:sys.implementation.name,E:C,D:C,X:C,G:sys.platform,K:'UNKNOWN',V:C,I:C,a:C})
	if A[G].startswith('pyb'):A[G]='stm32'
	elif A[G]==b:A[G]='windows'
	elif A[G]=='linux':A[G]=c
	try:A[E]=L.join([Y(A)for A in sys.implementation.version])
	except H:pass
	try:N=sys.implementation._machine if'_machine'in R(sys.implementation)else os.uname().machine;A[K]=P.join(N.split(P)[:-1]).strip();A[V]=N.split(P)[-1].strip();A[I]=sys.implementation._mpy if'_mpy'in R(sys.implementation)else sys.implementation.mpy if I in R(sys.implementation)else C
	except(H,S):pass
	B.collect();A0(A);B.collect()
	try:
		A[D]=W(os.uname()[3])
		if not A[D]:A[D]=W(os.uname()[2])
		if not A[D]and';'in sys.version:A[D]=W(sys.version.split(';')[1])
	except(H,S):pass
	if A[D]and M(A[D])>5:A[D]=C
	if A[E]==C and sys.platform not in(c,b):
		try:h=os.uname();A[E]=h.release
		except(S,H,TypeError):pass
	for(i,j,k)in[(d,d,'const'),(e,e,'FAT'),(g,'pybricks.hubs','EV3Brick')]:
		try:l=__import__(j,F,F,k);A[O]=i;del l;break
		except(Q,T):pass
	if A[O]==g:A['release']='2.0.0'
	if A[O]==Z:
		if A[E]and A[E].endswith('.0')and A[E]>='1.10.0'and A[E]<='1.19.9':A[E]=A[E][:-2]
	if I in A and A[I]:
		J=int(A[I]);U=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][J>>10]
		if U:A[a]=U
		A[I]='v{}.{}'.format(J&255,J>>8&3)
	A[X]=f"v{A[E]}-{A[D]}"if A[D]else f"v{A[E]}";return A
def A0(info,desc=C):
	G='with ';C=info;E=D
	for F in[A+'/board_info.csv'for A in g]:
		if j(F):
			A=desc or C[K].strip()
			if i(C,A,F):E=J;break
			if P in A:
				A=A.split(P)[0].strip()
				if i(C,A,F):E=J;break
	if not E:
		A=desc or C[K].strip()
		if G+C[V].upper()in A:A=A.split(G+C[V].upper())[0].strip()
		C[K]=A
	C[K]=C[K].replace(' ',U);B.collect()
def i(info,board_descr,filename):
	with I(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,E=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[K]=E;return J
	return D
def get_root():
	try:B=os.getcwd()
	except(A,H):B=L
	C=B
	for C in[B,'/sd','/flash',G,L]:
		try:D=os.stat(C);break
		except A:continue
	return C
def j(filename):
	try:
		if os.stat(filename)[0]>>14:return J
		return D
	except A:return D
def k():sys.exit(1)
def read_path():
	path=C
	if M(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:k()
	elif M(sys.argv)==2:k()
	return path
def l():
	try:A=bytes('abc',encoding='utf8');B=l.__module__;return D
	except(m,H):return J
def main():
	L='failed';G='modulelist.done';import machine as O
	try:C=I(G,'r+b');N=J
	except A:C=I(G,'w+b');N=D
	stubber=Stubber(path=read_path())
	if not N:stubber.clean()
	A1(stubber);E={}
	try:
		with I(G)as C:
			for F in C.read().split('\n'):
				F=F.strip();B.collect()
				if M(F)>0:P,Q=F.split('=',1);E[P]=Q
	except(A,SyntaxError):pass
	B.collect();R=[A for A in stubber.modules if A not in E.keys()];B.collect()
	for H in R:
		K=D
		try:K=stubber.create_one_stub(H)
		except n:O.reset()
		B.collect();E[H]=Y(stubber._report[-1]if K else L)
		with I(G,'a')as C:C.write('{}={}\n'.format(H,'ok'if K else L))
	if E:stubber._report=[A for(B,A)in E.items()if A!=L];stubber.report()
def A1(stubber):
	E='/modulelist.txt';stubber.modules=[]
	for D in g:
		try:
			with I(D+E)as F:
				N('DEBUG: list of modules: '+D+E)
				for C in F.read().split('\n'):
					C=C.strip()
					if M(C)>0 and C[0]!='#':stubber.modules.append(C)
				B.collect();break
		except A:pass
	if not stubber.modules:stubber.modules=[Z];_log.warn('Could not find modulelist.txt, using default modules')
	B.collect()
if __name__=='__main__'or l():
	try:A2=logging.getLogger(x);logging.basicConfig(level=logging.INFO)
	except p:pass
	if not j('no_auto_stubber.txt'):
		try:B.threshold(4*1024);B.enable()
		except BaseException:pass
		main()