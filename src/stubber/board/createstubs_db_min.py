'\nCreate stubs for (all) modules on a MicroPython board.\n\n    This variant of the createstubs.py script is optimized for use on very-low-memory devices.\n    Note: this version has undergone limited testing.\n\n    1) reads the list of modules from a text file `modulelist.txt` that should be uploaded to the device.\n    2) stored the already processed modules in a text file `modulelist.done`\n    3) process the modules in the database:\n        - stub the module\n        - update the modulelist.done file\n        - reboots the device if it runs out of memory\n    4) creates the modules.json\n\n    If that cannot be found then only a single module (micropython) is stubbed.\n    In order to run this on low-memory devices two additional steps are recommended:\n    - minification, using python-minifierto reduce overall size, and remove logging overhead.\n    - cross compilation, using mpy-cross, to avoid the compilation step on the micropython device\n\n\nThis variant was generated from createstubs.py by micropython-stubber v1.29.0\n'
AC='No report file'
AB='Failed to create the report.'
AA='method'
A9='function'
A8='micropython'
A7='stubber'
A6=ValueError
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
g=getattr
f='\n'
a='family'
X='board_id'
W='board'
e=str
V=IndexError
U=print
T=ImportError
S='mpy'
Z='*'
Y=len
Q='build'
P='.'
O=dir
M=open
I='port'
H=AttributeError
R=Exception
F='-'
N=True
E=OSError
A='version'
J=None
G='/'
D=''
B=False
import gc as K,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset as d
except T:
	def d():U('Reset called - exiting');sys.exit(0)
try:from collections import OrderedDict as z
except T:from ucollections import OrderedDict as z
A0='esp8266',
AD=sys.platform in A0
h=B
if not AD:
	try:import inspect as c;h=N
	except T:h=B
__version__='v1.29.0'
AE=2
AF=44
AI=2
AG=['lib','/lib','/sd/lib','/flash/lib',P]
class L:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=U
	@staticmethod
	def getLogger(name):return L()
	@classmethod
	def basicConfig(A,level):A.level=level
	def debug(A,msg):
		if A.level<=L.DEBUG:A.prnt('DEBUG :',msg)
	def info(A,msg):
		if A.level<=L.INFO:A.prnt('INFO  :',msg)
	def warning(A,msg):
		if A.level<=L.WARNING:A.prnt('WARN  :',msg)
	def error(A,msg):
		if A.level<=L.ERROR:A.prnt('ERROR :',msg)
