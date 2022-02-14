Z='micropython'
Y='{}/{}'
X=IndexError
W=NameError
V=print
U=NotImplementedError
Q=True
P='_'
N=open
O='version'
L=len
K=KeyError
J=ImportError
I='.'
H=AttributeError
G=''
F=False
B='/'
D=None
C=OSError
import sys,gc as E,uos as os
from utime import sleep_us as e
from ujson import dumps as M
__version__='1.5.5'
a=2
f=2
try:from machine import resetWDT as R
except J:
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
		L=file_name;A=module_name
		if A in H.problematic:return F
		if L is D:L=H.path+B+A.replace(I,P)+'.py'
		if B in A:A=A.replace(B,I)
		M=D
		try:M=__import__(A,D,D,'*')
		except J:return F
		S(L)
		with N(L,'w')as O:R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,H.info,__version__);O.write(R);O.write('from typing import Any\n\n');H.write_object_stub(O,M,A,G)
		H._report.append({'module':A,'file':L})
		if not A in['os','sys','logging','gc']:
			try:del M
			except (C,K):pass
			try:del sys.modules[A]
			except K:pass
		E.collect();return Q
	def write_object_stub(M,fp,object_expr,obj_name,indent,in_class=0):
		d='tuple';c='list';b='dict';a='{0}{1} = {2} # type: {3}\n';Z='bound_method';Y='Any';P=in_class;O=object_expr;N='Exception';I=fp;A=indent;E.collect()
		if O in M.problematic:return
		Q,g=M.get_obj_attributes(O)
		for (D,J,F,S) in Q:
			if D in['classmethod','staticmethod','BaseException',N]:continue
			R();e(1)
			if F=="<class 'type'>"and L(A)<=f*4:
				T=G;U=D.endswith(N)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if U:T=N
				B='\n{}class {}({}):\n'.format(A,D,T);B+=A+"    ''\n"
				if not U:B+=A+'    def __init__(self, *argv, **kwargs) -> None:\n';B+=A+"        ''\n";B+=A+'        ...\n'
				I.write(B);M.write_object_stub(I,S,'{0}.{1}'.format(obj_name,D),A+'    ',P+1)
			elif'method'in F or'function'in F:
				V=Y;X=G
				if P>0:X='self, '
				if Z in F or Z in J:B='{}@classmethod\n'.format(A);B+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(A,D,V)
				else:B='{}def {}({}*args, **kwargs) -> {}:\n'.format(A,D,X,V)
				B+=A+'    ...\n\n';I.write(B)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				H=F[8:-2];B=G
				if H in['str','int','float','bool','bytearray','bytes']:B=a.format(A,D,J,H)
				elif H in[b,c,d]:h={b:'{}',c:'[]',d:'()'};B=a.format(A,D,h[H],H)
				else:
					if not H in['object','set','frozenset']:H=Y
					B='{0}{1} : {2} ## {3} = {4}\n'.format(A,D,H,F,J)
				I.write(B)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(A+D+' # type: Any\n')
		del Q;del g
		try:del D,J,F,S
		except (C,K,W):pass
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
			with N(I,'w')as A:
				A.write('{');A.write(M({H:B.info})[1:-1]);A.write(D);A.write(M({'stubber':{O:__version__},'stubtype':H})[1:-1]);A.write(D);A.write('"modules" :[\n');G=Q
				for J in B._report:
					if G:G=F
					else:A.write(D)
					A.write(M(J))
				A.write('\n]}')
			K=B._start_free-E.mem_free()
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
	h=' on ';g='0.0.0';f='port';e='platform';d='machine';c='nodename';b='name';U='mpy';T='unknown';R='-';Q='sysname';N='v';M='build';F='family';C='ver';B='release';V=sys.implementation.name;W=sys.platform;A={b:V,B:g,O:g,M:G,Q:T,c:T,d:T,F:V,e:W,f:W,C:G}
	try:A[B]=I.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[b]=sys.implementation.name;A[U]=sys.implementation.mpy
	except H:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[c]=E.nodename;A[B]=E.release;A[d]=E.machine
			if h in E.version:
				P=E.version.split(h)[0]
				if A[Q]=='esp8266':
					if R in P:Y=P.split(R)[0]
					else:Y=P
					A[O]=A[B]=Y.lstrip(N)
				try:A[M]=P.split(R)[1]
				except X:pass
		except (X,H,TypeError):pass
	try:from pycopy import const as S;A[F]='pycopy';del S
	except (J,K):pass
	try:from pycom import FAT as S;A[F]='pycom';del S
	except (J,K):pass
	if A[e]=='esp32_LoBo':A[F]='loboris';A[f]='esp32'
	elif A[Q]=='ev3':
		A[F]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except J:pass
	if A[B]:A[C]=N+A[B].lstrip(N)
	if A[F]==Z:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[M]!=G and L(A[M])<4:A[C]+=R+A[M]
	if A[C][0]!=N:A[C]=N+A[C]
	if U in A:
		i=int(A[U]);a=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][i>>10]
		if a:A['arch']=a
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
	if L(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):B=sys.argv[2]
		else:A()
	elif L(sys.argv)==2:A()
	return B
def T():
	try:A=bytes('abc',encoding='utf8');B=T.__module__;return F
	except (U,H):return Q
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	try:stubber.modules=[A.strip()for A in N('modulelist'+'.txt')if L(A.strip())and A.strip()[0]!='#']
	except C:stubber.modules=[Z]
	E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or T():
	try:logging.basicConfig(level=logging.INFO)
	except W:pass
	main()