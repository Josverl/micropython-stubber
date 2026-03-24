'\nCreate stubs for (all) modules on a MicroPython board.\n\n    This variant of the createstubs.py script is optimized for use on very-low-memory devices.\n    Note: this version has undergone limited testing.\n\n    1) reads the list of modules from a text file `modulelist.txt` that should be uploaded to the device.\n    2) stored the already processed modules in a text file `modulelist.done`\n    3) process the modules in the database:\n        - stub the module\n        - update the modulelist.done file\n        - reboots the device if it runs out of memory\n    4) creates the modules.json\n\n    If that cannot be found then only a single module (micropython) is stubbed.\n    In order to run this on low-memory devices two additional steps are recommended:\n    - minification, using python-minifierto reduce overall size, and remove logging overhead.\n    - cross compilation, using mpy-cross, to avoid the compilation step on the micropython device\n\n\nThis variant was generated from createstubs.py by micropython-stubber v1.26.5\n'
A8='No report file'
A7='Failed to create the report.'
A6='method'
A5='function'
A4='micropython'
A3='stubber'
A2=isinstance
A1=KeyError
A0=MemoryError
z=NotImplementedError
v='arch'
u='variant'
t=',\n'
s='modules.json'
r='{}/{}'
q='w'
p='dict'
o='list'
n='tuple'
m=TypeError
l=repr
g='-preview'
f=getattr
d='\n'
a='family'
Y='board_id'
X='board'
c=len
b=str
V=IndexError
U=print
T=ImportError
S='mpy'
W='*'
Q=dir
P='build'
O='port'
M='.'
L=open
H=AttributeError
R=Exception
G='-'
N=True
J=None
E=OSError
A='version'
F='/'
C=''
B=False
import gc as K,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except T:pass
try:from collections import OrderedDict as w
except T:from ucollections import OrderedDict as w
try:import inspect as Z;e=N
except T:e=B
__version__='v1.26.5a0'
A9=2
AA=44
AB=2
AC=['lib','/lib','/sd/lib','/flash/lib',M]
class I:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=U
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
D=I.getLogger(A3)
I.basicConfig(level=I.INFO)
class Stubber:
	'Generate stubs for modules in firmware'
	def __init__(A,path=C,firmware_id=C):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise z('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A.info=_info();D.info('Port: {}'.format(A.info[O]));D.info('Board: {}'.format(A.info[X]));D.info('Board_ID: {}'.format(A.info[Y]));K.collect()
		if C:A._fwid=C.lower()
		elif A.info[a]==A4:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(G)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=K.mem_free()
		if path:
			if path.endswith(F):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',F)
		try:h(path+F)
		except E:D.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=J;A._json_first=B
	def load_exlusions(B):
		try:
			with L('modulelist_exclude.txt','r')as C:
				for F in C:
					A=F.strip()
					if A and A not in B.excluded:B.excluded.append(A);D.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except E:pass
	def get_obj_attributes(L,item_instance):
		'extract information of the objects members and attributes';G=item_instance;B=[];J=[]
		for A in Q(G):
			if A.startswith('__')and not A in L.modules:continue
			try:
				D=f(G,A)
				try:E=l(type(D)).split("'")[1]
				except V:E=C
				if E in{'int','float','str','bool',n,o,p}:F=1
				elif E in{A5,A6}:F=2
				elif E in'class':F=3
				else:F=4
				B.append((A,l(D),l(type(D)),D,F))
			except H as I:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,G,I))
			except A0 as I:U('MemoryError: {}'.format(I));sleep(1);reset()
		B=sorted([A for A in B if not A[0].startswith('__')],key=lambda x:x[4]);K.collect();return B,J
	def add_modules(A,modules):'Add additional modules to be exported';A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		'Create stubs for all configured modules';D.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();K.collect()
		for B in A.modules:A.create_one_stub(B)
		A.report_end();D.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:D.warning('Skip module: {:<25}        : Known problematic'.format(A));return B
		if A in C.excluded:D.warning('Skip module: {:<25}        : Excluded'.format(A));return B
		H='{}/{}.pyi'.format(C.path,A.replace(M,F));K.collect();G=B
		try:G=C.create_module_stub(A,H)
		except E:return B
		K.collect();return G
	def create_module_stub(H,module_name,file_name=J):
		"Create a Stub of a single python module\n\n        Args:\n        - module_name (str): name of the module to document. This module will be imported.\n        - file_name (Optional[str]): the 'path/filename.pyi' to write to. If omitted will be created based on the module name.\n        ";G=file_name;A=module_name
		if G is J:I=A.replace(M,'_')+'.pyi';G=H.path+F+I
		else:I=G.split(F)[-1]
		if F in A:A=A.replace(F,M)
		O=J
		try:O=__import__(A,J,J,W);Q=K.mem_free();D.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,I,Q))
		except T:return B
		h(G)
		with L(G,q)as P:R=b(H.info).replace('OrderedDict(',C).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,R,__version__);P.write(S);P.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n');H.write_object_stub(P,O,A,C)
		H.report_add(A,G)
		if A not in{'os','sys','logging','gc'}:
			try:del O
			except(E,A1):D.warning('could not del new_module')
		K.collect();return N
	def write_object_stub(k,fp,object_expr,obj_name,indent,in_class=0):
		'Write a module/object stub to an open file. Can be called recursive.';AA=' at ...>';A9='{0}{1}: {3} = {2}\n';A8='bound_method';A7='{}*args, **kwargs';A4='Incomplete';A3='    """{0}"""\n';A1='\\"\\"\\"';u='    ';t='Exception';l=object_expr;j=' at ';i=', ';h='self, ';X=in_class;S=fp;E=indent;K.collect()
		if l in k.problematic:D.warning('SKIPPING problematic module:{}'.format(l));return
		AC,v=k.get_obj_attributes(l)
		if v:D.error(v)
		for(G,O,T,U,_)in AC:
			if G in['classmethod','staticmethod','BaseException',t]:continue
			if G[0].isdigit():D.warning('NameError: invalid name {}'.format(G));continue
			if T=="<class 'type'>"and c(E)<=AB*4:
				w=C;x=G.endswith(t)or G.endswith('Error')or G in['KeyboardInterrupt','StopIteration','SystemExit']
				if x:w=t
				H='\n{}class {}({}):\n'.format(E,G,w)
				if x:H+=E+'    ...\n';S.write(H);continue
				S.write(H)
				try:
					L=U.__doc__
					if L and A2(L,b):
						L=L.strip().replace('"""',A1).replace(d,d+E+u)
						if L:S.write(E+A3.format(L))
				except R:pass
				k.write_object_stub(S,U,'{0}.{1}'.format(obj_name,G),E+u,X+1);H=E+'    def __init__(self, *argv, **kwargs) -> None:\n';H+=E+'        ...\n\n';S.write(H)
			elif any(A in T for A in[A6,A5,'closure']):
				m=A4;y=C
				if X>0:y=h
				g=B;q=B;z=B
				if e:
					try:g=Z.iscoroutinefunction(U)
					except R:pass
					if not g:
						try:q=f(Z,'isasyncgenfunction',lambda _:B)(U)
						except R:pass
					if not g and not q:
						try:z=Z.isgeneratorfunction(U)
						except R:pass
				V=J
				if e:
					try:
						r=Z.signature(U);A=[];I=B;Y=B
						for(M,s)in r.parameters.items():
							Q=f(s,'kind',J)
							if Q==0:I=N;A.append(M)
							elif Q==1:
								if I:A.append(F);I=B
								A.append(M)
							elif Q==2:
								if I:A.append(F);I=B
								Y=N;A.append(W+M)
							elif Q==3:
								if I:A.append(F);I=B
								if not Y:A.append(W);Y=N
								A.append(M)
							elif Q==4:
								if I:A.append(F);I=B
								A.append('**'+M)
							else:A.append(M)
						if I:A.append(F)
						if X>0 and A and A[0]not in(W,F):A=A[1:]
						if X>0:V=h+i.join(A)if A else'self'
						else:V=i.join(A)
					except R:pass
				if V is J:V=A7.format(y)
				if A8 in T or A8 in O:H='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,G,m)
				elif g:H='{}async def {}({}) -> {}:\n'.format(E,G,V,m)
				elif q:H='{}async def {}({}) -> AsyncGenerator:\n'.format(E,G,V)
				elif z:H='{}def {}({}) -> Generator:\n'.format(E,G,V)
				else:H='{}def {}({}) -> {}:\n'.format(E,G,V,m)
				try:
					L=U.__doc__
					if L and A2(L,b):
						L=L.strip().replace('"""',A1).replace(d,d+E+u)
						if L:H+=E+A3.format(L)
				except R:pass
				H+=E+'    ...\n\n';S.write(H)
			elif T=="<class 'module'>":0
			elif T.startswith("<class '"):
				P=T[8:-2];H=C
				if P in('str','int','float','bool','bytearray','bytes'):
					if G.upper()==G:H='{0}{1}: Final[{3}] = {2}\n'.format(E,G,O,P)
					else:H=A9.format(E,G,O,P)
				elif P in(p,o,n):AD={p:'{}',o:'[]',n:'()'};H=A9.format(E,G,AD[P],P)
				elif P in('object','set','frozenset','Pin'):H='{0}{1}: {2} ## = {4}\n'.format(E,G,P,T,O)
				elif P=='generator':
					AE=h if X>0 else C;a=J;A0=B
					if e:
						try:A0=Z.iscoroutinefunction(U)
						except R:pass
						try:
							r=Z.signature(U);A=[];I=B;Y=B
							for(M,s)in r.parameters.items():
								Q=f(s,'kind',J)
								if Q==0:I=N;A.append(M)
								elif Q==1:
									if I:A.append(F);I=B
									A.append(M)
								elif Q==2:
									if I:A.append(F);I=B
									Y=N;A.append(W+M)
								elif Q==3:
									if I:A.append(F);I=B
									if not Y:A.append(W);Y=N
									A.append(M)
								elif Q==4:
									if I:A.append(F);I=B
									A.append('**'+M)
								else:A.append(M)
							if I:A.append(F)
							if X>0 and A and A[0]not in(W,F):A=A[1:]
							if X>0:a=h+i.join(A)if A else'self'
							else:a=i.join(A)
						except R:pass
					if a is J:a=A7.format(AE)
					if A0:H='{0}async def {1}({2}) -> Incomplete:\n{0}    ...\n\n'.format(E,G,a)
					else:H='{0}def {1}({2}) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(E,G,a,P,O)
				else:
					P=A4
					if j in O:O=O.split(j)[0]+AA
					if j in O:O=O.split(j)[0]+AA
					H='{0}{1}: {2} ## {3} = {4}\n'.format(E,G,P,T,O)
				S.write(H)
			else:S.write("# all other, type = '{0}'\n".format(T));S.write(E+G+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		"Turn _fwid from 'v1.2.3' into '1_2_3' to be used in filename";A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(B,path=C):
		'Remove all files from the stub folder'
		if not path:path=B.path
		D.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except(E,H):return
		for F in C:
			A=r.format(path,F)
			try:os.remove(A)
			except E:
				try:B.clean(A);os.rmdir(A)
				except E:pass
	def report_start(B,filename=s):
		'Start a report of the modules that have been stubbed\n        "create json with list of exported modules';F='firmware';B._json_name=r.format(B.path,filename);B._json_first=N;h(B._json_name);D.info('Report file: {}'.format(B._json_name));K.collect()
		try:
			with L(B._json_name,q)as C:C.write('{');C.write(dumps({F:B.info})[1:-1]);C.write(t);C.write(dumps({A3:{A:__version__},'stubtype':F})[1:-1]);C.write(t);C.write('"modules" :[\n')
		except E as G:D.error(A7);B._json_name=J;raise G
	def report_add(A,module_name,stub_file):
		'Add a module to the report'
		if not A._json_name:raise R(A8)
		try:
			with L(A._json_name,'a')as C:
				if not A._json_first:C.write(t)
				else:A._json_first=B
				G='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',F));C.write(G)
		except E:D.error(A7)
	def report_end(A):
		if not A._json_name:raise R(A8)
		with L(A._json_name,'a')as B:B.write('\n]}')
		D.info('Path: {}'.format(A.path))
