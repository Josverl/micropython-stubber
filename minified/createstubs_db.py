l='utf8'
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
X='w'
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
L='.'
K=AttributeError
J=open
I=''
F='/'
H=len
G=print
E=None
D=False
C=OSError
import gc as B,sys,uos as os
from ujson import dumps as R
__version__='1.9.11'
m=2
n=2
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise a('MicroPython 1.13.0 cannot be stubbed')
		except K:pass
		A._report=[];A.info=_info();B.collect()
		if D:A._fwid=str(D).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=B.mem_free()
		if path:
			if path.endswith(F):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',F)
		try:Y(path+F)
		except C:G('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;A=[];H=[]
		for G in dir(F):
			try:
				C=getattr(F,G)
				try:D=O(type(C)).split("'")[1]
				except S:D=I
				if D in(e,f,g,h,T,U,V):E=1
				elif D in(i,j):E=2
				elif D in'class':E=3
				else:E=4
				A.append((G,O(C),O(type(C)),C,E))
			except K as J:H.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(G,F,J))
		A=b([B for B in A if not B[0].startswith(W)],key=lambda x:x[4]);B.collect();return A,H
	def add_modules(A,modules):A.modules=b(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(E,module_name):
		A=module_name
		if A in E.problematic:return D
		if A in E.excluded:return D
		H='{}/{}.py'.format(E.path,A.replace(L,F));B.collect();J=B.mem_free();G('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,H,J));I=D
		try:I=E.create_module_stub(A,H)
		except C:return D
		B.collect();return I
	def create_module_stub(H,module_name,file_name=E):
		K=file_name;A=module_name
		if A in H.problematic:return D
		if K is E:K=H.path+F+A.replace(L,W)+'.py'
		if F in A:A=A.replace(F,L)
		O=E
		try:O=__import__(A,E,E,'*')
		except P:G('{}Skip module: {:<25} {:<79}'.format('\x1b[1A',A,'Module not found.'));return D
		Y(K)
		with J(K,X)as Q:R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,H.info,__version__);Q.write(R);Q.write('from typing import Any\n\n');H.write_object_stub(Q,O,A,I)
		H._report.append({'module':A,'file':K})
		if not A in['os','sys','logging','gc']:
			try:del O
			except (C,M):pass
			try:del sys.modules[A]
			except M:pass
		B.collect();return N
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		k='{0}{1} = {2} # type: {3}\n';d='bound_method';b='Any';R=in_class;Q=object_expr;P='Exception';J=fp;D=indent;B.collect()
		if Q in N.problematic:return
		S,O=N.get_obj_attributes(Q)
		if O:G(O)
		for (E,L,F,W,m) in S:
			if E in['classmethod','staticmethod','BaseException',P]:continue
			if F=="<class 'type'>"and H(D)<=n*4:
				X=I;Y=E.endswith(P)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if Y:X=P
				A='\n{}class {}({}):\n'.format(D,E,X)
				if Y:A+=D+'    ...\n';J.write(A);return
				J.write(A);N.write_object_stub(J,W,'{0}.{1}'.format(obj_name,E),D+'    ',R+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';J.write(A)
			elif j in F or i in F:
				Z=b;a=I
				if R>0:a='self, '
				if d in F or d in L:A='{}@classmethod\n'.format(D);A+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,Z)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,a,Z)
				A+=D+'    ...\n\n';J.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				K=F[8:-2];A=I
				if K in[g,e,f,h,'bytearray','bytes']:A=k.format(D,E,L,K)
				elif K in[V,U,T]:l={V:'{}',U:'[]',T:'()'};A=k.format(D,E,l[K],K)
				else:
					if not K in['object','set','frozenset']:K=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,K,F,L)
				J.write(A)
			else:J.write("# all other, type = '{0}'\n".format(F));J.write(D+E+' # type: Any\n')
		del S;del O
		try:del E,L,F,W
		except (C,M,c):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,W)
		return A
	def clean(B,path=E):
		if path is E:path=B.path
		G('Clean/remove files in folder: {}'.format(path))
		try:D=os.listdir(path)
		except (C,K):return
		for F in D:
			A=k.format(path,F)
			try:os.remove(A)
			except C:
				try:B.clean(A);os.rmdir(A)
				except C:pass
	def report(E,filename='modules.json'):
		K='firmware';F=',\n';G('Created stubs for {} modules on board {}\nPath: {}'.format(H(E._report),E._fwid,E.path));L=k.format(E.path,filename);B.collect()
		try:
			with J(L,X)as A:
				A.write('{');A.write(R({K:E.info})[1:-1]);A.write(F);A.write(R({'stubber':{Q:__version__},'stubtype':K})[1:-1]);A.write(F);A.write('"modules" :[\n');I=N
				for M in E._report:
					if I:I=D
					else:A.write(F)
					A.write(R(M))
				A.write('\n]}')
			O=E._start_free-B.mem_free()
		except C:G('Failed to create the report.')
