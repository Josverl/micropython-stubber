A3='No report file'
A2='Failed to create the report.'
A1='method'
A0='function'
z='str'
y='float'
x='int'
w='micropython'
v='stubber'
u=Exception
t=KeyError
s=sorted
r=MemoryError
q=NotImplementedError
m='variant'
l=',\n'
k='modules.json'
j='{}/{}'
i='w'
h='dict'
g='list'
f='tuple'
e=TypeError
d=str
c=repr
X='-preview'
W=True
V='family'
U='board_id'
T='board'
S=len
R=IndexError
Q=print
P=ImportError
O=open
N=dir
M='port'
L='.'
J=AttributeError
I=False
H=None
G='/'
E='-'
D=OSError
C='version'
B=''
import gc as F,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except P:pass
try:from collections import OrderedDict as n
except P:from ucollections import OrderedDict as n
__version__='v1.26.1'
A4=2
A5=44
A6=2
A7=['lib','/lib','/sd/lib','/flash/lib',L]
class K:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=Q
	@staticmethod
	def getLogger(name):return K()
	@classmethod
	def basicConfig(A,level):A.level=level
	def debug(A,msg):
		if A.level<=K.DEBUG:A.prnt('DEBUG :',msg)
	def info(A,msg):
		if A.level<=K.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=K.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=K.ERROR:A.prnt('ERROR :',msg)
