'\nCreate stubs for (all) modules on a MicroPython board.\n\n    This variant of the createstubs.py script is optimized for use on very-low-memory devices.\n    Note: this version has undergone limited testing.\n\n    1) reads the list of modules from a text file `modulelist.txt` that should be uploaded to the device.\n    2) stored the already processed modules in a text file `modulelist.done`\n    3) process the modules in the database:\n        - stub the module\n        - update the modulelist.done file\n        - reboots the device if it runs out of memory\n    4) creates the modules.json\n\n    If that cannot be found then only a single module (micropython) is stubbed.\n    In order to run this on low-memory devices two additional steps are recommended:\n    - minification, using python-minifierto reduce overall size, and remove logging overhead.\n    - cross compilation, using mpy-cross, to avoid the compilation step on the micropython device\n\n\nThis variant was generated from createstubs.py by micropython-stubber v1.28.3\n'
AB='No report file'
AA='Failed to create the report.'
A9='method'
A8='function'
A7='micropython'
A6='stubber'
A5=isinstance
A4=KeyError
A3=NotImplementedError
y='arch'
x='variant'
w=',\n'
v='modules.json'
u='{}/{}'
t='w'
s='dict'
r='list'
q='tuple'
p='__'
o=TypeError
n=MemoryError
m=repr
b='-preview'
i='\n'
Z='family'
Y='board_id'
X='board'
h=len
g=str
W=IndexError
d=getattr
V=print
T=ImportError
R='mpy'
Q='build'
P='.'
O=dir
N=open
I='port'
H=AttributeError
U='*'
G='-'
S=Exception
L=True
F=OSError
A='version'
J=None
E=''
C='/'
B=False
import gc as M,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset as c
except T:
	def c():V('Reset called - exiting');sys.exit(0)
try:from collections import OrderedDict as z
except T:from ucollections import OrderedDict as z
A0='esp8266',
AC=sys.platform in A0
e=B
if not AC:
	try:import inspect as a;e=L
	except T:e=B