def Y(path):
	H='failed to create folder {}';A=D=0
	while A!=-1:
		A=path.find(F,D)
		if A!=-1:
			if A==0:B=path[0]
			else:B=path[0:A]
			try:J=os.stat(B)
			except C as E:
				if E.args[0]==m:
					try:os.mkdir(B)
					except C as I:G(H.format(B));raise I
				else:G(H.format(B));raise E
		D=A+1
def _info():
	g=' on ';f='0.0.0';e='port';d='platform';c='machine';b='nodename';a='name';V='mpy';U='unknown';R='-';O='sysname';J='v';G='build';F='family';C='ver';B='release';W=sys.implementation.name;X=sys.platform if not sys.platform.startswith('pyb')else'stm32';A={a:W,B:f,Q:f,G:I,O:U,b:U,c:U,F:W,d:X,e:X,C:I}
	try:A[B]=L.join([str(A)for A in sys.implementation.version]);A[Q]=A[B];A[a]=sys.implementation.name;A[V]=sys.implementation.mpy
	except K:pass
	if sys.platform not in('unix','win32'):
		try:
			D=os.uname();A[O]=D[0];A[b]=D[1];A[B]=D[2];A[c]=D[4]
			if g in D[3]:
				N=D[3].split(g)[0]
				if A[O]=='esp8266':
					if R in N:Y=N.split(R)[0]
					else:Y=N
					A[Q]=A[B]=Y.lstrip(J)
				try:A[G]=N.split(R)[1]
				except S:pass
		except (S,K,TypeError):pass
	try:from pycopy import const as T;A[F]='pycopy';del T
	except (P,M):pass
	try:from pycom import FAT as T;A[F]='pycom';del T
	except (P,M):pass
	if A[d]=='esp32_LoBo':A[F]='loboris';A[e]='esp32'
	elif A[O]=='ev3':
		A[F]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except P:pass
	if A[B]:A[C]=J+A[B].lstrip(J)
	if A[F]=='micropython':
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[G]!=I and H(A[G])<4:A[C]+=R+A[G]
	if A[C][0]!=J:A[C]=J+A[C]
	if V in A:
		h=int(A[V]);Z=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][h>>10]
		if Z:A['arch']=Z
	return A
def get_root():
	try:A=os.getcwd()
	except (C,K):A=L
	B=A
	for B in [A,'/sd','/flash',F,L]:
		try:D=os.stat(B);break
		except C:continue
	return B
def o(filename):
	try:os.stat(filename);return N
	except C:return D
def A():sys.exit(1)
def read_path():
	path=I
	if H(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):path=sys.argv[2]
		else:A()
	elif H(sys.argv)==2:A()
	return path
def Z():
	try:A=d('abc',encoding=l);B=Z.__module__;return D
	except (a,K):return N
def p():
	L='#';I='\n';G='.done';F='modulelist';import machine as R
	try:A=J(F+G,'r+b');M=N
	except C:A=J(F+G,'w+b');M=D
	stubber=Stubber(path=read_path())
	if not M:stubber.clean()
	with J(F+'.txt')as A:K=[B.strip()for B in A.read().split(I)if H(B.strip())and B.strip()[0]!=L]
	B.collect()
	with J(F+G)as A:E=[B.strip()for B in A.read().split(I)if H(B.strip())and B.strip()[0]!=L]
	B.collect();K=[A for A in K if A not in E];B.collect()
	for P in K:
		Q=D
		try:Q=stubber.create_one_stub(P)
		except MemoryError:R.reset()
		if Q:S=d(O(stubber._report[-1]),l)
		else:S=b'fail'
		E.append(P)
		with J(F+G,X)as A:A.write(I.join(E))
	with J(F+G)as A:E=[B.strip()for B in A.read().split(I)if H(B.strip())and B.strip()[0]!=L]
	if H(E)>0:stubber._report=E;stubber.report()
if __name__=='__main__'or Z():
	try:logging.basicConfig(level=logging.INFO)
	except c:pass
	if not o('no_auto_stubber.txt'):p()