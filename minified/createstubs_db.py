j='{}/{}'
i='method'
h='function'
g='bool'
f='str'
e='float'
d='int'
c=NameError
b=sorted
a=NotImplementedError
W='_'
V='dict'
U='list'
R='tuple'
T=IndexError
Q=repr
S=str
P='version'
O=ImportError
N=True
M=KeyError
L='.'
K=open
J=AttributeError
I=len
H=''
F='/'
G=print
E=None
D=False
C=OSError
import gc as B,sys,uos as os
from ujson import dumps as X
__version__='1.9.11'
k=2
l=2
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise a('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		A._report=[];A.info=_info();B.collect()
		if D:A._fwid=S(D).lower()
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
		F=item_instance;A=[];I=[]
		for G in dir(F):
			try:
				C=getattr(F,G)
				try:D=Q(type(C)).split("'")[1]
				except T:D=H
				if D in(d,e,f,g,R,U,V):E=1
				elif D in(h,i):E=2
				elif D in'class':E=3
				else:E=4
				A.append((G,Q(C),Q(type(C)),C,E))
			except J as K:I.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(G,F,K))
		A=b([B for B in A if not B[0].startswith(W)],key=lambda x:x[4]);B.collect();return A,I
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
	def create_module_stub(I,module_name,file_name=E):
		J=file_name;A=module_name
		if A in I.problematic:return D
		if J is E:J=I.path+F+A.replace(L,W)+'.py'
		if F in A:A=A.replace(F,L)
		P=E
		try:P=__import__(A,E,E,'*')
		except O:G('{}Skip module: {:<25} {:<79}'.format('\x1b[1A',A,'Module not found.'));return D
		Y(J)
		with K(J,'w')as Q:R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,I._fwid,I.info,__version__);Q.write(R);Q.write('from typing import Any\n\n');I.write_object_stub(Q,P,A,H)
		I._report.append('{{"module": {}, "file": {}}}'.format(A,J))
		if not A in['os','sys','logging','gc']:
			try:del P
			except (C,M):pass
			try:del sys.modules[A]
			except M:pass
		B.collect();return N
	def write_object_stub(N,fp,object_expr,obj_name,indent,in_class=0):
		k='{0}{1} = {2} # type: {3}\n';j='bound_method';b='Any';S=in_class;Q=object_expr;P='Exception';J=fp;D=indent;B.collect()
		if Q in N.problematic:return
		T,O=N.get_obj_attributes(Q)
		if O:G(O)
		for (E,L,F,W,n) in T:
			if E in['classmethod','staticmethod','BaseException',P]:continue
			if F=="<class 'type'>"and I(D)<=l*4:
				X=H;Y=E.endswith(P)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if Y:X=P
				A='\n{}class {}({}):\n'.format(D,E,X)
				if Y:A+=D+'    ...\n';J.write(A);return
				J.write(A);N.write_object_stub(J,W,'{0}.{1}'.format(obj_name,E),D+'    ',S+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';J.write(A)
			elif i in F or h in F:
				Z=b;a=H
				if S>0:a='self, '
				if j in F or j in L:A='{}@classmethod\n'.format(D);A+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,Z)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,a,Z)
				A+=D+'    ...\n\n';J.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				K=F[8:-2];A=H
				if K in[f,d,e,g,'bytearray','bytes']:A=k.format(D,E,L,K)
				elif K in[V,U,R]:m={V:'{}',U:'[]',R:'()'};A=k.format(D,E,m[K],K)
				else:
					if not K in['object','set','frozenset']:K=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,K,F,L)
				J.write(A)
			else:J.write("# all other, type = '{0}'\n".format(F));J.write(D+E+' # type: Any\n')
		del T;del O
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
		try:os.stat(path);D=os.listdir(path)
		except (C,J):return
		for F in D:
			A=j.format(path,F)
			try:os.remove(A)
			except C:
				try:B.clean(A);os.rmdir(A)
				except C:pass
	def report(E,filename='modules.json'):
		J='firmware';F=',\n';G('Created stubs for {} modules on board {}\nPath: {}'.format(I(E._report),E._fwid,E.path));L=j.format(E.path,filename);B.collect()
		try:
			with K(L,'w')as A:
				A.write('{');A.write(X({J:E.info})[1:-1]);A.write(F);A.write(X({'stubber':{P:__version__},'stubtype':J})[1:-1]);A.write(F);A.write('"modules" :[\n');H=N
				for M in E._report:
					if H:H=D
					else:A.write(F)
					A.write(M)
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
				if E.args[0]==k:
					try:os.mkdir(B)
					except C as I:G(H.format(B));raise I
				else:G(H.format(B));raise E
		D=A+1
