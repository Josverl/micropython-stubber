A3='No report file'
A2='Failed to create the report.'
A1='method'
A0='function'
z='micropython'
y='stubber'
x=Exception
w=KeyError
v=sorted
u=MemoryError
t=NotImplementedError
p='arch'
o='variant'
n=',\n'
m='modules.json'
l='{}/{}'
k='w'
j='dict'
i='list'
h='tuple'
g=TypeError
f=str
e=repr
Z='-preview'
Y=True
X='family'
W='board_id'
V='board'
U=len
T=IndexError
S=print
R=ImportError
Q='mpy'
P=dir
O='build'
N='port'
M='.'
L=open
J=AttributeError
I=False
H=None
G='/'
E='-'
D=OSError
C='version'
A=''
import gc as F,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except R:pass
try:from collections import OrderedDict as q
except R:from ucollections import OrderedDict as q
__version__='v1.26.3'
A4=2
A5=44
A6=2
A7=['lib','/lib','/sd/lib','/flash/lib',M]
class K:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=S
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
B=K.getLogger(y)
K.basicConfig(level=K.INFO)
class Stubber:
	def __init__(A,path=A,firmware_id=A):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise t('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		A.info=_info();B.info('Port: {}'.format(A.info[N]));B.info('Board: {}'.format(A.info[V]));B.info('Board_ID: {}'.format(A.info[W]));F.collect()
		if C:A._fwid=C.lower()
		elif A.info[X]==z:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(E)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=F.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:a(path+G)
		except D:B.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=H;A._json_first=I
	def load_exlusions(C):
		try:
			with L('modulelist_exclude.txt','r')as E:
				for F in E:
					A=F.strip()
					if A and A not in C.excluded:C.excluded.append(A);B.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except D:pass
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for B in P(H):
			if B.startswith('__')and not B in L.modules:continue
			try:
				D=getattr(H,B)
				try:E=e(type(D)).split("'")[1]
				except T:E=A
				if E in{'int','float','str','bool',h,i,j}:G=1
				elif E in{A0,A1}:G=2
				elif E in'class':G=3
				else:G=4
				C.append((B,e(D),e(type(D)),D,G))
			except J as I:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(B,H,I))
			except u as I:S('MemoryError: {}'.format(I));sleep(1);reset()
		C=v([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return C,K
	def add_modules(A,modules):A.modules=v(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();F.collect()
		for C in A.modules:A.create_one_stub(C)
		A.report_end();B.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:B.warning('Skip module: {:<25}        : Known problematic'.format(A));return I
		if A in C.excluded:B.warning('Skip module: {:<25}        : Excluded'.format(A));return I
		H='{}/{}.pyi'.format(C.path,A.replace(M,G));F.collect();E=I
		try:E=C.create_module_stub(A,H)
		except D:return I
		F.collect();return E
	def create_module_stub(J,module_name,file_name=H):
		E=file_name;C=module_name
		if E is H:K=C.replace(M,'_')+'.pyi';E=J.path+G+K
		else:K=E.split(G)[-1]
		if G in C:C=C.replace(G,M)
		N=H
		try:N=__import__(C,H,H,'*');P=F.mem_free();B.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,K,P))
		except R:return I
		a(E)
		with L(E,k)as O:Q=f(J.info).replace('OrderedDict(',A).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,J._fwid,Q,__version__);O.write(S);O.write('from __future__ import annotations\nfrom typing import Any, Final, Generator\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(O,N,C,A)
		J.report_add(C,E)
		if C not in{'os','sys','logging','gc'}:
			try:del N
			except(D,w):B.warning('could not del new_module')
		F.collect();return Y
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		Y=' at ...>';X='{0}{1}: {3} = {2}\n';W='bound_method';V='Incomplete';O=in_class;N='Exception';M=object_expr;K=' at ';J=fp;E=indent;F.collect()
		if M in L.problematic:B.warning('SKIPPING problematic module:{}'.format(M));return
		Z,P=L.get_obj_attributes(M)
		if P:B.error(P)
		for(C,H,I,a,c)in Z:
			if C in['classmethod','staticmethod','BaseException',N]:continue
			if C[0].isdigit():B.warning('NameError: invalid name {}'.format(C));continue
			if I=="<class 'type'>"and U(E)<=A6*4:
				Q=A;R=C.endswith(N)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=N
				D='\n{}class {}({}):\n'.format(E,C,Q)
				if R:D+=E+'    ...\n';J.write(D);continue
				J.write(D);L.write_object_stub(J,a,'{0}.{1}'.format(obj_name,C),E+'    ',O+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';J.write(D)
			elif any(A in I for A in[A1,A0,'closure']):
				S=V;T=A
				if O>0:T='self, '
				if W in I or W in H:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,C,S)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,C,T,S)
				D+=E+'    ...\n\n';J.write(D)
			elif I=="<class 'module'>":0
			elif I.startswith("<class '"):
				G=I[8:-2];D=A
				if G in('str','int','float','bool','bytearray','bytes'):
					if C.upper()==C:D='{0}{1}: Final[{3}] = {2}\n'.format(E,C,H,G)
					else:D=X.format(E,C,H,G)
				elif G in(j,i,h):b={j:'{}',i:'[]',h:'()'};D=X.format(E,C,b[G],G)
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
	def clean(C,path=A):
		if not path:path=C.path
		B.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except(D,J):return
		for F in E:
			A=l.format(path,F)
			try:os.remove(A)
			except D:
				try:C.clean(A);os.rmdir(A)
				except D:pass
	def report_start(A,filename=m):
		G='firmware';A._json_name=l.format(A.path,filename);A._json_first=Y;a(A._json_name);B.info('Report file: {}'.format(A._json_name));F.collect()
		try:
			with L(A._json_name,k)as E:E.write('{');E.write(dumps({G:A.info})[1:-1]);E.write(n);E.write(dumps({y:{C:__version__},'stubtype':G})[1:-1]);E.write(n);E.write('"modules" :[\n')
		except D as I:B.error(A2);A._json_name=H;raise I
	def report_add(A,module_name,stub_file):
		if not A._json_name:raise x(A3)
		try:
			with L(A._json_name,'a')as C:
				if not A._json_first:C.write(n)
				else:A._json_first=I
				E='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',G));C.write(E)
		except D:B.error(A2)
	def report_end(A):
		if not A._json_name:raise x(A3)
		with L(A._json_name,'a')as C:C.write('\n]}')
		B.info('Path: {}'.format(A.path))
