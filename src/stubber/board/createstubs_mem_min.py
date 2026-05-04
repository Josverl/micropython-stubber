'Create stubs for (all) modules on a MicroPython board.\n\n    This variant of the createstubs.py script is optimised for use on low-memory devices, and reads the list of modules from a text file\n    `modulelist.txt` in the root or `libs` folder that should be uploaded to the device.\n    If that cannot be found then only a single module (micropython) is stubbed.\n    In order to run this on low-memory devices two additional steps are recommended:\n    - minifification, using python-minifier\n      to reduce overall size, and remove logging overhead.\n    - cross compilation, using mpy-cross,\n      to avoid the compilation step on the micropython device\n\nThis variant was generated from createstubs.py by micropython-stubber v1.28.3\n'
A6='No report file'
A5='Failed to create the report.'
A4='method'
A3='function'
A2='stubber'
A1=isinstance
A0=KeyError
z=MemoryError
y=NotImplementedError
p='arch'
o='variant'
n=',\n'
s='dict'
r='list'
q='tuple'
m='__'
l='micropython'
j=TypeError
i=repr
b='-preview'
k=str
Z='family'
Y='board_id'
X='board'
g=len
W=IndexError
d=getattr
V=open
T=print
R=ImportError
Q='mpy'
P='build'
O='.'
N=dir
I='port'
H=AttributeError
U='*'
G='-'
S=Exception
F=OSError
M=True
A='version'
J=None
D=''
C='/'
B=False
import gc as L,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset as c
except R:
	def c():T('Reset called - exiting');sys.exit(0)
try:from collections import OrderedDict as t
except R:from ucollections import OrderedDict as t
u='esp8266',
A7=sys.platform in u
e=B
if not A7:
	try:import inspect as a;e=M
	except R:e=B
