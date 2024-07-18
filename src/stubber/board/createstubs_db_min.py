A3='No report file'
A2='Failed to create the report.'
A1='method'
A0='function'
z='bool'
y='str'
x='float'
w='int'
v='micropython'
u='stubber'
t=Exception
s=KeyError
r=sorted
q=MemoryError
p=NotImplementedError
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
W='-'
V='board'
U=IndexError
T=print
R=True
Q='family'
P=len
O=ImportError
N=dir
M=open
K='port'
J='.'
I=AttributeError
H=False
G='/'
E=None
D=OSError
C='version'
B=''
import gc as F,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except O:pass
try:from collections import OrderedDict as m
except O:from ucollections import OrderedDict as m
__version__='v1.23.2'
S=__version__.rsplit(J,1)[0]
A4=2
A5=2
A6=['lib','/lib','/sd/lib','/flash/lib',J]
class L:
	INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=T
	@staticmethod
	def getLogger(name):return L()
	@classmethod
	def basicConfig(A,level):A.level=level
	def info(A,msg):
		if A.level<=L.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=L.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=L.ERROR:A.prnt('ERROR :',msg)
A=L.getLogger(u)
L.basicConfig(level=L.INFO)
class Stubber:
	def __init__(B,path=E,firmware_id=E):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise p('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		B.info=_info();A.info('Port: {}'.format(B.info[K]));A.info('Board: {}'.format(B.info[V]));F.collect()
		if C:B._fwid=C.lower()
		elif B.info[Q]==v:B._fwid='{family}-v{version}-{port}-{board}'.format(**B.info).rstrip(W)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=F.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',G)
		try:Y(path+G)
		except D:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[];B._json_name=E;B._json_first=H
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for A in N(H):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=getattr(H,A)
				try:E=c(type(D)).split("'")[1]
				except U:E=B
				if E in{w,x,y,z,f,g,h}:G=1
				elif E in{A0,A1}:G=2
				elif E in'class':G=3
				else:G=4
				C.append((A,c(D),c(type(D)),D,G))
			except I as J:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,J))
			except q as J:T('MemoryError: {}'.format(J));sleep(1);reset()
		C=r([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return C,K
	def add_modules(A,modules):A.modules=r(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber {} on {}'.format(__version__,B._fwid));B.report_start();F.collect()
		for C in B.modules:B.create_one_stub(C)
		B.report_end();A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return H
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return H
		I='{}/{}.pyi'.format(C.path,B.replace(J,G));F.collect();E=H
		try:E=C.create_module_stub(B,I)
		except D:return H
		F.collect();return E
	def create_module_stub(K,module_name,file_name=E):
		I=file_name;C=module_name
		if I is E:L=C.replace(J,'_')+'.pyi';I=K.path+G+L
		else:L=I.split(G)[-1]
		if G in C:C=C.replace(G,J)
		N=E
		try:N=__import__(C,E,E,'*');Q=F.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,L,Q))
		except O:return H
		Y(I)
		with M(I,i)as P:T=d(K.info).replace('OrderedDict(',B).replace('})','}');U='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,K._fwid,T,S);P.write(U);P.write('from __future__ import annotations\nfrom typing import Any, Generator\nfrom _typeshed import Incomplete\n\n');K.write_object_stub(P,N,C,B)
		K.report_add(C,I)
		if C not in{'os','sys','logging','gc'}:
			try:del N
			except(D,s):A.warning('could not del new_module')
		F.collect();return R
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		Z=' at ...>';Y='generator';X='{0}{1}: {3} = {2}\n';W='bound_method';V='Incomplete';O=in_class;N='Exception';M=object_expr;K=' at ';J=fp;D=indent;F.collect()
		if M in L.problematic:A.warning('SKIPPING problematic module:{}'.format(M));return
		a,Q=L.get_obj_attributes(M)
		if Q:A.error(Q)
		for(E,H,I,b,d)in a:
			if E in['classmethod','staticmethod','BaseException',N]:continue
			if E[0].isdigit():A.warning('NameError: invalid name {}'.format(E));continue
			if I=="<class 'type'>"and P(D)<=A5*4:
				R=B;S=E.endswith(N)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if S:R=N
				C='\n{}class {}({}):\n'.format(D,E,R)
				if S:C+=D+'    ...\n';J.write(C);continue
				J.write(C);L.write_object_stub(J,b,'{0}.{1}'.format(obj_name,E),D+'    ',O+1);C=D+'    def __init__(self, *argv, **kwargs) -> None:\n';C+=D+'        ...\n\n';J.write(C)
			elif any(A in I for A in[A1,A0,'closure']):
				T=V;U=B
				if O>0:U='self, '
				if W in I or W in H:C='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,T)
				else:C='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,U,T)
				C+=D+'    ...\n\n';J.write(C)
			elif I=="<class 'module'>":0
			elif I.startswith("<class '"):
				G=I[8:-2];C=B
				if G in(y,w,x,z,'bytearray','bytes'):C=X.format(D,E,H,G)
				elif G in(h,g,f):c={h:'{}',g:'[]',f:'()'};C=X.format(D,E,c[G],G)
				elif G in('object','set','frozenset','Pin',Y):
					if G==Y:G='Generator'
					C='{0}{1}: {2} ## = {4}\n'.format(D,E,G,I,H)
				else:
					G=V
					if K in H:H=H.split(K)[0]+Z
					if K in H:H=H.split(K)[0]+Z
					C='{0}{1}: {2} ## {3} = {4}\n'.format(D,E,G,I,H)
				J.write(C)
			else:J.write("# all other, type = '{0}'\n".format(I));J.write(D+E+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(C,path=E):
		if path is E:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);F=os.listdir(path)
		except(D,I):return
		for G in F:
			B=j.format(path,G)
			try:os.remove(B)
			except D:
				try:C.clean(B);os.rmdir(B)
				except D:pass
	def report_start(B,filename=k):
		H='firmware';B._json_name=j.format(B.path,filename);B._json_first=R;Y(B._json_name);A.info('Report file: {}'.format(B._json_name));F.collect()
		try:
			with M(B._json_name,i)as G:G.write('{');G.write(dumps({H:B.info})[1:-1]);G.write(l);G.write(dumps({u:{C:S},'stubtype':H})[1:-1]);G.write(l);G.write('"modules" :[\n')
		except D as I:A.error(A2);B._json_name=E;raise I
	def report_add(B,module_name,stub_file):
		if not B._json_name:raise t(A3)
		try:
			with M(B._json_name,'a')as C:
				if not B._json_first:C.write(l)
				else:B._json_first=H
				E='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',G));C.write(E)
		except D:A.error(A2)
	def report_end(B):
		if not B._json_name:raise t(A3)
		with M(B._json_name,'a')as C:C.write('\n]}')
		A.info('Path: {}'.format(B.path))
