b='{}/{}'
a=bytes
Z=IndexError
Y=NameError
X=print
W=NotImplementedError
S='utf8'
R='_'
Q=repr
O='version'
L=True
N=KeyError
M=ImportError
K=open
J='.'
I=len
H=AttributeError
G=''
F='/'
B=False
D=None
C=OSError
import sys,gc as E,uos as os
from utime import sleep_us as e
from ujson import dumps as P
__version__='1.7.1'
c=2
f=2
try:from machine import resetWDT as T
except M:
	def T():0
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		D=firmware_id;B=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise W('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();E.collect()
		if D:A._fwid=str(D).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if B:
			if B.endswith(F):B=B[:-1]
		else:B=get_root()
		A.path='{}/stubs/{}'.format(B,A.flat_fwid).replace('//',F)
		try:U(B+F)
		except C:pass
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(I,item_instance):
		B=item_instance;A=[];F=[]
		for C in dir(B):
			try:D=getattr(B,C);A.append((C,Q(D),Q(type(D)),D))
			except H as G:F.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(C,B,G))
		A=[B for B in A if not B[0].startswith(R)];E.collect();return A,F
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(D,module_name):
		A=module_name
		if A in D.problematic:return B
		if A in D.excluded:return B
		G='{}/{}.py'.format(D.path,A.replace(J,F));E.collect();I=E.mem_free();X('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(A,G,I));H=B
		try:H=D.create_module_stub(A,G)
		except C:return B
		E.collect();return H
	def create_module_stub(H,module_name,file_name=D):
		I=file_name;A=module_name
		if A in H.problematic:return B
		if I is D:I=H.path+F+A.replace(J,R)+'.py'
		if F in A:A=A.replace(F,J)
		O=D
		try:O=__import__(A,D,D,'*')
		except M:return B
		U(I)
		with K(I,'w')as P:Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,H.info,__version__);P.write(Q);P.write('from typing import Any\n\n');H.write_object_stub(P,O,A,G)
		H._report.append({'module':A,'file':I})
		if not A in['os','sys','logging','gc']:
			try:del O
			except (C,N):pass
			try:del sys.modules[A]
			except N:pass
		E.collect();return L
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='tuple';c='list';b='dict';a='{0}{1} = {2} # type: {3}\n';Z='bound_method';X='Any';P=in_class;O=object_expr;M='Exception';J=fp;A=indent;E.collect()
		if O in L.problematic:return
		Q,g=L.get_obj_attributes(O)
		for (D,K,F,R) in Q:
			if D in['classmethod','staticmethod','BaseException',M]:continue
			T();e(1)
			if F=="<class 'type'>"and I(A)<=f*4:
				S=G;U=D.endswith(M)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if U:S=M
				B='\n{}class {}({}):\n'.format(A,D,S)
				if U:B+=A+'    ...\n'
				else:B+=A+'    def __init__(self, *argv, **kwargs) -> None:\n';B+=A+'        ...\n\n'
				J.write(B);L.write_object_stub(J,R,'{0}.{1}'.format(obj_name,D),A+'    ',P+1)
			elif'method'in F or'function'in F:
				V=X;W=G
				if P>0:W='self, '
				if Z in F or Z in K:B='{}@classmethod\n'.format(A);B+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(A,D,V)
				else:B='{}def {}({}*args, **kwargs) -> {}:\n'.format(A,D,W,V)
				B+=A+'    ...\n\n';J.write(B)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				H=F[8:-2];B=G
				if H in['str','int','float','bool','bytearray','bytes']:B=a.format(A,D,K,H)
				elif H in[b,c,d]:h={b:'{}',c:'[]',d:'()'};B=a.format(A,D,h[H],H)
				else:
					if not H in['object','set','frozenset']:H=X
					B='{0}{1} : {2} ## {3} = {4}\n'.format(A,D,H,F,K)
				J.write(B)
			else:J.write("# all other, type = '{0}'\n".format(F));J.write(A+D+' # type: Any\n')
		del Q;del g
		try:del D,K,F,R
		except (C,N,Y):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,R)
		return A
	def clean(E,path=D):
		A=path
		if A is D:A=E.path
		X('Clean/remove files in folder: {}'.format(A))
		try:F=os.listdir(A)
		except (C,H):return
		for G in F:
			B=b.format(A,G)
			try:os.remove(B)
			except C:
				try:E.clean(B);os.rmdir(B)
				except C:pass
	def report(D,filename='modules.json'):
		H='firmware';F=',\n';I=b.format(D.path,filename);E.collect()
		try:
			with K(I,'w')as A:
				A.write('{');A.write(P({H:D.info})[1:-1]);A.write(F);A.write(P({'stubber':{O:__version__},'stubtype':H})[1:-1]);A.write(F);A.write('"modules" :[\n');G=L
				for J in D._report:
					if G:G=B
					else:A.write(F)
					A.write(P(J))
				A.write('\n]}')
			M=D._start_free-E.mem_free()
		except C:pass