__version__='v1.28.3'
A8=2
A9=44
AJ=2
AA=['lib','/lib','/sd/lib','/flash/lib',O]
class K:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=T
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
E=K.getLogger(A2)
K.basicConfig(level=K.INFO)
class Stubber:
	'Generate stubs for modules in firmware'
	def __init__(A,path=D,firmware_id=D):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise y('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A.info=_info();E.info('Port: {}'.format(A.info[I]));E.info('Board: {}'.format(A.info[X]));E.info('Board_ID: {}'.format(A.info[Y]));A._is_low_mem_port=A.info[I]in u;A._capture_docstrings=not A._is_low_mem_port;A._use_inspect=e and not A._is_low_mem_port
		if A._is_low_mem_port:E.info('Low-memory mode: disabling inspect and docstrings')
		L.collect()
		if D:A._fwid=D.lower()
		elif A.info[Z]==l:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(G)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=L.mem_free()
		if path:
			if path.endswith(C):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',C)
		try:f(path+C)
		except F:E.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=J;A._json_first=B
	def load_exlusions(B):
		try:
			with V('modulelist_exclude.txt','r')as C:
				for D in C:
					A=D.strip()
					if A and A not in B.excluded:B.excluded.append(A);E.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except F:pass
	def get_obj_attributes(K,item_instance):
		'extract information of the objects members and attributes';G=item_instance;B=[];J=[]
		for A in N(G):
			if A.startswith(m)and not A in K.modules:continue
			try:
				C=d(G,A)
				try:E=i(type(C)).split("'")[1]
				except W:E=D
				if E in{'int','float','str','bool',q,r,s}:F=1
				elif E in{A3,A4}:F=2
				elif E in'class':F=3
				else:F=4
				B.append((A,i(C),i(type(C)),C,F))
			except H as I:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,G,I))
			except z as I:T('MemoryError: {}'.format(I));sleep(1);c()
		B=sorted([A for A in B if not A[0].startswith(m)],key=lambda x:x[4]);L.collect();return B,J
	def add_modules(A,modules):'Add additional modules to be exported';A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		'Create stubs for all configured modules';E.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();L.collect()
		for B in A.modules:A.create_one_stub(B)
		A.report_end();E.info('Finally done')
	def create_one_stub(D,module_name):
		A=module_name
		if A in D.problematic:E.warning('Skip module: {:<25}        : Known problematic'.format(A));return B
		if A in D.excluded:E.warning('Skip module: {:<25}        : Excluded'.format(A));return B
		H='{}/{}.pyi'.format(D.path,A.replace(O,C));L.collect();G=B
		try:G=D.create_module_stub(A,H)
		except F:return B
		L.collect();return G
	def create_module_stub(G,module_name,file_name=J):
		"Create a Stub of a single python module\n\n        Args:\n        - module_name (str): name of the module to document. This module will be imported.\n        - file_name (Optional[str]): the 'path/filename.pyi' to write to. If omitted will be created based on the module name.\n        ";H=file_name;A=module_name
		if H is J:N=A.replace(O,'_')+'.pyi';H=G.path+C+N
		else:N=H.split(C)[-1]
		if C in A:A=A.replace(C,O)
		I=J
		try:I=__import__(A,J,J,U);P=L.mem_free();E.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,N,P))
		except R:return B
		f(H)
		with V(H,'w')as K:
			Q=k(G.info).replace('OrderedDict(',D).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,G._fwid,Q,__version__);K.write(S);K.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n')
			if G._is_low_mem_port and A in{'builtins','uasyncio.__init__'}:E.warning('Low-memory mode: using shallow stub strategy.');G.write_shallow_stub(K,I)
			else:
				try:G.write_object_stub(K,I,A,D)
				except z:
					if not G._is_low_mem_port:raise
					L.collect();E.warning('Low-memory mode: MemoryError while stubbing {}, resetting'.format(A));c()
		G.report_add(A,H)
		if A not in{'os','sys','logging','gc'}:
			try:del I
			except(F,A0):E.warning('could not del new_module')
		L.collect();return M
	def write_shallow_stub(B,fp,module_obj):
		fp.write('# Low-memory mode: shallow stub with names only\n')
		for A in N(module_obj):
			if A.startswith(m)and not A in B.modules:continue
			if not A or A[0].isdigit():continue
			fp.write('{}: Incomplete\n'.format(A))
	def write_object_stub(W,fp,object_expr,obj_name,indent,in_class=0):
		'Write a module/object stub to an open file. Can be called recursive.';AI=' at ...>';AH='{0}{1}: {3} = {2}\n';AG='{}def {}({}) -> {}:\n';AF='__func__';AE='bound_method';AD='{}*args, **kwargs';AC='Incomplete';AB='    """{0}"""\n';AA='\\"\\"\\"';A0='kind';z='    ';y='Exception';t=object_expr;p=' at ';o='self, ';n='\n';j=', ';b=in_class;X=fp;F=indent;L.collect()
		if t in W.problematic:E.warning('SKIPPING problematic module:{}'.format(t));return
		AK,A2=W.get_obj_attributes(t)
		if A2:E.error(A2)
		for(G,P,Y,Q,_)in AK:
			if G in['classmethod','staticmethod','BaseException',y]:continue
			if G[0].isdigit():E.warning('NameError: invalid name {}'.format(G));continue
			if Y=="<class 'type'>"and g(F)<=AJ*4:
				A5=D;A6=G.endswith(y)or G.endswith('Error')or G in['KeyboardInterrupt','StopIteration','SystemExit']
				if A6:A5=y
				H='\n{}class {}({}):\n'.format(F,G,A5)
				if A6:H+=F+'    ...\n';X.write(H);continue
				X.write(H)
				if W._capture_docstrings:
					try:
						N=Q.__doc__
						if N and A1(N,k):
							N=N.strip().replace('"""',AA).replace(n,n+F+z)
							if N:X.write(F+AB.format(N))
					except S:pass
				W.write_object_stub(X,Q,'{0}.{1}'.format(obj_name,G),F+z,b+1);H=F+'    def __init__(self, *argv, **kwargs) -> None:\n';H+=F+'        ...\n\n';X.write(H)
			elif any(A in Y for A in[A4,A3,'closure']):
				u=AC;A7=D
				if b>0:A7=o
				l=B;v=B;A8=B
				if W._use_inspect:
					try:l=a.iscoroutinefunction(Q)
					except S:pass
					if not l:
						try:v=d(a,'isasyncgenfunction',lambda _:B)(Q)
						except S:pass
					if not l and not v:
						try:A8=a.isgeneratorfunction(Q)
						except S:pass
				Z=J
				if W._use_inspect:
					try:
						h=a.signature(Q);A=[];I=B;c=B
						for(O,w)in h.parameters.items():
							T=d(w,A0,J)
							if T==0:I=M;A.append(O)
							elif T==1:
								if I:A.append(C);I=B
								A.append(O)
							elif T==2:
								if I:A.append(C);I=B
								c=M;A.append(U+O)
							elif T==3:
								if I:A.append(C);I=B
								if not c:A.append(U);c=M
								A.append(O)
							elif T==4:
								if I:A.append(C);I=B
								A.append('**'+O)
							else:A.append(O)
						if I:A.append(C)
						if b>0 and A and A[0]not in(U,C):A=A[1:]
						if b>0:Z=o+j.join(A)if A else'self'
						else:Z=j.join(A)
					except S:pass
				if Z is J:Z=AD.format(A7)
				if AE in Y or AE in P or hasattr(Q,AF):
					m=J
					if W._use_inspect:
						try:
							AL=d(Q,AF,Q);h=a.signature(AL);K=[];V=B;x=B
							for(e,AM)in h.parameters.items():
								i=d(AM,A0,J)
								if i==0:V=M;K.append(e)
								elif i==1:
									if V:K.append(C);V=B
									K.append(e)
								elif i==2:
									if V:K.append(C);V=B
									x=M;K.append(U+e)
								elif i==3:
									if V:K.append(C);V=B
									if not x:K.append(U);x=M
									K.append(e)
								elif i==4:
									if V:K.append(C);V=B
									K.append('**'+e)
								else:K.append(e)
							if V:K.append(C)
							if K and K[0]not in(U,C):K=K[1:]
							m='cls, '+j.join(K)if K else'cls'
						except S:pass
					if m is J:m='cls, *args, **kwargs'
					H='{}@classmethod\n'.format(F)+AG.format(F,G,m,u)
				elif l:H='{}async def {}({}) -> {}:\n'.format(F,G,Z,u)
				elif v:H='{}async def {}({}) -> AsyncGenerator:\n'.format(F,G,Z)
				elif A8:H='{}def {}({}) -> Generator:\n'.format(F,G,Z)
				else:H=AG.format(F,G,Z,u)
				if W._capture_docstrings:
					try:
						N=Q.__doc__
						if N and A1(N,k):
							N=N.strip().replace('"""',AA).replace(n,n+F+z)
							if N:H+=F+AB.format(N)
					except S:pass
				H+=F+'    ...\n\n';X.write(H)
			elif Y=="<class 'module'>":0
			elif Y.startswith("<class '"):
				R=Y[8:-2];H=D
				if R in('str','int','float','bool','bytearray','bytes'):
					if G.upper()==G:H='{0}{1}: Final[{3}] = {2}\n'.format(F,G,P,R)
					else:H=AH.format(F,G,P,R)
				elif R in(s,r,q):AN={s:'{}',r:'[]',q:'()'};H=AH.format(F,G,AN[R],R)
				elif R in('object','set','frozenset','Pin'):H='{0}{1}: {2} ## = {4}\n'.format(F,G,R,Y,P)
				elif R=='generator':
					AO=o if b>0 else D;f=J;A9=B
					if W._use_inspect:
						try:A9=a.iscoroutinefunction(Q)
						except S:pass
						try:
							h=a.signature(Q);A=[];I=B;c=B
							for(O,w)in h.parameters.items():
								T=d(w,A0,J)
								if T==0:I=M;A.append(O)
								elif T==1:
									if I:A.append(C);I=B
									A.append(O)
								elif T==2:
									if I:A.append(C);I=B
									c=M;A.append(U+O)
								elif T==3:
									if I:A.append(C);I=B
									if not c:A.append(U);c=M
									A.append(O)
								elif T==4:
									if I:A.append(C);I=B
									A.append('**'+O)
								else:A.append(O)
							if I:A.append(C)
							if b>0 and A and A[0]not in(U,C):A=A[1:]
							if b>0:f=o+j.join(A)if A else'self'
							else:f=j.join(A)
						except S:pass
					if f is J:f=AD.format(AO)
					if A9:H='{0}async def {1}({2}) -> Incomplete:\n{0}    ...\n\n'.format(F,G,f)
					else:H='{0}def {1}({2}) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(F,G,f,R,P)
				else:
					R=AC
					if p in P:P=P.split(p)[0]+AI
					if p in P:P=P.split(p)[0]+AI
					H='{0}{1}: {2} ## {3} = {4}\n'.format(F,G,R,Y,P)
				X.write(H)
			else:X.write("# all other, type = '{0}'\n".format(Y));X.write(F+G+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		"Turn _fwid from 'v1.2.3' into '1_2_3' to be used in filename";A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(B,path=D):
		'Remove all files from the stub folder'
		if not path:path=B.path
		E.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except(F,H):return
		for D in C:
			A='{}/{}'.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report_start(B,filename='modules.json'):
		'Start a report of the modules that have been stubbed\n        "create json with list of exported modules';D='firmware';B._json_name='{}/{}'.format(B.path,filename);B._json_first=M;f(B._json_name);E.info('Report file: {}'.format(B._json_name));L.collect()
		try:
			with V(B._json_name,'w')as C:C.write('{');C.write(dumps({D:B.info})[1:-1]);C.write(n);C.write(dumps({A2:{A:__version__},'stubtype':D})[1:-1]);C.write(n);C.write('"modules" :[\n')
		except F as G:E.error(A5);B._json_name=J;raise G
	def report_add(A,module_name,stub_file):
		'Add a module to the report'
		if not A._json_name:raise S(A6)
		try:
			with V(A._json_name,'a')as D:
				if not A._json_first:D.write(n)
				else:A._json_first=B
				G='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',C));D.write(G)
		except F:E.error(A5)
	def report_end(A):
		if not A._json_name:raise S(A6)
		with V(A._json_name,'a')as B:B.write('\n]}')
		E.info('Path: {}'.format(A.path))