def Y(path):
	B=E=0
	while B!=-1:
		B=path.find(G,E)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except D as F:
				if F.args[0]==A4:
					try:os.mkdir(C)
					except D as H:A.error('failed to create folder {}'.format(C));raise H
		E=B+1
def Z(s):
	C=' on '
	if not s:return B
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not W in s:return B
		A=s.split(W)[1];return A
	if not X in s:return B
	A=s.split(X)[1].split(J)[1];return A
def _info():
	b='ev3-pybricks';a='pycom';Y='pycopy';W='unix';T='win32';R='arch';P='cpu';M='ver';F='mpy';D='build'
	try:H=sys.implementation[0]
	except e:H=sys.implementation.name
	A=m({Q:H,C:B,D:B,M:B,K:sys.platform,V:'UNKNOWN',P:B,F:B,R:B})
	if A[K].startswith('pyb'):A[K]='stm32'
	elif A[K]==T:A[K]='windows'
	elif A[K]=='linux':A[K]=W
	try:A[C]=S(sys.implementation.version)
	except I:pass
	try:J=sys.implementation._machine if'_machine'in N(sys.implementation)else os.uname().machine;A[V]=J;A[P]=J.split('with')[-1].strip();A[F]=sys.implementation._mpy if'_mpy'in N(sys.implementation)else sys.implementation.mpy if F in N(sys.implementation)else B
	except(I,U):pass
	A[V]=A7()
	try:
		if'uname'in N(os):
			A[D]=Z(os.uname()[3])
			if not A[D]:A[D]=Z(os.uname()[2])
		elif C in N(sys):A[D]=Z(sys.version)
	except(I,U,e):pass
	if A[C]==B and sys.platform not in(W,T):
		try:c=os.uname();A[C]=c.release
		except(U,I,e):pass
	for(d,f,g)in[(Y,Y,'const'),(a,a,'FAT'),(b,'pybricks.hubs','EV3Brick')]:
		try:h=__import__(f,E,E,g);A[Q]=d;del h;break
		except(O,s):pass
	if A[Q]==b:A['release']='2.0.0'
	if A[Q]==v:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if F in A and A[F]:
		G=int(A[F]);L=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][G>>10]
		if L:A[R]=L
		A[F]='v{}.{}'.format(G&255,G>>8&3)
	if A[D]and not A[C].endswith(X):A[C]=A[C]+X
	A[M]=f"{A[C]}-{A[D]}"if A[D]else f"{A[C]}";return A
def S(version):
	A=version;B=J.join([d(A)for A in A[:3]])
	if P(A)>3 and A[3]:B+=W+A[3]
	return B
def A7():
	try:from boardname import BOARDNAME as C;A.info('Found BOARDNAME: {}'.format(C))
	except O:A.warning('BOARDNAME not found');C=B
	return C
def get_root():
	try:A=os.getcwd()
	except(D,I):A=J
	B=A
	for B in[A,'/sd','/flash',G,J]:
		try:C=os.stat(B);break
		except D:continue
	return B
def a(filename):
	try:
		if os.stat(filename)[0]>>14:return R
		return H
	except D:return H
def n():T("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if P(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:n()
	elif P(sys.argv)==2:n()
	return path
def o():
	try:A=bytes('abc',encoding='utf8');B=o.__module__;return H
	except(p,I):return R
b='modulelist.done'
def A8(skip=0):
	for E in A6:
		B=E+'/modulelist.txt'
		if not a(B):continue
		try:
			with M(B)as F:
				C=0
				while R:
					A=F.readline().strip()
					if not A:break
					if P(A)>0 and A[0]=='#':continue
					C+=1
					if C<skip:continue
					yield A
				break
		except D:pass
def A9(done):
	with M(b,i)as A:A.write(d(done)+'\n')
def AA():
	A=0
	try:
		with M(b)as B:A=int(B.readline().strip())
	except D:pass
	return A
def main():
	import machine as D;C=a(b)
	if C:A.info('Continue from last run')
	else:A.info('Starting new run')
	stubber=Stubber(path=read_path());B=0
	if not C:stubber.clean();stubber.report_start(k)
	else:B=AA();stubber._json_name=j.format(stubber.path,k)
	for E in A8(B):
		try:stubber.create_one_stub(E)
		except q:D.reset()
		F.collect();B+=1;A9(B)
	T('All modules have been processed, Finalizing report');stubber.report_end()
if __name__=='__main__'or o():
	if not a('no_auto_stubber.txt'):
		try:F.threshold(4*1024);F.enable()
		except BaseException:pass
		main()