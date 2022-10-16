k='{}/{}'
j='method'
i='function'
h='bool'
g='str'
f='float'
e='int'
d=bytes
c=NameError
b=sorted
a=NotImplementedError
X='utf8'
W='_'
V='dict'
U='list'
T='tuple'
S=IndexError
Q='version'
P=ImportError
O=repr
N=True
M=KeyError
L=open
K='.'
J=AttributeError
I=len
H=''
F='/'
G=print
D=None
C=False
B=OSError
import gc as E,sys,uos as os
from ujson import dumps as R
__version__='1.9.11'
l=2
m=2
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise a('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		A._report=[];A.info=_info();E.collect()
		if C:A._fwid=str(C).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if path:
			if path.endswith(F):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',F)
		try:Y(path+F)
		except B:G('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;A=[];I=[]
		for G in dir(F):
			try:
				B=getattr(F,G)
				try:C=O(type(B)).split("'")[1]
				except S:C=H
				if C in(e,f,g,h,T,U,V):D=1
				elif C in(i,j):D=2
				elif C in'class':D=3
				else:D=4
				A.append((G,O(B),O(type(B)),B,D))
			except J as K:I.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(G,F,K))
		A=b([B for B in A if not B[0].startswith(W)],key=lambda x:x[4]);E.collect();return A,I
	def add_modules(A,modules):A.modules=b(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(D,module_name):
		A=module_name
		if A in D.problematic:return C
		if A in D.excluded:return C
		H='{}/{}.py'.format(D.path,A.replace(K,F));E.collect();J=E.mem_free();G('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,H,J));I=C
		try:I=D.create_module_stub(A,H)
		except B:return C
		E.collect();return I
	def create_module_stub(I,module_name,file_name=D):
		J=file_name;A=module_name
		if A in I.problematic:return C
		if J is D:J=I.path+F+A.replace(K,W)+'.py'
		if F in A:A=A.replace(F,K)
		O=D
		try:O=__import__(A,D,D,'*')
		except P:G('{}Skip module: {:<25} {:<79}'.format('\x1b[1A',A,'Module not found.'));return C
		Y(J)
		with L(J,'w')as Q:R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,I._fwid,I.info,__version__);Q.write(R);Q.write('from typing import Any\n\n');I.write_object_stub(Q,O,A,H)
		I._report.append({'module':A,'file':J})
		if not A in['os','sys','logging','gc']:
			try:del O
			except (B,M):pass
			try:del sys.modules[A]
			except M:pass
		E.collect();return N
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		k='{0}{1} = {2} # type: {3}\n';d='bound_method';b='Any';R=in_class;Q=object_expr;P='Exception';J=fp;C=indent;E.collect()
		if Q in N.problematic:return
		S,O=N.get_obj_attributes(Q)
		if O:G(O)
		for (D,L,F,W,n) in S:
			if D in['classmethod','staticmethod','BaseException',P]:continue
			if F=="<class 'type'>"and I(C)<=m*4:
				X=H;Y=D.endswith(P)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if Y:X=P
				A='\n{}class {}({}):\n'.format(C,D,X)
				if Y:A+=C+'    ...\n';J.write(A);return
				J.write(A);N.write_object_stub(J,W,'{0}.{1}'.format(obj_name,D),C+'    ',R+1);A=C+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=C+'        ...\n\n';J.write(A)
			elif j in F or i in F:
				Z=b;a=H
				if R>0:a='self, '
				if d in F or d in L:A='{}@classmethod\n'.format(C);A+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(C,D,Z)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(C,D,a,Z)
				A+=C+'    ...\n\n';J.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				K=F[8:-2];A=H
				if K in[g,e,f,h,'bytearray','bytes']:A=k.format(C,D,L,K)
				elif K in[V,U,T]:l={V:'{}',U:'[]',T:'()'};A=k.format(C,D,l[K],K)
				else:
					if not K in['object','set','frozenset']:K=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(C,D,K,F,L)
				J.write(A)
			else:J.write("# all other, type = '{0}'\n".format(F));J.write(C+D+' # type: Any\n')
		del S;del O
		try:del D,L,F,W
		except (B,M,c):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,W)
		return A
	def clean(C,path=D):
		if path is D:path=C.path
		G('Clean/remove files in folder: {}'.format(path))
		try:E=os.listdir(path)
		except (B,J):return
		for F in E:
			A=k.format(path,F)
			try:os.remove(A)
			except B:
				try:C.clean(A);os.rmdir(A)
				except B:pass
	def report(D,filename='modules.json'):
		J='firmware';F=',\n';G('Created stubs for {} modules on board {}\nPath: {}'.format(I(D._report),D._fwid,D.path));K=k.format(D.path,filename);E.collect()
		try:
			with L(K,'w')as A:
				A.write('{');A.write(R({J:D.info})[1:-1]);A.write(F);A.write(R({'stubber':{Q:__version__},'stubtype':J})[1:-1]);A.write(F);A.write('"modules" :[\n');H=N
				for M in D._report:
					if H:H=C
					else:A.write(F)
					A.write(R(M))
				A.write('\n]}')
			O=D._start_free-E.mem_free()
		except B:G('Failed to create the report.')
def Y(path):
	H='failed to create folder {}';A=D=0
	while A!=-1:
		A=path.find(F,D)
		if A!=-1:
			if A==0:C=path[0]
			else:C=path[0:A]
			try:J=os.stat(C)
			except B as E:
				if E.args[0]==l:
					try:os.mkdir(C)
					except B as I:G(H.format(C));raise I
				else:G(H.format(C));raise E
		D=A+1
def _info():
	g=' on ';f='0.0.0';e='port';d='platform';c='machine';b='nodename';a='name';V='mpy';U='unknown';R='-';O='sysname';L='v';G='build';F='family';C='ver';B='release';W=sys.implementation.name;X=sys.platform if not sys.platform.startswith('pyb')else'stm32';A={a:W,B:f,Q:f,G:H,O:U,b:U,c:U,F:W,d:X,e:X,C:H}
	try:A[B]=K.join([str(A)for A in sys.implementation.version]);A[Q]=A[B];A[a]=sys.implementation.name;A[V]=sys.implementation.mpy
	except J:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[O]=E.sysname;A[b]=E.nodename;A[B]=E.release;A[c]=E.machine
			if g in E.version:
				N=E.version.split(g)[0]
				if A[O]=='esp8266':
					if R in N:Y=N.split(R)[0]
					else:Y=N
					A[Q]=A[B]=Y.lstrip(L)
				try:A[G]=N.split(R)[1]
				except S:pass
		except (S,J,TypeError):pass
	try:from pycopy import const as T;A[F]='pycopy';del T
	except (P,M):pass
	try:from pycom import FAT as T;A[F]='pycom';del T
	except (P,M):pass
	if A[d]=='esp32_LoBo':A[F]='loboris';A[e]='esp32'
	elif A[O]=='ev3':
		A[F]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except P:pass
	if A[B]:A[C]=L+A[B].lstrip(L)
	if A[F]=='micropython':
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[G]!=H and I(A[G])<4:A[C]+=R+A[G]
	if A[C][0]!=L:A[C]=L+A[C]
	if V in A:
		h=int(A[V]);Z=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][h>>10]
		if Z:A['arch']=Z
	return A
