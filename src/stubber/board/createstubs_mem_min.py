v='{}/{}'
u='method'
t='function'
s='bool'
r='str'
q='float'
p='int'
o='stubber'
n=TypeError
m=KeyError
l=sorted
k=NotImplementedError
e=',\n'
d='dict'
c='list'
b='tuple'
a='_'
Z='micropython'
Y=open
W='-preview'
V='-'
U='board'
T=IndexError
S=repr
R=print
Q=True
P='family'
O=ImportError
N=len
M=dir
L='port'
K='.'
J=False
I=AttributeError
G='/'
F=None
D=OSError
C='version'
B=''
import gc as E,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except O:pass
try:from collections import OrderedDict as f
except O:from ucollections import OrderedDict as f
__version__='v1.16.3'
w=2
x=2
y=['lib','/lib','/sd/lib','/flash/lib',K]
class H:
	DEBUG=10;TRACE=15;INFO=20;WARNING=30;ERROR=40;CRITICAL=50;level=INFO;prnt=R
	@staticmethod
	def getLogger(name):return H()
	@classmethod
	def basicConfig(A,level):A.level=level
	def trace(A,msg):
		if A.level<=H.TRACE:A.prnt('TRACE :',msg)
	def debug(A,msg):
		if A.level<=H.DEBUG:A.prnt('DEBUG :',msg)
	def info(A,msg):
		if A.level<=H.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=H.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=H.ERROR:A.prnt('ERROR :',msg)
	def critical(A,msg):
		if A.level<=H.CRITICAL:A.prnt('CRIT  :',msg)
