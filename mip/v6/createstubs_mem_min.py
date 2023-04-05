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
V=open
U=IndexError
T=repr
S='-'
R='sysname'
Q='version'
P=True
O=ImportError
N='v'
M='build'
L=KeyError
J='.'
K=len
I=AttributeError
G=False
H=print
F=''
D=None
A='/'
C='release'
B=OSError
import gc as E,sys,uos as os
from ujson import dumps as a
__version__='v1.12.2'
r=2
s=2
class Stubber:
	def __init__(C,path=D,firmware_id=D):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise e('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		C._report=[];C.info=_info();E.collect()
		if D:C._fwid=D.lower()
		else:C._fwid='{family}-{ver}-{port}'.format(**C.info).lower()
		C._start_free=E.mem_free()
		if path:
			if path.endswith(A):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',A)
		try:b(path+A)
		except B:H('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		G=item_instance;A=[];J=[]
		for H in dir(G):
			try:
				B=getattr(G,H)
				try:C=T(type(B)).split("'")[1]
				except U:C=F
				if C in{h,i,j,k,W,X,Y}:D=1
				elif C in{l,m}:D=2
				elif C in'class':D=3
				else:D=4
				A.append((H,T(B),T(type(B)),B,D))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(H,G,K))
		A=f([B for B in A if not B[0].startswith(Z)],key=lambda x:x[4]);E.collect();return A,J
	def add_modules(A,modules):A.modules=f(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(D,module_name):
		C=module_name
		if C in D.problematic:return G
		if C in D.excluded:return G
		F='{}/{}.py'.format(D.path,C.replace(J,A));E.collect();K=E.mem_free();H('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,F,K));I=G
		try:I=D.create_module_stub(C,F)
		except B:return G
		E.collect();return I
	def create_module_stub(I,module_name,file_name=D):
		K=file_name;C=module_name
		if K is D:K=I.path+A+C.replace(J,Z)+'.py'
		if A in C:C=C.replace(A,J)
		M=D
		try:M=__import__(C,D,D,'*')
		except O:H('{}Skip module: {:<25} {:<79}'.format('\x1b[1A',C,'Module not found.'));return G
		b(K)
		with V(K,'w')as N:Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,I._fwid,I.info,__version__);N.write(Q);N.write('from typing import Any\n\n');I.write_object_stub(N,M,C,F)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(C,K.replace('\\',A)))
		if C not in{'os','sys','logging','gc'}:
			try:del M
			except (B,L):pass
			try:del sys.modules[C]
			except L:pass
		E.collect();return P
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';R=in_class;Q=object_expr;P='Exception';I=fp;C=indent;E.collect()
		if Q in N.problematic:return
		S,O=N.get_obj_attributes(Q)
		if O:H(O)
		for (D,M,G,T,f) in S:
			if D in['classmethod','staticmethod','BaseException',P]:continue
			if G=="<class 'type'>"and K(C)<=s*4:
				U=F;V=D.endswith(P)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=P
				A='\n{}class {}({}):\n'.format(C,D,U)
				if V:A+=C+'    ...\n';I.write(A);return
				I.write(A);N.write_object_stub(I,T,'{0}.{1}'.format(obj_name,D),C+'    ',R+1);A=C+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=C+'        ...\n\n';I.write(A)
			elif m in G or l in G:
				Z=b;a=F
				if R>0:a='self, '
				if c in G or c in M:A='{}@classmethod\n'.format(C)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(C,D,Z)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(C,D,a,Z)
				A+=C+'    ...\n\n';I.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				J=G[8:-2];A=F
				if J in[j,h,i,k,'bytearray','bytes']:A=d.format(C,D,M,J)
				elif J in[Y,X,W]:e={Y:'{}',X:'[]',W:'()'};A=d.format(C,D,e[J],J)
				else:
					if J not in['object','set','frozenset']:J=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(C,D,J,G,M)
				I.write(A)
			else:I.write("# all other, type = '{0}'\n".format(G));I.write(C+D+' # type: Any\n')
		del S;del O
		try:del D,M,G,T
		except (B,L,g):pass
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
	def report(A,filename='modules.json'):
		H('Created stubs for {} modules on board {}\nPath: {}'.format(K(A._report),A._fwid,A.path));C=n.format(A.path,filename);E.collect()
		try:
			with V(C,'w')as D:A.write_json_node(D)
			F=A._start_free-E.mem_free()
		except B:H('Failed to create the report.')
	def write_json_node(B,f):
		D='firmware';A=',\n';f.write('{');f.write(a({D:B.info})[1:-1]);f.write(A);f.write(a({'stubber':{Q:__version__},'stubtype':D})[1:-1]);f.write(A);f.write('"modules" :[\n');C=P
		for E in B._report:
			if C:C=G
			else:f.write(A)
			f.write(E)
		f.write('\n]}')
def b(path):
	C=E=0
	while C!=-1:
		C=path.find(A,E)
		if C!=-1:
			D=path[0]if C==0 else path[:C]
			try:I=os.stat(D)
			except B as F:
				if F.args[0]==r:
					try:os.mkdir(D)
					except B as G:H('failed to create folder {}'.format(D));raise G
		E=C+1
def _info():
	a='0.0.0';Z='port';Y='platform';X='name';P='mpy';H='unknown';E='family';B='ver';T=sys.implementation.name;V='stm32'if sys.platform.startswith('pyb')else sys.platform;A={X:T,C:a,Q:a,M:F,R:H,o:H,p:H,E:T,Y:V,Z:V,B:F}
	try:A[C]=J.join([str(A)for A in sys.implementation.version]);A[Q]=A[C];A[X]=sys.implementation.name;A[P]=sys.implementation.mpy
	except I:pass
	if sys.platform not in('unix','win32'):
		try:t(A)
		except (U,I,TypeError):pass
	try:from pycopy import const as G;A[E]='pycopy';del G
	except (O,L):pass
	try:from pycom import FAT as G;A[E]='pycom';del G
	except (O,L):pass
	if A[Y]=='esp32_LoBo':A[E]='loboris';A[Z]='esp32'
	elif A[R]=='ev3':
		A[E]='ev3-pybricks';A[C]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[C]='2.0.0'
		except O:pass
	if A[C]:A[B]=N+A[C].lstrip(N)
	if A[E]==q:
		if A[C]and A[C]>='1.10.0'and A[C].endswith('.0'):A[B]=A[C][:-2]
		else:A[B]=A[C]
		if A[M]!=F and K(A[M])<4:A[B]+=S+A[M]
	if A[B][0]!=N:A[B]=N+A[B]
	if P in A:
		b=int(A[P]);W=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][b>>10]
		if W:A['arch']=W
	return A
def t(info):
	E=' on ';A=info;B=os.uname();A[R]=B[0];A[o]=B[1];A[C]=B[2];A[p]=B[4]
	if E in B[3]:
		D=B[3].split(E)[0]
		if A[R]=='esp8266':F=D.split(S)[0]if S in D else D;A[Q]=A[C]=F.lstrip(N)
		try:A[M]=D.split(S)[1]
		except U:pass
def get_root():
	try:C=os.getcwd()
	except (B,I):C=J
	D=C
	for D in [C,'/sd','/flash',A,J]:
		try:E=os.stat(D);break
		except B:continue
	return D
def u(filename):
	try:os.stat(filename);return P
	except B:return G
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
	except (e,I):return P
def main():
	stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[q]
	for C in [F,A,'/lib/']:
		try:
			with V(C+'modulelist'+'.txt')as D:stubber.modules=[A.strip()for A in D.read().split('\n')if K(A.strip())and A.strip()[0]!='#'];break
		except B:pass
	E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or d():
	try:logging.basicConfig(level=logging.INFO)
	except g:pass
	if not u('no_auto_stubber.txt'):main()