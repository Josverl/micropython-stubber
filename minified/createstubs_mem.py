j='micropython'
i='{}/{}'
h='method'
g='function'
f='bool'
e='str'
d='float'
c='int'
b=NameError
a=print
Z=sorted
Y=NotImplementedError
V='_'
U='dict'
T='list'
R='tuple'
Q=open
S=IndexError
P=repr
O='version'
L=True
N=ImportError
K=len
J=KeyError
I='.'
H=AttributeError
F=False
G=''
D='/'
C=None
B=OSError
import gc as E,sys,uos as os
from ujson import dumps as M
__version__='1.9.11'
k=2
l=2
class Stubber:
	def __init__(A,path=C,firmware_id=C):
		F=firmware_id;C=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise Y('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();E.collect()
		if F:A._fwid=str(F).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if C:
			if C.endswith(D):C=C[:-1]
		else:C=get_root()
		A.path='{}/stubs/{}'.format(C,A.flat_fwid).replace('//',D)
		try:W(C+D)
		except B:pass
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;A=[];J=[]
		for I in dir(F):
			try:
				B=getattr(F,I)
				try:C=P(type(B)).split("'")[1]
				except S:C=G
				if C in(c,d,e,f,R,T,U):D=1
				elif C in(g,h):D=2
				elif C in'class':D=3
				else:D=4
				A.append((I,P(B),P(type(B)),B,D))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(I,F,K))
		A=Z([B for B in A if not B[0].startswith(V)],key=lambda x:x[4]);E.collect();return A,J
	def add_modules(A,modules):A.modules=Z(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:return F
		if A in C.excluded:return F
		G='{}/{}.py'.format(C.path,A.replace(I,D));E.collect();J=E.mem_free();a('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(A,G,J));H=F
		try:H=C.create_module_stub(A,G)
		except B:return F
		E.collect();return H
	def create_module_stub(H,module_name,file_name=C):
		K=file_name;A=module_name
		if A in H.problematic:return F
		if K is C:K=H.path+D+A.replace(I,V)+'.py'
		if D in A:A=A.replace(D,I)
		M=C
		try:M=__import__(A,C,C,'*')
		except N:return F
		W(K)
		with Q(K,'w')as O:P='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,H.info,__version__);O.write(P);O.write('from typing import Any\n\n');H.write_object_stub(O,M,A,G)
		H._report.append({'module':A,'file':K})
		if not A in['os','sys','logging','gc']:
			try:del M
			except (B,J):pass
			try:del sys.modules[A]
			except J:pass
		E.collect();return L
	def write_object_stub(M,fp,object_expr,obj_name,indent,in_class=0):
		i='{0}{1} = {2} # type: {3}\n';a='bound_method';Z='Any';P=in_class;O=object_expr;N='Exception';H=fp;C=indent;E.collect()
		if O in M.problematic:return
		Q,j=M.get_obj_attributes(O)
		for (D,L,F,S,m) in Q:
			if D in['classmethod','staticmethod','BaseException',N]:continue
			if F=="<class 'type'>"and K(C)<=l*4:
				V=G;W=D.endswith(N)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if W:V=N
				A='\n{}class {}({}):\n'.format(C,D,V)
				if W:A+=C+'    ...\n';H.write(A);return
				H.write(A);M.write_object_stub(H,S,'{0}.{1}'.format(obj_name,D),C+'    ',P+1);A=C+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=C+'        ...\n\n';H.write(A)
			elif h in F or g in F:
				X=Z;Y=G
				if P>0:Y='self, '
				if a in F or a in L:A='{}@classmethod\n'.format(C);A+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(C,D,X)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(C,D,Y,X)
				A+=C+'    ...\n\n';H.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				I=F[8:-2];A=G
				if I in[e,c,d,f,'bytearray','bytes']:A=i.format(C,D,L,I)
				elif I in[U,T,R]:k={U:'{}',T:'[]',R:'()'};A=i.format(C,D,k[I],I)
				else:
					if not I in['object','set','frozenset']:I=Z
					A='{0}{1} : {2} ## {3} = {4}\n'.format(C,D,I,F,L)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(F));H.write(C+D+' # type: Any\n')
		del Q;del j
		try:del D,L,F,S
		except (B,J,b):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,V)
		return A
	def clean(E,path=C):
		A=path
		if A is C:A=E.path
		a('Clean/remove files in folder: {}'.format(A))
		try:F=os.listdir(A)
		except (B,H):return
		for G in F:
			D=i.format(A,G)
			try:os.remove(D)
			except B:
				try:E.clean(D);os.rmdir(D)
				except B:pass
	def report(C,filename='modules.json'):
		H='firmware';D=',\n';I=i.format(C.path,filename);E.collect()
		try:
			with Q(I,'w')as A:
				A.write('{');A.write(M({H:C.info})[1:-1]);A.write(D);A.write(M({'stubber':{O:__version__},'stubtype':H})[1:-1]);A.write(D);A.write('"modules" :[\n');G=L
				for J in C._report:
					if G:G=F
					else:A.write(D)
					A.write(M(J))
				A.write('\n]}')
			K=C._start_free-E.mem_free()
		except B:pass