def f(path):
	'Create nested folders if needed';A=D=0
	while A!=-1:
		A=path.find(C,D)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except F as G:
				if G.args[0]in[A8,A9]:
					try:E.debug('Create folder {}'.format(B));os.mkdir(B)
					except F as H:E.error('failed to create folder {}'.format(B));raise H
		D=A+1
def h(s):
	B=' on '
	if not s:return D
	s=s.split(B,1)[0]if B in s else s
	if s.startswith('v'):
		if not G in s:return D
		A=s.split(G)[1];return A
	if not b in s:return D
	A=s.split(b)[1].split(O)[1];return A
def AB():
	'Get basic system implementation details.'
	try:B=sys.implementation[0]
	except j:B=sys.implementation.name
	C=t({Z:B,A:D,P:D,'ver':D,I:sys.platform,X:'UNKNOWN',Y:D,o:D,'cpu':D,Q:D,p:D});return C
def AC(info):
	'Normalize port names to be consistent with the repo.';A=info
	if A[I].startswith('pyb'):A[I]='stm32'
	elif A[I]=='win32':A[I]='windows'
	elif A[I]=='linux':A[I]='unix'
def AD(info):
	'Extract version information from sys.implementation.'
	try:info[A]=AL(sys.implementation.version)
	except H:pass
