A6='No report file'
A5='Failed to create the report.'
A4='method'
A3='function'
A2='micropython'
A1='stubber'
A0=KeyError
z=MemoryError
y=NotImplementedError
u='arch'
t='variant'
s=',\n'
r='modules.json'
q='{}/{}'
p='w'
o='dict'
n='list'
m='tuple'
l=TypeError
k=str
j=repr
e='-preview'
d=getattr
b='family'
Z='board_id'
X='board'
a=len
W=IndexError
V=print
T=ImportError
S='mpy'
U='*'
Q=dir
P='build'
O='port'
N='.'
R=Exception
L=open
H=AttributeError
G='-'
M=True
J=None
F=OSError
A='version'
E='/'
C=''
B=False
import gc as K,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except T:pass
try:from collections import OrderedDict as v
except T:from ucollections import OrderedDict as v
try:import inspect as Y;c=M
except T:c=B
__version__='v1.26.4'
A7=2
A8=44
A9=2
AA=['lib','/lib','/sd/lib','/flash/lib',N]
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
D=I.getLogger(A1)
I.basicConfig(level=I.INFO)
class Stubber:
	def __init__(A,path=C,firmware_id=C):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise y('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A.info=_info();D.info('Port: {}'.format(A.info[O]));D.info('Board: {}'.format(A.info[X]));D.info('Board_ID: {}'.format(A.info[Z]));K.collect()
		if C:A._fwid=C.lower()
		elif A.info[b]==A2:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(G)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=K.mem_free()
		if path:
			if path.endswith(E):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',E)
		try:f(path+E)
		except F:D.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=J;A._json_first=B
	def load_exlusions(B):
		try:
			with L('modulelist_exclude.txt','r')as C:
				for E in C:
					A=E.strip()
					if A and A not in B.excluded:B.excluded.append(A);D.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except F:pass
	def get_obj_attributes(L,item_instance):
		G=item_instance;B=[];J=[]
		for A in Q(G):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=d(G,A)
				try:E=j(type(D)).split("'")[1]
				except W:E=C
				if E in{'int','float','str','bool',m,n,o}:F=1
				elif E in{A3,A4}:F=2
				elif E in'class':F=3
				else:F=4
				B.append((A,j(D),j(type(D)),D,F))
			except H as I:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,G,I))
			except z as I:V('MemoryError: {}'.format(I));sleep(1);reset()
		B=sorted([A for A in B if not A[0].startswith('__')],key=lambda x:x[4]);K.collect();return B,J
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		D.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();K.collect()
		for B in A.modules:A.create_one_stub(B)
		A.report_end();D.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:D.warning('Skip module: {:<25}        : Known problematic'.format(A));return B
		if A in C.excluded:D.warning('Skip module: {:<25}        : Excluded'.format(A));return B
		H='{}/{}.pyi'.format(C.path,A.replace(N,E));K.collect();G=B
		try:G=C.create_module_stub(A,H)
		except F:return B
		K.collect();return G
	def create_module_stub(H,module_name,file_name=J):
		G=file_name;A=module_name
		if G is J:I=A.replace(N,'_')+'.pyi';G=H.path+E+I
		else:I=G.split(E)[-1]
		if E in A:A=A.replace(E,N)
		O=J
		try:O=__import__(A,J,J,U);Q=K.mem_free();D.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,I,Q))
		except T:return B
		f(G)
		with L(G,p)as P:R=k(H.info).replace('OrderedDict(',C).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,R,__version__);P.write(S);P.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n');H.write_object_stub(P,O,A,C)
		H.report_add(A,G)
		if A not in{'os','sys','logging','gc'}:
			try:del O
			except(F,A0):D.warning('could not del new_module')
		K.collect();return M
	def write_object_stub(h,fp,object_expr,obj_name,indent,in_class=0):
		A5=' at ...>';A2='{0}{1}: {3} = {2}\n';A1='bound_method';A0='{}*args, **kwargs';z='self';y='kind';x='Incomplete';q='Exception';i=object_expr;g=' at ';f=', ';e='self, ';V=in_class;S=fp;H=indent;K.collect()
		if i in h.problematic:D.warning('SKIPPING problematic module:{}'.format(i));return
		A6,r=h.get_obj_attributes(i)
		if r:D.error(r)
		for(F,N,Q,W,_)in A6:
			if F in['classmethod','staticmethod','BaseException',q]:continue
			if F[0].isdigit():D.warning('NameError: invalid name {}'.format(F));continue
			if Q=="<class 'type'>"and a(H)<=A9*4:
				s=C;t=F.endswith(q)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if t:s=q
				G='\n{}class {}({}):\n'.format(H,F,s)
				if t:G+=H+'    ...\n';S.write(G);continue
				S.write(G);h.write_object_stub(S,W,'{0}.{1}'.format(obj_name,F),H+'    ',V+1);G=H+'    def __init__(self, *argv, **kwargs) -> None:\n';G+=H+'        ...\n\n';S.write(G)
			elif any(A in Q for A in[A4,A3,'closure']):
				j=x;u=C
				if V>0:u=e
				b=B;k=B;v=B
				if c:
					try:b=Y.iscoroutinefunction(W)
					except R:pass
					if not b:
						try:k=d(Y,'isasyncgenfunction',lambda _:B)(W)
						except R:pass
					if not b and not k:
						try:v=Y.isgeneratorfunction(W)
						except R:pass
				T=J
				if c:
					try:
						l=Y.signature(W);A=[];I=B;X=B
						for(L,p)in l.parameters.items():
							P=d(p,y,J)
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
						if V>0:T=e+f.join(A)if A else z
						else:T=f.join(A)
					except R:pass
				if T is J:T=A0.format(u)
				if A1 in Q or A1 in N:G='{}@classmethod\n'.format(H)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(H,F,j)
				elif b:G='{}async def {}({}) -> {}:\n'.format(H,F,T,j)
				elif k:G='{}async def {}({}) -> AsyncGenerator:\n'.format(H,F,T)
				elif v:G='{}def {}({}) -> Generator:\n'.format(H,F,T)
				else:G='{}def {}({}) -> {}:\n'.format(H,F,T,j)
				G+=H+'    ...\n\n';S.write(G)
			elif Q=="<class 'module'>":0
			elif Q.startswith("<class '"):
				O=Q[8:-2];G=C
				if O in('str','int','float','bool','bytearray','bytes'):
					if F.upper()==F:G='{0}{1}: Final[{3}] = {2}\n'.format(H,F,N,O)
					else:G=A2.format(H,F,N,O)
				elif O in(o,n,m):A7={o:'{}',n:'[]',m:'()'};G=A2.format(H,F,A7[O],O)
				elif O in('object','set','frozenset','Pin'):G='{0}{1}: {2} ## = {4}\n'.format(H,F,O,Q,N)
				elif O=='generator':
					A8=e if V>0 else C;Z=J;w=B
					if c:
						try:w=Y.iscoroutinefunction(W)
						except R:pass
						try:
							l=Y.signature(W);A=[];I=B;X=B
							for(L,p)in l.parameters.items():
								P=d(p,y,J)
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
							if V>0:Z=e+f.join(A)if A else z
							else:Z=f.join(A)
						except R:pass
					if Z is J:Z=A0.format(A8)
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
			A=q.format(path,E)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report_start(B,filename=r):
		E='firmware';B._json_name=q.format(B.path,filename);B._json_first=M;f(B._json_name);D.info('Report file: {}'.format(B._json_name));K.collect()
		try:
			with L(B._json_name,p)as C:C.write('{');C.write(dumps({E:B.info})[1:-1]);C.write(s);C.write(dumps({A1:{A:__version__},'stubtype':E})[1:-1]);C.write(s);C.write('"modules" :[\n')
		except F as G:D.error(A5);B._json_name=J;raise G
	def report_add(A,module_name,stub_file):
		if not A._json_name:raise R(A6)
		try:
			with L(A._json_name,'a')as C:
				if not A._json_first:C.write(s)
				else:A._json_first=B
				G='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',E));C.write(G)
		except F:D.error(A5)
	def report_end(A):
		if not A._json_name:raise R(A6)
		with L(A._json_name,'a')as B:B.write('\n]}')
		D.info('Path: {}'.format(A.path))