def W(path):
	C=path;A=F=0
	while A!=-1:
		A=C.find(D,F)
		if A!=-1:
			if A==0:E=C[0]
			else:E=C[0:A]
			try:I=os.stat(E)
			except B as G:
				if G.args[0]==k:
					try:os.mkdir(E)
					except B as H:raise H
				else:raise G
		F=A+1
def _info():
	g=' on ';f='0.0.0';e='port';d='platform';c='machine';b='nodename';a='name';V='mpy';U='unknown';R='-';Q='sysname';M='v';L='build';F='family';D='ver';B='release';W=sys.implementation.name;X=sys.platform if not sys.platform.startswith('pyb')else'stm32';A={a:W,B:f,O:f,L:G,Q:U,b:U,c:U,F:W,d:X,e:X,D:G}
	try:A[B]=I.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[a]=sys.implementation.name;A[V]=sys.implementation.mpy
	except H:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[b]=E.nodename;A[B]=E.release;A[c]=E.machine
			if g in E.version:
				P=E.version.split(g)[0]
				if A[Q]=='esp8266':
					if R in P:Y=P.split(R)[0]
					else:Y=P
					A[O]=A[B]=Y.lstrip(M)
				try:A[L]=P.split(R)[1]
				except S:pass
		except (S,H,TypeError):pass
	try:from pycopy import const as T;A[F]='pycopy';del T
	except (N,J):pass
	try:from pycom import FAT as T;A[F]='pycom';del T
	except (N,J):pass
	if A[d]=='esp32_LoBo':A[F]='loboris';A[e]='esp32'
	elif A[Q]=='ev3':
		A[F]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except N:pass
	if A[B]:A[D]=M+A[B].lstrip(M)
	if A[F]==j:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[D]=A[B][:-2]
		else:A[D]=A[B]
		if A[L]!=G and K(A[L])<4:A[D]+=R+A[L]
	if A[D][0]!=M:A[D]=M+A[D]
	if V in A:
		h=int(A[V]);Z=[C,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][h>>10]
		if Z:A['arch']=Z
	return A
def get_root():
	try:A=os.getcwd()
	except (B,H):A=I
	C=A
	for C in [A,'/sd','/flash',D,I]:
		try:E=os.stat(C);break
		except B:continue
	return C
def m(filename):
	try:os.stat(filename);return L
	except B:return F
def A():sys.exit(1)
def read_path():
	B=G
	if K(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):B=sys.argv[2]
		else:A()
	elif K(sys.argv)==2:A()
	return B
def X():
	try:A=bytes('abc',encoding='utf8');B=X.__module__;return F
	except (Y,H):return L
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	try:
		with Q('modulelist'+'.txt')as C:stubber.modules=[A.strip()for A in C.read().splitlines()if K(A.strip())and A.strip()[0]!='#']
	except B:stubber.modules=[j]
	E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or X():
	try:logging.basicConfig(level=logging.INFO)
	except b:pass
	if not m('no_auto_stubber.txt'):main()