C=L.getLogger(A7)
L.basicConfig(level=L.INFO)
class Stubber:
	'Generate stubs for modules in firmware'
	def __init__(A,path=D,firmware_id=D):
		D=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise A3('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A.info=_info();C.info('Port: {}'.format(A.info[I]));C.info('Board: {}'.format(A.info[W]));C.info('Board_ID: {}'.format(A.info[X]));A._is_low_mem_port=A.info[I]in A0;A._capture_docstrings=not A._is_low_mem_port;A._use_inspect=h and not A._is_low_mem_port
		if A._is_low_mem_port:C.info('Low-memory mode: disabling inspect and docstrings')
		K.collect()
		if D:A._fwid=D.lower()
		elif A.info[a]==A8:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(F)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=K.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:i(path+G)
		except E:C.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=J;A._json_first=B
	def load_exlusions(B):
		try:
			with M('modulelist_exclude.txt','r')as D:
				for F in D:
					A=F.strip()
					if A and A not in B.excluded:B.excluded.append(A);C.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except E:pass
	def get_obj_attributes(L,item_instance):
		'extract information of the objects members and attributes';G=item_instance;B=[];J=[]
		for A in O(G):
			if A.startswith(p)and not A in L.modules:continue
			try:
				C=g(G,A)
				try:E=m(type(C)).split("'")[1]
				except V:E=D
				if E in{'int','float','str','bool',q,r,s}:F=1
				elif E in{A9,AA}:F=2
				elif E in'class':F=3
				else:F=4
				B.append((A,m(C),m(type(C)),C,F))
			except H as I:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,G,I))
			except n as I:U('MemoryError: {}'.format(I));sleep(1);d()
		B=sorted([A for A in B if not A[0].startswith(p)],key=lambda x:x[4]);K.collect();return B,J
	def add_modules(A,modules):'Add additional modules to be exported';A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		'Create stubs for all configured modules';C.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();K.collect()
		for B in A.modules:A.create_one_stub(B)
		A.report_end();C.info('Finally done')
	def create_one_stub(D,module_name):
		A=module_name
		if A in D.problematic:C.warning('Skip module: {:<25}        : Known problematic'.format(A));return B
		if A in D.excluded:C.warning('Skip module: {:<25}        : Excluded'.format(A));return B
		H='{}/{}.pyi'.format(D.path,A.replace(P,G));K.collect();F=B
		try:F=D.create_module_stub(A,H)
		except E:return B
		K.collect();return F
	def create_module_stub(F,module_name,file_name=J):
		"Create a Stub of a single python module\n\n        Args:\n        - module_name (str): name of the module to document. This module will be imported.\n        - file_name (Optional[str]): the 'path/filename.pyi' to write to. If omitted will be created based on the module name.\n        ";H=file_name;A=module_name
		if H is J:O=A.replace(P,'_')+'.pyi';H=F.path+G+O
		else:O=H.split(G)[-1]
		if G in A:A=A.replace(G,P)
		I=J
		try:I=__import__(A,J,J,Z);Q=K.mem_free();C.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,O,Q))
		except T:return B
		i(H)
		with M(H,t)as L:
			R=e(F.info).replace('OrderedDict(',D).replace('})','}');S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,F._fwid,R,__version__);L.write(S);L.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n')
			if F._is_low_mem_port and A in{'builtins','uasyncio.__init__'}:C.warning('Low-memory mode: using shallow stub strategy.');F.write_shallow_stub(L,I)
			else:
				try:F.write_object_stub(L,I,A,D)
				except n:
					if not F._is_low_mem_port:raise
					K.collect();C.warning('Low-memory mode: MemoryError while stubbing {}, resetting'.format(A));d()
		F.report_add(A,H)
		if A not in{'os','sys','logging','gc'}:
			try:del I
			except(E,A4):C.warning('could not del new_module')
		K.collect();return N
	def write_shallow_stub(B,fp,module_obj):
		fp.write('# Low-memory mode: shallow stub with names only\n')
		for A in O(module_obj):
			if A.startswith(p)and not A in B.modules:continue
			if not A or A[0].isdigit():continue
			fp.write('{}: Incomplete\n'.format(A))
	def write_object_stub(X,fp,object_expr,obj_name,indent,in_class=0):
		'Write a module/object stub to an open file. Can be called recursive.';AH=' at ...>';AG='{0}{1}: {3} = {2}\n';AF='{}# inspect: arity={}\n';AE='{}def {}({}) -> {}:\n';AD='bound_method';AC='{}*args, **kwargs';AB='inspect returned arity-only parameters';A8='Incomplete';A7='    """{0}"""\n';A4='\\"\\"\\"';x='self';w='    ';v='Exception';m=object_expr;l=' at ';k=', ';j='kind';i='self, ';a=in_class;S=fp;E=indent;K.collect()
		if m in X.problematic:C.warning('SKIPPING problematic module:{}'.format(m));return
		AJ,y=X.get_obj_attributes(m)
		if y:C.error(y)
		for(H,O,T,U,_)in AJ:
			if H in['classmethod','staticmethod','BaseException',v]:continue
			if H[0].isdigit():C.warning('NameError: invalid name {}'.format(H));continue
			if T=="<class 'type'>"and Y(E)<=AI*4:
				z=D;A0=H.endswith(v)or H.endswith('Error')or H in['KeyboardInterrupt','StopIteration','SystemExit']
				if A0:z=v
				F='\n{}class {}({}):\n'.format(E,H,z)
				if A0:F+=E+'    ...\n';S.write(F);continue
				S.write(F)
				if X._capture_docstrings:
					try:
						L=U.__doc__
						if L and A5(L,e):
							L=L.strip().replace('"""',A4).replace(f,f+E+w)
							if L:S.write(E+A7.format(L))
					except R:pass
				X.write_object_stub(S,U,'{0}.{1}'.format(obj_name,H),E+w,a+1);F=E+'    def __init__(self, *argv, **kwargs) -> None:\n';F+=E+'        ...\n\n';S.write(F)
			elif any(A in T for A in[AA,A9,'closure']):
				n=A8;A1=D
				if a>0:A1=i
				h=B;o=B;A2=B
				if X._use_inspect:
					try:h=c.iscoroutinefunction(U)
					except R:pass
					if not h:
						try:o=g(c,'isasyncgenfunction',lambda _:B)(U)
						except R:pass
					if not h and not o:
						try:A2=c.isgeneratorfunction(U)
						except R:pass
				V=J;p=J
				if X._use_inspect:
					try:
						W=c.signature(U)
						if W.parameters and not all(hasattr(A,j)for A in W.parameters.values()):p=Y(W.parameters);raise A6(AB)
						A=[];I=B;b=B
						for(M,t)in W.parameters.items():
							Q=g(t,j,J)
							if Q==0:I=N;A.append(M)
							elif Q==1:
								if I:A.append(G);I=B
								A.append(M)
							elif Q==2:
								if I:A.append(G);I=B
								b=N;A.append(Z+M)
							elif Q==3:
								if I:A.append(G);I=B
								if not b:A.append(Z);b=N
								A.append(M)
							elif Q==4:
								if I:A.append(G);I=B
								A.append('**'+M)
							else:A.append(M)
						if I:A.append(G)
						if a>0 and A and A[0]not in(Z,G):A=A[1:]
						if a>0:V=i+k.join(A)if A else x
						else:V=k.join(A)
					except R:pass
				if V is J:V=AC.format(A1)
				if AD in T or AD in O:F='{}@classmethod\n'.format(E)+AE.format(E,H,V.replace(x,'cls',1),n)
				elif h:F='{}async def {}({}) -> {}:\n'.format(E,H,V,n)
				elif o:F='{}async def {}({}) -> AsyncGenerator:\n'.format(E,H,V)
				elif A2:F='{}def {}({}) -> Generator:\n'.format(E,H,V)
				else:F=AE.format(E,H,V,n)
				if p is not J:F=AF.format(E,p)+F
				if X._capture_docstrings:
					try:
						L=U.__doc__
						if L and A5(L,e):
							L=L.strip().replace('"""',A4).replace(f,f+E+w)
							if L:F+=E+A7.format(L)
					except R:pass
				F+=E+'    ...\n\n';S.write(F)
			elif T=="<class 'module'>":0
			elif T.startswith("<class '"):
				P=T[8:-2];F=D
				if P in('str','int','float','bool','bytearray','bytes'):
					if H.upper()==H:F='{0}{1}: Final[{3}] = {2}\n'.format(E,H,O,P)
					else:F=AG.format(E,H,O,P)
				elif P in(s,r,q):AK={s:'{}',r:'[]',q:'()'};F=AG.format(E,H,AK[P],P)
				elif P in('object','set','frozenset','Pin'):F='{0}{1}: {2} ## = {4}\n'.format(E,H,P,T,O)
				elif P=='generator':
					AL=i if a>0 else D;d=J;u=J;A3=B
					if X._use_inspect:
						try:A3=c.iscoroutinefunction(U)
						except R:pass
						try:
							W=c.signature(U)
							if W.parameters and not all(hasattr(A,j)for A in W.parameters.values()):u=Y(W.parameters);raise A6(AB)
							A=[];I=B;b=B
							for(M,t)in W.parameters.items():
								Q=g(t,j,J)
								if Q==0:I=N;A.append(M)
								elif Q==1:
									if I:A.append(G);I=B
									A.append(M)
								elif Q==2:
									if I:A.append(G);I=B
									b=N;A.append(Z+M)
								elif Q==3:
									if I:A.append(G);I=B
									if not b:A.append(Z);b=N
									A.append(M)
								elif Q==4:
									if I:A.append(G);I=B
									A.append('**'+M)
								else:A.append(M)
							if I:A.append(G)
							if a>0 and A and A[0]not in(Z,G):A=A[1:]
							if a>0:d=i+k.join(A)if A else x
							else:d=k.join(A)
						except R:pass
					if d is J:d=AC.format(AL)
					if A3:F='{0}async def {1}({2}) -> Incomplete:\n{0}    ...\n\n'.format(E,H,d)
					else:F='{0}def {1}({2}) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(E,H,d,P,O)
					if u is not J:F=AF.format(E,u)+F
				else:
					P=A8
					if l in O:O=O.split(l)[0]+AH
					if l in O:O=O.split(l)[0]+AH
					F='{0}{1}: {2} ## {3} = {4}\n'.format(E,H,P,T,O)
				S.write(F)
			else:S.write("# all other, type = '{0}'\n".format(T));S.write(E+H+' # type: Incomplete\n')
	@property
	def flat_fwid(self):
		"Turn _fwid from 'v1.2.3' into '1_2_3' to be used in filename";A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(B,path=D):
		'Remove all files from the stub folder'
		if not path:path=B.path
		C.info('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);D=os.listdir(path)
		except(E,H):return
		for F in D:
			A=u.format(path,F)
			try:os.remove(A)
			except E:
				try:B.clean(A);os.rmdir(A)
				except E:pass
	def report_start(B,filename=v):
		'Start a report of the modules that have been stubbed\n        "create json with list of exported modules';F='firmware';B._json_name=u.format(B.path,filename);B._json_first=N;i(B._json_name);C.info('Report file: {}'.format(B._json_name));K.collect()
		try:
			with M(B._json_name,t)as D:D.write('{');D.write(dumps({F:B.info})[1:-1]);D.write(w);D.write(dumps({A7:{A:__version__},'stubtype':F})[1:-1]);D.write(w);D.write('"modules" :[\n')
		except E as G:C.error(AB);B._json_name=J;raise G
	def report_add(A,module_name,stub_file):
		'Add a module to the report'
		if not A._json_name:raise R(AC)
		try:
			with M(A._json_name,'a')as D:
				if not A._json_first:D.write(w)
				else:A._json_first=B
				F='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',G));D.write(F)
		except E:C.error(AB)
	def report_end(A):
		if not A._json_name:raise R(AC)
		with M(A._json_name,'a')as B:B.write('\n]}')
		C.info('Path: {}'.format(A.path))
