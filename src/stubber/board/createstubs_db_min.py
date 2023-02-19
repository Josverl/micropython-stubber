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
G=''
F=False
E='/'
D=None
C='release'
B=OSError
import gc as A,sys,uos as os
from ujson import dumps as a
__version__='1.11.2'
q=2
r=2
class Stubber:
	def __init__(C,path=D,firmware_id=D):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise e('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		C._report=[];C.info=_info();A.collect()
		if D:C._fwid=D.lower()
		else:C._fwid='{family}-{ver}-{port}'.format(**C.info).lower()
		C._start_free=A.mem_free()
		if path:
			if path.endswith(E):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',E)
		try:b(path+E)
		except B:H('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;B=[];J=[]
		for H in dir(F):
			try:
				C=getattr(F,H)
				try:D=U(type(C)).split("'")[1]
				except V:D=G
				if D in{h,i,j,k,W,X,Y}:E=1
				elif D in{l,m}:E=2
				elif D in'class':E=3
				else:E=4
				B.append((H,U(C),U(type(C)),C,E))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(H,F,K))
		B=f([A for A in B if not A[0].startswith(Z)],key=lambda x:x[4]);A.collect();return B,J
	def add_modules(A,modules):A.modules=f(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.collect()
		for C in B.modules:B.create_one_stub(C)
	def create_one_stub(D,module_name):
		C=module_name
		if C in D.problematic:return F
		if C in D.excluded:return F
		G='{}/{}.py'.format(D.path,C.replace(L,E));A.collect();J=A.mem_free();H('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,G,J));I=F
		try:I=D.create_module_stub(C,G)
		except B:return F
		A.collect();return I
	def create_module_stub(I,module_name,file_name=D):
		K=file_name;C=module_name
		if K is D:K=I.path+E+C.replace(L,Z)+'.py'
		if E in C:C=C.replace(E,L)
		O=D
		try:O=__import__(C,D,D,'*')
		except Q:H('{}Skip module: {:<25} {:<79}'.format('\x1b[1A',C,'Module not found.'));return F
		b(K)
		with J(K,'w')as P:R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,I._fwid,I.info,__version__);P.write(R);P.write('from typing import Any\n\n');I.write_object_stub(P,O,C,G)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(C,K.replace('\\',E)))
		if C not in{'os','sys','logging','gc'}:
			try:del O
			except (B,M):pass
			try:del sys.modules[C]
			except M:pass
		A.collect();return N
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';R=in_class;Q=object_expr;P='Exception';I=fp;D=indent;A.collect()
		if Q in N.problematic:return
		S,O=N.get_obj_attributes(Q)
		if O:H(O)
		for (E,L,F,T,f) in S:
			if E in['classmethod','staticmethod','BaseException',P]:continue
			if F=="<class 'type'>"and K(D)<=r*4:
				U=G;V=E.endswith(P)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=P
				C='\n{}class {}({}):\n'.format(D,E,U)
				if V:C+=D+'    ...\n';I.write(C);return
				I.write(C);N.write_object_stub(I,T,'{0}.{1}'.format(obj_name,E),D+'    ',R+1);C=D+'    def __init__(self, *argv, **kwargs) -> None:\n';C+=D+'        ...\n\n';I.write(C)
			elif m in F or l in F:
				Z=b;a=G
				if R>0:a='self, '
				if c in F or c in L:C='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,Z)
				else:C='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,a,Z)
				C+=D+'    ...\n\n';I.write(C)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				J=F[8:-2];C=G
				if J in[j,h,i,k,'bytearray','bytes']:C=d.format(D,E,L,J)
				elif J in[Y,X,W]:e={Y:'{}',X:'[]',W:'()'};C=d.format(D,E,e[J],J)
				else:
					if J not in['object','set','frozenset']:J=b
					C='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,J,F,L)
				I.write(C)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(D+E+' # type: Any\n')
		del S;del O
		try:del E,L,F,T
		except (B,M,g):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,Z)
		return A
	def clean(C,path=D):
		if path is D:path=C.path
		H('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except (B,I):return
		for F in E:
			A=n.format(path,F)
			try:os.remove(A)
			except B:
				try:C.clean(A);os.rmdir(A)
				except B:pass
	def report(C,filename='modules.json'):
		H('Created stubs for {} modules on board {}\nPath: {}'.format(K(C._report),C._fwid,C.path));D=n.format(C.path,filename);A.collect()
		try:
			with J(D,'w')as E:C.write_json_node(E)
			F=C._start_free-A.mem_free()
		except B:H('Failed to create the report.')
	def write_json_node(B,f):
		D='firmware';A=',\n';f.write('{');f.write(a({D:B.info})[1:-1]);f.write(A);f.write(a({'stubber':{R:__version__},'stubtype':D})[1:-1]);f.write(A);f.write('"modules" :[\n');C=N
		for E in B._report:
			if C:C=F
			else:f.write(A)
			f.write(E)
		f.write('\n]}')
def b(path):
	A=D=0
	while A!=-1:
		A=path.find(E,D)
		if A!=-1:
			C=path[0]if A==0 else path[:A]
			try:I=os.stat(C)
			except B as F:
				if F.args[0]==q:
					try:os.mkdir(C)
					except B as G:H('failed to create folder {}'.format(C));raise G
		D=A+1
def _info():
	a='0.0.0';Z='port';Y='platform';X='name';J='mpy';H='unknown';E='family';B='ver';N=sys.implementation.name;U='stm32'if sys.platform.startswith('pyb')else sys.platform;A={X:N,C:a,R:a,O:G,S:H,o:H,p:H,E:N,Y:U,Z:U,B:G}
	try:A[C]=L.join([str(A)for A in sys.implementation.version]);A[R]=A[C];A[X]=sys.implementation.name;A[J]=sys.implementation.mpy
	except I:pass
	if sys.platform not in('unix','win32'):
		try:s(A)
		except (V,I,TypeError):pass
	try:from pycopy import const as F;A[E]='pycopy';del F
	except (Q,M):pass
	try:from pycom import FAT as F;A[E]='pycom';del F
	except (Q,M):pass
	if A[Y]=='esp32_LoBo':A[E]='loboris';A[Z]='esp32'
	elif A[S]=='ev3':
		A[E]='ev3-pybricks';A[C]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[C]='2.0.0'
		except Q:pass
	if A[C]:A[B]=P+A[C].lstrip(P)
	if A[E]=='micropython':
		if A[C]and A[C]>='1.10.0'and A[C].endswith('.0'):A[B]=A[C][:-2]
		else:A[B]=A[C]
		if A[O]!=G and K(A[O])<4:A[B]+=T+A[O]
	if A[B][0]!=P:A[B]=P+A[B]
	if J in A:
		b=int(A[J]);W=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][b>>10]
		if W:A['arch']=W
	return A