def f(path):
	A=C=0
	while A!=-1:
		A=path.find(E,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except F as G:
				if G.args[0]in[A7,A8]:
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
	A=s.split(e)[1].split(N)[1];return A
def AB():
	try:B=sys.implementation[0]
	except l:B=sys.implementation.name
	D=v({b:B,A:C,P:C,'ver':C,O:sys.platform,X:'UNKNOWN',Z:C,t:C,'cpu':C,S:C,u:C});return D
def AC(info):
	A=info
	if A[O].startswith('pyb'):A[O]='stm32'
	elif A[O]=='win32':A[O]='windows'
	elif A[O]=='linux':A[O]='unix'
def AD(info):
	try:info[A]=AK(sys.implementation.version)
	except H:pass
def AE(info):
	A=info
	try:
		D=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[X]=D.strip();B=sys.implementation._build if'_build'in Q(sys.implementation)else C
		if B:A[X]=B.split(G)[0];A[t]=B.split(G)[1]if G in B else C
		A[Z]=B;A['cpu']=D.split('with')[-1].strip();A[S]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if S in Q(sys.implementation)else C
	except(H,W):pass
	if not A[Z]:AL(A)
def AF(info):
	B=info
	try:
		if'uname'in Q(os):
			B[P]=g(os.uname()[3])
			if not B[P]:B[P]=g(os.uname()[2])
		elif A in Q(sys):B[P]=g(sys.version)
	except(H,W,l):pass
	if B[A]==C and sys.platform not in('unix','win32'):
		try:D=os.uname();B[A]=D.release
		except(W,H,l):pass
def AG(info):
	D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,J,J,G);A[b]=E;del H;break
		except(T,A0):pass
	if A[b]==D:A['release']='2.0.0'