def AE(info):
	'Extract board, CPU, and machine details.';A=info
	try:
		C=sys.implementation._machine if'_machine'in N(sys.implementation)else os.uname().machine;A[X]=C.strip();B=sys.implementation._build if'_build'in N(sys.implementation)else D
		if B:A[X]=B.split(G)[0];A[o]=B.split(G)[1]if G in B else D
		A[Y]=B;A['cpu']=C.split('with')[-1].strip();A[Q]=sys.implementation._mpy if'_mpy'in N(sys.implementation)else sys.implementation.mpy if Q in N(sys.implementation)else D
	except(H,W):pass
	if not A[Y]:AM(A)
def AF(info):
	'Extract build information from various system sources.';B=info
	try:
		if'uname'in N(os):
			B[P]=h(os.uname()[3])
			if not B[P]:B[P]=h(os.uname()[2])
		elif A in N(sys):B[P]=h(sys.version)
	except(H,W,j):pass
	if B[A]==D and sys.platform not in('unix','win32'):
		try:C=os.uname();B[A]=C.release
		except(W,H,j):pass
def AG(info):
	'Detect special firmware families (pycopy, pycom, ev3-pybricks).';D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,J,J,G);A[Z]=E;del H;break
		except(R,A0):pass
	if A[Z]==D:A['release']='2.0.0'