def s(info):
	E=' on ';A=info;B=os.uname();A[S]=B[0];A[o]=B[1];A[C]=B[2];A[p]=B[4]
	if E in B[3]:
		D=B[3].split(E)[0]
		if A[S]=='esp8266':F=D.split(T)[0]if T in D else D;A[R]=A[C]=F.lstrip(P)
		try:A[O]=D.split(T)[1]
		except V:pass
def get_root():
	try:A=os.getcwd()
	except (B,I):A=L
	C=A
	for C in [A,'/sd','/flash',E,L]:
		try:D=os.stat(C);break
		except B:continue
	return C
def t(filename):
	try:os.stat(filename);return N
	except B:return F
def c():sys.exit(1)
def read_path():
	path=G
	if K(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:c()
	elif K(sys.argv)==2:c()
	return path
def d():
	try:A=bytes('abc',encoding='utf8');B=d.__module__;return F
	except (e,I):return N
def main():
	R='failed';Q='\\n';H='.done';E='modulelist';import machine as S
	try:C=J(E+H,'r+b');M=N
	except B:C=J(E+H,'w+b');M=F
	stubber=Stubber(path=read_path())
	if not M:stubber.clean()
	with J(E+'.txt')as C:I=[A.strip()for A in C.read().split(Q)if K(A.strip())and A.strip()[0]!='#']
	A.collect();D={}
	try:
		with J(E+H)as C:
			for G in C.read().split(Q):
				G=G.strip();A.collect()
				if K(G)>0:T,U=G.split('=',1);D[T]=U
	except (B,SyntaxError):pass
	A.collect();I=[A for A in I if A not in D.keys()];A.collect()
	for L in I:
		O=F
		try:O=stubber.create_one_stub(L)
		except MemoryError:S.reset()
		P=stubber._report[-1]if O else R;D[L]=str(P)
		with J(E+H,'a')as C:C.write('{}={}\n'.format(L,P))
	if D:stubber._report=[A for(B,A)in D.items()if A!=R];stubber.report()
if __name__=='__main__'or d():
	try:logging.basicConfig(level=logging.INFO)
	except g:pass
	if not t('no_auto_stubber.txt'):main()