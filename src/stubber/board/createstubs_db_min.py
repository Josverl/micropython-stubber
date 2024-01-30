y='{}/{}'
x='method'
w='function'
v='bool'
u='str'
t='float'
s='int'
r='stubber'
q=TypeError
p=KeyError
o=sorted
n=MemoryError
m=NotImplementedError
g=',\n'
e='dict'
d='list'
c='tuple'
b='_'
a='micropython'
Z=repr
X='modulelist.done'
W='-preview'
V='-'
U='board'
T=IndexError
S='family'
R=ImportError
Q=len
P=dir
O=True
N=open
L='port'
K='.'
J=print
I=AttributeError
H=False
G='/'
F=None
E=OSError
D='version'
C=''
import gc as A,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except R:pass
try:from collections import OrderedDict as f
except R:from ucollections import OrderedDict as f
__version__='v1.16.3'
z=2
A0=2
A1=['lib','/lib','/sd/lib','/flash/lib',K]
class M:
	INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=J
	@staticmethod
	def getLogger(name):return M()
	@classmethod
	def basicConfig(A,level):A.level=level
	def info(A,msg):
		if A.level<=M.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=M.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=M.ERROR:A.prnt('ERROR :',msg)
B=M.getLogger(r)
M.basicConfig(level=M.INFO)
class Stubber:
	def __init__(C,path=F,firmware_id=F):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise m('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		C._report=[];C.info=_info();B.info('Port: {}'.format(C.info[L]));B.info('Board: {}'.format(C.info[U]));A.collect()
		if D:C._fwid=D.lower()
		elif C.info[S]==a:C._fwid='{family}-v{version}-{port}-{board}'.format(**C.info).rstrip(V)
		else:C._fwid='{family}-v{version}-{port}'.format(**C.info)
		C._start_free=A.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',G)
		try:h(path+G)
		except E:B.error('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(M,item_instance):
		H=item_instance;D=[];L=[]
		for B in P(H):
			if B.startswith(b)and not B in M.modules:continue
			try:
				E=getattr(H,B)
				try:F=Z(type(E)).split("'")[1]
				except T:F=C
				if F in{s,t,u,v,c,d,e}:G=1
				elif F in{w,x}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((B,Z(E),Z(type(E)),E,G))
			except I as K:L.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(B,H,K))
			except n as K:J('MemoryError: {}'.format(K));sleep(1);reset()
		D=o([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);A.collect();return D,L
	def add_modules(A,modules):A.modules=o(set(A.modules)|set(modules))
	def create_all_stubs(C):
		B.info('Start micropython-stubber v{} on {}'.format(__version__,C._fwid));A.collect()
		for D in C.modules:C.create_one_stub(D)
		B.info('Finally done')
	def create_one_stub(D,module_name):
		C=module_name
		if C in D.problematic:B.warning('Skip module: {:<25}        : Known problematic'.format(C));return H
		if C in D.excluded:B.warning('Skip module: {:<25}        : Excluded'.format(C));return H
		I='{}/{}.py'.format(D.path,C.replace(K,G));A.collect();F=H
		try:F=D.create_module_stub(C,I)
		except E:return H
		A.collect();return F
	def create_module_stub(J,module_name,file_name=F):
		I=file_name;D=module_name
		if I is F:L=D.replace(K,b)+'.py';I=J.path+G+L
		else:L=I.split(G)[-1]
		if G in D:D=D.replace(G,K)
		M=F
		try:M=__import__(D,F,F,'*');Q=A.mem_free();B.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(D,L,Q))
		except R:return H
		h(I)
		with N(I,'w')as P:S=str(J.info).replace('OrderedDict(',C).replace('})','}');T='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,J._fwid,S,__version__);P.write(T);P.write('from __future__ import annotations\nfrom typing import Any\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(P,M,D,C)
		J._report.append('{{"module": "{}", "file": "{}"}}'.format(D,I.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del M
			except(E,p):B.warning('could not del new_module')
		A.collect();return O
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		W='{0}{1} = {2} # type: {3}\n';V='bound_method';U='Incomplete';N=in_class;M='Exception';L=object_expr;I=fp;E=indent;A.collect()
		if L in K.problematic:B.warning('SKIPPING problematic module:{}'.format(L));return
		X,O=K.get_obj_attributes(L)
		if O:B.error(O)
		for(F,J,G,Y,a)in X:
			if F in['classmethod','staticmethod','BaseException',M]:continue
			if F[0].isdigit():B.warning('NameError: invalid name {}'.format(F));continue
			if G=="<class 'type'>"and Q(E)<=A0*4:
				P=C;R=F.endswith(M)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:P=M
				D='\n{}class {}({}):\n'.format(E,F,P)
				if R:D+=E+'    ...\n';I.write(D);continue
				I.write(D);K.write_object_stub(I,Y,'{0}.{1}'.format(obj_name,F),E+'    ',N+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';I.write(D)
			elif any(A in G for A in[x,w,'closure']):
				S=U;T=C
				if N>0:T='self, '
				if V in G or V in J:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,S)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,T,S)
				D+=E+'    ...\n\n';I.write(D)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				H=G[8:-2];D=C
				if H in[u,s,t,v,'bytearray','bytes']:D=W.format(E,F,J,H)
				elif H in[e,d,c]:Z={e:'{}',d:'[]',c:'()'};D=W.format(E,F,Z[H],H)
				elif H in['object','set','frozenset','Pin','FileIO']:D='{0}{1} : {2} ## = {4}\n'.format(E,F,H,G,J)
				else:H=U;D='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,H,G,J)
				I.write(D)
			else:I.write("# all other, type = '{0}'\n".format(G));I.write(E+F+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,b)
		return A
	def clean(C,path=F):
		if path is F:path=C.path
		B.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);D=os.listdir(path)
		except(E,I):return
		for G in D:
			A=y.format(path,G)
			try:os.remove(A)
			except E:
				try:C.clean(A);os.rmdir(A)
				except E:pass
	def report(C,filename='modules.json'):
		B.info('Created stubs for {} modules on board {}\nPath: {}'.format(Q(C._report),C._fwid,C.path));F=y.format(C.path,filename);B.info('Report file: {}'.format(F));A.collect()
		try:
			with N(F,'w')as D:
				C.write_json_header(D);G=O
				for I in C._report:C.write_json_node(D,I,G);G=H
				C.write_json_end(D)
			J=C._start_free-A.mem_free()
		except E:B.error('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(dumps({A:B.info})[1:-1]);f.write(g);f.write(dumps({r:{D:__version__},'stubtype':A})[1:-1]);f.write(g);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(g)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def h(path):
	A=D=0
	while A!=-1:
		A=path.find(G,D)
		if A!=-1:
			C=path[0]if A==0 else path[:A]
			try:I=os.stat(C)
			except E as F:
				if F.args[0]==z:
					try:os.mkdir(C)
					except E as H:B.error('failed to create folder {}'.format(C));raise H
		D=A+1
def Y(s):
	B=' on '
	if not s:return C
	s=s.split(B,1)[0]if B in s else s
	if s.startswith('v'):
		if not V in s:return C
		A=s.split(V)[1];return A
	if not W in s:return C
	A=s.split(W)[1].split(K)[1];return A
def _info():
	Z='ev3-pybricks';X='pycom';V='pycopy';Q='unix';O='win32';N='arch';M='cpu';K='ver';E='mpy';B='build';A=f({S:sys.implementation.name,D:C,B:C,K:C,L:sys.platform,U:'UNKNOWN',M:C,E:C,N:C})
	if A[L].startswith('pyb'):A[L]='stm32'
	elif A[L]==O:A[L]='windows'
	elif A[L]=='linux':A[L]=Q
	try:A[D]=A2(sys.implementation.version)
	except I:pass
	try:H=sys.implementation._machine if'_machine'in P(sys.implementation)else os.uname().machine;A[U]=H;A[M]=H.split('with')[-1].strip();A[E]=sys.implementation._mpy if'_mpy'in P(sys.implementation)else sys.implementation.mpy if E in P(sys.implementation)else C
	except(I,T):pass
	A[U]=A3()
	try:
		if'uname'in P(os):
			A[B]=Y(os.uname()[3])
			if not A[B]:A[B]=Y(os.uname()[2])
		elif D in P(sys):A[B]=Y(sys.version)
	except(I,T,q):pass
	if A[D]==C and sys.platform not in(Q,O):
		try:b=os.uname();A[D]=b.release
		except(T,I,q):pass
	for(c,d,e)in[(V,V,'const'),(X,X,'FAT'),(Z,'pybricks.hubs','EV3Brick')]:
		try:g=__import__(d,F,F,e);A[S]=c;del g;break
		except(R,p):pass
	if A[S]==Z:A['release']='2.0.0'
	if A[S]==a:
		A[D]
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if E in A and A[E]:
		G=int(A[E]);J=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][G>>10]
		if J:A[N]=J
		A[E]='v{}.{}'.format(G&255,G>>8&3)
	if A[B]and not A[D].endswith(W):A[D]=A[D]+W
	A[K]=f"{A[D]}-{A[B]}"if A[B]else f"{A[D]}";return A
def A2(version):
	A=version;B=K.join([str(A)for A in A[:3]])
	if Q(A)>3 and A[3]:B+=V+A[3]
	return B
def A3():
	try:from boardname import BOARDNAME as A;B.info('Found BOARDNAME: {}'.format(A))
	except R:B.warning('BOARDNAME not found');A=C
	return A
def get_root():
	try:A=os.getcwd()
	except(E,I):A=K
	B=A
	for B in[A,'/sd','/flash',G,K]:
		try:C=os.stat(B);break
		except E:continue
	return B
def i(filename):
	try:
		if os.stat(filename)[0]>>14:return O
		return H
	except E:return H
def j():J("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=C
	if Q(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:j()
	elif Q(sys.argv)==2:j()
	return path
def k():
	try:A=bytes('abc',encoding='utf8');B=k.__module__;return H
	except(m,I):return O
def main():
	I='failed';import machine as K
	try:C=N(X,'r+b');D=O;J('Opened existing db')
	except E:C=N(X,'w+b');J('created new db');D=H
	stubber=Stubber(path=read_path())
	if not D:stubber.clean()
	B=l();A4(stubber,B)
	if not stubber.modules:J('All modules have been processed, exiting')
	else:
		del B;A.collect()
		for F in stubber.modules:
			G=H
			try:G=stubber.create_one_stub(F)
			except n:K.reset()
			A.collect()
			with N(X,'a')as C:C.write('{}={}\n'.format(F,'ok'if G else I))
	B=l()
	if B:
		stubber._report=[]
		for(L,M)in B.items():
			if M!=I:stubber._report.append('{{"module": "{0}", "file": "{0}.py"}}'.format(L))
		stubber.report()
def l():
	C={}
	try:
		with N(X)as D:
			while O:
				B=D.readline().strip()
				if not B:break
				if Q(B)>0 and B[0]!='#':F,G=B.split('=',1);C[F]=G
	except(E,SyntaxError):J('could not read modulelist.done')
	finally:A.collect();return C
def A4(stubber,modules_done):
	A.collect();stubber.modules=[]
	for D in A1:
		C=D+'/modulelist.txt'
		if not i(C):continue
		with N(C)as E:
			while O:
				B=E.readline().strip()
				if not B:break
				if B and B not in modules_done.keys():stubber.modules.append(B)
			A.collect();J('BREAK');break
	if not stubber.modules:stubber.modules=[a]
	A.collect()
if __name__=='__main__'or k():
	if not i('no_auto_stubber.txt'):
		try:A.threshold(4*1024);A.enable()
		except BaseException:pass
		main()