A2='No report file'
A1='Failed to create the report.'
A0='method'
z='function'
y='bool'
x='str'
w='float'
v='int'
u='micropython'
t='stubber'
s=Exception
r=KeyError
q=sorted
p=MemoryError
o=NotImplementedError
k=',\n'
j='modules.json'
i='{}/{}'
h='w'
g='dict'
f='list'
e='tuple'
d=TypeError
c=str
b=repr
W='-preview'
V='-'
U='board'
T=True
S='family'
R=len
Q=IndexError
P=print
O=ImportError
N=dir
M=open
L='port'
K='.'
I=AttributeError
H=False
G=None
E='/'
D=OSError
C='version'
B=''
import gc as F,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except O:pass
try:from collections import OrderedDict as l
except O:from ucollections import OrderedDict as l
__version__='v1.24.0'
A3=2
A4=44
A5=2
A6=['lib','/lib','/sd/lib','/flash/lib',K]
class J:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=P
	@staticmethod
	def getLogger(name):return J()
	@classmethod
	def basicConfig(A,level):A.level=level
	def debug(A,msg):
		if A.level<=J.DEBUG:A.prnt('DEBUG :',msg)
	def info(A,msg):
		if A.level<=J.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=J.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=J.ERROR:A.prnt('ERROR :',msg)
A=J.getLogger(t)
J.basicConfig(level=J.INFO)
class Stubber:
	def __init__(B,path=B,firmware_id=B):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise o('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		B.info=_info();A.info('Port: {}'.format(B.info[L]));A.info('Board: {}'.format(B.info[U]));F.collect()
		if C:B._fwid=C.lower()
		elif B.info[S]==u:B._fwid='{family}-v{version}-{port}-{board}'.format(**B.info).rstrip(V)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=F.mem_free()
		if path:
			if path.endswith(E):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',E)
		try:X(path+E)
		except D:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[];B._json_name=G;B._json_first=H
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for A in N(H):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=getattr(H,A)
				try:E=b(type(D)).split("'")[1]
				except Q:E=B
				if E in{v,w,x,y,e,f,g}:G=1
				elif E in{z,A0}:G=2
				elif E in'class':G=3
				else:G=4
				C.append((A,b(D),b(type(D)),D,G))
			except I as J:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,J))
			except p as J:P('MemoryError: {}'.format(J));sleep(1);reset()
		C=q([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return C,K
	def add_modules(A,modules):A.modules=q(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber {} on {}'.format(__version__,B._fwid));B.report_start();F.collect()
		for C in B.modules:B.create_one_stub(C)
		B.report_end();A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return H
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return H
		I='{}/{}.pyi'.format(C.path,B.replace(K,E));F.collect();G=H
		try:G=C.create_module_stub(B,I)
		except D:return H
		F.collect();return G
	def create_module_stub(J,module_name,file_name=G):
		I=file_name;C=module_name
		if I is G:L=C.replace(K,'_')+'.pyi';I=J.path+E+L
		else:L=I.split(E)[-1]
		if E in C:C=C.replace(E,K)
		N=G
		try:N=__import__(C,G,G,'*');Q=F.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,L,Q))
		except O:return H
		X(I)
		with M(I,h)as P:R=c(J.info).replace('OrderedDict(',B).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,J._fwid,R,__version__);P.write(S);P.write('from __future__ import annotations\nfrom typing import Any, Final, Generator\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(P,N,C,B)
		J.report_add(C,I)
		if C not in{'os','sys','logging','gc'}:
			try:del N
			except(D,r):A.warning('could not del new_module')
		F.collect();return T
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		Y=' at ...>';X='{0}{1}: {3} = {2}\n';W='bound_method';V='Incomplete';O=in_class;N='Exception';M=object_expr;K=' at ';J=fp;E=indent;F.collect()
		if M in L.problematic:A.warning('SKIPPING problematic module:{}'.format(M));return
		Z,P=L.get_obj_attributes(M)
		if P:A.error(P)
		for(C,H,I,a,c)in Z:
			if C in['classmethod','staticmethod','BaseException',N]:continue
			if C[0].isdigit():A.warning('NameError: invalid name {}'.format(C));continue
			if I=="<class 'type'>"and R(E)<=A5*4:
				Q=B;S=C.endswith(N)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if S:Q=N
				D='\n{}class {}({}):\n'.format(E,C,Q)
				if S:D+=E+'    ...\n';J.write(D);continue
				J.write(D);L.write_object_stub(J,a,'{0}.{1}'.format(obj_name,C),E+'    ',O+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';J.write(D)
			elif any(A in I for A in[A0,z,'closure']):
				T=V;U=B
				if O>0:U='self, '
				if W in I or W in H:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,C,T)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,C,U,T)
				D+=E+'    ...\n\n';J.write(D)
			elif I=="<class 'module'>":0
			elif I.startswith("<class '"):
				G=I[8:-2];D=B
				if G in(x,v,w,y,'bytearray','bytes'):
					if C.upper()==C:D='{0}{1}: Final[{3}] = {2}\n'.format(E,C,H,G)
					else:D=X.format(E,C,H,G)
				elif G in(g,f,e):b={g:'{}',f:'[]',e:'()'};D=X.format(E,C,b[G],G)
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
		except(D,I):return
		for F in E:
			B=i.format(path,F)
			try:os.remove(B)
			except D:
				try:C.clean(B);os.rmdir(B)
				except D:pass
	def report_start(B,filename=j):
		H='firmware';B._json_name=i.format(B.path,filename);B._json_first=T;X(B._json_name);A.info('Report file: {}'.format(B._json_name));F.collect()
		try:
			with M(B._json_name,h)as E:E.write('{');E.write(dumps({H:B.info})[1:-1]);E.write(k);E.write(dumps({t:{C:__version__},'stubtype':H})[1:-1]);E.write(k);E.write('"modules" :[\n')
		except D as I:A.error(A1);B._json_name=G;raise I
	def report_add(B,module_name,stub_file):
		if not B._json_name:raise s(A2)
		try:
			with M(B._json_name,'a')as C:
				if not B._json_first:C.write(k)
				else:B._json_first=H
				F='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',E));C.write(F)
		except D:A.error(A1)
	def report_end(B):
		if not B._json_name:raise s(A2)
		with M(B._json_name,'a')as C:C.write('\n]}')
		A.info('Path: {}'.format(B.path))
