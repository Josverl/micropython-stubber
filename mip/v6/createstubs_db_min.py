A6='No report file'
A5='Failed to create the report.'
A4='method'
A3='function'
A2='micropython'
A1='stubber'
A0=KeyError
z=sorted
y=MemoryError
x=NotImplementedError
t='arch'
s='variant'
r=',\n'
q='modules.json'
p='{}/{}'
o='w'
n='dict'
m='list'
l='tuple'
k=TypeError
j=str
i=repr
h=getattr
b='-preview'
Z='family'
Y='board_id'
X='board'
W=len
V=IndexError
U=print
T=True
S=Exception
R=ImportError
Q='mpy'
P=dir
O='build'
N='port'
M='.'
L=open
J=AttributeError
I='/'
E='-'
H=None
F=False
D=OSError
C='version'
A=''
import gc as G,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except R:pass
try:from collections import OrderedDict as u
except R:from ucollections import OrderedDict as u
try:import inspect as a;c=T
except R:c=F
__version__='v1.26.4'
A7=2
A8=44
A9=2
AA=['lib','/lib','/sd/lib','/flash/lib',M]
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
B=K.getLogger(A1)
K.basicConfig(level=K.INFO)
class Stubber:
	def __init__(A,path=A,firmware_id=A):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise x('MicroPython 1.13.0 cannot be stubbed')
		except J:pass
		A.info=_info();B.info('Port: {}'.format(A.info[N]));B.info('Board: {}'.format(A.info[X]));B.info('Board_ID: {}'.format(A.info[Y]));G.collect()
		if C:A._fwid=C.lower()
		elif A.info[Z]==A2:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(E)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=G.mem_free()
		if path:
			if path.endswith(I):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',I)
		try:d(path+I)
		except D:B.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=H;A._json_first=F
	def load_exlusions(C):
		try:
			with L('modulelist_exclude.txt','r')as E:
				for F in E:
					A=F.strip()
					if A and A not in C.excluded:C.excluded.append(A);B.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except D:pass
	def get_obj_attributes(L,item_instance):
		H=item_instance;C=[];K=[]
		for B in P(H):
			if B.startswith('__')and not B in L.modules:continue
			try:
				D=h(H,B)
				try:E=i(type(D)).split("'")[1]
				except V:E=A
				if E in{'int','float','str','bool',l,m,n}:F=1
				elif E in{A3,A4}:F=2
				elif E in'class':F=3
				else:F=4
				C.append((B,i(D),i(type(D)),D,F))
			except J as I:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(B,H,I))
			except y as I:U('MemoryError: {}'.format(I));sleep(1);reset()
		C=z([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);G.collect();return C,K
	def add_modules(A,modules):A.modules=z(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();G.collect()
		for C in A.modules:A.create_one_stub(C)
		A.report_end();B.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:B.warning('Skip module: {:<25}        : Known problematic'.format(A));return F
		if A in C.excluded:B.warning('Skip module: {:<25}        : Excluded'.format(A));return F
		H='{}/{}.pyi'.format(C.path,A.replace(M,I));G.collect();E=F
		try:E=C.create_module_stub(A,H)
		except D:return F
		G.collect();return E
	def create_module_stub(J,module_name,file_name=H):
		E=file_name;C=module_name
		if E is H:K=C.replace(M,'_')+'.pyi';E=J.path+I+K
		else:K=E.split(I)[-1]
		if I in C:C=C.replace(I,M)
		N=H
		try:N=__import__(C,H,H,'*');P=G.mem_free();B.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(C,K,P))
		except R:return F
		d(E)
		with L(E,o)as O:Q=j(J.info).replace('OrderedDict(',A).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,J._fwid,Q,__version__);O.write(S);O.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(O,N,C,A)
		J.report_add(C,E)
		if C not in{'os','sys','logging','gc'}:
			try:del N
			except(D,A0):B.warning('could not del new_module')
		G.collect();return T
	def write_object_stub(T,fp,object_expr,obj_name,indent,in_class=0):
		r=' at ...>';q='{0}{1}: {3} = {2}\n';p='bound_method';o='self';k='self, ';j='Incomplete';Z='Exception';U=object_expr;R=' at ';P=in_class;M=fp;E=indent;G.collect()
		if U in T.problematic:B.warning('SKIPPING problematic module:{}'.format(U));return
		s,b=T.get_obj_attributes(U)
		if b:B.error(b)
		for(C,J,K,O,w)in s:
			if C in['classmethod','staticmethod','BaseException',Z]:continue
			if C[0].isdigit():B.warning('NameError: invalid name {}'.format(C));continue
			if K=="<class 'type'>"and W(E)<=A9*4:
				d=A;e=C.endswith(Z)or C.endswith('Error')or C in['KeyboardInterrupt','StopIteration','SystemExit']
				if e:d=Z
				D='\n{}class {}({}):\n'.format(E,C,d)
				if e:D+=E+'    ...\n';M.write(D);continue
				M.write(D);T.write_object_stub(M,O,'{0}.{1}'.format(obj_name,C),E+'    ',P+1);D=E+'    def __init__(self, *argv, **kwargs) -> None:\n';D+=E+'        ...\n\n';M.write(D)
			elif any(A in K for A in[A4,A3,'closure']):
				V=j;f=A
				if P>0:f=k
				Q=F;X=F;g=F
				if c:
					try:Q=a.iscoroutinefunction(O)
					except S:pass
					if not Q:
						try:X=h(a,'isasyncgenfunction',lambda _:F)(O)
						except S:pass
					if not Q and not X:
						try:g=a.isgeneratorfunction(O)
						except S:pass
				N=H
				if c:
					try:
						t=a.signature(O);L=[]
						for(Y,u)in t.parameters.items():
							i=h(u,'kind',H)
							if i==2:L.append('*'+Y)
							elif i==4:L.append('**'+Y)
							else:L.append(Y)
						if P>0 and L and L[0]in(o,'cls'):L=L[1:]
						if P>0:N=k+', '.join(L)if L else o
						else:N=', '.join(L)
					except S:pass
				if N is H:N='{}*args, **kwargs'.format(f)
				if p in K or p in J:D='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,C,V)
				elif Q:D='{}async def {}({}) -> {}:\n'.format(E,C,N,V)
				elif X:D='{}async def {}({}) -> AsyncGenerator:\n'.format(E,C,N)
				elif g:D='{}def {}({}) -> Generator:\n'.format(E,C,N)
				else:D='{}def {}({}) -> {}:\n'.format(E,C,N,V)
				D+=E+'    ...\n\n';M.write(D)
			elif K=="<class 'module'>":0
			elif K.startswith("<class '"):
				I=K[8:-2];D=A
				if I in('str','int','float','bool','bytearray','bytes'):
					if C.upper()==C:D='{0}{1}: Final[{3}] = {2}\n'.format(E,C,J,I)
					else:D=q.format(E,C,J,I)
				elif I in(n,m,l):v={n:'{}',m:'[]',l:'()'};D=q.format(E,C,v[I],I)
				elif I in('object','set','frozenset','Pin'):D='{0}{1}: {2} ## = {4}\n'.format(E,C,I,K,J)
				elif I=='generator':I='Generator';D='{0}def {1}(*args, **kwargs) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(E,C,I,K,J)
				else:
					I=j
					if R in J:J=J.split(R)[0]+r
					if R in J:J=J.split(R)[0]+r
					D='{0}{1}: {2} ## {3} = {4}\n'.format(E,C,I,K,J)
				M.write(D)
			else:M.write("# all other, type = '{0}'\n".format(K));M.write(E+C+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(C,path=A):
		if not path:path=C.path
		B.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except(D,J):return
		for F in E:
			A=p.format(path,F)
			try:os.remove(A)
			except D:
				try:C.clean(A);os.rmdir(A)
				except D:pass
	def report_start(A,filename=q):
		F='firmware';A._json_name=p.format(A.path,filename);A._json_first=T;d(A._json_name);B.info('Report file: {}'.format(A._json_name));G.collect()
		try:
			with L(A._json_name,o)as E:E.write('{');E.write(dumps({F:A.info})[1:-1]);E.write(r);E.write(dumps({A1:{C:__version__},'stubtype':F})[1:-1]);E.write(r);E.write('"modules" :[\n')
		except D as I:B.error(A5);A._json_name=H;raise I
	def report_add(A,module_name,stub_file):
		if not A._json_name:raise S(A6)
		try:
			with L(A._json_name,'a')as C:
				if not A._json_first:C.write(r)
				else:A._json_first=F
				E='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',I));C.write(E)
		except D:B.error(A5)
	def report_end(A):
		if not A._json_name:raise S(A6)
		with L(A._json_name,'a')as C:C.write('\n]}')
		B.info('Path: {}'.format(A.path))