def i(path):
	'Create nested folders if needed';A=D=0
	while A!=-1:
		A=path.find(G,D)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except E as F:
				if F.args[0]in[AE,AF]:
					try:C.debug('Create folder {}'.format(B));os.mkdir(B)
					except E as H:C.error('failed to create folder {}'.format(B));raise H
		D=A+1
def j(s):
	B=' on '
	if not s:return D
	s=s.split(B,1)[0]if B in s else s
	if s.startswith('v'):
		if not F in s:return D
		A=s.split(F)[1];return A
	if not b in s:return D
	A=s.split(b)[1].split(P)[1];return A
def AH():
	'Get basic system implementation details.'
	try:B=sys.implementation[0]
	except o:B=sys.implementation.name
	C=z({a:B,A:D,Q:D,'ver':D,I:sys.platform,W:'UNKNOWN',X:D,x:D,'cpu':D,S:D,y:D});return C
def AJ(info):
	'Normalize port names to be consistent with the repo.';A=info
	if A[I].startswith('pyb'):A[I]='stm32'
	elif A[I]=='win32':A[I]='windows'
	elif A[I]=='linux':A[I]='unix'
def AK(info):
	'Extract version information from sys.implementation.'
	try:info[A]=AR(sys.implementation.version)
	except H:pass
