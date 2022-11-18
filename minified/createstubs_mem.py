j='micropython'
i='{}/{}'
h='method'
g='function'
f='bool'
e='str'
d='float'
c='int'
b=NameError
a=sorted
Z=NotImplementedError
V='_'
U='dict'
T='list'
R='tuple'
Q=open
S=IndexError
P=repr
O='version'
M=True
N=ImportError
L=KeyError
J='.'
K=len
I=AttributeError
F=False
H=''
G=print
D='/'
C=None
B=OSError
import gc as E,sys,uos as os
from ujson import dumps as W
__version__='1.9.11'
k=2
l=2
class Stubber:
	def __init__(A,path=C,firmware_id=C):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise Z('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();E.collect()
		if C:A._fwid=str(C).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if path:
			if path.endswith(D):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',D)
		try:X(path+D)
		except B:G('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;A=[];J=[]
		for G in dir(F):
			try:
				B=getattr(F,G)
				try:C=P(type(B)).split("'")[1]
				except S:C=H
				if C in(c,d,e,f,R,T,U):D=1
				elif C in(g,h):D=2
				elif C in'class':D=3
				else:D=4
				A.append((G,P(B),P(type(B)),B,D))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(G,F,K))
		A=a([B for B in A if not B[0].startswith(V)],key=lambda x:x[4]);E.collect();return A,J
	def add_modules(A,modules):A.modules=a(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:return F
		if A in C.excluded:return F
		H='{}/{}.py'.format(C.path,A.replace(J,D));E.collect();K=E.mem_free();G('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,H,K));I=F
		try:I=C.create_module_stub(A,H)
		except B:return F
		E.collect();return I
	def create_module_stub(I,module_name,file_name=C):
		K=file_name;A=module_name
		if A in I.problematic:return F
		if K is C:K=I.path+D+A.replace(J,V)+'.py'
		if D in A:A=A.replace(D,J)
		O=C
		try:O=__import__(A,C,C,'*')
		except N:G('{}Skip module: {:<25} {:<79}'.format('\x1b[1A',A,'Module not found.'));return F
		X(K)
		with Q(K,'w')as P:R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,I._fwid,I.info,__version__);P.write(R);P.write('from typing import Any\n\n');I.write_object_stub(P,O,A,H)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(A,K.replace('\\',D)))
		if not A in['os','sys','logging','gc']:
			try:del O
			except (B,L):pass
			try:del sys.modules[A]
			except L:pass
		E.collect();return M
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		k='{0}{1} = {2} # type: {3}\n';j='bound_method';i='Any';S=in_class;Q=object_expr;P='Exception';I=fp;C=indent;E.collect()
		if Q in N.problematic:return
		V,O=N.get_obj_attributes(Q)
		if O:G(O)
		for (D,M,F,W,n) in V:
			if D in['classmethod','staticmethod','BaseException',P]:continue
			if F=="<class 'type'>"and K(C)<=l*4:
				X=H;Y=D.endswith(P)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if Y:X=P
				A='\n{}class {}({}):\n'.format(C,D,X)
				if Y:A+=C+'    ...\n';I.write(A);return
				I.write(A);N.write_object_stub(I,W,'{0}.{1}'.format(obj_name,D),C+'    ',S+1);A=C+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=C+'        ...\n\n';I.write(A)
			elif h in F or g in F:
				Z=i;a=H
				if S>0:a='self, '
				if j in F or j in M:A='{}@classmethod\n'.format(C);A+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(C,D,Z)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(C,D,a,Z)
				A+=C+'    ...\n\n';I.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				J=F[8:-2];A=H
				if J in[e,c,d,f,'bytearray','bytes']:A=k.format(C,D,M,J)
				elif J in[U,T,R]:m={U:'{}',T:'[]',R:'()'};A=k.format(C,D,m[J],J)
				else:
					if not J in['object','set','frozenset']:J=i
					A='{0}{1} : {2} ## {3} = {4}\n'.format(C,D,J,F,M)
				I.write(A)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(C+D+' # type: Any\n')
		del V;del O
		try:del D,M,F,W
		except (B,L,b):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,V)
		return A
	def clean(D,path=C):
		if path is C:path=D.path
		G('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except (B,I):return
		for F in E:
			A=i.format(path,F)
			try:os.remove(A)
			except B:
				try:D.clean(A);os.rmdir(A)
				except B:pass
	def report(C,filename='modules.json'):
		I='firmware';D=',\n';G('Created stubs for {} modules on board {}\nPath: {}'.format(K(C._report),C._fwid,C.path));J=i.format(C.path,filename);E.collect()
		try:
			with Q(J,'w')as A:
				A.write('{');A.write(W({I:C.info})[1:-1]);A.write(D);A.write(W({'stubber':{O:__version__},'stubtype':I})[1:-1]);A.write(D);A.write('"modules" :[\n');H=M
				for L in C._report:
					if H:H=F
					else:A.write(D)
					A.write(L)
				A.write('\n]}')
			N=C._start_free-E.mem_free()
		except B:G('Failed to create the report.')
def X(path):
	H='failed to create folder {}';A=E=0
	while A!=-1:
		A=path.find(D,E)
		if A!=-1:
			if A==0:C=path[0]
			else:C=path[0:A]
			try:J=os.stat(C)
			except B as F:
				if F.args[0]==k:
					try:os.mkdir(C)
					except B as I:G(H.format(C));raise I
				else:G(H.format(C));raise F
		E=A+1
def _info():
	g=' on ';f='0.0.0';e='port';d='platform';c='machine';b='nodename';a='name';V='mpy';U='unknown';R='-';Q='sysname';M='v';G='build';F='family';D='ver';B='release';W=sys.implementation.name;X=sys.platform if not sys.platform.startswith('pyb')else'stm32';A={a:W,B:f,O:f,G:H,Q:U,b:U,c:U,F:W,d:X,e:X,D:H}
	try:A[B]=J.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[a]=sys.implementation.name;A[V]=sys.implementation.mpy
	except I:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E[0];A[b]=E[1];A[B]=E[2];A[c]=E[4]
			if g in E[3]:
				P=E[3].split(g)[0]
				if A[Q]=='esp8266':
					if R in P:Y=P.split(R)[0]
					else:Y=P
					A[O]=A[B]=Y.lstrip(M)
				try:A[G]=P.split(R)[1]
				except S:pass
		except (S,I,TypeError):pass
	try:from pycopy import const as T;A[F]='pycopy';del T
	except (N,L):pass
	try:from pycom import FAT as T;A[F]='pycom';del T
	except (N,L):pass
	if A[d]=='esp32_LoBo':A[F]='loboris';A[e]='esp32'
	elif A[Q]=='ev3':
		A[F]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except N:pass
	if A[B]:A[D]=M+A[B].lstrip(M)
	if A[F]==j:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[D]=A[B][:-2]
		else:A[D]=A[B]
		if A[G]!=H and K(A[G])<4:A[D]+=R+A[G]
	if A[D][0]!=M:A[D]=M+A[D]
	if V in A:
		h=int(A[V]);Z=[C,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][h>>10]
		if Z:A['arch']=Z
	return A
def get_root():
	try:A=os.getcwd()
	except (B,I):A=J
	C=A
	for C in [A,'/sd','/flash',D,J]:
		try:E=os.stat(C);break
		except B:continue
	return C
def m(filename):
	try:os.stat(filename);return M
	except B:return F
def A():sys.exit(1)
def read_path():
	path=H
	if K(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):path=sys.argv[2]
		else:A()
	elif K(sys.argv)==2:A()
	return path
def Y():
	try:A=bytes('abc',encoding='utf8');B=Y.__module__;return F
	except (Z,I):return M
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	try:
		with Q('modulelist'+'.txt')as C:stubber.modules=[A.strip()for A in C.read().split('\n')if K(A.strip())and A.strip()[0]!='#']
	except B:stubber.modules=[j]
	E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or Y():
	try:logging.basicConfig(level=logging.INFO)
	except b:pass
	if not m('no_auto_stubber.txt'):main()