r='micropython'
q='machine'
p='nodename'
o='{}/{}'
n='method'
m='function'
l='bool'
k='str'
j='float'
i='int'
h=NameError
g=sorted
f=NotImplementedError
a=',\n'
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
I=print
H=AttributeError
G=False
F=''
E='/'
D=None
C='release'
B=OSError
import gc as A,sys,uos as os
from ujson import dumps as b
__version__='v1.12.2'
s=2
t=2
class Stubber:
	def __init__(C,path=D,firmware_id=D):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise f('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		C._report=[];C.info=_info();A.collect()
		if D:C._fwid=D.lower()
		else:C._fwid='{family}-{ver}-{port}'.format(**C.info).lower()
		C._start_free=A.mem_free()
		if path:
			if path.endswith(E):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',E)
		try:c(path+E)
		except B:I('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(L,item_instance):
		G=item_instance;B=[];J=[]
		for I in dir(G):
			try:
				C=getattr(G,I)
				try:D=U(type(C)).split("'")[1]
				except V:D=F
				if D in{i,j,k,l,W,X,Y}:E=1
				elif D in{m,n}:E=2
				elif D in'class':E=3
				else:E=4
				B.append((I,U(C),U(type(C)),C,E))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(I,G,K))
		B=g([A for A in B if not A[0].startswith(Z)],key=lambda x:x[4]);A.collect();return B,J
	def add_modules(A,modules):A.modules=g(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.collect()
		for C in B.modules:B.create_one_stub(C)
	def create_one_stub(D,module_name):
		C=module_name
		if C in D.problematic:return G
		if C in D.excluded:return G
		F='{}/{}.py'.format(D.path,C.replace(L,E));A.collect();J=A.mem_free();I('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,F,J));H=G
		try:H=D.create_module_stub(C,F)
		except B:return G
		A.collect();return H
	def create_module_stub(H,module_name,file_name=D):
		K=file_name;C=module_name
		if K is D:K=H.path+E+C.replace(L,Z)+'.py'
		if E in C:C=C.replace(E,L)
		O=D
		try:O=__import__(C,D,D,'*')
		except Q:I('{}Skip module: {:<25} {:<79}'.format('\x1b[1A',C,'Module not found.'));return G
		c(K)
		with J(K,'w')as P:R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,H._fwid,H.info,__version__);P.write(R);P.write('from typing import Any\n\n');H.write_object_stub(P,O,C,F)
		H._report.append('{{"module": "{}", "file": "{}"}}'.format(C,K.replace('\\',E)))
		if C not in{'os','sys','logging','gc'}:
			try:del O
			except (B,M):pass
			try:del sys.modules[C]
			except M:pass
		A.collect();return N
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';R=in_class;Q=object_expr;P='Exception';H=fp;D=indent;A.collect()
		if Q in N.problematic:return
		S,O=N.get_obj_attributes(Q)
		if O:I(O)
		for (E,L,G,T,f) in S:
			if E in['classmethod','staticmethod','BaseException',P]:continue
			if G=="<class 'type'>"and K(D)<=t*4:
				U=F;V=E.endswith(P)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=P
				C='\n{}class {}({}):\n'.format(D,E,U)
				if V:C+=D+'    ...\n';H.write(C);return
				H.write(C);N.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),D+'    ',R+1);C=D+'    def __init__(self, *argv, **kwargs) -> None:\n';C+=D+'        ...\n\n';H.write(C)
			elif n in G or m in G:
				Z=b;a=F
				if R>0:a='self, '
				if c in G or c in L:C='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,Z)
				else:C='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,a,Z)
				C+=D+'    ...\n\n';H.write(C)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				J=G[8:-2];C=F
				if J in[k,i,j,l,'bytearray','bytes']:C=d.format(D,E,L,J)
				elif J in[Y,X,W]:e={Y:'{}',X:'[]',W:'()'};C=d.format(D,E,e[J],J)
				else:
					if J not in['object','set','frozenset']:J=b
					C='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,J,G,L)
				H.write(C)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+E+' # type: Any\n')
		del S;del O
		try:del E,L,G,T
		except (B,M,h):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,Z)
		return A
	def clean(C,path=D):
		if path is D:path=C.path
		I('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except (B,H):return
		for F in E:
			A=o.format(path,F)
			try:os.remove(A)
			except B:
				try:C.clean(A);os.rmdir(A)
				except B:pass
	def report(C,filename='modules.json'):
		I('Created stubs for {} modules on board {}\nPath: {}'.format(K(C._report),C._fwid,C.path));F=o.format(C.path,filename);A.collect()
		try:
			with J(F,'w')as D:
				C.write_json_header(D);E=N
				for H in C._report:C.write_json_node(D,H,E);E=G
				C.write_json_end(D)
			L=C._start_free-A.mem_free()
		except B:I('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(b({A:B.info})[1:-1]);f.write(a);f.write(b({'stubber':{R:__version__},'stubtype':A})[1:-1]);f.write(a);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(a)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def c(path):
	A=D=0
	while A!=-1:
		A=path.find(E,D)
		if A!=-1:
			C=path[0]if A==0 else path[:A]
			try:H=os.stat(C)
			except B as F:
				if F.args[0]==s:
					try:os.mkdir(C)
					except B as G:I('failed to create folder {}'.format(C));raise G
		D=A+1
def _info():
	a='0.0.0';Z='port';Y='platform';X='name';J='mpy';I='unknown';E='family';B='ver';N=sys.implementation.name;U='stm32'if sys.platform.startswith('pyb')else sys.platform;A={X:N,C:a,R:a,O:F,S:I,p:I,q:I,E:N,Y:U,Z:U,B:F}
	try:A[C]=L.join([str(A)for A in sys.implementation.version]);A[R]=A[C];A[X]=sys.implementation.name;A[J]=sys.implementation.mpy
	except H:pass
	if sys.platform not in('unix','win32'):
		try:u(A)
		except (V,H,TypeError):pass
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
	if A[E]==r:
		if A[C]and A[C]>='1.10.0'and A[C].endswith('.0'):A[B]=A[C][:-2]
		else:A[B]=A[C]
		if A[O]!=F and K(A[O])<4:A[B]+=T+A[O]
	if A[B][0]!=P:A[B]=P+A[B]
	if J in A:
		b=int(A[J]);W=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][b>>10]
		if W:A['arch']=W
	return A
def u(info):
	E=' on ';A=info;B=os.uname();A[S]=B[0];A[p]=B[1];A[C]=B[2];A[q]=B[4]
	if E in B[3]:
		D=B[3].split(E)[0]
		if A[S]=='esp8266':F=D.split(T)[0]if T in D else D;A[R]=A[C]=F.lstrip(P)
		try:A[O]=D.split(T)[1]
		except V:pass
def get_root():
	try:A=os.getcwd()
	except (B,H):A=L
	C=A
	for C in [A,'/sd','/flash',E,L]:
		try:D=os.stat(C);break
		except B:continue
	return C
def v(filename):
	try:os.stat(filename);return N
	except B:return G
def d():sys.exit(1)
def read_path():
	path=F
	if K(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:d()
	elif K(sys.argv)==2:d()
	return path
def e():
	try:A=bytes('abc',encoding='utf8');B=e.__module__;return G
	except (f,H):return N
def main():
	P='failed';L='.done';I='modulelist';import machine as R
	try:A.threshold(512)
	except H:pass
	try:D=J(I+L,'r+b');Q=N
	except B:D=J(I+L,'w+b');Q=G
	stubber=Stubber(path=read_path())
	if not Q:stubber.clean()
	stubber.modules=[r]
	for S in [F,'/libs']:
		try:
			with J(S+I+'.txt')as D:
				for C in D.read().split('\n'):
					C=C.strip()
					if K(C)>0 and C[0]!='#':stubber.modules.append(C)
				A.collect();break
		except B:pass
	A.collect();E={}
	try:
		with J(I+L)as D:
			for C in D.read().split('\n'):
				C=C.strip();A.collect()
				if K(C)>0:T,U=C.split('=',1);E[T]=U
	except (B,SyntaxError):pass
	A.collect();V=[A for A in stubber.modules if A not in E.keys()];A.collect()
	for M in V:
		O=G
		try:O=stubber.create_one_stub(M)
		except MemoryError:R.reset()
		A.collect();E[M]=str(stubber._report[-1]if O else P)
		with J(I+L,'a')as D:D.write('{}={}\n'.format(M,'ok'if O else P))
	if E:stubber._report=[A for(B,A)in E.items()if A!=P];stubber.report()
if __name__=='__main__'or e():
	try:logging.basicConfig(level=logging.INFO)
	except h:pass
	if not v('no_auto_stubber.txt'):main()