def AH(info):
	B=info
	if B[b]==A2:
		if B[A]and B[A].endswith('.0')and B[A]>='1.10.0'and B[A]<='1.19.9':B[A]=B[A][:-2]
def AI(info):
	A=info
	if S in A and A[S]:
		B=int(A[S])
		try:
			C=[J,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[u]=C
		except W:A[u]='unknown'
		A[S]='v{}.{}'.format(B&255,B>>8&3)
def AJ(info):
	B=info
	if B[P]and not B[A].endswith(e):B[A]=B[A]+e
	B['ver']=f"{B[A]}-{B[P]}"if B[P]else f"{B[A]}"
def _info():A=AB();AC(A);AD(A);AE(A);AF(A);AG(A);AH(A);AI(A);AJ(A);return A
def AK(version):
	A=version;B=N.join([k(A)for A in A[:3]])
	if a(A)>3 and A[3]:B+=G+A[3]
	return B
def AL(info):
	B=info
	try:from boardname import BOARD_ID as A;D.info('Found BOARD_ID: {}'.format(A))
	except T:D.warning('BOARD_ID not found');A=C
	B[Z]=A;B[X]=A.split(G)[0]if G in A else A;B[t]==A.split(G)[1]if G in A else C
def get_root():
	try:A=os.getcwd()
	except(F,H):A=N
	B=A
	for B in['/remote','/sd','/flash',E,A,N]:
		try:C=os.stat(B);break
		except F:continue
	return B
def h(filename):
	try:
		if os.stat(filename)[0]>>14:return M
		return B
	except F:return B
def w():V("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=C
	if a(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:w()
	elif a(sys.argv)==2:w()
	return path
def x():
	try:A=bytes('abc',encoding='utf8');C=x.__module__;return B
	except(y,H):return M
i='modulelist.done'
def AM(skip=0):
	for D in AA:
		B=D+'/modulelist.txt'
		if not h(B):continue
		try:
			with L(B,encoding='utf-8')as E:
				C=0
				while M:
					A=E.readline().strip()
					if not A:break
					if a(A)>0 and A[0]=='#':continue
					C+=1
					if C<skip:continue
					yield A
				break
		except F:pass
def AN(done):
	with L(i,p)as A:A.write(k(done)+'\n')
def AO():
	A=0
	try:
		with L(i)as B:A=int(B.readline().strip())
	except F:pass
	return A
def main():
	import machine as C;B=h(i)
	if B:D.info('Continue from last run')
	else:D.info('Starting new run')
	stubber=Stubber(path=read_path());A=0
	if not B:stubber.clean();stubber.report_start(r)
	else:A=AO();stubber._json_name=q.format(stubber.path,r)
	for E in AM(A):
		try:stubber.create_one_stub(E)
		except z:C.reset()
		K.collect();A+=1;AN(A)
	V('All modules have been processed, Finalizing report');stubber.report_end()
if __name__=='__main__'or x():
	if not h('no_auto_stubber.txt'):
		V(f"createstubs.py: {__version__}")
		try:K.threshold(4096);K.enable()
		except BaseException:pass
		main()