def _info():
	h=' on ';g='0.0.0';f='port';e='platform';d='machine';c='nodename';b='name';W='mpy';V='unknown';R='-';Q='sysname';K='v';G='build';F='family';C='ver';B='release';X=sys.implementation.name;Y=sys.platform if not sys.platform.startswith('pyb')else'stm32';A={b:X,B:g,P:g,G:H,Q:V,c:V,d:V,F:X,e:Y,f:Y,C:H}
	try:A[B]=L.join([S(A)for A in sys.implementation.version]);A[P]=A[B];A[b]=sys.implementation.name;A[W]=sys.implementation.mpy
	except J:pass
	if sys.platform not in('unix','win32'):
		try:
			D=os.uname();A[Q]=D[0];A[c]=D[1];A[B]=D[2];A[d]=D[4]
			if h in D[3]:
				N=D[3].split(h)[0]
				if A[Q]=='esp8266':
					if R in N:Z=N.split(R)[0]
					else:Z=N
					A[P]=A[B]=Z.lstrip(K)
				try:A[G]=N.split(R)[1]
				except T:pass
		except (T,J,TypeError):pass
	try:from pycopy import const as U;A[F]='pycopy';del U
	except (O,M):pass
	try:from pycom import FAT as U;A[F]='pycom';del U
	except (O,M):pass
	if A[e]=='esp32_LoBo':A[F]='loboris';A[f]='esp32'
	elif A[Q]=='ev3':
		A[F]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except O:pass
	if A[B]:A[C]=K+A[B].lstrip(K)
	if A[F]=='micropython':
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[G]!=H and I(A[G])<4:A[C]+=R+A[G]
	if A[C][0]!=K:A[C]=K+A[C]
	if W in A:
		i=int(A[W]);a=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][i>>10]
		if a:A['arch']=a
	return A
def get_root():
	try:A=os.getcwd()
	except (C,J):A=L
	B=A
	for B in [A,'/sd','/flash',F,L]:
		try:D=os.stat(B);break
		except C:continue
	return B
def m(filename):
	try:os.stat(filename);return N
	except C:return D
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
	try:A=bytes('abc',encoding='utf8');B=Z.__module__;return D
	except (a,J):return N
def n():
	Q='failed';H='.done';F='modulelist';import machine as R
	try:A=K(F+H,'r+b');O=N
	except C:A=K(F+H,'w+b');O=D
	stubber=Stubber(path=read_path())
	if not O:stubber.clean()
	with K(F+'.txt')as A:J=[B.strip()for B in A.read().split('\n')if I(B.strip())and B.strip()[0]!='#']
	B.collect();E={}
	try:
		with K(F+H)as A:
			for G in A.read().split('\n'):
				G=G.strip();B.collect()
				if I(G)>0:T,U=G.split('=',1);E[T]=U
	except (C,SyntaxError):pass
	B.collect();J=[A for A in J if A not in E.keys()];B.collect()
	for L in J:
		P=D
		try:P=stubber.create_one_stub(L)
		except MemoryError:R.reset()
		if P:M=stubber._report[-1]
		else:M=Q
		E[L]=S(M)
		with K(F+H,'a')as A:A.write('{}={}\n'.format(L,M))
	if I(E)>0:stubber._report=[A for(B,A)in E.items()if A!=Q];stubber.report()
if __name__=='__main__'or Z():
	try:logging.basicConfig(level=logging.INFO)
	except c:pass
	if not m('no_auto_stubber.txt'):n()