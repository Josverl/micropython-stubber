A3='No report file'
A2='Failed to create the report.'
A1='method'
A0='function'
z='float'
y='int'
x='stubber'
w=KeyError
v=sorted
u=NotImplementedError
p='arch'
o='variant'
n=',\n'
m='dict'
l='list'
k='tuple'
j='micropython'
i=TypeError
h=repr
g=getattr
c='-preview'
b='*'
Z='family'
Y='board_id'
X='board'
W=len
V=IndexError
U=print
T=Exception
S=open
R=ImportError
Q='mpy'
P=dir
N='build'
M='port'
L='.'
O=True
G=AttributeError
F='-'
J=None
E=OSError
C='version'
H='/'
D=False
A=''
import gc as I,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except R:pass
try:from collections import OrderedDict as q
except R:from ucollections import OrderedDict as q
try:import inspect as a;d=O
except R:d=D
__version__='v1.26.4'
A4=2
A5=44
A6=2
A7=['lib','/lib','/sd/lib','/flash/lib',L]
class K:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=U
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
B=K.getLogger(x)
K.basicConfig(level=K.INFO)
class Stubber:
	def __init__(A,path=A,firmware_id=A):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise u('MicroPython 1.13.0 cannot be stubbed')
		except G:pass
		A.info=_info();B.info('Port: {}'.format(A.info[M]));B.info('Board: {}'.format(A.info[X]));B.info('Board_ID: {}'.format(A.info[Y]));I.collect()
		if C:A._fwid=C.lower()
		elif A.info[Z]==j:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(F)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=I.mem_free()
		if path:
			if path.endswith(H):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',H)
		try:e(path+H)
		except E:B.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=J;A._json_first=D
	def load_exlusions(C):
		try:
			with S('modulelist_exclude.txt','r')as D:
				for F in D:
					A=F.strip()
					if A and A not in C.excluded:C.excluded.append(A);B.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except E:pass
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for B in P(H):
			if B.startswith('__')and not B in L.modules:continue
			try:
				D=g(H,B)
				try:E=h(type(D)).split("'")[1]
				except V:E=A
				if E in{y,z,'str','bool',k,l,m}:F=1
				elif E in{A0,A1}:F=2
				elif E in'class':F=3
				else:F=4
				C.append((B,h(D),h(type(D)),D,F))
			except G as J:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(B,H,J))
			except MemoryError as J:U('MemoryError: {}'.format(J));sleep(1);reset()
		C=v([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);I.collect();return C,K
	def add_modules(A,modules):A.modules=v(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();I.collect()
		for C in A.modules:A.create_one_stub(C)
		A.report_end();B.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:B.warning('Skip module: {:<25}        : Known problematic'.format(A));return D
		if A in C.excluded:B.warning('Skip module: {:<25}        : Excluded'.format(A));return D
		G='{}/{}.pyi'.format(C.path,A.replace(L,H));I.collect();F=D
		try:F=C.create_module_stub(A,G)
		except E:return D
		I.collect();return F
	def create_module_stub(G,module_name,file_name=J):
		F=file_name;C=module_name
		if F is J:K=C.replace(L,'_')+'.pyi';F=G.path+H+K
		else:K=F.split(H)[-1]
		if H in C:C=C.replace(H,L)
		M=J
		try:M=__import__(C,J,J,b);P=I.mem_free();B.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,K,P))
		except R:return D
		e(F)
		with S(F,'w')as N:Q=str(G.info).replace('OrderedDict(',A).replace('})','}');T='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,G._fwid,Q,__version__);N.write(T);N.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n');G.write_object_stub(N,M,C,A)
		G.report_add(C,F)
		if C not in{'os','sys','logging','gc'}:
			try:del M
			except(E,w):B.warning('could not del new_module')
		I.collect();return O
	def write_object_stub(Z,fp,object_expr,obj_name,indent,in_class=0):
		v=' at ...>';u='{0}{1}: {3} = {2}\n';t='bound_method';s='self, ';r='Incomplete';i='Exception';c=object_expr;Y=' at ';V=in_class;P=fp;F=indent;I.collect()
		if c in Z.problematic:B.warning('SKIPPING problematic module:{}'.format(c));return
		w,j=Z.get_obj_attributes(c)
		if j:B.error(j)
		for(C,L,M,S,_)in w:
			if C in['classmethod','staticmethod','BaseException',i]:continue
			if C[0].isdigit():B.warning('NameError: invalid name {}'.format(C));continue
			if M=="<class 'type'>"and W(F)<=A6*4:
				n=A;o=C.endswith(i)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if o:n=i
				E='\n{}class {}({}):\n'.format(F,C,n)
				if o:E+=F+'    ...\n';P.write(E);continue
				P.write(E);Z.write_object_stub(P,S,'{0}.{1}'.format(obj_name,C),F+'    ',V+1);E=F+'    def __init__(self, *argv, **kwargs) -> None:\n';E+=F+'        ...\n\n';P.write(E)
			elif any(A in M for A in[A1,A0,'closure']):
				e=r;p=A
				if V>0:p=s
				X=D;f=D;q=D
				if d:
					try:X=a.iscoroutinefunction(S)
					except T:pass
					if not X:
						try:f=g(a,'isasyncgenfunction',lambda _:D)(S)
						except T:pass
					if not X and not f:
						try:q=a.isgeneratorfunction(S)
						except T:pass
				Q=J
				if d:
					try:
						x=a.signature(S);G=[];N=D;h=D
						for(R,A2)in x.parameters.items():
							U=g(A2,'kind',J)
							if U==0:N=O;G.append(R)
							elif U==1:
								if N:G.append(H);N=D
								G.append(R)
							elif U==2:
								if N:G.append(H);N=D
								h=O;G.append(b+R)
							elif U==3:
								if N:G.append(H);N=D
								if not h:G.append(b);h=O
								G.append(R)
							elif U==4:
								if N:G.append(H);N=D
								G.append('**'+R)
							else:G.append(R)
						if N:G.append(H)
						if V>0 and G and G[0]not in(b,H):G=G[1:]
						if V>0:Q=s+', '.join(G)if G else'self'
						else:Q=', '.join(G)
					except T:pass
				if Q is J:Q='{}*args, **kwargs'.format(p)
				if t in M or t in L:E='{}@classmethod\n'.format(F)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(F,C,e)
				elif X:E='{}async def {}({}) -> {}:\n'.format(F,C,Q,e)
				elif f:E='{}async def {}({}) -> AsyncGenerator:\n'.format(F,C,Q)
				elif q:E='{}def {}({}) -> Generator:\n'.format(F,C,Q)
				else:E='{}def {}({}) -> {}:\n'.format(F,C,Q,e)
				E+=F+'    ...\n\n';P.write(E)
			elif M=="<class 'module'>":0
			elif M.startswith("<class '"):
				K=M[8:-2];E=A
				if K in('str',y,z,'bool','bytearray','bytes'):
					if C.upper()==C:E='{0}{1}: Final[{3}] = {2}\n'.format(F,C,L,K)
					else:E=u.format(F,C,L,K)
				elif K in(m,l,k):A3={m:'{}',l:'[]',k:'()'};E=u.format(F,C,A3[K],K)
				elif K in('object','set','frozenset','Pin'):E='{0}{1}: {2} ## = {4}\n'.format(F,C,K,M,L)
				elif K=='generator':K='Generator';E='{0}def {1}(*args, **kwargs) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(F,C,K,M,L)
				else:
					K=r
					if Y in L:L=L.split(Y)[0]+v
					if Y in L:L=L.split(Y)[0]+v
					E='{0}{1}: {2} ## {3} = {4}\n'.format(F,C,K,M,L)
				P.write(E)
			else:P.write("# all other, type = '{0}'\n".format(M));P.write(F+C+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(C,path=A):
		if not path:path=C.path
		B.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);D=os.listdir(path)
		except(E,G):return
		for F in D:
			A='{}/{}'.format(path,F)
			try:os.remove(A)
			except E:
				try:C.clean(A);os.rmdir(A)
				except E:pass
	def report_start(A,filename='modules.json'):
		F='firmware';A._json_name='{}/{}'.format(A.path,filename);A._json_first=O;e(A._json_name);B.info('Report file: {}'.format(A._json_name));I.collect()
		try:
			with S(A._json_name,'w')as D:D.write('{');D.write(dumps({F:A.info})[1:-1]);D.write(n);D.write(dumps({x:{C:__version__},'stubtype':F})[1:-1]);D.write(n);D.write('"modules" :[\n')
		except E as G:B.error(A2);A._json_name=J;raise G
	def report_add(A,module_name,stub_file):
		if not A._json_name:raise T(A3)
		try:
			with S(A._json_name,'a')as C:
				if not A._json_first:C.write(n)
				else:A._json_first=D
				F='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',H));C.write(F)
		except E:B.error(A2)
	def report_end(A):
		if not A._json_name:raise T(A3)
		with S(A._json_name,'a')as C:C.write('\n]}')
		B.info('Path: {}'.format(A.path))
