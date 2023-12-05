v='{}/{}'
u='method'
t='function'
s='bool'
r='str'
q='float'
p='int'
o='port'
n=NameError
m=sorted
l=NotImplementedError
A=',\n'
c='dict'
b='list'
a='tuple'
Z='micropython'
Y='stubber'
X=str
W=repr
U='_'
T=KeyError
S=open
R=IndexError
Q=dir
P=ImportError
O=True
N='family'
M=len
L='.'
K='board'
J=AttributeError
I=False
H='/'
G=print
E='version'
D=None
F=OSError
C=''
import gc as B,os,sys
from ujson import dumps as d
try:from machine import reset
except P:pass
try:from collections import OrderedDict as e
except P:from ucollections import OrderedDict as e
__version__='v1.15.0'
w=2
x=2
f=[L,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise l('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		A.log=D;A.log=logging.getLogger(Y);A._report=[];A.info=_info();G('Port: {}'.format(A.info[o]));G('Board: {}'.format(A.info[K]));B.collect()
		if C:A._fwid=C.lower()
		elif A.info[N]==Z:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=B.mem_free()
		if path:
			if path.endswith(H):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',H)
		try:g(path+H)
		except F:G('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;D=[];I=[]
		for A in Q(H):
			if A.startswith(U)and not A in L.modules:continue
			try:
				E=getattr(H,A)
				try:F=W(type(E)).split("'")[1]
				except R:F=C
				if F in{p,q,r,s,a,b,c}:G=1
				elif F in{t,u}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,W(E),W(type(E)),E,G))
			except J as K:I.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,K))
			except MemoryError as K:sleep(1);reset()
		D=m([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);B.collect();return D,I
	def add_modules(A,modules):A.modules=m(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(A,module_name):
		C=module_name
		if C in A.problematic:return I
		if C in A.excluded:return I
		E='{}/{}.py'.format(A.path,C.replace(L,H));B.collect();D=I
		try:D=A.create_module_stub(C,E)
		except F:return I
		B.collect();return D
	def create_module_stub(J,module_name,file_name=D):
		E=file_name;A=module_name
		if E is D:K=A.replace(L,U)+'.py';E=J.path+H+K
		else:K=E.split(H)[-1]
		if H in A:A=A.replace(H,L)
		M=D
		try:M=__import__(A,D,D,'*');Q=B.mem_free();G('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,K,Q))
		except P:return I
		g(E)
		with S(E,'w')as N:R=X(J.info).replace('OrderedDict(',C).replace('})','}');V='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,J._fwid,R,__version__);N.write(V);N.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(N,M,A,C)
		J._report.append('{{"module": "{}", "file": "{}"}}'.format(A,E.replace('\\',H)))
		if A not in{'os','sys','logging','gc'}:
			try:del M
			except (F,T):pass
			try:del sys.modules[A]
			except T:pass
		B.collect();return O
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';Z='bound_method';Y='Incomplete';Q=in_class;P=object_expr;O='Exception';I=fp;D=indent;B.collect()
		if P in L.problematic:return
		R,N=L.get_obj_attributes(P)
		if N:G(N)
		for (E,K,H,S,f) in R:
			if E in['classmethod','staticmethod','BaseException',O]:continue
			if E[0].isdigit():continue
			if H=="<class 'type'>"and M(D)<=x*4:
				U=C;V=E.endswith(O)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';I.write(A);return
				I.write(A);L.write_object_stub(I,S,'{0}.{1}'.format(obj_name,E),D+'    ',Q+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';I.write(A)
			elif any((A in H for A in[u,t,'closure'])):
				W=Y;X=C
				if Q>0:X='self, '
				if Z in H or Z in K:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,X,W)
				A+=D+'    ...\n\n';I.write(A)
			elif H=="<class 'module'>":0
			elif H.startswith("<class '"):
				J=H[8:-2];A=C
				if J in[r,p,q,s,'bytearray','bytes']:A=d.format(D,E,K,J)
				elif J in[c,b,a]:e={c:'{}',b:'[]',a:'()'};A=d.format(D,E,e[J],J)
				else:
					if J not in['object','set','frozenset']:J=Y
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,J,H,K)
				I.write(A)
			else:I.write("# all other, type = '{0}'\n".format(H));I.write(D+E+' # type: Incomplete\n')
		del R;del N
		try:del E,K,H,S
		except (F,T,n):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,U)
		return A
	def clean(B,path=D):
		if path is D:path=B.path
		G('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except (F,J):return
		for E in C:
			A=v.format(path,E)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(A,filename='modules.json'):
		G('Created stubs for {} modules on board {}\nPath: {}'.format(M(A._report),A._fwid,A.path));E=v.format(A.path,filename);B.collect()
		try:
			with S(E,'w')as C:
				A.write_json_header(C);D=O
				for H in A._report:A.write_json_node(C,H,D);D=I
				A.write_json_end(C)
			J=A._start_free-B.mem_free()
		except F:G('Failed to create the report.')
	def write_json_header(C,f):B='firmware';f.write('{');f.write(d({B:C.info})[1:-1]);f.write(A);f.write(d({Y:{E:__version__},'stubtype':B})[1:-1]);f.write(A);f.write('"modules" :[\n')
	def write_json_node(B,f,n,first):
		if not first:f.write(A)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def g(path):
	A=C=0
	while A!=-1:
		A=path.find(H,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except F as D:
				if D.args[0]==w:
					try:os.mkdir(B)
					except F as E:G('failed to create folder {}'.format(B));raise E
		C=A+1
def V(s):
	A=' on '
	if not s:return C
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else C
def _info():
	k='ev3-pybricks';j='pycom';g='pycopy';d='GENERIC';c='arch';b='cpu';a='ver';S='with';G='mpy';F='build';A=e({N:sys.implementation.name,E:C,F:C,a:C,o:'stm32'if sys.platform.startswith('pyb')else sys.platform,K:d,b:C,G:C,c:C})
	try:A[E]=L.join([X(A)for A in sys.implementation.version])
	except J:pass
	try:W=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[K]=W.strip();A[b]=W.split(S)[1].strip();A[G]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if G in Q(sys.implementation)else C
	except (J,R):pass
	B.collect()
	for I in [A+'/board_info.csv'for A in f]:
		if i(I):
			H=A[K].strip()
			if h(A,H,I):break
			if S in H:
				H=H.split(S)[0].strip()
				if h(A,H,I):break
			A[K]=d
	A[K]=A[K].replace(' ',U);B.collect()
	try:
		A[F]=V(os.uname()[3])
		if not A[F]:A[F]=V(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=V(sys.version.split(';')[1])
	except (J,R):pass
	if A[F]and M(A[F])>5:A[F]=C
	if A[E]==C and sys.platform not in('unix','win32'):
		try:l=os.uname();A[E]=l.release
		except (R,J,TypeError):pass
	for (m,n,p) in [(g,g,'const'),(j,j,'FAT'),(k,'pybricks.hubs','EV3Brick')]:
		try:q=__import__(n,D,D,p);A[N]=m;del q;break
		except (P,T):pass
	if A[N]==k:A['release']='2.0.0'
	if A[N]==Z:
		if A[E]and A[E].endswith('.0')and A[E]>='1.10.0'and A[E]<='1.19.9':A[E]=A[E][:-2]
	if G in A and A[G]:
		O=int(A[G]);Y=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][O>>10]
		if Y:A[c]=Y
		A[G]='v{}.{}'.format(O&255,O>>8&3)
	A[a]=f"v{A[E]}-{A[F]}"if A[F]else f"v{A[E]}";return A
def h(info,board_descr,filename):
	with S(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[K]=D;return O
	return I
def get_root():
	try:A=os.getcwd()
	except (F,J):A=L
	B=A
	for B in [A,'/sd','/flash',H,L]:
		try:C=os.stat(B);break
		except F:continue
	return B
def i(filename):
	try:
		if os.stat(filename)[0]>>14:return O
		return I
	except F:return I
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
	try:A=bytes('abc',encoding='utf8');B=k.__module__;return I
	except (l,J):return O
def main():
	E='/modulelist.txt';stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[]
	for C in f:
		try:
			F=B.mem_free()
			with S(C+E)as D:
				G('Debug: List of modules: '+C+E);A=D.readline()
				while A:
					A=A.strip()
					if M(A)>0 and A[0]!='#':stubber.modules.append(A)
					A=D.readline()
				B.collect();G('Debug: Used memory to load modulelist.txt: '+X(F-B.mem_free())+' bytes');break
		except Exception:pass
	if not stubber.modules:stubber.modules=[Z]
	B.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or k():
	try:y=logging.getLogger(Y);logging.basicConfig(level=logging.INFO)
	except n:pass
	if not i('no_auto_stubber.txt'):
		try:B.threshold(4*1024);B.enable()
		except BaseException:pass
		main()