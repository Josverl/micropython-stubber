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
e='-preview'
d=getattr
b='family'
Z='board_id'
X='board'
a=len
W=IndexError
V=print
T=open
S=ImportError
Q='mpy'
U='*'
P=dir
O='build'
N='port'
L='.'
R=Exception
H=AttributeError
G='-'
M=True
F=OSError
K=None
A='version'
E='/'
C=''
B=False
import gc as J,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except S:pass
try:from collections import OrderedDict as q
except S:from ucollections import OrderedDict as q
try:import inspect as Y;c=M
except S:c=B
__version__='v1.26.5a0'
A4=2
A5=44
A6=2
A7=['lib','/lib','/sd/lib','/flash/lib',L]
class I:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=V
	@staticmethod
	def getLogger(name):return I()
	@classmethod
	def basicConfig(A,level):A.level=level
	def debug(A,msg):
		if A.level<=I.DEBUG:A.prnt('DEBUG :',msg)
	def info(A,msg):
		if A.level<=I.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=I.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=I.ERROR:A.prnt('ERROR :',msg)
D=I.getLogger(x)
I.basicConfig(level=I.INFO)
class Stubber:
	def __init__(A,path=C,firmware_id=C):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise u('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A.info=_info();D.info('Port: {}'.format(A.info[N]));D.info('Board: {}'.format(A.info[X]));D.info('Board_ID: {}'.format(A.info[Z]));J.collect()
		if C:A._fwid=C.lower()
		elif A.info[b]==j:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(G)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=J.mem_free()
		if path:
			if path.endswith(E):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',E)
		try:f(path+E)
		except F:D.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=K;A._json_first=B
	def load_exlusions(B):
		try:
			with T('modulelist_exclude.txt','r')as C:
				for E in C:
					A=E.strip()
					if A and A not in B.excluded:B.excluded.append(A);D.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except F:pass
	def get_obj_attributes(L,item_instance):
		G=item_instance;B=[];K=[]
		for A in P(G):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=d(G,A)
				try:E=h(type(D)).split("'")[1]
				except W:E=C
				if E in{y,z,'str','bool',k,l,m}:F=1
				elif E in{A0,A1}:F=2
				elif E in'class':F=3
				else:F=4
				B.append((A,h(D),h(type(D)),D,F))
			except H as I:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,G,I))
			except MemoryError as I:V('MemoryError: {}'.format(I));sleep(1);reset()
		B=v([A for A in B if not A[0].startswith('__')],key=lambda x:x[4]);J.collect();return B,K
	def add_modules(A,modules):A.modules=v(set(A.modules)|set(modules))
	def create_all_stubs(A):
		D.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();J.collect()
		for B in A.modules:A.create_one_stub(B)
		A.report_end();D.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:D.warning('Skip module: {:<25}        : Known problematic'.format(A));return B
		if A in C.excluded:D.warning('Skip module: {:<25}        : Excluded'.format(A));return B
		H='{}/{}.pyi'.format(C.path,A.replace(L,E));J.collect();G=B
		try:G=C.create_module_stub(A,H)
		except F:return B
		J.collect();return G
	def create_module_stub(H,module_name,file_name=K):
		G=file_name;A=module_name
		if G is K:I=A.replace(L,'_')+'.pyi';G=H.path+E+I
		else:I=G.split(E)[-1]
		if E in A:A=A.replace(E,L)
		N=K
		try:N=__import__(A,K,K,U);P=J.mem_free();D.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,I,P))
		except S:return B
		f(G)
		with T(G,'w')as O:Q=str(H.info).replace('OrderedDict(',C).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,Q,__version__);O.write(R);O.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n');H.write_object_stub(O,N,A,C)
		H.report_add(A,G)
		if A not in{'os','sys','logging','gc'}:
			try:del N
			except(F,w):D.warning('could not del new_module')
		J.collect();return M
	def write_object_stub(h,fp,object_expr,obj_name,indent,in_class=0):
		A5=' at ...>';A4='{0}{1}: {3} = {2}\n';A3='bound_method';A2='{}*args, **kwargs';x='Incomplete';q='Exception';i=object_expr;g=' at ';f=', ';e='self, ';V=in_class;S=fp;H=indent;J.collect()
		if i in h.problematic:D.warning('SKIPPING problematic module:{}'.format(i));return
		A7,r=h.get_obj_attributes(i)
		if r:D.error(r)
		for(F,N,Q,W,_)in A7:
			if F in['classmethod','staticmethod','BaseException',q]:continue
			if F[0].isdigit():D.warning('NameError: invalid name {}'.format(F));continue
			if Q=="<class 'type'>"and a(H)<=A6*4:
				s=C;t=F.endswith(q)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if t:s=q
				G='\n{}class {}({}):\n'.format(H,F,s)
				if t:G+=H+'    ...\n';S.write(G);continue
				S.write(G);h.write_object_stub(S,W,'{0}.{1}'.format(obj_name,F),H+'    ',V+1);G=H+'    def __init__(self, *argv, **kwargs) -> None:\n';G+=H+'        ...\n\n';S.write(G)
			elif any(A in Q for A in[A1,A0,'closure']):
				j=x;u=C
				if V>0:u=e
				b=B;n=B;v=B
				if c:
					try:b=Y.iscoroutinefunction(W)
					except R:pass
					if not b:
						try:n=d(Y,'isasyncgenfunction',lambda _:B)(W)
						except R:pass
					if not b and not n:
						try:v=Y.isgeneratorfunction(W)
						except R:pass
				T=K
				if c:
					try:
						o=Y.signature(W);A=[];I=B;X=B
						for(L,p)in o.parameters.items():
							P=d(p,'kind',K)
							if P==0:I=M;A.append(L)
							elif P==1:
								if I:A.append(E);I=B
								A.append(L)
							elif P==2:
								if I:A.append(E);I=B
								X=M;A.append(U+L)
							elif P==3:
								if I:A.append(E);I=B
								if not X:A.append(U);X=M
								A.append(L)
							elif P==4:
								if I:A.append(E);I=B
								A.append('**'+L)
							else:A.append(L)
						if I:A.append(E)
						if V>0 and A and A[0]not in(U,E):A=A[1:]
						if V>0:T=e+f.join(A)if A else'self'
						else:T=f.join(A)
					except R:pass
				if T is K:T=A2.format(u)
				if A3 in Q or A3 in N:G='{}@classmethod\n'.format(H)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(H,F,j)
				elif b:G='{}async def {}({}) -> {}:\n'.format(H,F,T,j)
				elif n:G='{}async def {}({}) -> AsyncGenerator:\n'.format(H,F,T)
				elif v:G='{}def {}({}) -> Generator:\n'.format(H,F,T)
				else:G='{}def {}({}) -> {}:\n'.format(H,F,T,j)
				G+=H+'    ...\n\n';S.write(G)
			elif Q=="<class 'module'>":0
			elif Q.startswith("<class '"):
				O=Q[8:-2];G=C
				if O in('str',y,z,'bool','bytearray','bytes'):
					if F.upper()==F:G='{0}{1}: Final[{3}] = {2}\n'.format(H,F,N,O)
					else:G=A4.format(H,F,N,O)
				elif O in(m,l,k):A8={m:'{}',l:'[]',k:'()'};G=A4.format(H,F,A8[O],O)
				elif O in('object','set','frozenset','Pin'):G='{0}{1}: {2} ## = {4}\n'.format(H,F,O,Q,N)
				elif O=='generator':
					A9=e if V>0 else C;Z=K;w=B
					if c:
						try:w=Y.iscoroutinefunction(W)
						except R:pass
						try:
							o=Y.signature(W);A=[];I=B;X=B
							for(L,p)in o.parameters.items():
								P=d(p,'kind',K)
								if P==0:I=M;A.append(L)
								elif P==1:
									if I:A.append(E);I=B
									A.append(L)
								elif P==2:
									if I:A.append(E);I=B
									X=M;A.append(U+L)
								elif P==3:
									if I:A.append(E);I=B
									if not X:A.append(U);X=M
									A.append(L)
								elif P==4:
									if I:A.append(E);I=B
									A.append('**'+L)
								else:A.append(L)
							if I:A.append(E)
							if V>0 and A and A[0]not in(U,E):A=A[1:]
							if V>0:Z=e+f.join(A)if A else'self'
							else:Z=f.join(A)
						except R:pass
					if Z is K:Z=A2.format(A9)
					if w:G='{0}async def {1}({2}) -> Incomplete:\n{0}    ...\n\n'.format(H,F,Z)
					else:G='{0}def {1}({2}) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(H,F,Z,O,N)
				else:
					O=x
					if g in N:N=N.split(g)[0]+A5
					if g in N:N=N.split(g)[0]+A5
					G='{0}{1}: {2} ## {3} = {4}\n'.format(H,F,O,Q,N)
				S.write(G)
			else:S.write("# all other, type = '{0}'\n".format(Q));S.write(H+F+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(B,path=C):
		if not path:path=B.path
		D.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except(F,H):return
		for E in C:
			A='{}/{}'.format(path,E)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report_start(B,filename='modules.json'):
		E='firmware';B._json_name='{}/{}'.format(B.path,filename);B._json_first=M;f(B._json_name);D.info('Report file: {}'.format(B._json_name));J.collect()
		try:
			with T(B._json_name,'w')as C:C.write('{');C.write(dumps({E:B.info})[1:-1]);C.write(n);C.write(dumps({x:{A:__version__},'stubtype':E})[1:-1]);C.write(n);C.write('"modules" :[\n')
		except F as G:D.error(A2);B._json_name=K;raise G
	def report_add(A,module_name,stub_file):
		if not A._json_name:raise R(A3)
		try:
			with T(A._json_name,'a')as C:
				if not A._json_first:C.write(n)
				else:A._json_first=B
				G='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',E));C.write(G)
		except F:D.error(A2)
	def report_end(A):
		if not A._json_name:raise R(A3)
		with T(A._json_name,'a')as B:B.write('\n]}')
		D.info('Path: {}'.format(A.path))