def X(path):
	B=F=0
	while B!=-1:
		B=path.find(E,F)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except D as G:
				if G.args[0]in[A3,A4]:
					try:A.debug('Create folder {}'.format(C));os.mkdir(C)
					except D as H:A.error('failed to create folder {}'.format(C));raise H
		F=B+1
def Y(s):
	C=' on '
	if not s:return B
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not V in s:return B
		A=s.split(V)[1];return A
	if not W in s:return B
	A=s.split(W)[1].split(K)[1];return A
def _info():
	a='ev3-pybricks';Z='pycom';X='pycopy';V='unix';T='win32';R='arch';P='cpu';M='ver';E='mpy';D='build'
	try:J=sys.implementation[0]
	except d:J=sys.implementation.name
	A=l({S:J,C:B,D:B,M:B,L:sys.platform,U:'UNKNOWN',P:B,E:B,R:B})
	if A[L].startswith('pyb'):A[L]='stm32'
	elif A[L]==T:A[L]='windows'
	elif A[L]=='linux':A[L]=V
	try:A[C]=A7(sys.implementation.version)
	except I:pass
	try:K=sys.implementation._machine if'_machine'in N(sys.implementation)else os.uname().machine;A[U]=K;A[P]=K.split('with')[-1].strip();A[E]=sys.implementation._mpy if'_mpy'in N(sys.implementation)else sys.implementation.mpy if E in N(sys.implementation)else B
	except(I,Q):pass
	A[U]=A8()
	try:
		if'uname'in N(os):
			A[D]=Y(os.uname()[3])
			if not A[D]:A[D]=Y(os.uname()[2])
		elif C in N(sys):A[D]=Y(sys.version)
	except(I,Q,d):pass
	if A[C]==B and sys.platform not in(V,T):
		try:b=os.uname();A[C]=b.release
		except(Q,I,d):pass
	for(c,e,f)in[(X,X,'const'),(Z,Z,'FAT'),(a,'pybricks.hubs','EV3Brick')]:
		try:g=__import__(e,G,G,f);A[S]=c;del g;break
		except(O,r):pass
	if A[S]==a:A['release']='2.0.0'
	if A[S]==u:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if E in A and A[E]:
		F=int(A[E])
		try:H=[G,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][F>>10]
		except Q:H='unknown'
		if H:A[R]=H
		A[E]='v{}.{}'.format(F&255,F>>8&3)
	if A[D]and not A[C].endswith(W):A[C]=A[C]+W
	A[M]=f"{A[C]}-{A[D]}"if A[D]else f"{A[C]}";return A
def A7(version):
	A=version;B=K.join([c(A)for A in A[:3]])
	if R(A)>3 and A[3]:B+=V+A[3]
	return B
def A8():
	try:from boardname import BOARDNAME as C;A.info('Found BOARDNAME: {}'.format(C))
	except O:A.warning('BOARDNAME not found');C=B
	return C
def get_root():
	try:A=os.getcwd()
	except(D,I):A=K
	B=A
	for B in['/remote','/sd','/flash',E,A,K]:
		try:C=os.stat(B);break
		except D:continue
	return B
def Z(filename):
	try:
		if os.stat(filename)[0]>>14:return T
		return H
	except D:return H
def m():P("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if R(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:m()
	elif R(sys.argv)==2:m()
	return path
def n():
	try:A=bytes('abc',encoding='utf8');B=n.__module__;return H
	except(o,I):return T
a='modulelist.done'
def A9(skip=0):
	for E in A6:
		B=E+'/modulelist.txt'
		if not Z(B):continue
		try:
			with M(B)as F:
				C=0
				while T:
					A=F.readline().strip()
					if not A:break
					if R(A)>0 and A[0]=='#':continue
					C+=1
					if C<skip:continue
					yield A
				break
		except D:pass
def AA(done):
	with M(a,h)as A:A.write(c(done)+'\n')
def AB():
	A=0
	try:
		with M(a)as B:A=int(B.readline().strip())
	except D:pass
	return A
def main():
	import machine as D;C=Z(a)
	if C:A.info('Continue from last run')
	else:A.info('Starting new run')
	stubber=Stubber(path=read_path());B=0
	if not C:stubber.clean();stubber.report_start(j)
	else:B=AB();stubber._json_name=i.format(stubber.path,j)
	for E in A9(B):
		try:stubber.create_one_stub(E)
		except p:D.reset()
		F.collect();B+=1;AA(B)
	P('All modules have been processed, Finalizing report');stubber.report_end()
if __name__=='__main__'or n():
	if not Z('no_auto_stubber.txt'):
		P(f"createstubs.py: {__version__}")
		try:F.threshold(4096);F.enable()
		except BaseException:pass
		main()