A=H.getLogger(o)
H.basicConfig(level=H.INFO)
class Stubber:
	def __init__(B,path=F,firmware_id=F):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise k('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		B._report=[];B.info=_info();A.info('Port: {}'.format(B.info[L]));A.info('Board: {}'.format(B.info[U]));E.collect()
		if C:B._fwid=C.lower()
		elif B.info[P]==Z:B._fwid='{family}-v{version}-{port}-{board}'.format(**B.info).rstrip(V)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=E.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',G);A.debug(B.path)
		try:g(path+G)
		except D:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[]
	def get_obj_attributes(N,item_instance):
		D=item_instance;G=[];L=[];A.debug('get attributes {} {}'.format(S(D),D))
		for C in M(D):
			if C.startswith(a)and not C in N.modules:continue
			A.debug('get attribute {}'.format(C))
			try:
				F=getattr(D,C);A.debug('attribute {}:{}'.format(C,F))
				try:H=S(type(F)).split("'")[1]
				except T:H=B
				if H in{p,q,r,s,b,c,d}:J=1
				elif H in{t,u}:J=2
				elif H in'class':J=3
				else:J=4
				G.append((C,S(F),S(type(F)),F,J))
			except I as K:L.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(C,D,K))
			except MemoryError as K:R('MemoryError: {}'.format(K));sleep(1);reset()
		G=l([A for A in G if not A[0].startswith('__')],key=lambda x:x[4]);E.collect();return G,L
	def add_modules(A,modules):A.modules=l(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber v{} on {}'.format(__version__,B._fwid));E.collect()
		for C in B.modules:B.create_one_stub(C)
		A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return J
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return J
		H='{}/{}.py'.format(C.path,B.replace(K,G));E.collect();F=J
		try:F=C.create_module_stub(B,H)
		except D:return J
		E.collect();return F
	def create_module_stub(I,module_name,file_name=F):
		H=file_name;C=module_name
		if H is F:L=C.replace(K,a)+'.py';H=I.path+G+L
		else:L=H.split(G)[-1]
		if G in C:C=C.replace(G,K)
		M=F
		try:M=__import__(C,F,F,'*');P=E.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,L,P))
		except O:A.trace('Skip module: {:<25} {:<79}'.format(C,'Module not found.'));return J
		g(H)
		with Y(H,'w')as N:R=str(I.info).replace('OrderedDict(',B).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,I._fwid,R,__version__);N.write(S);N.write('from __future__ import annotations\nfrom typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(N,M,C,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(C,H.replace('\\',G)))
		if C not in{'os','sys','logging','gc'}:
			try:del M
			except(D,m):A.warning('could not del new_module')
		E.collect();return Q
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		W='{0}{1} = {2} # type: {3}\n';V='bound_method';U='Incomplete';O=in_class;M='Exception';L=object_expr;I=fp;F=indent;E.collect()
		if L in K.problematic:A.warning('SKIPPING problematic module:{}'.format(L));return
		X,P=K.get_obj_attributes(L)
		if P:A.error(P)
		for(C,J,G,Y,a)in X:
			if C in['classmethod','staticmethod','BaseException',M]:continue
			if C[0].isdigit():A.warning('NameError: invalid name {}'.format(C));continue
			if G=="<class 'type'>"and N(F)<=x*4:
				A.trace('{0}class {1}:'.format(F,C));Q=B;R=C.endswith(M)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=M
				D='\n{}class {}({}):\n'.format(F,C,Q)
				if R:D+=F+'    ...\n';I.write(D);continue
				I.write(D);A.debug('# recursion over class {0}'.format(C));K.write_object_stub(I,Y,'{0}.{1}'.format(obj_name,C),F+'    ',O+1);D=F+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=F+'        ...\n\n';I.write(D)
			elif any(A in G for A in[u,t,'closure']):
				A.debug("# def {1} function/method/closure, type = '{0}'".format(G,C));S=U;T=B
				if O>0:T='self, '
				if V in G or V in J:D='{}@classmethod\n'.format(F)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(F,C,S)
				else:D='{}def {}({}*args, **kwargs) -> {}:\n'.format(F,C,T,S)
				D+=F+'    ...\n\n';I.write(D);A.debug('\n'+D)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				H=G[8:-2];D=B
				if H in[r,p,q,s,'bytearray','bytes']:D=W.format(F,C,J,H)
				elif H in[d,c,b]:Z={d:'{}',c:'[]',b:'()'};D=W.format(F,C,Z[H],H)
				elif H in['object','set','frozenset','Pin','FileIO']:D='{0}{1} : {2} ## = {4}\n'.format(F,C,H,G,J)
				else:H=U;D='{0}{1} : {2} ## {3} = {4}\n'.format(F,C,H,G,J)
				I.write(D);A.debug('\n'+D)
			else:A.debug("# all other, type = '{0}'".format(G));I.write("# all other, type = '{0}'\n".format(G));I.write(F+C+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,a)
		return A
	def clean(C,path=F):
		if path is F:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except(D,I):return
		for G in E:
			B=v.format(path,G)
			try:os.remove(B)
			except D:
				try:C.clean(B);os.rmdir(B)
				except D:pass
	def report(B,filename='modules.json'):
		A.info('Created stubs for {} modules on board {}\nPath: {}'.format(N(B._report),B._fwid,B.path));F=v.format(B.path,filename);A.info('Report file: {}'.format(F));E.collect()
		try:
			with Y(F,'w')as C:
				B.write_json_header(C);G=Q
				for H in B._report:B.write_json_node(C,H,G);G=J
				B.write_json_end(C)
			I=B._start_free-E.mem_free();A.trace('Memory used: {0} Kb'.format(I//1024))
		except D:A.error('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(dumps({A:B.info})[1:-1]);f.write(e);f.write(dumps({o:{C:__version__},'stubtype':A})[1:-1]);f.write(e);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(e)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def g(path):
	B=E=0
	while B!=-1:
		B=path.find(G,E)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except D as F:
				if F.args[0]==w:
					try:os.mkdir(C)
					except D as H:A.error('failed to create folder {}'.format(C));raise H
		E=B+1
def X(s):
	C=' on '
	if not s:return B
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not V in s:return B
		A=s.split(V)[1];return A
	if not W in s:return B
	A=s.split(W)[1].split(K)[1];return A
def _info():
	a='ev3-pybricks';Y='pycom';V='pycopy';S='unix';R='win32';Q='arch';N='cpu';K='ver';E='mpy';D='build';A=f({P:sys.implementation.name,C:B,D:B,K:B,L:sys.platform,U:'UNKNOWN',N:B,E:B,Q:B})
	if A[L].startswith('pyb'):A[L]='stm32'
	elif A[L]==R:A[L]='windows'
	elif A[L]=='linux':A[L]=S
	try:A[C]=z(sys.implementation.version)
	except I:pass
	try:H=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[U]=H;A[N]=H.split('with')[-1].strip();A[E]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if E in M(sys.implementation)else B
	except(I,T):pass
	A[U]=A0()
	try:
		if'uname'in M(os):
			A[D]=X(os.uname()[3])
			if not A[D]:A[D]=X(os.uname()[2])
		elif C in M(sys):A[D]=X(sys.version)
	except(I,T,n):pass
	if A[C]==B and sys.platform not in(S,R):
		try:b=os.uname();A[C]=b.release
		except(T,I,n):pass
	for(c,d,e)in[(V,V,'const'),(Y,Y,'FAT'),(a,'pybricks.hubs','EV3Brick')]:
		try:g=__import__(d,F,F,e);A[P]=c;del g;break
		except(O,m):pass
	if A[P]==a:A['release']='2.0.0'
	if A[P]==Z:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if E in A and A[E]:
		G=int(A[E]);J=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][G>>10]
		if J:A[Q]=J
		A[E]='v{}.{}'.format(G&255,G>>8&3)
	if A[D]and not A[C].endswith(W):A[C]=A[C]+W
	A[K]=f"{A[C]}-{A[D]}"if A[D]else f"{A[C]}";return A
def z(version):
	A=version;B=K.join([str(A)for A in A[:3]])
	if N(A)>3 and A[3]:B+=V+A[3]
	return B
def A0():
	try:from boardname import BOARDNAME as C;A.info('Found BOARDNAME: {}'.format(C))
	except O:A.warning('BOARDNAME not found');C=B
	return C
def get_root():
	try:A=os.getcwd()
	except(D,I):A=K
	B=A
	for B in[A,'/sd','/flash',G,K]:
		try:C=os.stat(B);break
		except D:continue
	return B
def h(filename):
	try:
		if os.stat(filename)[0]>>14:return Q
		return J
	except D:return J
def i():R("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if N(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:i()
	elif N(sys.argv)==2:i()
	return path
def j():
	try:A=bytes('abc',encoding='utf8');B=j.__module__;return J
	except(k,I):return Q
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	def A(stubber):
		E.collect();stubber.modules=[]
		for C in y:
			B=C+'/modulelist.txt'
			if not h(B):continue
			with Y(B)as D:
				while Q:
					A=D.readline().strip()
					if not A:break
					if N(A)>0 and A[0]!='#':stubber.modules.append(A)
				E.collect();R('BREAK');break
		if not stubber.modules:stubber.modules=[Z]
		E.collect()
	stubber.modules=[];A(stubber);E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or j():
	if not h('no_auto_stubber.txt'):
		try:E.threshold(4*1024);E.enable()
		except BaseException:pass
		main()