r='{}/{}'
q='method'
p='function'
o='bool'
n='str'
m='float'
l='int'
k=NameError
j=sorted
i=NotImplementedError
a=',\n'
Z='dict'
Y='list'
X='tuple'
W='micropython'
V=repr
T='_'
S=KeyError
R=dir
Q='family'
P=IndexError
O=ImportError
N=True
M='.'
L='board'
K=len
J=print
I=open
H='/'
A=False
G=AttributeError
F=None
E='version'
D=OSError
C=''
import gc as B,sys,uos as os
from ujson import dumps as b
try:from machine import reset
except O:pass
try:from collections import OrderedDict as c
except O:from ucollections import OrderedDict as c
__version__='v1.12.2'
s=2
t=2
class Stubber:
	def __init__(A,path=F,firmware_id=F):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise i('MicroPython 1.13.0 cannot be stubbed')
		except G:pass
		A._report=[];A.info=_info();B.collect()
		if C:A._fwid=C.lower()
		elif A.info[Q]==W:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=B.mem_free()
		if path:
			if path.endswith(H):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',H)
		try:d(path+H)
		except D:J('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;A=[];J=[]
		for I in R(H):
			try:
				D=getattr(H,I)
				try:E=V(type(D)).split("'")[1]
				except P:E=C
				if E in{l,m,n,o,X,Y,Z}:F=1
				elif E in{p,q}:F=2
				elif E in'class':F=3
				else:F=4
				A.append((I,V(D),V(type(D)),D,F))
			except G as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(I,H,K))
		A=j([A for A in A if not A[0].startswith(T)],key=lambda x:x[4]);B.collect();return A,J
	def add_modules(A,modules):A.modules=j(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(C,module_name):
		E=module_name
		if E in C.problematic:return A
		if E in C.excluded:return A
		G='{}/{}.py'.format(C.path,E.replace(M,H));B.collect();F=A
		try:F=C.create_module_stub(E,G)
		except D:return A
		B.collect();return F
	def create_module_stub(K,module_name,file_name=F):
		G=file_name;E=module_name
		if B.mem_free()<8500:
			try:from machine import reset;reset()
			except O:pass
		if G is F:G=K.path+H+E.replace(M,T)+'.py'
		if H in E:E=E.replace(H,M)
		L=F
		try:L=__import__(E,F,F,'*');J('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(E,G,B.mem_free()))
		except O:return A
		d(G)
		with I(G,'w')as P:Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(E,K._fwid,K.info,__version__);P.write(Q);P.write('from typing import Any\n\n');K.write_object_stub(P,L,E,C)
		K._report.append('{{"module": "{}", "file": "{}"}}'.format(E,G.replace('\\',H)))
		if E not in{'os','sys','logging','gc'}:
			try:del L
			except (D,S):pass
			try:del sys.modules[E]
			except S:pass
		B.collect();return N
	def write_object_stub(M,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';Q=in_class;P=object_expr;O='Exception';H=fp;E=indent;B.collect()
		if P in M.problematic:return
		R,N=M.get_obj_attributes(P)
		if N:J(N)
		for (F,L,G,T,f) in R:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if G=="<class 'type'>"and K(E)<=t*4:
				U=C;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(E,F,U)
				if V:A+=E+'    ...\n';H.write(A);return
				H.write(A);M.write_object_stub(H,T,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);A=E+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=E+'        ...\n\n';H.write(A)
			elif q in G or p in G:
				W=b;a=C
				if Q>0:a='self, '
				if c in G or c in L:A='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,a,W)
				A+=E+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=C
				if I in[n,l,m,o,'bytearray','bytes']:A=d.format(E,F,L,I)
				elif I in[Z,Y,X]:e={Z:'{}',Y:'[]',X:'()'};A=d.format(E,F,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,I,G,L)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(E+F+' # type: Any\n')
		del R;del N
		try:del F,L,G,T
		except (D,S,k):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,T)
		return A
	def clean(B,path=F):
		if path is F:path=B.path
		J('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except (D,G):return
		for E in C:
			A=r.format(path,E)
			try:os.remove(A)
			except D:
				try:B.clean(A);os.rmdir(A)
				except D:pass
	def report(C,filename='modules.json'):
		J('Created stubs for {} modules on board {}\nPath: {}'.format(K(C._report),C._fwid,C.path));G=r.format(C.path,filename);B.collect()
		try:
			with I(G,'w')as E:
				C.write_json_header(E);F=N
				for H in C._report:C.write_json_node(E,H,F);F=A
				C.write_json_end(E)
			L=C._start_free-B.mem_free()
		except D:J('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(b({A:B.info})[1:-1]);f.write(a);f.write(b({'stubber':{E:__version__},'stubtype':A})[1:-1]);f.write(a);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(a)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def d(path):
	A=C=0
	while A!=-1:
		A=path.find(H,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:G=os.stat(B)
			except D as E:
				if E.args[0]==s:
					try:os.mkdir(B)
					except D as F:J('failed to create folder {}'.format(B));raise F
		C=A+1
def U(s):
	A=' on '
	if not s:return C
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else C
def _info():
	j='ev3-pybricks';i='pycom';h='pycopy';g='GENERIC';d='arch';b='cpu';a='ver';X='with';I='mpy';H='build';A=c({Q:sys.implementation.name,E:C,H:C,a:C,'port':'stm32'if sys.platform.startswith('pyb')else sys.platform,L:g,b:C,I:C,d:C})
	try:A[E]=M.join([str(A)for A in sys.implementation.version])
	except G:pass
	try:Y=sys.implementation._machine if'_machine'in R(sys.implementation)else os.uname().machine;A[L]=Y.strip();A[b]=Y.split(X)[1].strip();A[I]=sys.implementation._mpy if'_mpy'in R(sys.implementation)else sys.implementation.mpy if I in R(sys.implementation)else C
	except (G,P):pass
	B.collect()
	try:
		for N in ['board_info.csv','lib/board_info.csv']:
			if f(N):
				J=A[L].strip()
				if e(A,J,N):break
				if X in J:
					J=J.split(X)[0].strip()
					if e(A,J,N):break
				A[L]=g
	except (G,P,D):pass
	A[L]=A[L].replace(' ',T);B.collect()
	try:
		A[H]=U(os.uname()[3])
		if not A[H]:A[H]=U(os.uname()[2])
		if not A[H]and';'in sys.version:A[H]=U(sys.version.split(';')[1])
	except (G,P):pass
	if A[H]and K(A[H])>5:A[H]=C
	if A[E]==C and sys.platform not in('unix','win32'):
		try:k=os.uname();A[E]=k.release
		except (P,G,TypeError):pass
	for (l,m,n) in [(h,h,'const'),(i,i,'FAT'),(j,'pybricks.hubs','EV3Brick')]:
		try:o=__import__(m,F,F,n);A[Q]=l;del o;break
		except (O,S):pass
	if A[Q]==j:A['release']='2.0.0'
	if A[Q]==W:
		if A[E]and A[E].endswith('.0')and A[E]>='1.10.0'and A[E]<='1.20.0':A[E]=A[E][:-2]
	if I in A and A[I]:
		V=int(A[I]);Z=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][V>>10]
		if Z:A[d]=Z
		A[I]='v{}.{}'.format(V&255,V>>8&3)
	A[a]=f"v{A[E]}-{A[H]}"if A[H]else f"v{A[E]}";return A
def e(info,board_descr,filename):
	with I(filename,'r')as C:
		while 1:
			B=C.readline()
			if not B:break
			D,E=B.split(',')[0].strip(),B.split(',')[1].strip()
			if D==board_descr:info[L]=E;return N
	return A
def get_root():
	try:A=os.getcwd()
	except (D,G):A=M
	B=A
	for B in [A,'/sd','/flash',H,M]:
		try:C=os.stat(B);break
		except D:continue
	return B
def f(filename):
	try:os.stat(filename);return N
	except D:return A
def g():sys.exit(1)
def read_path():
	path=C
	if K(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:g()
	elif K(sys.argv)==2:g()
	return path
def h():
	try:B=bytes('abc',encoding='utf8');C=h.__module__;return A
	except (i,G):return N
def main():
	P='failed';L='.done';J='modulelist';import machine as R
	try:B.threshold(512)
	except G:pass
	try:F=I(J+L,'r+b');Q=N
	except D:F=I(J+L,'w+b');Q=A
	stubber=Stubber(path=read_path())
	if not Q:stubber.clean()
	stubber.modules=[W]
	for S in [C,'/libs']:
		try:
			with I(S+J+'.txt')as F:
				for E in F.read().split('\n'):
					E=E.strip()
					if K(E)>0 and E[0]!='#':stubber.modules.append(E)
				B.collect();break
		except D:pass
	B.collect();H={}
	try:
		with I(J+L)as F:
			for E in F.read().split('\n'):
				E=E.strip();B.collect()
				if K(E)>0:T,U=E.split('=',1);H[T]=U
	except (D,SyntaxError):pass
	B.collect();V=[A for A in stubber.modules if A not in H.keys()];B.collect()
	for M in V:
		O=A
		try:O=stubber.create_one_stub(M)
		except MemoryError:R.reset()
		B.collect();H[M]=str(stubber._report[-1]if O else P)
		with I(J+L,'a')as F:F.write('{}={}\n'.format(M,'ok'if O else P))
	if H:stubber._report=[A for(B,A)in H.items()if A!=P];stubber.report()
if __name__=='__main__'or h():
	try:logging.basicConfig(level=logging.INFO)
	except k:pass
	if not f('no_auto_stubber.txt'):main()