def e(path):
	A=D=0
	while A!=-1:
		A=path.find(H,D)
		if A!=-1:
			C=path[0]if A==0 else path[:A]
			try:I=os.stat(C)
			except E as F:
				if F.args[0]in[A4,A5]:
					try:B.debug('Create folder {}'.format(C));os.mkdir(C)
					except E as G:B.error('failed to create folder {}'.format(C));raise G
		D=A+1
def f(s):
	C=' on '
	if not s:return A
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not F in s:return A
		B=s.split(F)[1];return B
	if not c in s:return A
	B=s.split(c)[1].split(L)[1];return B
def A8():
	try:B=sys.implementation[0]
	except i:B=sys.implementation.name
	D=q({Z:B,C:A,N:A,'ver':A,M:sys.platform,X:'UNKNOWN',Y:A,o:A,'cpu':A,Q:A,p:A});return D
def A9(info):
	A=info
	if A[M].startswith('pyb'):A[M]='stm32'
	elif A[M]=='win32':A[M]='windows'
	elif A[M]=='linux':A[M]='unix'
def AA(info):
	try:info[C]=AH(sys.implementation.version)
	except G:pass
def AB(info):
	B=info
	try:
		D=sys.implementation._machine if'_machine'in P(sys.implementation)else os.uname().machine;B[X]=D.strip();C=sys.implementation._build if'_build'in P(sys.implementation)else A
		if C:B[X]=C.split(F)[0];B[o]=C.split(F)[1]if F in C else A
		B[Y]=C;B['cpu']=D.split('with')[-1].strip();B[Q]=sys.implementation._mpy if'_mpy'in P(sys.implementation)else sys.implementation.mpy if Q in P(sys.implementation)else A
	except(G,V):pass
	if not B[Y]:AI(B)
