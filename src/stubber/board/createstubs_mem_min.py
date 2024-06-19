x='No report file'
w='Failed to create the report.'
v='{}/{}'
u='method'
t='function'
s='bool'
r='str'
q='float'
p='int'
o='stubber'
n=Exception
m=KeyError
l=sorted
k=NotImplementedError
f=',\n'
e='dict'
d='list'
c='tuple'
b='micropython'
a=TypeError
Z=repr
W='-preview'
V='-'
U='board'
T=IndexError
S=print
R=True
Q='family'
P=len
O=open
N=ImportError
M=dir
K='port'
J='.'
I=AttributeError
H=False
G='/'
F=OSError
E=None
C='version'
B=''
import gc as D,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except N:pass
try:from collections import OrderedDict as g
except N:from ucollections import OrderedDict as g
__version__='v1.20.6'
y=2
z=2
A0=['lib','/lib','/sd/lib','/flash/lib',J]
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
A=L.getLogger(o)
L.basicConfig(level=L.INFO)
class Stubber:
	def __init__(B,path=E,firmware_id=E):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise k('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		B.info=_info();A.info('Port: {}'.format(B.info[K]));A.info('Board: {}'.format(B.info[U]));D.collect()
		if C:B._fwid=C.lower()
		elif B.info[Q]==b:B._fwid='{family}-v{version}-{port}-{board}'.format(**B.info).rstrip(V)
		else:B._fwid='{family}-v{version}-{port}'.format(**B.info)
		B._start_free=D.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		B.path='{}/stubs/{}'.format(path,B.flat_fwid).replace('//',G)
		try:X(path+G)
		except F:A.error('error creating stub folder {}'.format(path))
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[];B._json_name=E;B._json_first=H
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for A in M(H):
			if A.startswith('__')and not A in L.modules:continue
			try:
				E=getattr(H,A)
				try:F=Z(type(E)).split("'")[1]
				except T:F=B
				if F in{p,q,r,s,c,d,e}:G=1
				elif F in{t,u}:G=2
				elif F in'class':G=3
				else:G=4
				C.append((A,Z(E),Z(type(E)),E,G))
			except I as J:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,J))
			except MemoryError as J:S('MemoryError: {}'.format(J));sleep(1);reset()
		C=l([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);D.collect();return C,K
	def add_modules(A,modules):A.modules=l(set(A.modules)|set(modules))
	def create_all_stubs(B):
		A.info('Start micropython-stubber {} on {}'.format(__version__,B._fwid));B.report_start();D.collect()
		for C in B.modules:B.create_one_stub(C)
		B.report_end();A.info('Finally done')
	def create_one_stub(C,module_name):
		B=module_name
		if B in C.problematic:A.warning('Skip module: {:<25}        : Known problematic'.format(B));return H
		if B in C.excluded:A.warning('Skip module: {:<25}        : Excluded'.format(B));return H
		I='{}/{}.pyi'.format(C.path,B.replace(J,G));D.collect();E=H
		try:E=C.create_module_stub(B,I)
		except F:return H
		D.collect();return E
	def create_module_stub(K,module_name,file_name=E):
		I=file_name;C=module_name
		if I is E:L=C.replace(J,'_')+'.pyi';I=K.path+G+L
		else:L=I.split(G)[-1]
		if G in C:C=C.replace(G,J)
		M=E
		try:M=__import__(C,E,E,'*');Q=D.mem_free();A.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,L,Q))
		except N:return H
		X(I)
		with O(I,'w')as P:S=str(K.info).replace('OrderedDict(',B).replace('})','}');T='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,K._fwid,S,__version__);P.write(T);P.write('from __future__ import annotations\nfrom typing import Any, Generator\nfrom _typeshed import Incomplete\n\n');K.write_object_stub(P,M,C,B)
		K.report_add(C,I)
		if C not in{'os','sys','logging','gc'}:
			try:del M
			except(F,m):A.warning('could not del new_module')
		D.collect();return R
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		Z=' at ...>';Y='generator';X='{0}{1}: {3} = {2}\n';W='bound_method';V='Incomplete';O=in_class;N='Exception';M=object_expr;K=' at ';J=fp;E=indent;D.collect()
		if M in L.problematic:A.warning('SKIPPING problematic module:{}'.format(M));return
		a,Q=L.get_obj_attributes(M)
		if Q:A.error(Q)
		for(F,H,I,b,g)in a:
			if F in['classmethod','staticmethod','BaseException',N]:continue
			if F[0].isdigit():A.warning('NameError: invalid name {}'.format(F));continue
			if I=="<class 'type'>"and P(E)<=z*4:
				R=B;S=F.endswith(N)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if S:R=N
				C='\n{}class {}({}):\n'.format(E,F,R)
				if S:C+=E+'    ...\n';J.write(C);continue
				J.write(C);L.write_object_stub(J,b,'{0}.{1}'.format(obj_name,F),E+'    ',O+1);C=E+'    def __init__(self, *argv, **kwargs) -> None:\n';C+=E+'        ...\n\n';J.write(C)
			elif any(A in I for A in[u,t,'closure']):
				T=V;U=B
				if O>0:U='self, '
				if W in I or W in H:C='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,T)
				else:C='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,U,T)
				C+=E+'    ...\n\n';J.write(C)
			elif I=="<class 'module'>":0
			elif I.startswith("<class '"):
				G=I[8:-2];C=B
				if G in(r,p,q,s,'bytearray','bytes'):C=X.format(E,F,H,G)
				elif G in(e,d,c):f={e:'{}',d:'[]',c:'()'};C=X.format(E,F,f[G],G)
				elif G in('object','set','frozenset','Pin',Y):
					if G==Y:G='Generator'
					C='{0}{1}: {2} ## = {4}\n'.format(E,F,G,I,H)
				else:
					G=V
					if K in H:H=H.split(K)[0]+Z
					if K in H:H=H.split(K)[0]+Z
					C='{0}{1}: {2} ## {3} = {4}\n'.format(E,F,G,I,H)
				J.write(C)
			else:J.write("# all other, type = '{0}'\n".format(I));J.write(E+F+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(C,path=E):
		if path is E:path=C.path
		A.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);D=os.listdir(path)
		except(F,I):return
		for G in D:
			B=v.format(path,G)
			try:os.remove(B)
			except F:
				try:C.clean(B);os.rmdir(B)
				except F:pass
	def report_start(B,filename='modules.json'):
		H='firmware';B._json_name=v.format(B.path,filename);B._json_first=R;X(B._json_name);A.info('Report file: {}'.format(B._json_name));D.collect()
		try:
			with O(B._json_name,'w')as G:G.write('{');G.write(dumps({H:B.info})[1:-1]);G.write(f);G.write(dumps({o:{C:__version__},'stubtype':H})[1:-1]);G.write(f);G.write('"modules" :[\n')
		except F as I:A.error(w);B._json_name=E;raise I
	def report_add(B,module_name,stub_file):
		if not B._json_name:raise n(x)
		try:
			with O(B._json_name,'a')as C:
				if not B._json_first:C.write(f)
				else:B._json_first=H
				D='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',G));C.write(D)
		except F:A.error(w)
	def report_end(B):
		if not B._json_name:raise n(x)
		with O(B._json_name,'a')as C:C.write('\n]}')
		A.info('Path: {}'.format(B.path))