A=K.getLogger(v)
K.basicConfig(level=K.INFO)
class Stubber:
	def __init__(B,path=B,firmware_id=B):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise q('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		B.info=_info();A.info('Port: {}'.format(B.info[M]));A.info('Board: {}'.format(B.info[T]));A.info('Board_ID: {}'.format(B.info[U]));F.collect()
		if C:B._fwid=C.lower()
		elif B.info[V]==w:B._fwid='{family}-v{version}-{port}-{board_id}'.format(**B.info).rstrip(E)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=F.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',G)
		try:Y(path+G)
		except D:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[];B._json_name=H;B._json_first=I
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for A in N(H):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=getattr(H,A)
				try:E=c(type(D)).split("'")[1]
				except R:E=B
				if E in{x,y,z,'bool',f,g,h}:G=1
				elif E in{A0,A1}:G=2
				elif E in'class':G=3
				else:G=4
				C.append((A,c(D),c(type(D)),D,G))
			except J as I:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,I))
			except r as I:Q('MemoryError: {}'.format(I));sleep(1);reset()
		C=s([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return C,K
	def add_modules(A,modules):A.modules=s(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber {} on {}'.format(__version__,B._fwid));B.report_start();F.collect()
		for C in B.modules:B.create_one_stub(C)
		B.report_end();A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return I
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return I
		H='{}/{}.pyi'.format(C.path,B.replace(L,G));F.collect();E=I
		try:E=C.create_module_stub(B,H)
		except D:return I
		F.collect();return E
	def create_module_stub(J,module_name,file_name=H):
		E=file_name;C=module_name
		if E is H:K=C.replace(L,'_')+'.pyi';E=J.path+G+K
		else:K=E.split(G)[-1]
		if G in C:C=C.replace(G,L)
		M=H
		try:M=__import__(C,H,H,'*');Q=F.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,K,Q))
		except P:return I
		Y(E)
		with O(E,i)as N:R=d(J.info).replace('OrderedDict(',B).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,J._fwid,R,__version__);N.write(S);N.write('from __future__ import annotations\nfrom typing import Any, Final, Generator\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(N,M,C,B)
		J.report_add(C,E)
		if C not in{'os','sys','logging','gc'}:
			try:del M
			except(D,t):A.warning('could not del new_module')
		F.collect();return W
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		Y=' at ...>';X='{0}{1}: {3} = {2}\n';W='bound_method';V='Incomplete';O=in_class;N='Exception';M=object_expr;K=' at ';J=fp;E=indent;F.collect()
		if M in L.problematic:A.warning('SKIPPING problematic module:{}'.format(M));return
		Z,P=L.get_obj_attributes(M)
		if P:A.error(P)
		for(C,H,I,a,c)in Z:
			if C in['classmethod','staticmethod','BaseException',N]:continue
			if C[0].isdigit():A.warning('NameError: invalid name {}'.format(C));continue
			if I=="<class 'type'>"and S(E)<=A6*4:
				Q=B;R=C.endswith(N)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=N
				D='\n{}class {}({}):\n'.format(E,C,Q)
				if R:D+=E+'    ...\n';J.write(D);continue
				J.write(D);L.write_object_stub(J,a,'{0}.{1}'.format(obj_name,C),E+'    ',O+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';J.write(D)
			elif any(A in I for A in[A1,A0,'closure']):
				T=V;U=B
				if O>0:U='self, '
				if W in I or W in H:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,C,T)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,C,U,T)
				D+=E+'    ...\n\n';J.write(D)
			elif I=="<class 'module'>":0
			elif I.startswith("<class '"):
				G=I[8:-2];D=B
				if G in(z,x,y,'bool','bytearray','bytes'):
					if C.upper()==C:D='{0}{1}: Final[{3}] = {2}\n'.format(E,C,H,G)
					else:D=X.format(E,C,H,G)
				elif G in(h,g,f):b={h:'{}',g:'[]',f:'()'};D=X.format(E,C,b[G],G)
				elif G in('object','set','frozenset','Pin'):D='{0}{1}: {2} ## = {4}\n'.format(E,C,G,I,H)
				elif G=='generator':G='Generator';D='{0}def {1}(*args, **kwargs) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(E,C,G,I,H)
				else:
					G=V
					if K in H:H=H.split(K)[0]+Y
					if K in H:H=H.split(K)[0]+Y
					D='{0}{1}: {2} ## {3} = {4}\n'.format(E,C,G,I,H)
				J.write(D)
			else:J.write("# all other, type = '{0}'\n".format(I));J.write(E+C+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(C,path=B):
		if not path:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except(D,J):return
		for F in E:
			B=j.format(path,F)
			try:os.remove(B)
			except D:
				try:C.clean(B);os.rmdir(B)
				except D:pass
	def report_start(B,filename=k):
		G='firmware';B._json_name=j.format(B.path,filename);B._json_first=W;Y(B._json_name);A.info('Report file: {}'.format(B._json_name));F.collect()
		try:
			with O(B._json_name,i)as E:E.write('{');E.write(dumps({G:B.info})[1:-1]);E.write(l);E.write(dumps({v:{C:__version__},'stubtype':G})[1:-1]);E.write(l);E.write('"modules" :[\n')
		except D as I:A.error(A2);B._json_name=H;raise I
	def report_add(B,module_name,stub_file):
		if not B._json_name:raise u(A3)
		try:
			with O(B._json_name,'a')as C:
				if not B._json_first:C.write(l)
				else:B._json_first=I
				E='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',G));C.write(E)
		except D:A.error(A2)
	def report_end(B):
		if not B._json_name:raise u(A3)
		with O(B._json_name,'a')as C:C.write('\n]}')
		A.info('Path: {}'.format(B.path))
def Y(path):
	B=E=0
	while B!=-1:
		B=path.find(G,E)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except D as F:
				if F.args[0]in[A4,A5]:
					try:A.debug('Create folder {}'.format(C));os.mkdir(C)
					except D as H:A.error('failed to create folder {}'.format(C));raise H
		E=B+1
def Z(s):
	C=' on '
	if not s:return B
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not E in s:return B
		A=s.split(E)[1];return A
	if not X in s:return B
	A=s.split(X)[1].split(L)[1];return A
