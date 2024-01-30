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
Y='modulelist.done'
X='-preview'
W='-'
V='board'
U=IndexError
T=repr
S='family'
R=ImportError
Q=dir
P=True
O=len
N=open
M='port'
L='.'
K=print
J=AttributeError
H=False
G='/'
F=None
E=OSError
D='version'
C=''
import gc as B,os,sys
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
A1=['lib','/lib','/sd/lib','/flash/lib',L]
class I:
	DEBUG=10;TRACE=15;INFO=20;WARNING=30;ERROR=40;CRITICAL=50;level=INFO;prnt=K
	@staticmethod
	def getLogger(name):return I()
	@classmethod
	def basicConfig(A,level):A.level=level
	def trace(A,msg):
		if A.level<=I.TRACE:A.prnt('TRACE :',msg)
	def debug(A,msg):
		if A.level<=I.DEBUG:A.prnt('DEBUG :',msg)
	def info(A,msg):
		if A.level<=I.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=I.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=I.ERROR:A.prnt('ERROR :',msg)
	def critical(A,msg):
		if A.level<=I.CRITICAL:A.prnt('CRIT  :',msg)
A=I.getLogger(r)
I.basicConfig(level=I.INFO)
class Stubber:
	def __init__(C,path=F,firmware_id=F):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise m('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		C._report=[];C.info=_info();A.info('Port: {}'.format(C.info[M]));A.info('Board: {}'.format(C.info[V]));B.collect()
		if D:C._fwid=D.lower()
		elif C.info[S]==a:C._fwid='{family}-v{version}-{port}-{board}'.format(**C.info).rstrip(W)
		else:C._fwid='{family}-v{version}-{port}'.format(**C.info)
		C._start_free=B.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		C.path='{}/stubs/{}'.format(path,C.flat_fwid).replace('//',G);A.debug(C.path)
		try:h(path+G)
		except E:A.error('error creating stub folder {}'.format(path))
		C.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];C.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];C.modules=[]
	def get_obj_attributes(N,item_instance):
		E=item_instance;G=[];M=[];A.debug('get attributes {} {}'.format(T(E),E))
		for D in Q(E):
			if D.startswith(b)and not D in N.modules:continue
			A.debug('get attribute {}'.format(D))
			try:
				F=getattr(E,D);A.debug('attribute {}:{}'.format(D,F))
				try:H=T(type(F)).split("'")[1]
				except U:H=C
				if H in{s,t,u,v,c,d,e}:I=1
				elif H in{w,x}:I=2
				elif H in'class':I=3
				else:I=4
				G.append((D,T(F),T(type(F)),F,I))
			except J as L:M.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(D,E,L))
			except n as L:K('MemoryError: {}'.format(L));sleep(1);reset()
		G=o([A for A in G if not A[0].startswith('__')],key=lambda x:x[4]);B.collect();return G,M
	def add_modules(A,modules):A.modules=o(set(A.modules)|set(modules))
	def create_all_stubs(C):
		A.info('Start micropython-stubber v{} on {}'.format(__version__,C._fwid));B.collect()
		for D in C.modules:C.create_one_stub(D)
		A.info('Finally done')
	def create_one_stub(D,module_name):
		C=module_name
		if C in D.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(C));return H
		if C in D.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(C));return H
		I='{}/{}.py'.format(D.path,C.replace(L,G));B.collect();F=H
		try:F=D.create_module_stub(C,I)
		except E:return H
		B.collect();return F
	def create_module_stub(J,module_name,file_name=F):
		I=file_name;D=module_name
		if I is F:K=D.replace(L,b)+'.py';I=J.path+G+K
		else:K=I.split(G)[-1]
		if G in D:D=D.replace(G,L)
		M=F
		try:M=__import__(D,F,F,'*');Q=B.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(D,K,Q))
		except R:A.trace('Skip module: {:<25} {:<79}'.format(D,'Module not found.'));return H
		h(I)
		with N(I,'w')as O:S=str(J.info).replace('OrderedDict(',C).replace('})','}');T='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,J._fwid,S,__version__);O.write(T);O.write('from __future__ import annotations\nfrom typing import Any\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(O,M,D,C)
		J._report.append('{{"module": "{}", "file": "{}"}}'.format(D,I.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del M
			except(E,p):A.warning('could not del new_module')
		B.collect();return P
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		W='{0}{1} = {2} # type: {3}\n';V='bound_method';U='Incomplete';N=in_class;M='Exception';L=object_expr;I=fp;F=indent;B.collect()
		if L in K.problematic:A.warning('SKIPPING problematic module:{}'.format(L));return
		X,P=K.get_obj_attributes(L)
		if P:A.error(P)
		for(D,J,G,Y,a)in X:
			if D in['classmethod','staticmethod','BaseException',M]:continue
			if D[0].isdigit():A.warning('NameError: invalid name {}'.format(D));continue
			if G=="<class 'type'>"and O(F)<=A0*4:
				A.trace('{0}class {1}:'.format(F,D));Q=C;R=D.endswith(M)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=M
				E='\n{}class {}({}):\n'.format(F,D,Q)
				if R:E+=F+'    ...\n';I.write(E);continue
				I.write(E);A.debug('# recursion over class {0}'.format(D));K.write_object_stub(I,Y,'{0}.{1}'.format(obj_name,D),F+'    ',N+1);E=F+'    def __init__(self, *argv, **kwargs) -> None:\n';E+=F+'        ...\n\n';I.write(E)
			elif any(A in G for A in[x,w,'closure']):
				A.debug("# def {1} function/method/closure, type = '{0}'".format(G,D));S=U;T=C
				if N>0:T='self, '
				if V in G or V in J:E='{}@classmethod\n'.format(F)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(F,D,S)
				else:E='{}def {}({}*args, **kwargs) -> {}:\n'.format(F,D,T,S)
				E+=F+'    ...\n\n';I.write(E);A.debug('\n'+E)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				H=G[8:-2];E=C
				if H in[u,s,t,v,'bytearray','bytes']:E=W.format(F,D,J,H)
				elif H in[e,d,c]:Z={e:'{}',d:'[]',c:'()'};E=W.format(F,D,Z[H],H)
				elif H in['object','set','frozenset','Pin','FileIO']:E='{0}{1} : {2} ## = {4}\n'.format(F,D,H,G,J)
				else:H=U;E='{0}{1} : {2} ## {3} = {4}\n'.format(F,D,H,G,J)
				I.write(E);A.debug('\n'+E)
			else:A.debug("# all other, type = '{0}'".format(G));I.write("# all other, type = '{0}'\n".format(G));I.write(F+D+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,b)
		return A
	def clean(C,path=F):
		if path is F:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);D=os.listdir(path)
		except(E,J):return
		for G in D:
			B=y.format(path,G)
			try:os.remove(B)
			except E:
				try:C.clean(B);os.rmdir(B)
				except E:pass
	def report(C,filename='modules.json'):
		A.info('Created stubs for {} modules on board {}\nPath: {}'.format(O(C._report),C._fwid,C.path));F=y.format(C.path,filename);A.info('Report file: {}'.format(F));B.collect()
		try:
			with N(F,'w')as D:
				C.write_json_header(D);G=P
				for I in C._report:C.write_json_node(D,I,G);G=H
				C.write_json_end(D)
			J=C._start_free-B.mem_free();A.trace('Memory used: {0} Kb'.format(J//1024))
		except E:A.error('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(dumps({A:B.info})[1:-1]);f.write(g);f.write(dumps({r:{D:__version__},'stubtype':A})[1:-1]);f.write(g);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(g)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def h(path):
	B=D=0
	while B!=-1:
		B=path.find(G,D)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except E as F:
				if F.args[0]==z:
					try:os.mkdir(C)
					except E as H:A.error('failed to create folder {}'.format(C));raise H
		D=B+1
def Z(s):
	B=' on '
	if not s:return C
	s=s.split(B,1)[0]if B in s else s
	if s.startswith('v'):
		if not W in s:return C
		A=s.split(W)[1];return A
	if not X in s:return C
	A=s.split(X)[1].split(L)[1];return A
def _info():
	Y='ev3-pybricks';W='pycom';T='pycopy';P='unix';O='win32';N='arch';L='cpu';K='ver';E='mpy';B='build';A=f({S:sys.implementation.name,D:C,B:C,K:C,M:sys.platform,V:'UNKNOWN',L:C,E:C,N:C})
	if A[M].startswith('pyb'):A[M]='stm32'
	elif A[M]==O:A[M]='windows'
	elif A[M]=='linux':A[M]=P
	try:A[D]=A2(sys.implementation.version)
	except J:pass
	try:H=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[V]=H;A[L]=H.split('with')[-1].strip();A[E]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if E in Q(sys.implementation)else C
	except(J,U):pass
	A[V]=A3()
	try:
		if'uname'in Q(os):
			A[B]=Z(os.uname()[3])
			if not A[B]:A[B]=Z(os.uname()[2])
		elif D in Q(sys):A[B]=Z(sys.version)
	except(J,U,q):pass
	if A[D]==C and sys.platform not in(P,O):
		try:b=os.uname();A[D]=b.release
		except(U,J,q):pass
	for(c,d,e)in[(T,T,'const'),(W,W,'FAT'),(Y,'pybricks.hubs','EV3Brick')]:
		try:g=__import__(d,F,F,e);A[S]=c;del g;break
		except(R,p):pass
	if A[S]==Y:A['release']='2.0.0'
	if A[S]==a:
		A[D]
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if E in A and A[E]:
		G=int(A[E]);I=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][G>>10]
		if I:A[N]=I
		A[E]='v{}.{}'.format(G&255,G>>8&3)
	if A[B]and not A[D].endswith(X):A[D]=A[D]+X
	A[K]=f"{A[D]}-{A[B]}"if A[B]else f"{A[D]}";return A
def A2(version):
	A=version;B=L.join([str(A)for A in A[:3]])
	if O(A)>3 and A[3]:B+=W+A[3]
	return B
def A3():
	try:from boardname import BOARDNAME as B;A.info('Found BOARDNAME: {}'.format(B))
	except R:A.warning('BOARDNAME not found');B=C
	return B
def get_root():
	try:A=os.getcwd()
	except(E,J):A=L
	B=A
	for B in[A,'/sd','/flash',G,L]:
		try:C=os.stat(B);break
		except E:continue
	return B
def i(filename):
	try:
		if os.stat(filename)[0]>>14:return P
		return H
	except E:return H
def j():K("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=C
	if O(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:j()
	elif O(sys.argv)==2:j()
	return path
def k():
	try:A=bytes('abc',encoding='utf8');B=k.__module__;return H
	except(m,J):return P
def main():
	J='failed';import machine as L
	try:C=N(Y,'r+b');D=P;K('Opened existing db')
	except E:C=N(Y,'w+b');K('created new db');D=H
	stubber=Stubber(path=read_path())
	if not D:stubber.clean()
	A4(stubber);A=l();F=[B for B in stubber.modules if not B in A.keys()]
	if not F:K('All modules have been processed, exiting')
	else:
		del A;B.collect()
		for G in F:
			I=H
			try:I=stubber.create_one_stub(G)
			except n:L.reset()
			B.collect()
			with N(Y,'a')as C:C.write('{}={}\n'.format(G,'ok'if I else J))
	A=l()
	if A:
		stubber._report=[]
		for(M,O)in A.items():
			if O!=J:stubber._report.append('{{"module": "{0}", "file": "{0}.py"}}'.format(M))
		stubber.report()
def l():
	C={}
	try:
		with N(Y)as D:
			while P:
				A=D.readline().strip()
				if not A:break
				if O(A)>0 and A[0]!='#':F,G=A.split('=',1);C[F]=G
	except(E,SyntaxError):K('could not read modulelist.done')
	finally:B.collect();return C
def A4(stubber):
	B.collect();stubber.modules=[]
	for D in A1:
		C=D+'/modulelist.txt'
		if not i(C):continue
		with N(C)as E:
			while P:
				A=E.readline().strip()
				if not A:break
				if O(A)>0 and A[0]!='#':stubber.modules.append(A)
			B.collect();K('BREAK');break
	if not stubber.modules:stubber.modules=[a]
	B.collect()
if __name__=='__main__'or k():
	if not i('no_auto_stubber.txt'):
		try:B.threshold(4*1024);B.enable()
		except BaseException:pass
		main()