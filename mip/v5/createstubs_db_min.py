u='lib'
t='/lib'
s='{}/{}'
r='method'
q='function'
p='bool'
o='str'
n='float'
m='int'
l='port'
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
M=len
L='.'
K='board'
J=open
I=print
H=AttributeError
G='/'
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
v=2
w=2
class Stubber:
	def __init__(C,path=E,firmware_id=E):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise i('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		C._report=[];C.info=_info();I('Port: {}'.format(C.info[l]));I('Board: {}'.format(C.info[K]));B.collect()
		if D:C._fwid=D.lower()
		elif C.info[P]==W:C._fwid='{family}-{ver}-{port}-{board}'.format(**C.info)
		else:C._fwid='{family}-{ver}-{port}'.format(**C.info)
		C._start_free=B.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',G)
		try:d(path+G)
		except A:I('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		G=item_instance;A=[];J=[]
		for I in Q(G):
			try:
				D=getattr(G,I)
				try:E=V(type(D)).split("'")[1]
				except R:E=C
				if E in{m,n,o,p,X,Y,Z}:F=1
				elif E in{q,r}:F=2
				elif E in'class':F=3
				else:F=4
				A.append((I,V(D),V(type(D)),D,F))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(I,G,K))
		A=j([A for A in A if not A[0].startswith(T)],key=lambda x:x[4]);B.collect();return A,J
	def add_modules(A,modules):A.modules=j(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(C,module_name):
		D=module_name
		if D in C.problematic:return F
		if D in C.excluded:return F
		H='{}/{}.py'.format(C.path,D.replace(L,G));B.collect();E=F
		try:E=C.create_module_stub(D,H)
		except A:return F
		B.collect();return E
	def create_module_stub(K,module_name,file_name=E):
		H=file_name;D=module_name
		if B.mem_free()<8500:
			try:from machine import reset;reset()
			except O:pass
		if H is E:M=D.replace(L,T)+'.py';H=K.path+G+M
		else:M=H.split(G)[-1]
		if G in D:D=D.replace(G,L)
		P=E
		try:P=__import__(D,E,E,'*');I('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(D,M,B.mem_free()))
		except O:return F
		d(H)
		with J(H,'w')as Q:R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,K._fwid,K.info,__version__);Q.write(R);Q.write('from typing import Any\n\n');K.write_object_stub(Q,P,D,C)
		K._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del P
			except (A,S):pass
			try:del sys.modules[D]
			except S:pass
		B.collect();return N
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';Q=in_class;P=object_expr;O='Exception';H=fp;E=indent;B.collect()
		if P in L.problematic:return
		R,N=L.get_obj_attributes(P)
		if N:I(N)
		for (F,K,G,T,f) in R:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if G=="<class 'type'>"and M(E)<=w*4:
				U=C;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				D='\n{}class {}({}):\n'.format(E,F,U)
				if V:D+=E+'    ...\n';H.write(D);return
				H.write(D);L.write_object_stub(H,T,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';H.write(D)
			elif r in G or q in G:
				W=b;a=C
				if Q>0:a='self, '
				if c in G or c in K:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,a,W)
				D+=E+'    ...\n\n';H.write(D)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				J=G[8:-2];D=C
				if J in[o,m,n,p,'bytearray','bytes']:D=d.format(E,F,K,J)
				elif J in[Z,Y,X]:e={Z:'{}',Y:'[]',X:'()'};D=d.format(E,F,e[J],J)
				else:
					if J not in['object','set','frozenset']:J=b
					D='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,J,G,K)
				H.write(D)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(E+F+' # type: Any\n')
		del R;del N
		try:del F,K,G,T
		except (A,S,k):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,T)
		return A
	def clean(C,path=E):
		if path is E:path=C.path
		I('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);D=os.listdir(path)
		except (A,H):return
		for F in D:
			B=s.format(path,F)
			try:os.remove(B)
			except A:
				try:C.clean(B);os.rmdir(B)
				except A:pass
	def report(C,filename='modules.json'):
		I('Created stubs for {} modules on board {}\nPath: {}'.format(M(C._report),C._fwid,C.path));G=s.format(C.path,filename);B.collect()
		try:
			with J(G,'w')as D:
				C.write_json_header(D);E=N
				for H in C._report:C.write_json_node(D,H,E);E=F
				C.write_json_end(D)
			K=C._start_free-B.mem_free()
		except A:I('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(b({A:B.info})[1:-1]);f.write(a);f.write(b({'stubber':{D:__version__},'stubtype':A})[1:-1]);f.write(a);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(a)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def d(path):
	B=D=0
	while B!=-1:
		B=path.find(G,D)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:H=os.stat(C)
			except A as E:
				if E.args[0]==v:
					try:os.mkdir(C)
					except A as F:I('failed to create folder {}'.format(C));raise F
		D=B+1
def U(s):
	A=' on '
	if not s:return C
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else C
def _info():
	i='ev3-pybricks';h='pycom';g='pycopy';d='GENERIC';b='arch';a='cpu';Z='ver';V='with';G='mpy';F='build';A=c({P:sys.implementation.name,D:C,F:C,Z:C,l:'stm32'if sys.platform.startswith('pyb')else sys.platform,K:d,a:C,G:C,b:C})
	try:A[D]=L.join([str(A)for A in sys.implementation.version])
	except H:pass
	try:X=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[K]=X.strip();A[a]=X.split(V)[1].strip();A[G]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if G in Q(sys.implementation)else C
	except (H,R):pass
	B.collect()
	for J in [A+'/board_info.csv'for A in[L,t,u]]:
		if f(J):
			I=A[K].strip()
			if e(A,I,J):break
			if V in I:
				I=I.split(V)[0].strip()
				if e(A,I,J):break
			A[K]=d
	A[K]=A[K].replace(' ',T);B.collect()
	try:
		A[F]=U(os.uname()[3])
		if not A[F]:A[F]=U(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=U(sys.version.split(';')[1])
	except (H,R):pass
	if A[F]and M(A[F])>5:A[F]=C
	if A[D]==C and sys.platform not in('unix','win32'):
		try:j=os.uname();A[D]=j.release
		except (R,H,TypeError):pass
	for (k,m,n) in [(g,g,'const'),(h,h,'FAT'),(i,'pybricks.hubs','EV3Brick')]:
		try:o=__import__(m,E,E,n);A[P]=k;del o;break
		except (O,S):pass
	if A[P]==i:A['release']='2.0.0'
	if A[P]==W:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.20.0':A[D]=A[D][:-2]
	if G in A and A[G]:
		N=int(A[G]);Y=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][N>>10]
		if Y:A[b]=Y
		A[G]='v{}.{}'.format(N&255,N>>8&3)
	A[Z]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def e(info,board_descr,filename):
	with J(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[K]=D;return N
	return F
def get_root():
	try:B=os.getcwd()
	except (A,H):B=L
	C=B
	for C in [B,'/sd','/flash',G,L]:
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
	if M(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:g()
	elif M(sys.argv)==2:g()
	return path
def h():
	try:A=bytes('abc',encoding='utf8');B=h.__module__;return F
	except (i,H):return N
def main():
	O='failed';G='modulelist.done';import machine as Q
	try:B.threshold(512)
	except H:pass
	try:D=J(G,'r+b');P=N
	except A:D=J(G,'w+b');P=F
	stubber=Stubber(path=read_path())
	if not P:stubber.clean()
	stubber.modules=[W]
	for R in [L,t,u]:
		try:
			with J(R+'/modulelist.txt')as D:
				for C in D.read().split('\n'):
					C=C.strip()
					if M(C)>0 and C[0]!='#':stubber.modules.append(C)
				B.collect();break
		except A:pass
	B.collect();E={}
	try:
		with J(G)as D:
			for C in D.read().split('\n'):
				C=C.strip();B.collect()
				if M(C)>0:S,T=C.split('=',1);E[S]=T
	except (A,SyntaxError):pass
	B.collect();U=[A for A in stubber.modules if A not in E.keys()];B.collect()
	for I in U:
		K=F
		try:K=stubber.create_one_stub(I)
		except MemoryError:Q.reset()
		B.collect();E[I]=str(stubber._report[-1]if K else O)
		with J(G,'a')as D:D.write('{}={}\n'.format(I,'ok'if K else O))
	if E:stubber._report=[A for(B,A)in E.items()if A!=O];stubber.report()
if __name__=='__main__'or h():
	try:logging.basicConfig(level=logging.INFO)
	except k:pass
	if not f('no_auto_stubber.txt'):main()