def get_root():
	try:A=os.getcwd()
	except (B,J):A=K
	C=A
	for C in [A,'/sd','/flash',F,K]:
		try:D=os.stat(C);break
		except B:continue
	return C
def n(filename):
	try:os.stat(filename);return N
	except B:return C
def A():sys.exit(1)
def read_path():
	path=H
	if I(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):path=sys.argv[2]
		else:A()
	elif I(sys.argv)==2:A()
	return path
def Z():
	try:A=d('abc',encoding=X);B=Z.__module__;return C
	except (a,J):return N
def o():
	P=b'fail';M='.db';H=b'todo';G='modulelist';import btree,machine as Q
	try:D=L(G+M,'r+b');E=N
	except B:D=L(G+M,'w+b');E=C
	stubber=Stubber(path=read_path())
	if not E:stubber.clean()
	A=btree.open(D)
	if not E or I(list(A.keys()))==0:
		with L(G+'.txt')as D:
			R=[A.strip()for A in D.read().split('\n')if I(A.strip())and A.strip()[0]!='#']
			for S in R:A[S]=H
		A.flush()
	for F in A.keys():
		if A[F]!=H:continue
		J=C
		try:J=stubber.create_one_stub(F.decode(X))
		except MemoryError:A.close();D.close();Q.reset()
		if J:K=d(O(stubber._report[-1]),X)
		else:K=P
		A[F]=K;A.flush()
	all=[B for B in A.items()if not B[1]==H and not B[1]==P]
	if I(all)>0:stubber._report=all;stubber.report()
	A.close();D.close()
if __name__=='__main__'or Z():
	try:logging.basicConfig(level=logging.INFO)
	except c:pass
	if not n('no_auto_stubber.txt'):o()