__version__='v1.28.3'
AD=2
AE=44
AJ=2
AF=['lib','/lib','/sd/lib','/flash/lib',P]
class K:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=V
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
D=K.getLogger(A6)
K.basicConfig(level=K.INFO)
class Stubber:
	'Generate stubs for modules in firmware'
	def __init__(A,path=E,firmware_id=E):
		E=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise A3('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A.info=_info();D.info('Port: {}'.format(A.info[I]));D.info('Board: {}'.format(A.info[X]));D.info('Board_ID: {}'.format(A.info[Y]));A._is_low_mem_port=A.info[I]in A0;A._capture_docstrings=not A._is_low_mem_port;A._use_inspect=e and not A._is_low_mem_port
		if A._is_low_mem_port:D.info('Low-memory mode: disabling inspect and docstrings')
		M.collect()
		if E:A._fwid=E.lower()
		elif A.info[Z]==A7:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(G)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=M.mem_free()
		if path:
			if path.endswith(C):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',C)
		try:f(path+C)
		except F:D.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=J;A._json_first=B
	def load_exlusions(B):
		try:
			with N('modulelist_exclude.txt','r')as C:
				for E in C:
					A=E.strip()
					if A and A not in B.excluded:B.excluded.append(A);D.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except F:pass
	def get_obj_attributes(K,item_instance):
		'extract information of the objects members and attributes';G=item_instance;B=[];J=[]
		for A in O(G):
			if A.startswith(p)and not A in K.modules:continue
			try:
				C=d(G,A)
				try:D=m(type(C)).split("'")[1]
				except W:D=E
				if D in{'int','float','str','bool',q,r,s}:F=1
				elif D in{A8,A9}:F=2
				elif D in'class':F=3
				else:F=4
				B.append((A,m(C),m(type(C)),C,F))
			except H as I:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,G,I))
			except n as I:V('MemoryError: {}'.format(I));sleep(1);c()
		B=sorted([A for A in B if not A[0].startswith(p)],key=lambda x:x[4]);M.collect();return B,J
	def add_modules(A,modules):'Add additional modules to be exported';A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		'Create stubs for all configured modules';D.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();M.collect()
		for B in A.modules:A.create_one_stub(B)
		A.report_end();D.info('Finally done')
	def create_one_stub(E,module_name):
		A=module_name
		if A in E.problematic:D.warning('Skip module: {:<25}        : Known problematic'.format(A));return B
		if A in E.excluded:D.warning('Skip module: {:<25}        : Excluded'.format(A));return B
		H='{}/{}.pyi'.format(E.path,A.replace(P,C));M.collect();G=B
		try:G=E.create_module_stub(A,H)
		except F:return B
		M.collect();return G
	def create_module_stub(G,module_name,file_name=J):
		"Create a Stub of a single python module\n\n        Args:\n        - module_name (str): name of the module to document. This module will be imported.\n        - file_name (Optional[str]): the 'path/filename.pyi' to write to. If omitted will be created based on the module name.\n        ";H=file_name;A=module_name
		if H is J:O=A.replace(P,'_')+'.pyi';H=G.path+C+O
		else:O=H.split(C)[-1]
		if C in A:A=A.replace(C,P)
		I=J
		try:I=__import__(A,J,J,U);Q=M.mem_free();D.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,O,Q))
		except T:return B
		f(H)
		with N(H,t)as K:
			R=g(G.info).replace('OrderedDict(',E).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,G._fwid,R,__version__);K.write(S);K.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n')
			if G._is_low_mem_port and A in{'builtins','uasyncio.__init__'}:D.warning('Low-memory mode: using shallow stub strategy.');G.write_shallow_stub(K,I)
			else:
				try:G.write_object_stub(K,I,A,E)
				except n:
					if not G._is_low_mem_port:raise
					M.collect();D.warning('Low-memory mode: MemoryError while stubbing {}, resetting'.format(A));c()
		G.report_add(A,H)
		if A not in{'os','sys','logging','gc'}:
			try:del I
			except(F,A4):D.warning('could not del new_module')
		M.collect();return L
	def write_shallow_stub(B,fp,module_obj):
		fp.write('# Low-memory mode: shallow stub with names only\n')
		for A in O(module_obj):
			if A.startswith(p)and not A in B.modules:continue
			if not A or A[0].isdigit():continue
			fp.write('{}: Incomplete\n'.format(A))
	def write_object_stub(W,fp,object_expr,obj_name,indent,in_class=0):
		'Write a module/object stub to an open file. Can be called recursive.';AI=' at ...>';AH='{0}{1}: {3} = {2}\n';AG='{}def {}({}) -> {}:\n';AF='__func__';AE='bound_method';AD='{}*args, **kwargs';AC='Incomplete';AB='    """{0}"""\n';AA='\\"\\"\\"';A0='kind';z='    ';y='Exception';t=object_expr;p=' at ';o='self, ';l=', ';b=in_class;X=fp;F=indent;M.collect()
		if t in W.problematic:D.warning('SKIPPING problematic module:{}'.format(t));return
		AK,A1=W.get_obj_attributes(t)
		if A1:D.error(A1)
		for(G,P,Y,Q,_)in AK:
			if G in['classmethod','staticmethod','BaseException',y]:continue
			if G[0].isdigit():D.warning('NameError: invalid name {}'.format(G));continue
			if Y=="<class 'type'>"and h(F)<=AJ*4:
				A2=E;A3=G.endswith(y)or G.endswith('Error')or G in['KeyboardInterrupt','StopIteration','SystemExit']
				if A3:A2=y
				H='\n{}class {}({}):\n'.format(F,G,A2)
				if A3:H+=F+'    ...\n';X.write(H);continue
				X.write(H)
				if W._capture_docstrings:
					try:
						N=Q.__doc__
						if N and A5(N,g):
							N=N.strip().replace('"""',AA).replace(i,i+F+z)
							if N:X.write(F+AB.format(N))
					except S:pass
				W.write_object_stub(X,Q,'{0}.{1}'.format(obj_name,G),F+z,b+1);H=F+'    def __init__(self, *argv, **kwargs) -> None:\n';H+=F+'        ...\n\n';X.write(H)
			elif any(A in Y for A in[A9,A8,'closure']):
				u=AC;A4=E
				if b>0:A4=o
				m=B;v=B;A6=B
				if W._use_inspect:
					try:m=a.iscoroutinefunction(Q)
					except S:pass
					if not m:
						try:v=d(a,'isasyncgenfunction',lambda _:B)(Q)
						except S:pass
					if not m and not v:
						try:A6=a.isgeneratorfunction(Q)
						except S:pass
				Z=J
				if W._use_inspect:
					try:
						j=a.signature(Q);A=[];I=B;c=B
						for(O,w)in j.parameters.items():
							T=d(w,A0,J)
							if T==0:I=L;A.append(O)
							elif T==1:
								if I:A.append(C);I=B
								A.append(O)
							elif T==2:
								if I:A.append(C);I=B
								c=L;A.append(U+O)
							elif T==3:
								if I:A.append(C);I=B
								if not c:A.append(U);c=L
								A.append(O)
							elif T==4:
								if I:A.append(C);I=B
								A.append('**'+O)
							else:A.append(O)
						if I:A.append(C)
						if b>0 and A and A[0]not in(U,C):A=A[1:]
						if b>0:Z=o+l.join(A)if A else'self'
						else:Z=l.join(A)
					except S:pass
				if Z is J:Z=AD.format(A4)
				if AE in Y or AE in P or hasattr(Q,AF):
					n=J
					if W._use_inspect:
						try:
							AL=d(Q,AF,Q);j=a.signature(AL);K=[];V=B;x=B
							for(e,AM)in j.parameters.items():
								k=d(AM,A0,J)
								if k==0:V=L;K.append(e)
								elif k==1:
									if V:K.append(C);V=B
									K.append(e)
								elif k==2:
									if V:K.append(C);V=B
									x=L;K.append(U+e)
								elif k==3:
									if V:K.append(C);V=B
									if not x:K.append(U);x=L
									K.append(e)
								elif k==4:
									if V:K.append(C);V=B
									K.append('**'+e)
								else:K.append(e)
							if V:K.append(C)
							if K and K[0]not in(U,C):K=K[1:]
							n='cls, '+l.join(K)if K else'cls'
						except S:pass
					if n is J:n='cls, *args, **kwargs'
					H='{}@classmethod\n'.format(F)+AG.format(F,G,n,u)
				elif m:H='{}async def {}({}) -> {}:\n'.format(F,G,Z,u)
				elif v:H='{}async def {}({}) -> AsyncGenerator:\n'.format(F,G,Z)
				elif A6:H='{}def {}({}) -> Generator:\n'.format(F,G,Z)
				else:H=AG.format(F,G,Z,u)
				if W._capture_docstrings:
					try:
						N=Q.__doc__
						if N and A5(N,g):
							N=N.strip().replace('"""',AA).replace(i,i+F+z)
							if N:H+=F+AB.format(N)
					except S:pass
				H+=F+'    ...\n\n';X.write(H)
			elif Y=="<class 'module'>":0
			elif Y.startswith("<class '"):
				R=Y[8:-2];H=E
				if R in('str','int','float','bool','bytearray','bytes'):
					if G.upper()==G:H='{0}{1}: Final[{3}] = {2}\n'.format(F,G,P,R)
					else:H=AH.format(F,G,P,R)
				elif R in(s,r,q):AN={s:'{}',r:'[]',q:'()'};H=AH.format(F,G,AN[R],R)
				elif R in('object','set','frozenset','Pin'):H='{0}{1}: {2} ## = {4}\n'.format(F,G,R,Y,P)
				elif R=='generator':
					AO=o if b>0 else E;f=J;A7=B
					if W._use_inspect:
						try:A7=a.iscoroutinefunction(Q)
						except S:pass
						try:
							j=a.signature(Q);A=[];I=B;c=B
							for(O,w)in j.parameters.items():
								T=d(w,A0,J)
								if T==0:I=L;A.append(O)
								elif T==1:
									if I:A.append(C);I=B
									A.append(O)
								elif T==2:
									if I:A.append(C);I=B
									c=L;A.append(U+O)
								elif T==3:
									if I:A.append(C);I=B
									if not c:A.append(U);c=L
									A.append(O)
								elif T==4:
									if I:A.append(C);I=B
									A.append('**'+O)
								else:A.append(O)
							if I:A.append(C)
							if b>0 and A and A[0]not in(U,C):A=A[1:]
							if b>0:f=o+l.join(A)if A else'self'
							else:f=l.join(A)
						except S:pass
					if f is J:f=AD.format(AO)
					if A7:H='{0}async def {1}({2}) -> Incomplete:\n{0}    ...\n\n'.format(F,G,f)
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
	def clean(B,path=E):
		'Remove all files from the stub folder'
		if not path:path=B.path
		D.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except(F,H):return
		for E in C:
			A=u.format(path,E)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report_start(B,filename=v):
		'Start a report of the modules that have been stubbed\n        "create json with list of exported modules';E='firmware';B._json_name=u.format(B.path,filename);B._json_first=L;f(B._json_name);D.info('Report file: {}'.format(B._json_name));M.collect()
		try:
			with N(B._json_name,t)as C:C.write('{');C.write(dumps({E:B.info})[1:-1]);C.write(w);C.write(dumps({A6:{A:__version__},'stubtype':E})[1:-1]);C.write(w);C.write('"modules" :[\n')
		except F as G:D.error(AA);B._json_name=J;raise G
	def report_add(A,module_name,stub_file):
		'Add a module to the report'
		if not A._json_name:raise S(AB)
		try:
			with N(A._json_name,'a')as E:
				if not A._json_first:E.write(w)
				else:A._json_first=B
				G='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',C));E.write(G)
		except F:D.error(AA)
	def report_end(A):
		if not A._json_name:raise S(AB)
		with N(A._json_name,'a')as B:B.write('\n]}')
		D.info('Path: {}'.format(A.path))