def h(path):
	'Create nested folders if needed';A=C=0
	while A!=-1:
		A=path.find(F,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except E as G:
				if G.args[0]in[A9,AA]:
					try:D.debug('Create folder {}'.format(B));os.mkdir(B)
					except E as H:D.error('failed to create folder {}'.format(B));raise H
		C=A+1
def i(s):
	B=' on '
	if not s:return C
	s=s.split(B,1)[0]if B in s else s
	if s.startswith('v'):
		if not G in s:return C
		A=s.split(G)[1];return A
	if not g in s:return C
	A=s.split(g)[1].split(M)[1];return A
def AD():
	'Get basic system implementation details.'
	try:B=sys.implementation[0]
	except m:B=sys.implementation.name
	D=w({a:B,A:C,P:C,'ver':C,O:sys.platform,X:'UNKNOWN',Y:C,u:C,'cpu':C,S:C,v:C});return D
def AE(info):
	'Normalize port names to be consistent with the repo.';A=info
	if A[O].startswith('pyb'):A[O]='stm32'
	elif A[O]=='win32':A[O]='windows'
	elif A[O]=='linux':A[O]='unix'
def AF(info):
	'Extract version information from sys.implementation.'
	try:info[A]=AM(sys.implementation.version)
	except H:pass
def AG(info):
	'Extract board, CPU, and machine details.';A=info
	try:
		D=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[X]=D.strip();B=sys.implementation._build if'_build'in Q(sys.implementation)else C
		if B:A[X]=B.split(G)[0];A[u]=B.split(G)[1]if G in B else C
		A[Y]=B;A['cpu']=D.split('with')[-1].strip();A[S]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if S in Q(sys.implementation)else C
	except(H,V):pass
	if not A[Y]:AN(A)
def AH(info):
	'Extract build information from various system sources.';B=info
	try:
		if'uname'in Q(os):
			B[P]=i(os.uname()[3])
			if not B[P]:B[P]=i(os.uname()[2])
		elif A in Q(sys):B[P]=i(sys.version)
	except(H,V,m):pass
	if B[A]==C and sys.platform not in('unix','win32'):
		try:D=os.uname();B[A]=D.release
		except(V,H,m):pass
def AI(info):
	'Detect special firmware families (pycopy, pycom, ev3-pybricks).';D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,J,J,G);A[a]=E;del H;break
		except(T,A1):pass
	if A[a]==D:A['release']='2.0.0'