def d(path):
	A=E=0
	while A!=-1:
		A=path.find(I,E)
		if A!=-1:
			C=path[0]if A==0 else path[:A]
			try:H=os.stat(C)
			except D as F:
				if F.args[0]in[A7,A8]:
					try:B.debug('Create folder {}'.format(C));os.mkdir(C)
					except D as G:B.error('failed to create folder {}'.format(C));raise G
		E=A+1
def e(s):
	C=' on '
	if not s:return A
	s=s.split(C,1)[0]if C in s else s
	if s.startswith('v'):
		if not E in s:return A
		B=s.split(E)[1];return B
	if not b in s:return A
	B=s.split(b)[1].split(M)[1];return B
def AB():
	try:B=sys.implementation[0]
	except k:B=sys.implementation.name
	D=u({Z:B,C:A,O:A,'ver':A,N:sys.platform,X:'UNKNOWN',Y:A,s:A,'cpu':A,Q:A,t:A});return D
def AC(info):
	A=info
	if A[N].startswith('pyb'):A[N]='stm32'
	elif A[N]=='win32':A[N]='windows'
	elif A[N]=='linux':A[N]='unix'
def AD(info):
	try:info[C]=AK(sys.implementation.version)
	except J:pass
def AE(info):
	B=info
	try:
		D=sys.implementation._machine if'_machine'in P(sys.implementation)else os.uname().machine;B[X]=D.strip();C=sys.implementation._build if'_build'in P(sys.implementation)else A
		if C:B[X]=C.split(E)[0];B[s]=C.split(E)[1]if E in C else A
		B[Y]=C;B['cpu']=D.split('with')[-1].strip();B[Q]=sys.implementation._mpy if'_mpy'in P(sys.implementation)else sys.implementation.mpy if Q in P(sys.implementation)else A
	except(J,V):pass
	if not B[Y]:AL(B)