def f(path):
	'Create nested folders if needed';A=E=0
	while A!=-1:
		A=path.find(C,E)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except F as G:
				if G.args[0]in[AD,AE]:
					try:D.debug('Create folder {}'.format(B));os.mkdir(B)
					except F as H:D.error('failed to create folder {}'.format(B));raise H
		E=A+1
def j(s):
	B=' on '
	if not s:return E
	s=s.split(B,1)[0]if B in s else s
	if s.startswith('v'):
		if not G in s:return E
		A=s.split(G)[1];return A
	if not b in s:return E
	A=s.split(b)[1].split(P)[1];return A
def AG():
	'Get basic system implementation details.'
	try:B=sys.implementation[0]
	except o:B=sys.implementation.name
	C=z({Z:B,A:E,Q:E,'ver':E,I:sys.platform,X:'UNKNOWN',Y:E,x:E,'cpu':E,R:E,y:E});return C
def AH(info):
	'Normalize port names to be consistent with the repo.';A=info
	if A[I].startswith('pyb'):A[I]='stm32'
	elif A[I]=='win32':A[I]='windows'
	elif A[I]=='linux':A[I]='unix'
def AI(info):
	'Extract version information from sys.implementation.'
	try:info[A]=AQ(sys.implementation.version)
	except H:pass
