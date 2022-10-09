k='{}/{}'
j='method'
i='function'
h='bool'
g='str'
f='float'
e='int'
d=bytes
c=NameError
b=print
a=sorted
Z=NotImplementedError
W='utf8'
V='_'
U='dict'
T='list'
R='tuple'
S=IndexError
P='version'
O=ImportError
N=repr
M=True
L=KeyError
K=open
I='.'
J=len
H=AttributeError
G=''
F='/'
D=None
A=False
B=OSError
import gc as E,sys,uos as os
from ujson import dumps as Q
__version__='1.9.11'
l=2
m=2
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		D=firmware_id;C=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise Z('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();E.collect()
		if D:A._fwid=str(D).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if C:
			if C.endswith(F):C=C[:-1]
		else:C=get_root()
		A.path='{}/stubs/{}'.format(C,A.flat_fwid).replace('//',F)
		try:X(C+F)
		except B:pass
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;A=[];J=[]
		for I in dir(F):
			try:
				B=getattr(F,I)
				try:C=N(type(B)).split("'")[1]
				except S:C=G
				if C in(e,f,g,h,R,T,U):D=1
				elif C in(i,j):D=2
				elif C in'class':D=3
				else:D=4
				A.append((I,N(B),N(type(B)),B,D))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(I,F,K))
		A=a([B for B in A if not B[0].startswith(V)],key=lambda x:x[4]);E.collect();return A,J
	def add_modules(A,modules):A.modules=a(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(D,module_name):
		C=module_name
		if C in D.problematic:return A
		if C in D.excluded:return A
		G='{}/{}.py'.format(D.path,C.replace(I,F));E.collect();J=E.mem_free();b('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(C,G,J));H=A
		try:H=D.create_module_stub(C,G)
		except B:return A
		E.collect();return H
	def create_module_stub(H,module_name,file_name=D):
		J=file_name;C=module_name
		if C in H.problematic:return A
		if J is D:J=H.path+F+C.replace(I,V)+'.py'
		if F in C:C=C.replace(F,I)
		N=D
		try:N=__import__(C,D,D,'*')
		except O:return A
		X(J)
		with K(J,'w')as P:Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,H._fwid,H.info,__version__);P.write(Q);P.write('from typing import Any\n\n');H.write_object_stub(P,N,C,G)
		H._report.append({'module':C,'file':J})
		if not C in['os','sys','logging','gc']:
			try:del N
			except (B,L):pass
			try:del sys.modules[C]
			except L:pass
		E.collect();return M
	def write_object_stub(M,fp,object_expr,obj_name,indent,in_class=0):
		b='{0}{1} = {2} # type: {3}\n';a='bound_method';Z='Any';P=in_class;O=object_expr;N='Exception';H=fp;C=indent;E.collect()
		if O in M.problematic:return
		Q,d=M.get_obj_attributes(O)
		for (D,K,F,S,l) in Q:
			if D in['classmethod','staticmethod','BaseException',N]:continue
			if F=="<class 'type'>"and J(C)<=m*4:
				V=G;W=D.endswith(N)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if W:V=N
				A='\n{}class {}({}):\n'.format(C,D,V)
				if W:A+=C+'    ...\n';H.write(A);return
				H.write(A);M.write_object_stub(H,S,'{0}.{1}'.format(obj_name,D),C+'    ',P+1);A=C+'    def __init__(self, *argv, **kwargs) -> None: ##\n';A+=C+'        ...\n\n';H.write(A)
			elif j in F or i in F:
				X=Z;Y=G
				if P>0:Y='self, '
				if a in F or a in K:A='{}@classmethod\n'.format(C);A+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(C,D,X)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(C,D,Y,X)
				A+=C+'    ...\n\n';H.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				I=F[8:-2];A=G
				if I in[g,e,f,h,'bytearray','bytes']:A=b.format(C,D,K,I)
				elif I in[U,T,R]:k={U:'{}',T:'[]',R:'()'};A=b.format(C,D,k[I],I)
				else:
					if not I in['object','set','frozenset']:I=Z
					A='{0}{1} : {2} ## {3} = {4}\n'.format(C,D,I,F,K)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(F));H.write(C+D+' # type: Any\n')
		del Q;del d
		try:del D,K,F,S
		except (B,L,c):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,V)
		return A
	def clean(E,path=D):
		A=path
		if A is D:A=E.path
		b('Clean/remove files in folder: {}'.format(A))
		try:F=os.listdir(A)
		except (B,H):return
		for G in F:
			C=k.format(A,G)
			try:os.remove(C)
			except B:
				try:E.clean(C);os.rmdir(C)
				except B:pass
	def report(D,filename='modules.json'):
		H='firmware';F=',\n';I=k.format(D.path,filename);E.collect()
		try:
			with K(I,'w')as C:
				C.write('{');C.write(Q({H:D.info})[1:-1]);C.write(F);C.write(Q({'stubber':{P:__version__},'stubtype':H})[1:-1]);C.write(F);C.write('"modules" :[\n');G=M
				for J in D._report:
					if G:G=A
					else:C.write(F)
					C.write(Q(J))
				C.write('\n]}')
			L=D._start_free-E.mem_free()
		except B:pass