def AF(info):
	B=info
	try:
		if'uname'in P(os):
			B[O]=e(os.uname()[3])
			if not B[O]:B[O]=e(os.uname()[2])
		elif C in P(sys):B[O]=e(sys.version)
	except(J,V,k):pass
	if B[C]==A and sys.platform not in('unix','win32'):
		try:D=os.uname();B[C]=D.release
		except(V,J,k):pass
def AG(info):
	D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:I=__import__(F,H,H,G);A[Z]=E;del I;break
		except(R,A0):pass
	if A[Z]==D:A['release']='2.0.0'
def AH(info):
	A=info
	if A[Z]==A2:
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
def AI(info):
	A=info
	if Q in A and A[Q]:
		B=int(A[Q])
		try:
			C=[H,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[t]=C
		except V:A[t]='unknown'
		A[Q]='v{}.{}'.format(B&255,B>>8&3)
def AJ(info):
	A=info
	if A[O]and not A[C].endswith(b):A[C]=A[C]+b
	A['ver']=f"{A[C]}-{A[O]}"if A[O]else f"{A[C]}"
def _info():A=AB();AC(A);AD(A);AE(A);AF(A);AG(A);AH(A);AI(A);AJ(A);return A
def AK(version):
	A=version;B=M.join([j(A)for A in A[:3]])
	if W(A)>3 and A[3]:B+=E+A[3]
	return B
def AL(info):
	D=info
	try:from boardname import BOARD_ID as C;B.info('Found BOARD_ID: {}'.format(C))
	except R:B.warning('BOARD_ID not found');C=A
	D[Y]=C;D[X]=C.split(E)[0]if E in C else C;D[s]==C.split(E)[1]if E in C else A
def get_root():
	try:A=os.getcwd()
	except(D,J):A=M
	B=A
	for B in['/remote','/sd','/flash',I,A,M]:
		try:C=os.stat(B);break
		except D:continue
	return B
def f(filename):
	try:
		if os.stat(filename)[0]>>14:return T
		return F
	except D:return F
def v():U("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	path=A
	if W(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):path=sys.argv[2]
		else:v()
	elif W(sys.argv)==2:v()
	return path
def w():
	try:A=bytes('abc',encoding='utf8');B=w.__module__;return F
	except(x,J):return T
g='modulelist.done'
def AM(skip=0):
	for E in AA:
		B=E+'/modulelist.txt'
		if not f(B):continue
		try:
			with L(B,encoding='utf-8')as F:
				C=0
				while T:
					A=F.readline().strip()
					if not A:break
					if W(A)>0 and A[0]=='#':continue
					C+=1
					if C<skip:continue
					yield A
				break
		except D:pass
def AN(done):
	with L(g,o)as A:A.write(j(done)+'\n')
def AO():
	A=0
	try:
		with L(g)as B:A=int(B.readline().strip())
	except D:pass
	return A
def main():
	import machine as D;C=f(g)
	if C:B.info('Continue from last run')
	else:B.info('Starting new run')
	stubber=Stubber(path=read_path());A=0
	if not C:stubber.clean();stubber.report_start(q)
	else:A=AO();stubber._json_name=p.format(stubber.path,q)
	for E in AM(A):
		try:stubber.create_one_stub(E)
		except y:D.reset()
		G.collect();A+=1;AN(A)
	U('All modules have been processed, Finalizing report');stubber.report_end()
if __name__=='__main__'or w():
	if not f('no_auto_stubber.txt'):
		U(f"createstubs.py: {__version__}")
		try:G.threshold(4096);G.enable()
		except BaseException:pass
		main()