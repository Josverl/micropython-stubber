t='lib'
s='/lib'
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
R=IndexError
Q=dir
P='family'
O=ImportError
N=True
M='board'
L=len
K=print
J='.'
I=open
H='/'
G=AttributeError
F=False
E=None
D='version'
A=OSError
C=''
import gc as B,sys,uos as os
from ujson import dumps as b
try:from machine import reset
except O:pass
try:from collections import OrderedDict as c
except O:from ucollections import OrderedDict as c
__version__='v1.12.2'
u=2
v=2
class Stubber:
	def __init__(C,path=E,firmware_id=E):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise i('MicroPython 1.13.0 cannot be stubbed')
		except G:pass
		C._report=[];C.info=_info();B.collect()
		if D:C._fwid=D.lower()
		elif C.info[P]==W:C._fwid='{family}-{ver}-{port}-{board}'.format(**C.info)
		else:C._fwid='{family}-{ver}-{port}'.format(**C.info)
		C._start_free=B.mem_free()
		if path:
			if path.endswith(H):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',H)
		try:d(path+H)
		except A:K('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;A=[];J=[]
		for I in Q(H):
			try:
				D=getattr(H,I)
				try:E=V(type(D)).split("'")[1]
				except R:E=C
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
		D=module_name
		if D in C.problematic:return F
		if D in C.excluded:return F
		G='{}/{}.py'.format(C.path,D.replace(J,H));B.collect();E=F
		try:E=C.create_module_stub(D,G)
		except A:return F
		B.collect();return E
	def create_module_stub(L,module_name,file_name=E):
		G=file_name;D=module_name
		if B.mem_free()<8500:
			try:from machine import reset;reset()
			except O:pass
		if G is E:G=L.path+H+D.replace(J,T)+'.py'
		if H in D:D=D.replace(H,J)
		M=E
		try:M=__import__(D,E,E,'*');K('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(D,G,B.mem_free()))
		except O:return F
		d(G)
		with I(G,'w')as P:Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,L._fwid,L.info,__version__);P.write(Q);P.write('from typing import Any\n\n');L.write_object_stub(P,M,D,C)
		L._report.append('{{"module": "{}", "file": "{}"}}'.format(D,G.replace('\\',H)))
		if D not in{'os','sys','logging','gc'}:
			try:del M
			except (A,S):pass
			try:del sys.modules[D]
			except S:pass
		B.collect();return N
	def write_object_stub(M,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';Q=in_class;P=object_expr;O='Exception';H=fp;E=indent;B.collect()
		if P in M.problematic:return
		R,N=M.get_obj_attributes(P)
		if N:K(N)
		for (F,J,G,T,f) in R:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if G=="<class 'type'>"and L(E)<=v*4:
				U=C;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				D='\n{}class {}({}):\n'.format(E,F,U)
				if V:D+=E+'    ...\n';H.write(D);return
				H.write(D);M.write_object_stub(H,T,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';H.write(D)
			elif q in G or p in G:
				W=b;a=C
				if Q>0:a='self, '
				if c in G or c in J:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,a,W)
				D+=E+'    ...\n\n';H.write(D)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];D=C
				if I in[n,l,m,o,'bytearray','bytes']:D=d.format(E,F,J,I)
				elif I in[Z,Y,X]:e={Z:'{}',Y:'[]',X:'()'};D=d.format(E,F,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					D='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,I,G,J)
				H.write(D)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(E+F+' # type: Any\n')
		del R;del N
		try:del F,J,G,T
		except (A,S,k):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,T)
		return A
	def clean(C,path=E):
		if path is E:path=C.path
		K('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);D=os.listdir(path)
		except (A,G):return
		for F in D:
			B=r.format(path,F)
			try:os.remove(B)
			except A:
				try:C.clean(B);os.rmdir(B)
				except A:pass
	def report(C,filename='modules.json'):
		K('Created stubs for {} modules on board {}\nPath: {}'.format(L(C._report),C._fwid,C.path));G=r.format(C.path,filename);B.collect()
		try:
			with I(G,'w')as D:
				C.write_json_header(D);E=N
				for H in C._report:C.write_json_node(D,H,E);E=F
				C.write_json_end(D)
			J=C._start_free-B.mem_free()
		except A:K('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(b({A:B.info})[1:-1]);f.write(a);f.write(b({'stubber':{D:__version__},'stubtype':A})[1:-1]);f.write(a);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(a)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def d(path):
	B=D=0
	while B!=-1:
		B=path.find(H,D)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:G=os.stat(C)
			except A as E:
				if E.args[0]==u:
					try:os.mkdir(C)
					except A as F:K('failed to create folder {}'.format(C));raise F
		D=B+1
def U(s):
	A=' on '
	if not s:return C
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else C
def _info():
	i='ev3-pybricks';h='pycom';g='pycopy';d='GENERIC';b='arch';a='cpu';Z='ver';V='with';H='mpy';F='build';A=c({P:sys.implementation.name,D:C,F:C,Z:C,'port':'stm32'if sys.platform.startswith('pyb')else sys.platform,M:d,a:C,H:C,b:C})
	try:A[D]=J.join([str(A)for A in sys.implementation.version])
	except G:pass
	try:X=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[M]=X.strip();A[a]=X.split(V)[1].strip();A[H]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if H in Q(sys.implementation)else C
	except (G,R):pass
	B.collect()
	for K in [A+'/board_info.csv'for A in[J,s,t]]:
		if f(K):
			I=A[M].strip()
			if e(A,I,K):break
			if V in I:
				I=I.split(V)[0].strip()
				if e(A,I,K):break
			A[M]=d
	A[M]=A[M].replace(' ',T);B.collect()
	try:
		A[F]=U(os.uname()[3])
		if not A[F]:A[F]=U(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=U(sys.version.split(';')[1])
	except (G,R):pass
	if A[F]and L(A[F])>5:A[F]=C
	if A[D]==C and sys.platform not in('unix','win32'):
		try:j=os.uname();A[D]=j.release
		except (R,G,TypeError):pass
	for (k,l,m) in [(g,g,'const'),(h,h,'FAT'),(i,'pybricks.hubs','EV3Brick')]:
		try:n=__import__(l,E,E,m);A[P]=k;del n;break
		except (O,S):pass
	if A[P]==i:A['release']='2.0.0'
	if A[P]==W:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.20.0':A[D]=A[D][:-2]
	if H in A and A[H]:
		N=int(A[H]);Y=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][N>>10]
		if Y:A[b]=Y
		A[H]='v{}.{}'.format(N&255,N>>8&3)
	A[Z]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def e(info,board_descr,filename):
	with I(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[M]=D;return N
	return F
def get_root():
	try:B=os.getcwd()
	except (A,G):B=J
	C=B
	for C in [B,'/sd','/flash',H,J]:
		try:D=os.stat(C);break
		except A:continue
	return C
def f(filename):
	try:
		if os.stat(filename)[0]>>14:return N
		return F
	except A:return F
def g():sys.exit(1)
def read_path():
	path=C
	if L(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:g()
	elif L(sys.argv)==2:g()
	return path
def h():
	try:A=bytes('abc',encoding='utf8');B=h.__module__;return F
	except (i,G):return N
def main():
	P='failed';K='.done';H='modulelist';import machine as R
	try:B.threshold(512)
	except G:pass
	try:D=I(H+K,'r+b');Q=N
	except A:D=I(H+K,'w+b');Q=F
	stubber=Stubber(path=read_path())
	if not Q:stubber.clean()
	stubber.modules=[W]
	for S in [J,s,t]:
		try:
			with I(S+H+'.txt')as D:
				for C in D.read().split('\n'):
					C=C.strip()
					if L(C)>0 and C[0]!='#':stubber.modules.append(C)
				B.collect();break
		except A:pass
	B.collect();E={}
	try:
		with I(H+K)as D:
			for C in D.read().split('\n'):
				C=C.strip();B.collect()
				if L(C)>0:T,U=C.split('=',1);E[T]=U
	except (A,SyntaxError):pass
	B.collect();V=[A for A in stubber.modules if A not in E.keys()];B.collect()
	for M in V:
		O=F
		try:O=stubber.create_one_stub(M)
		except MemoryError:R.reset()
		B.collect();E[M]=str(stubber._report[-1]if O else P)
		with I(H+K,'a')as D:D.write('{}={}\n'.format(M,'ok'if O else P))
	if E:stubber._report=[A for(B,A)in E.items()if A!=P];stubber.report()
if __name__=='__main__'or h():
	try:logging.basicConfig(level=logging.INFO)
	except k:pass
	if not f('no_auto_stubber.txt'):main()