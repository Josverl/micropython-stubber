q='micropython'
p='machine'
o='nodename'
n='{}/{}'
m='method'
l='function'
k='bool'
j='str'
i='float'
h='int'
g=NameError
f=sorted
e=NotImplementedError
Z='_'
Y='dict'
X='list'
W='tuple'
V=IndexError
U=repr
T='-'
S='sysname'
R='version'
Q=ImportError
P='v'
O='build'
N=True
M=KeyError
L='.'
K=len
J=open
I=AttributeError
H=print
G=False
F=''
E='/'
D=None
C='release'
A=OSError
import gc as B,sys,uos as os
from ujson import dumps as a
__version__='1.11.2'
r=2
s=2
class Stubber:
	def __init__(C,path=D,firmware_id=D):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise e('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		C._report=[];C.info=_info();B.collect()
		if D:C._fwid=D.lower()
		else:C._fwid='{family}-{ver}-{port}'.format(**C.info).lower()
		C._start_free=B.mem_free()
		if path:
			if path.endswith(E):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',E)
		try:b(path+E)
		except A:H('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		G=item_instance;A=[];J=[]
		for H in dir(G):
			try:
				C=getattr(G,H)
				try:D=U(type(C)).split("'")[1]
				except V:D=F
				if D in{h,i,j,k,W,X,Y}:E=1
				elif D in{l,m}:E=2
				elif D in'class':E=3
				else:E=4
				A.append((H,U(C),U(type(C)),C,E))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(H,G,K))
		A=f([B for B in A if not B[0].startswith(Z)],key=lambda x:x[4]);B.collect();return A,J
	def add_modules(A,modules):A.modules=f(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(D,module_name):
		C=module_name
		if C in D.problematic:return G
		if C in D.excluded:return G
		F='{}/{}.py'.format(D.path,C.replace(L,E));B.collect();J=B.mem_free();H('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,F,J));I=G
		try:I=D.create_module_stub(C,F)
		except A:return G
		B.collect();return I
	def create_module_stub(I,module_name,file_name=D):
		K=file_name;C=module_name
		if K is D:K=I.path+E+C.replace(L,Z)+'.py'
		if E in C:C=C.replace(E,L)
		O=D
		try:O=__import__(C,D,D,'*')
		except Q:H('{}Skip module: {:<25} {:<79}'.format('\x1b[1A',C,'Module not found.'));return G
		b(K)
		with J(K,'w')as P:R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,I._fwid,I.info,__version__);P.write(R);P.write('from typing import Any\n\n');I.write_object_stub(P,O,C,F)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(C,K.replace('\\',E)))
		if C not in{'os','sys','logging','gc'}:
			try:del O
			except (A,M):pass
			try:del sys.modules[C]
			except M:pass
		B.collect();return N
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';R=in_class;Q=object_expr;P='Exception';I=fp;D=indent;B.collect()
		if Q in N.problematic:return
		S,O=N.get_obj_attributes(Q)
		if O:H(O)
		for (E,L,G,T,f) in S:
			if E in['classmethod','staticmethod','BaseException',P]:continue
			if G=="<class 'type'>"and K(D)<=s*4:
				U=F;V=E.endswith(P)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=P
				C='\n{}class {}({}):\n'.format(D,E,U)
				if V:C+=D+'    ...\n';I.write(C);return
				I.write(C);N.write_object_stub(I,T,'{0}.{1}'.format(obj_name,E),D+'    ',R+1);C=D+'    def __init__(self, *argv, **kwargs) -> None:\n';C+=D+'        ...\n\n';I.write(C)
			elif m in G or l in G:
				Z=b;a=F
				if R>0:a='self, '
				if c in G or c in L:C='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,Z)
				else:C='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,a,Z)
				C+=D+'    ...\n\n';I.write(C)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				J=G[8:-2];C=F
				if J in[j,h,i,k,'bytearray','bytes']:C=d.format(D,E,L,J)
				elif J in[Y,X,W]:e={Y:'{}',X:'[]',W:'()'};C=d.format(D,E,e[J],J)
				else:
					if J not in['object','set','frozenset']:J=b
					C='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,J,G,L)
				I.write(C)
			else:I.write("# all other, type = '{0}'\n".format(G));I.write(D+E+' # type: Any\n')
		del S;del O
		try:del E,L,G,T
		except (A,M,g):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,Z)
		return A
	def clean(C,path=D):
		if path is D:path=C.path
		H('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except (A,I):return
		for F in E:
			B=n.format(path,F)
			try:os.remove(B)
			except A:
				try:C.clean(B);os.rmdir(B)
				except A:pass
	def report(C,filename='modules.json'):
		H('Created stubs for {} modules on board {}\nPath: {}'.format(K(C._report),C._fwid,C.path));D=n.format(C.path,filename);B.collect()
		try:
			with J(D,'w')as E:C.write_json_node(E)
			F=C._start_free-B.mem_free()
		except A:H('Failed to create the report.')
	def write_json_node(B,f):
		D='firmware';A=',\n';f.write('{');f.write(a({D:B.info})[1:-1]);f.write(A);f.write(a({'stubber':{R:__version__},'stubtype':D})[1:-1]);f.write(A);f.write('"modules" :[\n');C=N
		for E in B._report:
			if C:C=G
			else:f.write(A)
			f.write(E)
		f.write('\n]}')
def b(path):
	B=D=0
	while B!=-1:
		B=path.find(E,D)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except A as F:
				if F.args[0]==r:
					try:os.mkdir(C)
					except A as G:H('failed to create folder {}'.format(C));raise G
		D=B+1
def _info():
	a='0.0.0';Z='port';Y='platform';X='name';J='mpy';H='unknown';E='family';B='ver';N=sys.implementation.name;U='stm32'if sys.platform.startswith('pyb')else sys.platform;A={X:N,C:a,R:a,O:F,S:H,o:H,p:H,E:N,Y:U,Z:U,B:F}
	try:A[C]=L.join([str(A)for A in sys.implementation.version]);A[R]=A[C];A[X]=sys.implementation.name;A[J]=sys.implementation.mpy
	except I:pass
	if sys.platform not in('unix','win32'):
		try:t(A)
		except (V,I,TypeError):pass
	try:from pycopy import const as G;A[E]='pycopy';del G
	except (Q,M):pass
	try:from pycom import FAT as G;A[E]='pycom';del G
	except (Q,M):pass
	if A[Y]=='esp32_LoBo':A[E]='loboris';A[Z]='esp32'
	elif A[S]=='ev3':
		A[E]='ev3-pybricks';A[C]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[C]='2.0.0'
		except Q:pass
	if A[C]:A[B]=P+A[C].lstrip(P)
	if A[E]==q:
		if A[C]and A[C]>='1.10.0'and A[C].endswith('.0'):A[B]=A[C][:-2]
		else:A[B]=A[C]
		if A[O]!=F and K(A[O])<4:A[B]+=T+A[O]
	if A[B][0]!=P:A[B]=P+A[B]
	if J in A:
		b=int(A[J]);W=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][b>>10]
		if W:A['arch']=W
	return A
