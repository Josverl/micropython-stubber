Z='utf8'
Y='{}/{}'
X=IndexError
W=NameError
V=print
U=NotImplementedError
Q='_'
O='version'
L=True
N=KeyError
M=ImportError
K=open
J='.'
I=len
H=False
F=AttributeError
G=''
B='/'
D=None
C=OSError
import sys,gc as E,uos as os
from utime import sleep_us as e
from ujson import dumps as P
__version__='1.5.4'
a=2
f=2
try:from machine import resetWDT as R
except M:
	def R():0
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		G=firmware_id;D=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise U('MicroPython 1.13.0 cannot be stubbed')
		except F:pass
		A._report=[];A.info=_info();E.collect()
		if G:A._fwid=str(G).lower()
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
		B=item_instance;A=[];G=[]
		for C in dir(B):
			try:D=getattr(B,C);A.append((C,repr(D),repr(type(D)),D))
			except F as H:G.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(C,B,H))
		A=[B for B in A if not B[0].startswith(Q)];E.collect();return A,G
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(D,module_name):
		A=module_name
		if A in D.problematic:return H
		if A in D.excluded:return H
		F='{}/{}.py'.format(D.path,A.replace(J,B));E.collect();G=E.mem_free();V('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(A,F,G))
		try:D.create_module_stub(A,F)
		except C:return H
		E.collect();return L
	def create_module_stub(F,module_name,file_name=D):
		H=file_name;A=module_name
		if A in F.problematic:return
		if H is D:H=F.path+B+A.replace(J,Q)+'.py'
		if B in A:A=A.replace(B,J)
		I=D
		try:I=__import__(A,D,D,'*')
		except M:return
		S(H)
		with K(H,'w')as L:O='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,F._fwid,F.info,__version__);L.write(O);L.write('from typing import Any\n\n');F.write_object_stub(L,I,A,G)
		F._report.append({'module':A,'file':H})
		if not A in['os','sys','logging','gc']:
			try:del I
			except (C,N):pass
			try:del sys.modules[A]
			except N:pass
		E.collect()
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='tuple';c='list';b='dict';a='{0}{1} = {2} # type: {3}\n';Z='bound_method';Y='Any';P=in_class;O=object_expr;M='Exception';J=fp;A=indent;E.collect()
		if O in L.problematic:return
		Q,g=L.get_obj_attributes(O)
		for (D,K,F,S) in Q:
			if D in['classmethod','staticmethod','BaseException',M]:continue
			R();e(1)
			if F=="<class 'type'>"and I(A)<=f*4:
				T=G;U=D.endswith(M)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if U:T=M
				B='\n{}class {}({}):\n'.format(A,D,T);B+=A+"    ''\n"
				if not U:B+=A+'    def __init__(self, *argv, **kwargs) -> None:\n';B+=A+"        ''\n";B+=A+'        ...\n'
				J.write(B);L.write_object_stub(J,S,'{0}.{1}'.format(obj_name,D),A+'    ',P+1)
			elif'method'in F or'function'in F:
				V=Y;X=G
				if P>0:X='self, '
				if Z in F or Z in K:B='{}@classmethod\n'.format(A);B+='{}def {}(cls, *args, **kwargs) -> {}:\n'.format(A,D,V)
				else:B='{}def {}({}*args, **kwargs) -> {}:\n'.format(A,D,X,V)
				B+=A+'    ...\n\n';J.write(B)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				H=F[8:-2];B=G
				if H in['str','int','float','bool','bytearray','bytes']:B=a.format(A,D,K,H)
				elif H in[b,c,d]:h={b:'{}',c:'[]',d:'()'};B=a.format(A,D,h[H],H)
				else:
					if not H in['object','set','frozenset']:H=Y
					B='{0}{1} : {2} ## {3} = {4}\n'.format(A,D,H,F,K)
				J.write(B)
			else:J.write("# all other, type = '{0}'\n".format(F));J.write(A+D+' # type: Any\n')
		del Q;del g
		try:del D,K,F,S
		except (C,N,W):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,Q)
		return A
	def clean(E,path=D):
		A=path
		if A is D:A=E.path
		V('Clean/remove files in folder: {}'.format(A))
		try:G=os.listdir(A)
		except (C,F):return
		for H in G:
			B=Y.format(A,H)
			try:os.remove(B)
			except C:
				try:E.clean(B);os.rmdir(B)
				except C:pass
	def report(B,filename='modules.json'):
		G='firmware';D=',\n';I=Y.format(B.path,filename);E.collect()
		try:
			with K(I,'w')as A:
				A.write('{');A.write(P({G:B.info})[1:-1]);A.write(D);A.write(P({'stubber':{O:__version__},'stubtype':G})[1:-1]);A.write(D);A.write('"modules" :[\n');F=L
				for J in B._report:
					if F:F=H
					else:A.write(D)
					A.write(P(J))
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
	f=' on ';e='0.0.0';d='port';c='platform';b='machine';a='nodename';Z='name';T='mpy';S='unknown';R='-';Q='sysname';L='v';K='family';H='build';C='ver';B='release';U=sys.implementation.name;V=sys.platform;A={Z:U,B:e,O:e,H:G,Q:S,a:S,b:S,K:U,c:V,d:V,C:G}
	try:A[B]=J.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[Z]=sys.implementation.name;A[T]=sys.implementation.mpy
	except F:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[a]=E.nodename;A[B]=E.release;A[b]=E.machine
			if f in E.version:
				P=E.version.split(f)[0]
				if A[Q]=='esp8266':
					if R in P:W=P.split(R)[0]
					else:W=P
					A[O]=A[B]=W.lstrip(L)
				try:A[H]=P.split(R)[1]
				except X:pass
		except (X,F,TypeError):pass
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
		if A[H]!=G and I(A[H])<4:A[C]+=R+A[H]
	if A[C][0]!=L:A[C]=L+A[C]
	if T in A:
		g=int(A[T]);Y=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][g>>10]
		if Y:A['arch']=Y
	return A
def get_root():
	try:A=os.getcwd()
	except (C,F):A=J
	D=A
	for D in [A,'/sd','/flash',B,J]:
		try:E=os.stat(D);break
		except C as G:continue
	return D
def A():sys.exit(1)
def read_path():
	B=G
	if I(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):B=sys.argv[2]
		else:A()
	elif I(sys.argv)==2:A()
	return B
def T():
	try:A=bytes('abc',encoding=Z);B=T.__module__;return H
	except (U,F):return L
def b():
	N=b'todo';M='.db';F='modulelist';import machine as O,btree
	try:D=K(F+M,'r+b');E=L
	except C:D=K(F+M,'w+b');E=H
	stubber=Stubber(path=read_path())
	if not E:stubber.clean()
	A=btree.open(D)
	if not E or I(list(A.keys()))==0:
		for P in K(F+'.txt'):
			B=P.strip()
			if I(B)and B[0]!='#':A[B]=N
		A.flush()
	for B in A.keys():
		if A[B]!=N:continue
		G=H
		try:G=stubber.create_one_stub(B.decode(Z))
		except MemoryError:A.close();D.close();O.reset()
		if G:J='good, I guess'
		else:J=b'skipped'
		A[B]=J;A.flush()
	A.close();D.close()
if __name__=='__main__'or T():
	try:logging.basicConfig(level=logging.INFO)
	except W:pass
	b()