def _info():
	d='ev3-pybricks';c='pycom';b='pycopy';a='unix';Y='win32';W='cpu';S='ver';K='arch';F='mpy';D='build'
	try:L=sys.implementation[0]
	except e:L=sys.implementation.name
	A=n({V:L,C:B,D:B,S:B,M:sys.platform,T:'UNKNOWN',U:B,m:B,W:B,F:B,K:B})
	if A[M].startswith('pyb'):A[M]='stm32'
	elif A[M]==Y:A[M]='windows'
	elif A[M]=='linux':A[M]=a
	try:A[C]=A8(sys.implementation.version)
	except J:pass
	try:
		O=sys.implementation._machine if'_machine'in N(sys.implementation)else os.uname().machine;A[T]=O.strip();G=sys.implementation._build if'_build'in N(sys.implementation)else B
		if G:A[T]=G.split(E)[0];A[m]=G.split(E)[1]if E in G else B
		A[U]=G;A[W]=O.split('with')[-1].strip();A[F]=sys.implementation._mpy if'_mpy'in N(sys.implementation)else sys.implementation.mpy if F in N(sys.implementation)else B
	except(J,R):pass
	if not A[U]:A9(A)
	try:
		if'uname'in N(os):
			A[D]=Z(os.uname()[3])
			if not A[D]:A[D]=Z(os.uname()[2])
		elif C in N(sys):A[D]=Z(sys.version)
	except(J,R,e):pass
	if A[C]==B and sys.platform not in(a,Y):
		try:f=os.uname();A[C]=f.release
		except(R,J,e):pass
	for(g,h,i)in[(b,b,'const'),(c,c,'FAT'),(d,'pybricks.hubs','EV3Brick')]:
		try:j=__import__(h,H,H,i);A[V]=g;del j;break
		except(P,t):pass
	if A[V]==d:A['release']='2.0.0'
	if A[V]==w:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if F in A and A[F]:
		I=int(A[F])
		try:
			Q=[H,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][I>>10]
			if Q:A[K]=Q
		except R:A[K]='unknown'
		A[F]='v{}.{}'.format(I&255,I>>8&3)
	if A[D]and not A[C].endswith(X):A[C]=A[C]+X
	A[S]=f"{A[C]}-{A[D]}"if A[D]else f"{A[C]}";return A
def A8(version):
	A=version;B=L.join([d(A)for A in A[:3]])
	if S(A)>3 and A[3]:B+=E+A[3]
	return B
def A9(info):
	D=info
	try:from boardname import BOARD_ID as C;A.info('Found BOARD_ID: {}'.format(C))
	except P:A.warning('BOARD_ID not found');C=B
	D[U]=C;D[T]=C.split(E)[0]if E in C else C;D[m]==C.split(E)[1]if E in C else B
def get_root():
	try:A=os.getcwd()
	except(D,J):A=L
	B=A
	for B in['/remote','/sd','/flash',G,A,L]:
		try:C=os.stat(B);break
		except D:continue
	return B
def a(filename):
	try:
		if os.stat(filename)[0]>>14:return W
		return I
	except D:return I
def o():Q("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if S(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:o()
	elif S(sys.argv)==2:o()
	return path
def p():
	try:A=bytes('abc',encoding='utf8');B=p.__module__;return I
	except(q,J):return W
b='modulelist.done'
def AA(skip=0):
	for E in A7:
		B=E+'/modulelist.txt'
		if not a(B):continue
		try:
			with O(B,encoding='utf-8')as F:
				C=0
				while W:
					A=F.readline().strip()
					if not A:break
					if S(A)>0 and A[0]=='#':continue
					C+=1
					if C<skip:continue
					yield A
				break
		except D:pass
def AB(done):
	with O(b,i)as A:A.write(d(done)+'\n')
def AC():
	A=0
	try:
		with O(b)as B:A=int(B.readline().strip())
	except D:pass
	return A
def main():
	import machine as D;C=a(b)
	if C:A.info('Continue from last run')
	else:A.info('Starting new run')
	stubber=Stubber(path=read_path());B=0
	if not C:stubber.clean();stubber.report_start(k)
	else:B=AC();stubber._json_name=j.format(stubber.path,k)
	for E in AA(B):
		try:stubber.create_one_stub(E)
		except r:D.reset()
		F.collect();B+=1;AB(B)
	Q('All modules have been processed, Finalizing report');stubber.report_end()
if __name__=='__main__'or p():
	if not a('no_auto_stubber.txt'):
		Q(f"createstubs.py: {__version__}")
		try:F.threshold(4096);F.enable()
		except BaseException:pass
		main()