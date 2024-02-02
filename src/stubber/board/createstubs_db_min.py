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
s=TypeError
r=Exception
q=KeyError
p=sorted
o=MemoryError
n=NotImplementedError
j=',\n'
i='modules.json'
h='{}/{}'
g='w'
f='dict'
e='list'
d='tuple'
c=str
b=repr
W='-preview'
V='-'
U='board'
T=IndexError
S=print
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
try:from collections import OrderedDict as k
except O:from ucollections import OrderedDict as k
__version__='v1.16.3'
A3=2
A4=2
A5=['lib','/lib','/sd/lib','/flash/lib',J]
class L:
	INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=S
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
A=L.getLogger(t)
L.basicConfig(level=L.INFO)
class Stubber:
	def __init__(B,path=E,firmware_id=E):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise n('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		B.info=_info();A.info('Port: {}'.format(B.info[K]));A.info('Board: {}'.format(B.info[U]));F.collect()
		if C:B._fwid=C.lower()
		elif B.info[Q]==u:B._fwid='{family}-v{version}-{port}-{board}'.format(**B.info).rstrip(V)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=F.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',G)
		try:X(path+G)
		except D:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[];B._json_name=E;B._json_first=H
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for A in N(H):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=getattr(H,A)
				try:E=b(type(D)).split("'")[1]
				except T:E=B
				if E in{v,w,x,y,d,e,f}:G=1
				elif E in{z,A0}:G=2
				elif E in'class':G=3
				else:G=4
				C.append((A,b(D),b(type(D)),D,G))
			except I as J:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,J))
			except o as J:S('MemoryError: {}'.format(J));sleep(1);reset()
		C=p([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);F.collect();return C,K
	def add_modules(A,modules):A.modules=p(set(A.modules)|set(modules))
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
		X(I)
		with M(I,g)as P:S=c(K.info).replace('OrderedDict(',B).replace('})','}');T='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,K._fwid,S,__version__);P.write(T);P.write('from __future__ import annotations\nfrom typing import Any, Generator\nfrom _typeshed import Incomplete\n\n');K.write_object_stub(P,N,C,B)
		K.report_add(C,I)
		if C not in{'os','sys','logging','gc'}:
			try:del N
			except(D,q):A.warning('could not del new_module')
		F.collect();return R
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		X='generator';W='{0}{1}: {3} = {2}\n';V='bound_method';U='Incomplete';N=in_class;M='Exception';L=object_expr;I=fp;D=indent;F.collect()
		if L in K.problematic:A.warning('SKIPPING problematic module:{}'.format(L));return
		Y,O=K.get_obj_attributes(L)
		if O:A.error(O)
		for(E,J,H,Z,b)in Y:
			if E in['classmethod','staticmethod','BaseException',M]:continue
			if E[0].isdigit():A.warning('NameError: invalid name {}'.format(E));continue
			if H=="<class 'type'>"and P(D)<=A4*4:
				Q=B;R=E.endswith(M)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=M
				C='\n{}class {}({}):\n'.format(D,E,Q)
				if R:C+=D+'    ...\n';I.write(C);continue
				I.write(C);K.write_object_stub(I,Z,'{0}.{1}'.format(obj_name,E),D+'    ',N+1);C=D+'    def __init__(self, *argv, **kwargs) -> None:\n';C+=D+'        ...\n\n';I.write(C)
			elif any(A in H for A in[A0,z,'closure']):
				S=U;T=B
				if N>0:T='self, '
				if V in H or V in J:C='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,S)
				else:C='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,T,S)
				C+=D+'    ...\n\n';I.write(C)
			elif H=="<class 'module'>":0
			elif H.startswith("<class '"):
				G=H[8:-2];C=B
				if G in(x,v,w,y,'bytearray','bytes'):C=W.format(D,E,J,G)
				elif G in(f,e,d):a={f:'{}',e:'[]',d:'()'};C=W.format(D,E,a[G],G)
				elif G in('object','set','frozenset','Pin',X):
					if G==X:G='Generator'
					C='{0}{1}: {2} ## = {4}\n'.format(D,E,G,H,J)
				else:G=U;C='{0}{1}: {2} ## {3} = {4}\n'.format(D,E,G,H,J)
				I.write(C)
			else:I.write("# all other, type = '{0}'\n".format(H));I.write(D+E+' # type: Incomplete\n')
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
			B=h.format(path,G)
			try:os.remove(B)
			except D:
				try:C.clean(B);os.rmdir(B)
				except D:pass
	def report_start(B,filename=i):
		H='firmware';B._json_name=h.format(B.path,filename);B._json_first=R;X(B._json_name);A.info('Report file: {}'.format(B._json_name));F.collect()
		try:
			with M(B._json_name,g)as G:G.write('{');G.write(dumps({H:B.info})[1:-1]);G.write(j);G.write(dumps({t:{C:__version__},'stubtype':H})[1:-1]);G.write(j);G.write('"modules" :[\n')
		except D as I:A.error(A1);B._json_name=E;raise I
	def report_add(B,module_name,stub_file):
		if not B._json_name:raise r(A2)
		try:
			with M(B._json_name,'a')as C:
				if not B._json_first:C.write(j)
				else:B._json_first=H
				E='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',G));C.write(E)
		except D:A.error(A1)
	def report_end(B):
		if not B._json_name:raise r(A2)
		with M(B._json_name,'a')as C:C.write('\n]}')
		A.info('Path: {}'.format(B.path))