def a(path):
	A=E=0
	while A!=-1:
		A=path.find(G,E)
		if A!=-1:
			C=path[0]if A==0 else path[:A]
			try:I=os.stat(C)
			except D as F:
				if F.args[0]in[A4,A5]:
					try:B.debug('Create folder {}'.format(C));os.mkdir(C)
					except D as H:B.error('failed to create folder {}'.format(C));raise H
		E=A+1
def b(s):
	C=' on '
	if not s:return A
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not E in s:return A
		B=s.split(E)[1];return B
	if not Z in s:return A
	B=s.split(Z)[1].split(M)[1];return B
def A8():
	try:B=sys.implementation[0]
	except g:B=sys.implementation.name
	D=q({X:B,C:A,O:A,'ver':A,N:sys.platform,V:'UNKNOWN',W:A,o:A,'cpu':A,Q:A,p:A});return D
def A9(info):
	A=info
	if A[N].startswith('pyb'):A[N]='stm32'
	elif A[N]=='win32':A[N]='windows'
	elif A[N]=='linux':A[N]='unix'
def AA(info):
	try:info[C]=AH(sys.implementation.version)
	except J:pass
def AB(info):
	B=info
	try:
		D=sys.implementation._machine if'_machine'in P(sys.implementation)else os.uname().machine;B[V]=D.strip();C=sys.implementation._build if'_build'in P(sys.implementation)else A
		if C:B[V]=C.split(E)[0];B[o]=C.split(E)[1]if E in C else A
		B[W]=C;B['cpu']=D.split('with')[-1].strip();B[Q]=sys.implementation._mpy if'_mpy'in P(sys.implementation)else sys.implementation.mpy if Q in P(sys.implementation)else A
	except(J,T):pass
	if not B[W]:AI(B)