def AK(info):
	'Extract board, CPU, and machine details.';A=info
	try:
		C=sys.implementation._machine if'_machine'in O(sys.implementation)else os.uname().machine;A[X]=C.strip();B=sys.implementation._build if'_build'in O(sys.implementation)else E
		if B:A[X]=B.split(G)[0];A[x]=B.split(G)[1]if G in B else E
		A[Y]=B;A['cpu']=C.split('with')[-1].strip();A[R]=sys.implementation._mpy if'_mpy'in O(sys.implementation)else sys.implementation.mpy if R in O(sys.implementation)else E
	except(H,W):pass
	if not A[Y]:AR(A)
def AL(info):
	'Extract build information from various system sources.';B=info
	try:
		if'uname'in O(os):
			B[Q]=j(os.uname()[3])
			if not B[Q]:B[Q]=j(os.uname()[2])
		elif A in O(sys):B[Q]=j(sys.version)
	except(H,W,o):pass
	if B[A]==E and sys.platform not in('unix','win32'):
		try:C=os.uname();B[A]=C.release
		except(W,H,o):pass
def AM(info):
	'Detect special firmware families (pycopy, pycom, ev3-pybricks).';D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,J,J,G);A[Z]=E;del H;break
		except(T,A4):pass
	if A[Z]==D:A['release']='2.0.0'
