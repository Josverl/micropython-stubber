Z='micropython'
Y='{}/{}'
X=IndexError
W=NameError
V=print
U=NotImplementedError
Q=True
P='_'
L=open
O='version'
N=KeyError
M=ImportError
J=len
I='.'
H=AttributeError
G=''
F=False
B='/'
D=None
C=OSError
import sys,gc as E,uos as os
from utime import sleep_us as e
from ujson import dumps as K
__version__='1.5.5'
a=2
f=2
try:from machine import resetWDT as R
except M:
	def R():0
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		F=firmware_id;D=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise U('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();E.collect()
		if F:A._fwid=str(F).lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if D:
			if D.endswith(B):D=D[:-1]
		else:D=get_root()
		A.path='{}/stubs/{}'.format(D,A.flat_fwid).replace('//',B)
		try:S(D+B)
		except C:pass
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(I,item_instance):
		B=item_instance;A=[];F=[]
		for C in dir(B):
			try:D=getattr(B,C);A.append((C,repr(D),repr(type(D)),D))
			except H as G:F.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(C,B,G))
		A=[B for B in A if not B[0].startswith(P)];E.collect();return A,F
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(D,module_name):
		A=module_name
		if A in D.problematic:return F
		if A in D.excluded:return F
		G='{}/{}.py'.format(D.path,A.replace(I,B));E.collect();J=E.mem_free();V('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(A,G,J));H=F
		try:H=D.create_module_stub(A,G)
		except C:return F
		E.collect();return H
	def create_module_stub(H,module_name,file_name=D):
		J=file_name;A=module_name
		if A in H.problematic:return F
		if J is D:J=H.path+B+A.replace(I,P)+'.py'
		if B in A:A=A.replace(B,I)
		K=D
		try:K=__import__(A,D,D,'*')
		except M:return F
		S(J)
		with L(J,'w')as O:R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,H.info,__version__);O.write(R);O.write('from typing import Any\n\n');H.write_object_stub(O,K,A,G)
		H._report.append({'module':A,'file':J})
		if not A in['os','sys','logging','gc']:
			try:del K
			except (C,N):pass
			try:del sys.modules[A]
			except N:pass
		E.collect();return Q
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='tuple';c='list';b='dict';a='{0}{1} = {2} # type: {3}\n';Z='bound_method';Y='Any';P=in_class;O=object_expr;M='Exception';I=fp;A=indent;E.collect()
		if O in L.problematic:return
		Q,g=L.get_obj_attributes(O)
		for (D,K,F,S) in Q:
			if D in['classmethod','staticmethod','BaseException',M]:continue
			R();e(1)
			if F=="<class 'type'>"and J(A)<=f*4:
				T=G;U=D.endswith(M)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if U:T=M
				B='\n{}class {}({}):\n'.format(A,D,T);B+=A+"    ''\n"
				if not U:B+=A+'    def __init__(self, *argv, **kwargs) -> None:\n';B+=A+"        ''\n";B+=A+'        ...\n'
				I.write(B);L.write_object_stub(I,S,'{0}.{1}'.format(obj_name,D),A+'    ',P+1)
			elif'method'in F or'function'in F:
				V=Y;X=G
				if P>0:X='self, '
				if Z in F or Z in K:B='{}@classmethod\n'.format(A);B+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(A,D,V)
				else:B='{}def {}({}*args, **kwargs) -> {}:\n'.format(A,D,X,V)
				B+=A+'    ...\n\n';I.write(B)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				H=F[8:-2];B=G
				if H in['str','int','float','bool','bytearray','bytes']:B=a.format(A,D,K,H)
				elif H in[b,c,d]:h={b:'{}',c:'[]',d:'()'};B=a.format(A,D,h[H],H)
				else:
					if not H in['object','set','frozenset']:H=Y
					B='{0}{1} : {2} ## {3} = {4}\n'.format(A,D,H,F,K)
				I.write(B)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(A+D+' # type: Any\n')
		del Q;del g
		try:del D,K,F,S
		except (C,N,W):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,P)
		return A
	def clean(E,path=D):
		A=path
		if A is D:A=E.path
		V('Clean/remove files in folder: {}'.format(A))
		try:F=os.listdir(A)
		except (C,H):return
		for G in F:
			B=Y.format(A,G)
			try:os.remove(B)
			except C:
				try:E.clean(B);os.rmdir(B)
				except C:pass
	def report(B,filename='modules.json'):
		H='firmware';D=',\n';I=Y.format(B.path,filename);E.collect()
		try:
			with L(I,'w')as A:
				A.write('{');A.write(K({H:B.info})[1:-1]);A.write(D);A.write(K({'stubber':{O:__version__},'stubtype':H})[1:-1]);A.write(D);A.write('"modules" :[\n');G=Q
				for J in B._report:
					if G:G=F
					else:A.write(D)
					A.write(K(J))
				A.write('\n]}')
			M=B._start_free-E.mem_free()
		except C:pass
def S(path):
	D=path;A=F=0
	while A!=-1:
		A=D.find(B,F)
		if A!=-1:
			if A==0:E=D[0]
			else:E=D[0:A]
			try:I=os.stat(E)
			except C as G:
				if G.args[0]==a:
					try:os.mkdir(E)
					except C as H:raise H
				else:raise G
		F=A+1
def _info():
	g=' on ';f='0.0.0';e='port';d='platform';c='machine';b='nodename';a='name';T='mpy';S='unknown';R='-';Q='sysname';L='v';K='family';F='build';C='ver';B='release';U=sys.implementation.name;V=sys.platform;A={a:U,B:f,O:f,F:G,Q:S,b:S,c:S,K:U,d:V,e:V,C:G}
	try:A[B]=I.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[a]=sys.implementation.name;A[T]=sys.implementation.mpy
	except H:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[b]=E.nodename;A[B]=E.release;A[c]=E.machine
			if g in E.version:
				P=E.version.split(g)[0]
				if A[Q]=='esp8266':
					if R in P:W=P.split(R)[0]
					else:W=P
					A[O]=A[B]=W.lstrip(L)
				try:A[F]=P.split(R)[1]
				except X:pass
		except (X,H,TypeError):pass
	try:from pycopy import const;A[K]='pycopy';del const
	except (M,N):pass
	if A[d]=='esp32_LoBo':A[K]='loboris';A[e]='esp32'
	elif A[Q]=='ev3':
		A[K]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except M:pass
	if A[B]:A[C]=L+A[B].lstrip(L)
	if A[K]==Z:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[F]!=G and J(A[F])<4:A[C]+=R+A[F]
	if A[C][0]!=L:A[C]=L+A[C]
	if T in A:
		h=int(A[T]);Y=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][h>>10]
		if Y:A['arch']=Y
	return A
def get_root():
	try:A=os.getcwd()
	except (C,H):A=I
	D=A
	for D in [A,'/sd','/flash',B,I]:
		try:E=os.stat(D);break
		except C as F:continue
	return D
def A():sys.exit(1)
def read_path():
	B=G
	if J(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):B=sys.argv[2]
		else:A()
	elif J(sys.argv)==2:A()
	return B
def T():
	try:A=bytes('abc',encoding='utf8');B=T.__module__;return F
	except (U,H):return Q
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	try:stubber.modules=[A.strip()for A in L('modulelist'+'.txt')if J(A.strip())and A.strip()[0]!='#']
	except C:stubber.modules=[Z]
	E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or T():
	try:logging.basicConfig(level=logging.INFO)
	except W:pass
	main()