def AC(info):
	B=info
	try:
		if'uname'in P(os):
			B[O]=b(os.uname()[3])
			if not B[O]:B[O]=b(os.uname()[2])
		elif C in P(sys):B[O]=b(sys.version)
	except(J,T,g):pass
	if B[C]==A and sys.platform not in('unix','win32'):
		try:D=os.uname();B[C]=D.release
		except(T,J,g):pass
def AD(info):
	D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:I=__import__(F,H,H,G);A[X]=E;del I;break
		except(R,w):pass
	if A[X]==D:A['release']='2.0.0'
def AE(info):
	A=info
	if A[X]==z:
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
def AF(info):
	A=info
	if Q in A and A[Q]:
		B=int(A[Q])
		try:
			C=[H,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[p]=C
		except T:A[p]='unknown'
		A[Q]='v{}.{}'.format(B&255,B>>8&3)
def AG(info):
	A=info
	if A[O]and not A[C].endswith(Z):A[C]=A[C]+Z
	A['ver']=f"{A[C]}-{A[O]}"if A[O]else f"{A[C]}"
def _info():A=A8();A9(A);AA(A);AB(A);AC(A);AD(A);AE(A);AF(A);AG(A);return A
def AH(version):
	A=version;B=M.join([f(A)for A in A[:3]])
	if U(A)>3 and A[3]:B+=E+A[3]
	return B
def AI(info):
	D=info
	try:from boardname import BOARD_ID as C;B.info('Found BOARD_ID: {}'.format(C))
	except R:B.warning('BOARD_ID not found');C=A
	D[W]=C;D[V]=C.split(E)[0]if E in C else C;D[o]==C.split(E)[1]if E in C else A
def get_root():
	try:A=os.getcwd()
	except(D,J):A=M
	B=A
	for B in['/remote','/sd','/flash',G,A,M]:
		try:C=os.stat(B);break
		except D:continue
	return B
def c(filename):
	try:
		if os.stat(filename)[0]>>14:return Y
		return I
	except D:return I
def r():S("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=A
	if U(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):path=sys.argv[2]
		else:r()
	elif U(sys.argv)==2:r()
	return path
def s():
	try:A=bytes('abc',encoding='utf8');B=s.__module__;return I
	except(t,J):return Y
d='modulelist.done'
def AJ(skip=0):
	for E in A7:
		B=E+'/modulelist.txt'
		if not c(B):continue
		try:
			with L(B,encoding='utf-8')as F:
				C=0
				while Y:
					A=F.readline().strip()
					if not A:break
					if U(A)>0 and A[0]=='#':continue
					C+=1
					if C<skip:continue
					yield A
				break
		except D:pass
def AK(done):
	with L(d,k)as A:A.write(f(done)+'\n')
def AL():
	A=0
	try:
		with L(d)as B:A=int(B.readline().strip())
	except D:pass
	return A
def main():
	import machine as D;C=c(d)
	if C:B.info('Continue from last run')
	else:B.info('Starting new run')
	stubber=Stubber(path=read_path());A=0
	if not C:stubber.clean();stubber.report_start(m)
	else:A=AL();stubber._json_name=l.format(stubber.path,m)
	for E in AJ(A):
		try:stubber.create_one_stub(E)
		except u:D.reset()
		F.collect();A+=1;AK(A)
	S('All modules have been processed, Finalizing report');stubber.report_end()
if __name__=='__main__'or s():
	if not c('no_auto_stubber.txt'):
		S(f"createstubs.py: {__version__}")
		try:F.threshold(4096);F.enable()
		except BaseException:pass
		main()