def U(path):
	B=path;A=E=0
	while A!=-1:
		A=B.find(F,E)
		if A!=-1:
			if A==0:D=B[0]
			else:D=B[0:A]
			try:I=os.stat(D)
			except C as G:
				if G.args[0]==c:
					try:os.mkdir(D)
					except C as H:raise H
				else:raise G
		E=A+1
def _info():
	f=' on ';e='0.0.0';d='port';c='platform';b='machine';a='nodename';Y='name';T='mpy';S='unknown';R='-';Q='sysname';L='v';K='family';F='build';C='ver';B='release';U=sys.implementation.name;V=sys.platform if not sys.platform.startswith('pyb')else'stm32';A={Y:U,B:e,O:e,F:G,Q:S,a:S,b:S,K:U,c:V,d:V,C:G}
	try:A[B]=J.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[Y]=sys.implementation.name;A[T]=sys.implementation.mpy
	except H:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[a]=E.nodename;A[B]=E.release;A[b]=E.machine
			if f in E.version:
				P=E.version.split(f)[0]
				if A[Q]=='esp8266':
					if R in P:W=P.split(R)[0]
					else:W=P
					A[O]=A[B]=W.lstrip(L)
				try:A[F]=P.split(R)[1]
				except Z:pass
		except (Z,H,TypeError):pass
	try:from pycopy import const;A[K]='pycopy';del const
	except (M,N):pass
	if A[c]=='esp32_LoBo':A[K]='loboris';A[d]='esp32'
	elif A[Q]=='ev3':
		A[K]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except M:pass
	if A[B]:A[C]=L+A[B].lstrip(L)
	if A[K]=='micropython':
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[F]!=G and I(A[F])<4:A[C]+=R+A[F]
	if A[C][0]!=L:A[C]=L+A[C]
	if T in A:
		g=int(A[T]);X=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][g>>10]
		if X:A['arch']=X
	return A
def get_root():
	try:A=os.getcwd()
	except (C,H):A=J
	B=A
	for B in [A,'/sd','/flash',F,J]:
		try:D=os.stat(B);break
		except C as E:continue
	return B
def A():sys.exit(1)
def read_path():
	B=G
	if I(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):B=sys.argv[2]
		else:A()
	elif I(sys.argv)==2:A()
	return B
def V():
	try:A=a('abc',encoding=S);C=V.__module__;return B
	except (W,H):return L
def d():
	O=b'fail';N='.db';H=b'todo';G='modulelist';import machine as P,btree
	try:E=K(G+N,'r+b');F=L
	except C:E=K(G+N,'w+b');F=B
	stubber=Stubber(path=read_path())
	if not F:stubber.clean()
	A=btree.open(E)
	if not F or I(list(A.keys()))==0:
		for R in K(G+'.txt'):
			D=R.strip()
			if I(D)and D[0]!='#':A[D]=H
		A.flush()
	for D in A.keys():
		if A[D]!=H:continue
		J=B
		try:J=stubber.create_one_stub(D.decode(S))
		except MemoryError:A.close();E.close();P.reset()
		if J:M=a(Q(stubber._report[-1]),S)
		else:M=O
		A[D]=M;A.flush()
	all=[B for B in A.items()if not B[1]==H and not B[1]==O]
	if I(all)>0:stubber._report=all;stubber.report()
	A.close();E.close()
if __name__=='__main__'or V():
	try:logging.basicConfig(level=logging.INFO)
	except Y:pass
	d()