def f(path):
	A=C=0
	while A!=-1:
		A=path.find(E,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except F as G:
				if G.args[0]in[A4,A5]:
					try:D.debug('Create folder {}'.format(B));os.mkdir(B)
					except F as H:D.error('failed to create folder {}'.format(B));raise H
		C=A+1
def g(s):
	B=' on '
	if not s:return C
	s=s.split(B,1)[0]if B in s else s
	if s.startswith('v'):
		if not G in s:return C
		A=s.split(G)[1];return A
	if not e in s:return C
	A=s.split(e)[1].split(L)[1];return A
def A8():
	try:B=sys.implementation[0]
	except i:B=sys.implementation.name
	D=q({b:B,A:C,O:C,'ver':C,N:sys.platform,X:'UNKNOWN',Z:C,o:C,'cpu':C,Q:C,p:C});return D
def A9(info):
	A=info
	if A[N].startswith('pyb'):A[N]='stm32'
	elif A[N]=='win32':A[N]='windows'
	elif A[N]=='linux':A[N]='unix'
def AA(info):
	try:info[A]=AH(sys.implementation.version)
	except H:pass
def AB(info):
	A=info
	try:
		D=sys.implementation._machine if'_machine'in P(sys.implementation)else os.uname().machine;A[X]=D.strip();B=sys.implementation._build if'_build'in P(sys.implementation)else C
		if B:A[X]=B.split(G)[0];A[o]=B.split(G)[1]if G in B else C
		A[Z]=B;A['cpu']=D.split('with')[-1].strip();A[Q]=sys.implementation._mpy if'_mpy'in P(sys.implementation)else sys.implementation.mpy if Q in P(sys.implementation)else C
	except(H,W):pass
	if not A[Z]:AI(A)
def AC(info):
	B=info
	try:
		if'uname'in P(os):
			B[O]=g(os.uname()[3])
			if not B[O]:B[O]=g(os.uname()[2])
		elif A in P(sys):B[O]=g(sys.version)
	except(H,W,i):pass
	if B[A]==C and sys.platform not in('unix','win32'):
		try:D=os.uname();B[A]=D.release
		except(W,H,i):pass
def AD(info):
	D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,K,K,G);A[b]=E;del H;break
		except(S,w):pass
	if A[b]==D:A['release']='2.0.0'