def X(path):
	B=E=0
	while B!=-1:
		B=path.find(G,E)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except D as F:
				if F.args[0]==A3:
					try:os.mkdir(C)
					except D as H:A.error('failed to create folder {}'.format(C));raise H
		E=B+1
def Y(s):
	C=' on '
	if not s:return B
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not V in s:return B
		A=s.split(V)[1];return A
	if not W in s:return B
	A=s.split(W)[1].split(J)[1];return A
def _info():
	Z='ev3-pybricks';X='pycom';V='pycopy';S='unix';R='win32';P='arch';M='cpu';L='ver';F='mpy';D='build';A=k({Q:sys.implementation.name,C:B,D:B,L:B,K:sys.platform,U:'UNKNOWN',M:B,F:B,P:B})
	if A[K].startswith('pyb'):A[K]='stm32'
	elif A[K]==R:A[K]='windows'
	elif A[K]=='linux':A[K]=S
	try:A[C]=A6(sys.implementation.version)
	except I:pass
	try:H=sys.implementation._machine if'_machine'in N(sys.implementation)else os.uname().machine;A[U]=H;A[M]=H.split('with')[-1].strip();A[F]=sys.implementation._mpy if'_mpy'in N(sys.implementation)else sys.implementation.mpy if F in N(sys.implementation)else B
	except(I,T):pass
	A[U]=A7()
	try:
		if'uname'in N(os):
			A[D]=Y(os.uname()[3])
			if not A[D]:A[D]=Y(os.uname()[2])
		elif C in N(sys):A[D]=Y(sys.version)
	except(I,T,s):pass
	if A[C]==B and sys.platform not in(S,R):
		try:a=os.uname();A[C]=a.release
		except(T,I,s):pass
	for(b,c,d)in[(V,V,'const'),(X,X,'FAT'),(Z,'pybricks.hubs','EV3Brick')]:
		try:e=__import__(c,E,E,d);A[Q]=b;del e;break
		except(O,q):pass
	if A[Q]==Z:A['release']='2.0.0'
	if A[Q]==u:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if F in A and A[F]:
		G=int(A[F]);J=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][G>>10]
		if J:A[P]=J
		A[F]='v{}.{}'.format(G&255,G>>8&3)
	if A[D]and not A[C].endswith(W):A[C]=A[C]+W
	A[L]=f"{A[C]}-{A[D]}"if A[D]else f"{A[C]}";return A
def A6(version):
	A=version;B=J.join([c(A)for A in A[:3]])
	if P(A)>3 and A[3]:B+=V+A[3]
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
def Z(filename):
	try:
		if os.stat(filename)[0]>>14:return R
		return H
	except D:return H
def l():S("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if P(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:l()
	elif P(sys.argv)==2:l()
	return path
def m():
	try:A=bytes('abc',encoding='utf8');B=m.__module__;return H
	except(n,I):return R
a='modulelist.done'
def A8(skip=0):
	for E in A5:
		B=E+'/modulelist.txt'
		if not Z(B):continue
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
	with M(a,g)as A:A.write(c(done)+'\n')
def AA():
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
	if not C:stubber.clean();stubber.report_start(i)
	else:B=AA();stubber._json_name=h.format(stubber.path,i)
	for E in A8(B):
		try:stubber.create_one_stub(E)
		except o:D.reset()
		F.collect();B+=1;A9(B)
	S('All modules have been processed, Finalizing report');stubber.report_end()
if __name__=='__main__'or m():
	if not Z('no_auto_stubber.txt'):
		try:F.threshold(4*1024);F.enable()
		except BaseException:pass
		main()