def AC(info):
	B=info
	try:
		if'uname'in P(os):
			B[N]=f(os.uname()[3])
			if not B[N]:B[N]=f(os.uname()[2])
		elif C in P(sys):B[N]=f(sys.version)
	except(G,V,i):pass
	if B[C]==A and sys.platform not in('unix','win32'):
		try:D=os.uname();B[C]=D.release
		except(V,G,i):pass
def AD(info):
	D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,J,J,G);A[Z]=E;del H;break
		except(R,w):pass
	if A[Z]==D:A['release']='2.0.0'
def AE(info):
	A=info
	if A[Z]==j:
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
def AF(info):
	A=info
	if Q in A and A[Q]:
		B=int(A[Q])
		try:
			C=[J,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[p]=C
		except V:A[p]='unknown'
		A[Q]='v{}.{}'.format(B&255,B>>8&3)
def AG(info):
	A=info
	if A[N]and not A[C].endswith(c):A[C]=A[C]+c
	A['ver']=f"{A[C]}-{A[N]}"if A[N]else f"{A[C]}"
def _info():A=A8();A9(A);AA(A);AB(A);AC(A);AD(A);AE(A);AF(A);AG(A);return A
def AH(version):
	A=version;B=L.join([str(A)for A in A[:3]])
	if W(A)>3 and A[3]:B+=F+A[3]
	return B
def AI(info):
	D=info
	try:from boardname import BOARD_ID as C;B.info('Found BOARD_ID: {}'.format(C))
	except R:B.warning('BOARD_ID not found');C=A
	D[Y]=C;D[X]=C.split(F)[0]if F in C else C;D[o]==C.split(F)[1]if F in C else A
def get_root():
	try:A=os.getcwd()
	except(E,G):A=L
	B=A
	for B in['/remote','/sd','/flash',H,A,L]:
		try:C=os.stat(B);break
		except E:continue
	return B
def r(filename):
	try:
		if os.stat(filename)[0]>>14:return O
		return D
	except E:return D
def s():U("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=A
	if W(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):path=sys.argv[2]
		else:s()
	elif W(sys.argv)==2:s()
	return path
def t():
	try:A=bytes('abc',encoding='utf8');B=t.__module__;return D
	except(u,G):return O
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	def A(stubber):
		I.collect();stubber.modules=[]
		for C in A7:
			B=C+'/modulelist.txt'
			if not r(B):continue
			with S(B)as D:
				while O:
					A=D.readline().strip()
					if not A:break
					if W(A)>0 and A[0]!='#':stubber.modules.append(A)
				I.collect();U('BREAK');break
		if not stubber.modules:stubber.modules=[j]
		I.collect()
	stubber.modules=[];A(stubber);I.collect();stubber.create_all_stubs()
if __name__=='__main__'or t():
	if not r('no_auto_stubber.txt'):
		U(f"createstubs.py: {__version__}")
		try:I.threshold(4096);I.enable()
		except BaseException:pass
		main()