def AE(info):
	B=info
	if B[b]==j:
		if B[A]and B[A].endswith('.0')and B[A]>='1.10.0'and B[A]<='1.19.9':B[A]=B[A][:-2]
def AF(info):
	A=info
	if Q in A and A[Q]:
		B=int(A[Q])
		try:
			C=[K,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[p]=C
		except W:A[p]='unknown'
		A[Q]='v{}.{}'.format(B&255,B>>8&3)
def AG(info):
	B=info
	if B[O]and not B[A].endswith(e):B[A]=B[A]+e
	B['ver']=f"{B[A]}-{B[O]}"if B[O]else f"{B[A]}"
def _info():A=A8();A9(A);AA(A);AB(A);AC(A);AD(A);AE(A);AF(A);AG(A);return A
def AH(version):
	A=version;B=L.join([str(A)for A in A[:3]])
	if a(A)>3 and A[3]:B+=G+A[3]
	return B
def AI(info):
	B=info
	try:from boardname import BOARD_ID as A;D.info('Found BOARD_ID: {}'.format(A))
	except S:D.warning('BOARD_ID not found');A=C
	B[Z]=A;B[X]=A.split(G)[0]if G in A else A;B[o]==A.split(G)[1]if G in A else C
def get_root():
	try:A=os.getcwd()
	except(F,H):A=L
	B=A
	for B in['/remote','/sd','/flash',E,A,L]:
		try:C=os.stat(B);break
		except F:continue
	return B
def r(filename):
	try:
		if os.stat(filename)[0]>>14:return M
		return B
	except F:return B
def s():V("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=C
	if a(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:s()
	elif a(sys.argv)==2:s()
	return path
def t():
	try:A=bytes('abc',encoding='utf8');C=t.__module__;return B
	except(u,H):return M
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	def A(stubber):
		J.collect();stubber.modules=[]
		for C in A7:
			B=C+'/modulelist.txt'
			if not r(B):continue
			with T(B)as D:
				while M:
					A=D.readline().strip()
					if not A:break
					if a(A)>0 and A[0]!='#':stubber.modules.append(A)
				J.collect();V('BREAK');break
		if not stubber.modules:stubber.modules=[j]
		J.collect()
	stubber.modules=[];A(stubber);J.collect();stubber.create_all_stubs()
if __name__=='__main__'or t():
	if not r('no_auto_stubber.txt'):
		V(f"createstubs.py: {__version__}")
		try:J.threshold(4096);J.enable()
		except BaseException:pass
		main()