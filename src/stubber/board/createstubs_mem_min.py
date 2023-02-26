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
a='_'
Z='dict'
Y='list'
X='tuple'
W=open
V=IndexError
U=repr
T='-'
S='sysname'
R='version'
Q=True
P=ImportError
O='v'
N='build'
M=KeyError
L='.'
K=len
J=AttributeError
I=False
H=print
G=''
F='/'
D=None
C='release'
B=OSError
import gc as E,sys,uos as os
from ujson import dumps as b
__version__='v1.12.2'
r=2
s=2
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise e('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		A._report=[];A.info=_info();E.collect()
		if C:A._fwid=C.lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if path:
			if path.endswith(F):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',F)
		try:c(path+F)
		except B:H('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;A=[];I=[]
		for H in dir(F):
			try:
				B=getattr(F,H)
				try:C=U(type(B)).split("'")[1]
				except V:C=G
				if C in{h,i,j,k,X,Y,Z}:D=1
				elif C in{l,m}:D=2
				elif C in'class':D=3
				else:D=4
				A.append((H,U(B),U(type(B)),B,D))
			except J as K:I.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(H,F,K))
		A=f([B for B in A if not B[0].startswith(a)],key=lambda x:x[4]);E.collect();return A,I
	def add_modules(A,modules):A.modules=f(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:return I
		if A in C.excluded:return I
		D='{}/{}.py'.format(C.path,A.replace(L,F));E.collect();J=E.mem_free();H('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,D,J));G=I
		try:G=C.create_module_stub(A,D)
		except B:return I
		E.collect();return G
	def create_module_stub(C,module_name,file_name=D):
		J=file_name;A=module_name
		if J is D:J=C.path+F+A.replace(L,a)+'.py'
		if F in A:A=A.replace(F,L)
		K=D
		try:K=__import__(A,D,D,'*')
		except P:H('{}Skip module: {:<25} {:<79}'.format('\x1b[1A',A,'Module not found.'));return I
		c(J)
		with W(J,'w')as N:O='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,C._fwid,C.info,__version__);N.write(O);N.write('from typing import Any\n\n');C.write_object_stub(N,K,A,G)
		C._report.append('{{"module": "{}", "file": "{}"}}'.format(A,J.replace('\\',F)))
		if A not in{'os','sys','logging','gc'}:
			try:del K
			except (B,M):pass
			try:del sys.modules[A]
			except M:pass
		E.collect();return Q
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';R=in_class;Q=object_expr;P='Exception';I=fp;C=indent;E.collect()
		if Q in N.problematic:return
		S,O=N.get_obj_attributes(Q)
		if O:H(O)
		for (D,L,F,T,f) in S:
			if D in['classmethod','staticmethod','BaseException',P]:continue
			if F=="<class 'type'>"and K(C)<=s*4:
				U=G;V=D.endswith(P)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=P
				A='\n{}class {}({}):\n'.format(C,D,U)
				if V:A+=C+'    ...\n';I.write(A);return
				I.write(A);N.write_object_stub(I,T,'{0}.{1}'.format(obj_name,D),C+'    ',R+1);A=C+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=C+'        ...\n\n';I.write(A)
			elif m in F or l in F:
				W=b;a=G
				if R>0:a='self, '
				if c in F or c in L:A='{}@classmethod\n'.format(C)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(C,D,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(C,D,a,W)
				A+=C+'    ...\n\n';I.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				J=F[8:-2];A=G
				if J in[j,h,i,k,'bytearray','bytes']:A=d.format(C,D,L,J)
				elif J in[Z,Y,X]:e={Z:'{}',Y:'[]',X:'()'};A=d.format(C,D,e[J],J)
				else:
					if J not in['object','set','frozenset']:J=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(C,D,J,F,L)
				I.write(A)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(C+D+' # type: Any\n')
		del S;del O
		try:del D,L,F,T
		except (B,M,g):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,a)
		return A
	def clean(C,path=D):
		if path is D:path=C.path
		H('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except (B,J):return
		for F in E:
			A=n.format(path,F)
			try:os.remove(A)
			except B:
				try:C.clean(A);os.rmdir(A)
				except B:pass
	def report(A,filename='modules.json'):
		H('Created stubs for {} modules on board {}\nPath: {}'.format(K(A._report),A._fwid,A.path));C=n.format(A.path,filename);E.collect()
		try:
			with W(C,'w')as D:A.write_json_node(D)
			F=A._start_free-E.mem_free()
		except B:H('Failed to create the report.')
	def write_json_node(B,f):
		D='firmware';A=',\n';f.write('{');f.write(b({D:B.info})[1:-1]);f.write(A);f.write(b({'stubber':{R:__version__},'stubtype':D})[1:-1]);f.write(A);f.write('"modules" :[\n');C=Q
		for E in B._report:
			if C:C=I
			else:f.write(A)
			f.write(E)
		f.write('\n]}')
def c(path):
	A=D=0
	while A!=-1:
		A=path.find(F,D)
		if A!=-1:
			C=path[0]if A==0 else path[:A]
			try:I=os.stat(C)
			except B as E:
				if E.args[0]==r:
					try:os.mkdir(C)
					except B as G:H('failed to create folder {}'.format(C));raise G
		D=A+1
def _info():
	a='0.0.0';Z='port';Y='platform';X='name';I='mpy';H='unknown';E='family';B='ver';Q=sys.implementation.name;U='stm32'if sys.platform.startswith('pyb')else sys.platform;A={X:Q,C:a,R:a,N:G,S:H,o:H,p:H,E:Q,Y:U,Z:U,B:G}
	try:A[C]=L.join([str(A)for A in sys.implementation.version]);A[R]=A[C];A[X]=sys.implementation.name;A[I]=sys.implementation.mpy
	except J:pass
	if sys.platform not in('unix','win32'):
		try:t(A)
		except (V,J,TypeError):pass
	try:from pycopy import const as F;A[E]='pycopy';del F
	except (P,M):pass
	try:from pycom import FAT as F;A[E]='pycom';del F
	except (P,M):pass
	if A[Y]=='esp32_LoBo':A[E]='loboris';A[Z]='esp32'
	elif A[S]=='ev3':
		A[E]='ev3-pybricks';A[C]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[C]='2.0.0'
		except P:pass
	if A[C]:A[B]=O+A[C].lstrip(O)
	if A[E]==q:
		if A[C]and A[C]>='1.10.0'and A[C].endswith('.0'):A[B]=A[C][:-2]
		else:A[B]=A[C]
		if A[N]!=G and K(A[N])<4:A[B]+=T+A[N]
	if A[B][0]!=O:A[B]=O+A[B]
	if I in A:
		b=int(A[I]);W=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][b>>10]
		if W:A['arch']=W
	return A
def t(info):
	E=' on ';A=info;B=os.uname();A[S]=B[0];A[o]=B[1];A[C]=B[2];A[p]=B[4]
	if E in B[3]:
		D=B[3].split(E)[0]
		if A[S]=='esp8266':F=D.split(T)[0]if T in D else D;A[R]=A[C]=F.lstrip(O)
		try:A[N]=D.split(T)[1]
		except V:pass
def get_root():
	try:A=os.getcwd()
	except (B,J):A=L
	C=A
	for C in [A,'/sd','/flash',F,L]:
		try:D=os.stat(C);break
		except B:continue
	return C
def u(filename):
	try:os.stat(filename);return Q
	except B:return I
def A():sys.exit(1)
def read_path():
	path=G
	if K(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):path=sys.argv[2]
		else:A()
	elif K(sys.argv)==2:A()
	return path
def d():
	try:A=bytes('abc',encoding='utf8');B=d.__module__;return I
	except (e,J):return Q
def main():
	stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[q]
	for A in [G,'/libs']:
		try:
			with W(A+'modulelist'+'.txt')as C:stubber.modules=[A.strip()for A in C.read().split('\n')if K(A.strip())and A.strip()[0]!='#'];break
		except B:pass
	E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or d():
	try:logging.basicConfig(level=logging.INFO)
	except g:pass
	if not u('no_auto_stubber.txt'):main()