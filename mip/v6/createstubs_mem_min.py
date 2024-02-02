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
X=repr
V='-preview'
U='-'
T='board'
S=IndexError
R=print
Q=True
P='family'
O=ImportError
N=len
M=dir
K='port'
J='.'
I=False
H=AttributeError
G='/'
F=None
E=OSError
C='version'
B=''
import gc as D,os,sys
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
y=['lib','/lib','/sd/lib','/flash/lib',J]
class L:
	INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=R
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
A=L.getLogger(o)
L.basicConfig(level=L.INFO)
class Stubber:
	def __init__(B,path=F,firmware_id=F):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise k('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		B._report=[];B.info=_info();A.info('Port: {}'.format(B.info[K]));A.info('Board: {}'.format(B.info[T]));D.collect()
		if C:B._fwid=C.lower()
		elif B.info[P]==Z:B._fwid='{family}-v{version}-{port}-{board}'.format(**B.info).rstrip(U)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=D.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',G)
		try:g(path+G)
		except E:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[]
	def get_obj_attributes(L,item_instance):
		I=item_instance;C=[];K=[]
		for A in M(I):
			if A.startswith(a)and not A in L.modules:continue
			try:
				E=getattr(I,A)
				try:F=X(type(E)).split("'")[1]
				except S:F=B
				if F in{p,q,r,s,b,c,d}:G=1
				elif F in{t,u}:G=2
				elif F in'class':G=3
				else:G=4
				C.append((A,X(E),X(type(E)),E,G))
			except H as J:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,I,J))
			except MemoryError as J:R('MemoryError: {}'.format(J));sleep(1);reset()
		C=l([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);D.collect();return C,K
	def add_modules(A,modules):A.modules=l(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber v{} on {}'.format(__version__,B._fwid));D.collect()
		for C in B.modules:B.create_one_stub(C)
		A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return I
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return I
		H='{}/{}.py'.format(C.path,B.replace(J,G));D.collect();F=I
		try:F=C.create_module_stub(B,H)
		except E:return I
		D.collect();return F
	def create_module_stub(K,module_name,file_name=F):
		H=file_name;C=module_name
		if H is F:L=C.replace(J,a)+'.py';H=K.path+G+L
		else:L=H.split(G)[-1]
		if G in C:C=C.replace(G,J)
		M=F
		try:M=__import__(C,F,F,'*');P=D.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,L,P))
		except O:return I
		g(H)
		with Y(H,'w')as N:R=str(K.info).replace('OrderedDict(',B).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,K._fwid,R,__version__);N.write(S);N.write('from __future__ import annotations\nfrom typing import Any\nfrom _typeshed import Incomplete\n\n');K.write_object_stub(N,M,C,B)
		K._report.append('{{"module": "{}", "file": "{}"}}'.format(C,H.replace('\\',G)))
		if C not in{'os','sys','logging','gc'}:
			try:del M
			except(E,m):A.warning('could not del new_module')
		D.collect();return Q
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		W='{0}{1} = {2} # type: {3}\n';V='bound_method';U='Incomplete';O=in_class;M='Exception';L=object_expr;I=fp;E=indent;D.collect()
		if L in K.problematic:A.warning('SKIPPING problematic module:{}'.format(L));return
		X,P=K.get_obj_attributes(L)
		if P:A.error(P)
		for(F,J,G,Y,a)in X:
			if F in['classmethod','staticmethod','BaseException',M]:continue
			if F[0].isdigit():A.warning('NameError: invalid name {}'.format(F));continue
			if G=="<class 'type'>"and N(E)<=x*4:
				Q=B;R=F.endswith(M)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if R:Q=M
				C='\n{}class {}({}):\n'.format(E,F,Q)
				if R:C+=E+'    ...\n';I.write(C);continue
				I.write(C);K.write_object_stub(I,Y,'{0}.{1}'.format(obj_name,F),E+'    ',O+1);C=E+'    def __init__(self, *argv, **kwargs) -> None:\n';C+=E+'        ...\n\n';I.write(C)
			elif any(A in G for A in[u,t,'closure']):
				S=U;T=B
				if O>0:T='self, '
				if V in G or V in J:C='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,S)
				else:C='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,T,S)
				C+=E+'    ...\n\n';I.write(C)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				H=G[8:-2];C=B
				if H in[r,p,q,s,'bytearray','bytes']:C=W.format(E,F,J,H)
				elif H in[d,c,b]:Z={d:'{}',c:'[]',b:'()'};C=W.format(E,F,Z[H],H)
				elif H in['object','set','frozenset','Pin','FileIO']:C='{0}{1} : {2} ## = {4}\n'.format(E,F,H,G,J)
				else:H=U;C='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,H,G,J)
				I.write(C)
			else:I.write("# all other, type = '{0}'\n".format(G));I.write(E+F+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,a)
		return A
	def clean(C,path=F):
		if path is F:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);D=os.listdir(path)
		except(E,H):return
		for G in D:
			B=v.format(path,G)
			try:os.remove(B)
			except E:
				try:C.clean(B);os.rmdir(B)
				except E:pass
	def report(B,filename='modules.json'):
		A.info('Created stubs for {} modules on board {}\nPath: {}'.format(N(B._report),B._fwid,B.path));F=v.format(B.path,filename);A.info('Report file: {}'.format(F));D.collect()
		try:
			with Y(F,'w')as C:
				B.write_json_header(C);G=Q
				for H in B._report:B.write_json_node(C,H,G);G=I
				B.write_json_end(C)
			J=B._start_free-D.mem_free()
		except E:A.error('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(dumps({A:B.info})[1:-1]);f.write(e);f.write(dumps({o:{C:__version__},'stubtype':A})[1:-1]);f.write(e);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(e)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def g(path):
	B=D=0
	while B!=-1:
		B=path.find(G,D)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except E as F:
				if F.args[0]==w:
					try:os.mkdir(C)
					except E as H:A.error('failed to create folder {}'.format(C));raise H
		D=B+1
def W(s):
	C=' on '
	if not s:return B
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not U in s:return B
		A=s.split(U)[1];return A
	if not V in s:return B
	A=s.split(V)[1].split(J)[1];return A
def _info():
	a='ev3-pybricks';Y='pycom';X='pycopy';U='unix';R='win32';Q='arch';N='cpu';L='ver';E='mpy';D='build';A=f({P:sys.implementation.name,C:B,D:B,L:B,K:sys.platform,T:'UNKNOWN',N:B,E:B,Q:B})
	if A[K].startswith('pyb'):A[K]='stm32'
	elif A[K]==R:A[K]='windows'
	elif A[K]=='linux':A[K]=U
	try:A[C]=z(sys.implementation.version)
	except H:pass
	try:I=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[T]=I;A[N]=I.split('with')[-1].strip();A[E]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if E in M(sys.implementation)else B
	except(H,S):pass
	A[T]=A0()
	try:
		if'uname'in M(os):
			A[D]=W(os.uname()[3])
			if not A[D]:A[D]=W(os.uname()[2])
		elif C in M(sys):A[D]=W(sys.version)
	except(H,S,n):pass
	if A[C]==B and sys.platform not in(U,R):
		try:b=os.uname();A[C]=b.release
		except(S,H,n):pass
	for(c,d,e)in[(X,X,'const'),(Y,Y,'FAT'),(a,'pybricks.hubs','EV3Brick')]:
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
	if A[D]and not A[C].endswith(V):A[C]=A[C]+V
	A[L]=f"{A[C]}-{A[D]}"if A[D]else f"{A[C]}";return A
def z(version):
	A=version;B=J.join([str(A)for A in A[:3]])
	if N(A)>3 and A[3]:B+=U+A[3]
	return B
def A0():
	try:from boardname import BOARDNAME as C;A.info('Found BOARDNAME: {}'.format(C))
	except O:A.warning('BOARDNAME not found');C=B
	return C
def get_root():
	try:A=os.getcwd()
	except(E,H):A=J
	B=A
	for B in[A,'/sd','/flash',G,J]:
		try:C=os.stat(B);break
		except E:continue
	return B
def h(filename):
	try:
		if os.stat(filename)[0]>>14:return Q
		return I
	except E:return I
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
	try:A=bytes('abc',encoding='utf8');B=j.__module__;return I
	except(k,H):return Q
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	def A(stubber):
		D.collect();stubber.modules=[]
		for C in y:
			B=C+'/modulelist.txt'
			if not h(B):continue
			with Y(B)as E:
				while Q:
					A=E.readline().strip()
					if not A:break
					if N(A)>0 and A[0]!='#':stubber.modules.append(A)
				D.collect();R('BREAK');break
		if not stubber.modules:stubber.modules=[Z]
		D.collect()
	stubber.modules=[];A(stubber);D.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or j():
	if not h('no_auto_stubber.txt'):
		try:D.threshold(4*1024);D.enable()
		except BaseException:pass
		main()