def AN(info):
	'Process MicroPython-specific version formatting.';B=info
	if B[Z]==A7:
		if B[A]and B[A].endswith('.0')and B[A]>='1.10.0'and B[A]<='1.19.9':B[A]=B[A][:-2]
def AO(info):
	'Process MPY architecture and version information.';A=info
	if R in A and A[R]:
		B=int(A[R])
		try:
			C=[J,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[y]=C
		except W:A[y]='unknown'
		A[R]='v{}.{}'.format(B&255,B>>8&3)
def AP(info):
	'Handle final version string formatting.';B=info
	if B[Q]and not B[A].endswith(b):B[A]=B[A]+b
	B['ver']=f"{B[A]}-{B[Q]}"if B[Q]else f"{B[A]}"
def _info():'\n    Gather comprehensive system information for MicroPython stubbing.\n\n    Returns a dictionary containing family, version, port, board, and other\n    system details needed for stub generation.\n    ';A=AG();AH(A);AI(A);AK(A);AL(A);AM(A);AN(A);AO(A);AP(A);return A
def AQ(version):
	A=version;B=P.join([g(A)for A in A[:3]])
	if h(A)>3 and A[3]:B+=G+A[3]
	return B
def AR(info):
	'Read the board_id from the boardname.py file that may have been created upfront';B=info
	try:from boardname import BOARD_ID as A;D.info('Found BOARD_ID: {}'.format(A))
	except T:D.warning('BOARD_ID not found');A=E
	B[Y]=A;B[X]=A.split(G)[0]if G in A else A;B[x]==A.split(G)[1]if G in A else E
def get_root():
	'Determine the root folder of the device'
	try:A=os.getcwd()
	except(F,H):A=P
	B=A
	for B in['/remote','/sd','/flash',C,A,P]:
		try:D=os.stat(B);break
		except F:continue
	return B
def k(filename):
	try:
		if os.stat(filename)[0]>>14:return L
		return B
	except F:return B
def A1():V("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	'get --path from cmdline. [unix/win]';path=E
	if h(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:A1()
	elif h(sys.argv)==2:A1()
	return path
def A2():
	'runtime test to determine full or micropython'
	try:A=bytes('abc',encoding='utf8');C=A2.__module__;return B
	except(A3,H):return L
l='modulelist.done'
def AS(skip=0):
	for D in AF:
		B=D+'/modulelist.txt'
		if not k(B):continue
		try:
			with N(B,encoding='utf-8')as E:
				C=0
				while L:
					A=E.readline().strip()
					if not A:break
					if h(A)>0 and A[0]=='#':continue
					C+=1
					if C<skip:continue
					yield A
				break
		except F:pass
def AT(done):
	with N(l,t)as A:A.write(g(done)+i)
def AU():
	A=0
	try:
		with N(l)as B:A=int(B.readline().strip())
	except F:pass
	return A
def main():
	import machine as C;B=k(l)
	if B:D.info('Continue from last run')
	else:D.info('Starting new run')
	stubber=Stubber(path=read_path());A=0
	if not B:stubber.clean();stubber.report_start(v)
	else:A=AU();stubber._json_name=u.format(stubber.path,v)
	for E in AS(A):
		try:stubber.create_one_stub(E)
		except n:C.reset()
		M.collect();A+=1;AT(A)
	V('All modules have been processed, Finalizing report');stubber.report_end()
if __name__=='__main__'or A2():
	if not k('no_auto_stubber.txt'):
		V(f"createstubs.py: {__version__}")
		try:M.threshold(4096);M.enable()
		except BaseException:pass
		main()