def AL(info):
	'Extract board, CPU, and machine details.';A=info
	try:
		C=sys.implementation._machine if'_machine'in O(sys.implementation)else os.uname().machine;A[W]=C.strip();B=sys.implementation._build if'_build'in O(sys.implementation)else D
		if B:A[W]=B.split(F)[0];A[x]=B.split(F)[1]if F in B else D
		A[X]=B;A['cpu']=C.split('with')[-1].strip();A[S]=sys.implementation._mpy if'_mpy'in O(sys.implementation)else sys.implementation.mpy if S in O(sys.implementation)else D
	except(H,V):pass
	if not A[X]:AS(A)
def AM(info):
	'Extract build information from various system sources.';B=info
	try:
		if'uname'in O(os):
			B[Q]=j(os.uname()[3])
			if not B[Q]:B[Q]=j(os.uname()[2])
		elif A in O(sys):B[Q]=j(sys.version)
	except(H,V,o):pass
	if B[A]==D and sys.platform not in('unix','win32'):
		try:C=os.uname();B[A]=C.release
		except(V,H,o):pass
def AN(info):
	'Detect special firmware families (pycopy, pycom, ev3-pybricks).';D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,J,J,G);A[a]=E;del H;break
		except(T,A4):pass
	if A[a]==D:A['release']='2.0.0'