def X(path):
	C=path;A=E=0
	while A!=-1:
		A=C.find(F,E)
		if A!=-1:
			if A==0:D=C[0]
			else:D=C[0:A]
			try:I=os.stat(D)
			except B as G:
				if G.args[0]==l:
					try:os.mkdir(D)
					except B as H:raise H
				else:raise G
		E=A+1
def _info():
	g=' on ';f='0.0.0';e='port';d='platform';c='machine';b='nodename';a='name';V='mpy';U='unknown';R='-';Q='sysname';M='v';K='build';F='family';C='ver';B='release';W=sys.implementation.name;X=sys.platform if not sys.platform.startswith('pyb')else'stm32';A={a:W,B:f,P:f,K:G,Q:U,b:U,c:U,F:W,d:X,e:X,C:G}
	try:A[B]=I.join([str(A)for A in sys.implementation.version]);A[P]=A[B];A[a]=sys.implementation.name;A[V]=sys.implementation.mpy
	except H:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[b]=E.nodename;A[B]=E.release;A[c]=E.machine
			if g in E.version:
				N=E.version.split(g)[0]
				if A[Q]=='esp8266':
					if R in N:Y=N.split(R)[0]
					else:Y=N
					A[P]=A[B]=Y.lstrip(M)
				try:A[K]=N.split(R)[1]
				except S:pass
		except (S,H,TypeError):pass
	try:from pycopy import const as T;A[F]='pycopy';del T
	except (O,L):pass
	try:from pycom import FAT as T;A[F]='pycom';del T
	except (O,L):pass
	if A[d]=='esp32_LoBo':A[F]='loboris';A[e]='esp32'
	elif A[Q]=='ev3':
		A[F]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except O:pass
	if A[B]:A[C]=M+A[B].lstrip(M)
	if A[F]=='micropython':
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[K]!=G and J(A[K])<4:A[C]+=R+A[K]
	if A[C][0]!=M:A[C]=M+A[C]
	if V in A:
		h=int(A[V]);Z=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][h>>10]
		if Z:A['arch']=Z
	return A
def get_root():
	try:A=os.getcwd()
	except (B,H):A=I
	C=A
	for C in [A,'/sd','/flash',F,I]:
		try:D=os.stat(C);break
		except B:continue
	return C
def n(filename):
	try:os.stat(filename);return M
	except B:return A
def C():sys.exit(1)
def read_path():
	A=G
	if J(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):A=sys.argv[2]
		else:C()
	elif J(sys.argv)==2:C()
	return A
def Y():
	try:B=d('abc',encoding=W);C=Y.__module__;return A
	except (Z,H):return M
def o():
	P=b'fail';O='.db';H=b'todo';G='modulelist';import btree,machine as Q
	try:E=K(G+O,'r+b');F=M
	except B:E=K(G+O,'w+b');F=A
	stubber=Stubber(path=read_path())
	if not F:stubber.clean()
	C=btree.open(E)
	if not F or J(list(C.keys()))==0:
		for R in K(G+'.txt'):
			D=R.strip()
			if J(D)and D[0]!='#':C[D]=H
		C.flush()
	for D in C.keys():
		if C[D]!=H:continue
		I=A
		try:I=stubber.create_one_stub(D.decode(W))
		except MemoryError:C.close();E.close();Q.reset()
		if I:L=d(N(stubber._report[-1]),W)
		else:L=P
		C[D]=L;C.flush()
	all=[A for A in C.items()if not A[1]==H and not A[1]==P]
	if J(all)>0:stubber._report=all;stubber.report()
	C.close();E.close()
if __name__=='__main__'or Y():
	try:logging.basicConfig(level=logging.INFO)
	except c:pass
	if not n('no_auto_stubber.txt'):o()