def t(info):
	E=' on ';A=info;B=os.uname();A[S]=B[0];A[o]=B[1];A[C]=B[2];A[p]=B[4]
	if E in B[3]:
		D=B[3].split(E)[0]
		if A[S]=='esp8266':F=D.split(T)[0]if T in D else D;A[R]=A[C]=F.lstrip(P)
		try:A[O]=D.split(T)[1]
		except V:pass
def get_root():
	try:B=os.getcwd()
	except (A,I):B=L
	C=B
	for C in [B,'/sd','/flash',E,L]:
		try:D=os.stat(C);break
		except A:continue
	return C
def u(filename):
	try:os.stat(filename);return N
	except A:return G
def c():sys.exit(1)
def read_path():
	path=F
	if K(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:c()
	elif K(sys.argv)==2:c()
	return path
def d():
	try:A=bytes('abc',encoding='utf8');B=d.__module__;return G
	except (e,I):return N
def main():
	R='failed';I='.done';E='modulelist';import machine as S
	try:C=J(E+I,'r+b');M=N
	except A:C=J(E+I,'w+b');M=G
	stubber=Stubber(path=read_path())
	if not M:stubber.clean()
	stubber.modules=[q]
	for T in [F,'/libs']:
		try:
			with J(T+E+'.txt')as C:stubber.modules=[A.strip()for A in C.read().split('\n')if K(A.strip())and A.strip()[0]!='#'];break
		except A:pass
	B.collect();D={}
	try:
		with J(E+I)as C:
			for H in C.read().split('\n'):
				H=H.strip();B.collect()
				if K(H)>0:U,V=H.split('=',1);D[U]=V
	except (A,SyntaxError):pass
	B.collect();O=[A for A in O if A not in D.keys()];B.collect()
	for L in O:
		P=G
		try:P=stubber.create_one_stub(L)
		except MemoryError:S.reset()
		Q=stubber._report[-1]if P else R;D[L]=str(Q)
		with J(E+I,'a')as C:C.write('{}={}\n'.format(L,Q))
	if D:stubber._report=[A for(B,A)in D.items()if A!=R];stubber.report()
if __name__=='__main__'or d():
	try:logging.basicConfig(level=logging.INFO)
	except g:pass
	if not u('no_auto_stubber.txt'):main()