def X(path):
	B=D=0
	while B!=-1:
		B=path.find(G,D)
		if B!=-1:
			C=path[0]if B==0 else path[:B]
			try:I=os.stat(C)
			except F as E:
				if E.args[0]==y:
					try:os.mkdir(C)
					except F as H:A.error('failed to create folder {}'.format(C));raise H
		D=B+1
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
	c='ev3-pybricks';Z='pycom';X='pycopy';V='unix';S='win32';R='arch';P='cpu';O='ver';F='mpy';D='build'
	try:H=sys.implementation[0]
	except a:H=sys.implementation.name
	A=g({Q:H,C:B,D:B,O:B,K:sys.platform,U:'UNKNOWN',P:B,F:B,R:B})
	if A[K].startswith('pyb'):A[K]='stm32'
	elif A[K]==S:A[K]='windows'
	elif A[K]=='linux':A[K]=V
	try:A[C]=A1(sys.implementation.version)
	except I:pass
	try:J=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[U]=J;A[P]=J.split('with')[-1].strip();A[F]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if F in M(sys.implementation)else B
	except(I,T):pass
	A[U]=A2()
	try:
		if'uname'in M(os):
			A[D]=Y(os.uname()[3])
			if not A[D]:A[D]=Y(os.uname()[2])
		elif C in M(sys):A[D]=Y(sys.version)
	except(I,T,a):pass
	if A[C]==B and sys.platform not in(V,S):
		try:d=os.uname();A[C]=d.release
		except(T,I,a):pass
	for(e,f,h)in[(X,X,'const'),(Z,Z,'FAT'),(c,'pybricks.hubs','EV3Brick')]:
		try:i=__import__(f,E,E,h);A[Q]=e;del i;break
		except(N,m):pass
	if A[Q]==c:A['release']='2.0.0'
	if A[Q]==b:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if F in A and A[F]:
		G=int(A[F]);L=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][G>>10]
		if L:A[R]=L
		A[F]='v{}.{}'.format(G&255,G>>8&3)
	if A[D]and not A[C].endswith(W):A[C]=A[C]+W
	A[O]=f"{A[C]}-{A[D]}"if A[D]else f"{A[C]}";return A
def A1(version):
	A=version;B=J.join([str(A)for A in A[:3]])
	if P(A)>3 and A[3]:B+=V+A[3]
	return B
def A2():
	try:from boardname import BOARDNAME as C;A.info('Found BOARDNAME: {}'.format(C))
	except N:A.warning('BOARDNAME not found');C=B
	return C
def get_root():
	try:A=os.getcwd()
	except(F,I):A=J
	B=A
	for B in[A,'/sd','/flash',G,J]:
		try:C=os.stat(B);break
		except F:continue
	return B
def h(filename):
	try:
		if os.stat(filename)[0]>>14:return R
		return H
	except F:return H
def i():S("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=B
	if P(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:i()
	elif P(sys.argv)==2:i()
	return path
def j():
	try:A=bytes('abc',encoding='utf8');B=j.__module__;return H
	except(k,I):return R
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	def A(stubber):
		D.collect();stubber.modules=[]
		for C in A0:
			B=C+'/modulelist.txt'
			if not h(B):continue
			with O(B)as E:
				while R:
					A=E.readline().strip()
					if not A:break
					if P(A)>0 and A[0]!='#':stubber.modules.append(A)
				D.collect();S('BREAK');break
		if not stubber.modules:stubber.modules=[b]
		D.collect()
	stubber.modules=[];A(stubber);D.collect();stubber.create_all_stubs()
if __name__=='__main__'or j():
	if not h('no_auto_stubber.txt'):
		try:D.threshold(4*1024);D.enable()
		except BaseException:pass
		main()