def AO(info):
	'Process MicroPython-specific version formatting.';B=info
	if B[a]==A8:
		if B[A]and B[A].endswith('.0')and B[A]>='1.10.0'and B[A]<='1.19.9':B[A]=B[A][:-2]
def AP(info):
	'Process MPY architecture and version information.';A=info
	if S in A and A[S]:
		B=int(A[S])
		try:
			C=[J,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[y]=C
		except V:A[y]='unknown'
		A[S]='v{}.{}'.format(B&255,B>>8&3)
def AQ(info):
	'Handle final version string formatting.';B=info
	if B[Q]and not B[A].endswith(b):B[A]=B[A]+b
	B['ver']=f"{B[A]}-{B[Q]}"if B[Q]else f"{B[A]}"
def _info():'\n    Gather comprehensive system information for MicroPython stubbing.\n\n    Returns a dictionary containing family, version, port, board, and other\n    system details needed for stub generation.\n    ';A=AH();AJ(A);AK(A);AL(A);AM(A);AN(A);AO(A);AP(A);AQ(A);return A
def AR(version):
	A=version;B=P.join([e(A)for A in A[:3]])
	if Y(A)>3 and A[3]:B+=F+A[3]
	return B
def AS(info):
	'Read the board_id from the boardname.py file that may have been created upfront';B=info
	try:from boardname import BOARD_ID as A;C.info('Found BOARD_ID: {}'.format(A))
	except T:C.warning('BOARD_ID not found');A=D
	B[X]=A;B[W]=A.split(F)[0]if F in A else A;B[x]==A.split(F)[1]if F in A else D
def get_root():
	'Determine the root folder of the device'
	try:A=os.getcwd()
	except(E,H):A=P
	B=A
	for B in['/remote','/sd','/flash',G,A,P]:
		try:C=os.stat(B);break
		except E:continue
	return B
def k(filename):
	try:
		if os.stat(filename)[0]>>14:return N
		return B
	except E:return B
def A1():U("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	'get --path from cmdline. [unix/win]';path=D
	if Y(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:A1()
	elif Y(sys.argv)==2:A1()
	return path
def A2():
	'runtime test to determine full or micropython'
	try:A=bytes('abc',encoding='utf8');C=A2.__module__;return B
	except(A3,H):return N
l='modulelist.done'
def AT(skip=0):
	for D in AG:
		B=D+'/modulelist.txt'
		if not k(B):continue
		try:
			with M(B,encoding='utf-8')as F:
				C=0
				while N:
					A=F.readline().strip()
					if not A:break
					if Y(A)>0 and A[0]=='#':continue
					C+=1
					if C<skip:continue
					yield A
				break
		except E:pass
def AU(done):
	with M(l,t)as A:A.write(e(done)+f)
def AV():
	A=0
	try:
		with M(l)as B:A=int(B.readline().strip())
	except E:pass
	return A
def main():
	import machine as D;B=k(l)
	if B:C.info('Continue from last run')
	else:C.info('Starting new run')
	stubber=Stubber(path=read_path());A=0
	if not B:stubber.clean();stubber.report_start(v)
	else:A=AV();stubber._json_name=u.format(stubber.path,v)
	for E in AT(A):
		try:stubber.create_one_stub(E)
		except n:D.reset()
		K.collect();A+=1;AU(A)
	U('All modules have been processed, Finalizing report');stubber.report_end()
if __name__=='__main__'or A2():
	if not k('no_auto_stubber.txt'):
		U(f"createstubs.py: {__version__}")
		try:K.threshold(4096);K.enable()
		except BaseException:pass
		main()