def AH(info):
	'Process MicroPython-specific version formatting.';B=info
	if B[Z]==l:
		if B[A]and B[A].endswith('.0')and B[A]>='1.10.0'and B[A]<='1.19.9':B[A]=B[A][:-2]
def AI(info):
	'Process MPY architecture and version information.';A=info
	if Q in A and A[Q]:
		B=int(A[Q])
		try:
			C=[J,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[p]=C
		except W:A[p]='unknown'
		A[Q]='v{}.{}'.format(B&255,B>>8&3)
def AK(info):
	'Handle final version string formatting.';B=info
	if B[P]and not B[A].endswith(b):B[A]=B[A]+b
	B['ver']=f"{B[A]}-{B[P]}"if B[P]else f"{B[A]}"
def _info():'\n    Gather comprehensive system information for MicroPython stubbing.\n\n    Returns a dictionary containing family, version, port, board, and other\n    system details needed for stub generation.\n    ';A=AB();AC(A);AD(A);AE(A);AF(A);AG(A);AH(A);AI(A);AK(A);return A
def AL(version):
	A=version;B=O.join([k(A)for A in A[:3]])
	if g(A)>3 and A[3]:B+=G+A[3]
	return B
def AM(info):
	'Read the board_id from the boardname.py file that may have been created upfront';B=info
	try:from boardname import BOARD_ID as A;E.info('Found BOARD_ID: {}'.format(A))
	except R:E.warning('BOARD_ID not found');A=D
	B[Y]=A;B[X]=A.split(G)[0]if G in A else A;B[o]==A.split(G)[1]if G in A else D
def get_root():
	'Determine the root folder of the device'
	try:A=os.getcwd()
	except(F,H):A=O
	B=A
	for B in['/remote','/sd','/flash',C,A,O]:
		try:D=os.stat(B);break
		except F:continue
	return B
def v(filename):
	try:
		if os.stat(filename)[0]>>14:return M
		return B
	except F:return B
def w():T("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	'get --path from cmdline. [unix/win]';path=D
	if g(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:w()
	elif g(sys.argv)==2:w()
	return path
def x():
	'runtime test to determine full or micropython'
	try:A=bytes('abc',encoding='utf8');C=x.__module__;return B
	except(y,H):return M
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	def A(stubber):
		L.collect();stubber.modules=[]
		for C in AA:
			B=C+'/modulelist.txt'
			if not v(B):continue
			with V(B)as D:
				while M:
					A=D.readline().strip()
					if not A:break
					if g(A)>0 and A[0]!='#':stubber.modules.append(A)
				L.collect();T('BREAK');break
		if not stubber.modules:stubber.modules=[l]
		L.collect()
	stubber.modules=[];A(stubber);L.collect();stubber.create_all_stubs()
if __name__=='__main__'or x():
	if not v('no_auto_stubber.txt'):
		T(f"createstubs.py: {__version__}")
		try:L.threshold(4096);L.enable()
		except BaseException:pass
		main()