def AJ(info):
	'Process MicroPython-specific version formatting.';B=info
	if B[a]==A4:
		if B[A]and B[A].endswith('.0')and B[A]>='1.10.0'and B[A]<='1.19.9':B[A]=B[A][:-2]
def AK(info):
	'Process MPY architecture and version information.';A=info
	if S in A and A[S]:
		B=int(A[S])
		try:
			C=[J,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[v]=C
		except V:A[v]='unknown'
		A[S]='v{}.{}'.format(B&255,B>>8&3)
def AL(info):
	'Handle final version string formatting.';B=info
	if B[P]and not B[A].endswith(g):B[A]=B[A]+g
	B['ver']=f"{B[A]}-{B[P]}"if B[P]else f"{B[A]}"
def _info():'\n    Gather comprehensive system information for MicroPython stubbing.\n\n    Returns a dictionary containing family, version, port, board, and other\n    system details needed for stub generation.\n    ';A=AD();AE(A);AF(A);AG(A);AH(A);AI(A);AJ(A);AK(A);AL(A);return A
def AM(version):
	A=version;B=M.join([b(A)for A in A[:3]])
	if c(A)>3 and A[3]:B+=G+A[3]
	return B
def AN(info):
	'Read the board_id from the boardname.py file that may have been created upfront';B=info
	try:from boardname import BOARD_ID as A;D.info('Found BOARD_ID: {}'.format(A))
	except T:D.warning('BOARD_ID not found');A=C
	B[Y]=A;B[X]=A.split(G)[0]if G in A else A;B[u]==A.split(G)[1]if G in A else C
def get_root():
	'Determine the root folder of the device'
	try:A=os.getcwd()
	except(E,H):A=M
	B=A
	for B in['/remote','/sd','/flash',F,A,M]:
		try:C=os.stat(B);break
		except E:continue
	return B
def j(filename):
	try:
		if os.stat(filename)[0]>>14:return N
		return B
	except E:return B
def x():U("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	'get --path from cmdline. [unix/win]';path=C
	if c(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:x()
	elif c(sys.argv)==2:x()
	return path
def y():
	'runtime test to determine full or micropython'
	try:A=bytes('abc',encoding='utf8');C=y.__module__;return B
	except(z,H):return N
k='modulelist.done'
def AO(skip=0):
	for D in AC:
		B=D+'/modulelist.txt'
		if not j(B):continue
		try:
			with L(B,encoding='utf-8')as F:
				C=0
				while N:
					A=F.readline().strip()
					if not A:break
					if c(A)>0 and A[0]=='#':continue
					C+=1
					if C<skip:continue
					yield A
				break
		except E:pass
def AP(done):
	with L(k,q)as A:A.write(b(done)+d)
def AQ():
	A=0
	try:
		with L(k)as B:A=int(B.readline().strip())
	except E:pass
	return A
def main():
	import machine as C;B=j(k)
	if B:D.info('Continue from last run')
	else:D.info('Starting new run')
	stubber=Stubber(path=read_path());A=0
	if not B:stubber.clean();stubber.report_start(s)
	else:A=AQ();stubber._json_name=r.format(stubber.path,s)
	for E in AO(A):
		try:stubber.create_one_stub(E)
		except A0:C.reset()
		K.collect();A+=1;AP(A)
	U('All modules have been processed, Finalizing report');stubber.report_end()
if __name__=='__main__'or y():
	if not j('no_auto_stubber.txt'):
		U(f"createstubs.py: {__version__}")
		try:K.threshold(4096);K.enable()
		except BaseException:pass
		main()