'Create stubs for (all) modules on a MicroPython board.\n\n    This variant of the createstubs.py script is optimised for use on low-memory devices, and reads the list of modules from a text file\n    `modulelist.txt` in the root or `libs` folder that should be uploaded to the device.\n    If that cannot be found then only a single module (micropython) is stubbed.\n    In order to run this on low-memory devices two additional steps are recommended:\n    - minifification, using python-minifier\n      to reduce overall size, and remove logging overhead.\n    - cross compilation, using mpy-cross,\n      to avoid the compilation step on the micropython device\n\nThis variant was generated from createstubs.py by micropython-stubber v1.28.2\n'
A6='No report file'
A5='Failed to create the report.'
A4='method'
A3='function'
A2='stubber'
A1=isinstance
A0=KeyError
z=MemoryError
y=NotImplementedError
s='arch'
r='variant'
q=',\n'
p='dict'
o='list'
n='tuple'
m='__'
l='micropython'
k=TypeError
j=repr
b='-preview'
e=str
d=getattr
Z='family'
Y='board_id'
W='board'
c=len
V=IndexError
U=open
T=print
S=ImportError
Q='mpy'
X='*'
P='build'
O='.'
M=dir
I='port'
H=AttributeError
R=Exception
G='-'
N=True
E=OSError
K=None
A='version'
F='/'
C=''
B=False
import gc as J,os,sys
from time import sleep
try:from ujson import dumps
except:from json import dumps
try:from machine import reset as f
except S:
	def f():T('Reset called - exiting');sys.exit(0)
try:from collections import OrderedDict as t
except S:from ucollections import OrderedDict as t
u='esp8266',
A7=sys.platform in u
g=B
if not A7:
	try:import inspect as a;g=N
	except S:g=B
__version__='v1.28.2'
A8=2
A9=44
AA=2
AB=['lib','/lib','/sd/lib','/flash/lib',O]
class L:
	DEBUG=10;INFO=20;WARNING=30;ERROR=40;level=INFO;prnt=T
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
D=L.getLogger(A2)
L.basicConfig(level=L.INFO)
class Stubber:
	'Generate stubs for modules in firmware'
	def __init__(A,path=C,firmware_id=C):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise y('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A.info=_info();D.info('Port: {}'.format(A.info[I]));D.info('Board: {}'.format(A.info[W]));D.info('Board_ID: {}'.format(A.info[Y]));A._is_low_mem_port=A.info[I]in u;A._capture_docstrings=not A._is_low_mem_port;A._use_inspect=g and not A._is_low_mem_port
		if A._is_low_mem_port:D.info('Low-memory mode: disabling inspect and docstrings')
		J.collect()
		if C:A._fwid=C.lower()
		elif A.info[Z]==l:A._fwid='{family}-v{version}-{port}-{board_id}'.format(**A.info).rstrip(G)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=J.mem_free()
		if path:
			if path.endswith(F):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',F)
		try:h(path+F)
		except E:D.error('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.load_exlusions();A.modules=[];A._json_name=K;A._json_first=B
	def load_exlusions(B):
		try:
			with U('modulelist_exclude.txt','r')as C:
				for F in C:
					A=F.strip()
					if A and A not in B.excluded:B.excluded.append(A);D.info('Added {} to excluded modules from modulelist_exclude.txt'.format(A))
		except E:pass
	def get_obj_attributes(L,item_instance):
		'extract information of the objects members and attributes';G=item_instance;B=[];K=[]
		for A in M(G):
			if A.startswith(m)and not A in L.modules:continue
			try:
				D=d(G,A)
				try:E=j(type(D)).split("'")[1]
				except V:E=C
				if E in{'int','float','str','bool',n,o,p}:F=1
				elif E in{A3,A4}:F=2
				elif E in'class':F=3
				else:F=4
				B.append((A,j(D),j(type(D)),D,F))
			except H as I:K.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,G,I))
			except z as I:T('MemoryError: {}'.format(I));sleep(1);f()
		B=sorted([A for A in B if not A[0].startswith(m)],key=lambda x:x[4]);J.collect();return B,K
	def add_modules(A,modules):'Add additional modules to be exported';A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		'Create stubs for all configured modules';D.info('Start micropython-stubber {} on {}'.format(__version__,A._fwid));A.report_start();J.collect()
		for B in A.modules:A.create_one_stub(B)
		A.report_end();D.info('Finally done')
	def create_one_stub(C,module_name):
		A=module_name
		if A in C.problematic:D.warning('Skip module: {:<25}        : Known problematic'.format(A));return B
		if A in C.excluded:D.warning('Skip module: {:<25}        : Excluded'.format(A));return B
		H='{}/{}.pyi'.format(C.path,A.replace(O,F));J.collect();G=B
		try:G=C.create_module_stub(A,H)
		except E:return B
		J.collect();return G
	def create_module_stub(G,module_name,file_name=K):
		"Create a Stub of a single python module\n\n        Args:\n        - module_name (str): name of the module to document. This module will be imported.\n        - file_name (Optional[str]): the 'path/filename.pyi' to write to. If omitted will be created based on the module name.\n        ";H=file_name;A=module_name
		if H is K:M=A.replace(O,'_')+'.pyi';H=G.path+F+M
		else:M=H.split(F)[-1]
		if F in A:A=A.replace(F,O)
		I=K
		try:I=__import__(A,K,K,X);P=J.mem_free();D.info('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,M,P))
		except S:return B
		h(H)
		with U(H,'w')as L:
			Q=e(G.info).replace('OrderedDict(',C).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,G._fwid,Q,__version__);L.write(R);L.write('from __future__ import annotations\nfrom typing import Any, Final, Generator, AsyncGenerator\nfrom _typeshed import Incomplete\n\n')
			if G._is_low_mem_port and A in{'builtins','uasyncio.__init__'}:D.warning('Low-memory mode: using shallow stub strategy.');G.write_shallow_stub(L,I)
			else:
				try:G.write_object_stub(L,I,A,C)
				except z:
					if not G._is_low_mem_port:raise
					J.collect();D.warning('Low-memory mode: MemoryError while stubbing {}, resetting'.format(A));f()
		G.report_add(A,H)
		if A not in{'os','sys','logging','gc'}:
			try:del I
			except(E,A0):D.warning('could not del new_module')
		J.collect();return N
	def write_shallow_stub(B,fp,module_obj):
		fp.write('# Low-memory mode: shallow stub with names only\n')
		for A in M(module_obj):
			if A.startswith(m)and not A in B.modules:continue
			if not A or A[0].isdigit():continue
			fp.write('{}: Incomplete\n'.format(A))
	def write_object_stub(V,fp,object_expr,obj_name,indent,in_class=0):
		'Write a module/object stub to an open file. Can be called recursive.';A9=' at ...>';A8='{0}{1}: {3} = {2}\n';A7='bound_method';A6='{}*args, **kwargs';A5='Incomplete';A2='    """{0}"""\n';A0='\\"\\"\\"';t='    ';s='Exception';k=object_expr;j=' at ';i=', ';h='self, ';g='\n';Y=in_class;S=fp;E=indent;J.collect()
		if k in V.problematic:D.warning('SKIPPING problematic module:{}'.format(k));return
		AB,u=V.get_obj_attributes(k)
		if u:D.error(u)
		for(G,O,T,U,_)in AB:
			if G in['classmethod','staticmethod','BaseException',s]:continue
			if G[0].isdigit():D.warning('NameError: invalid name {}'.format(G));continue
			if T=="<class 'type'>"and c(E)<=AA*4:
				v=C;w=G.endswith(s)or G.endswith('Error')or G in['KeyboardInterrupt','StopIteration','SystemExit']
				if w:v=s
				H='\n{}class {}({}):\n'.format(E,G,v)
				if w:H+=E+'    ...\n';S.write(H);continue
				S.write(H)
				if V._capture_docstrings:
					try:
						L=U.__doc__
						if L and A1(L,e):
							L=L.strip().replace('"""',A0).replace(g,g+E+t)
							if L:S.write(E+A2.format(L))
					except R:pass
				V.write_object_stub(S,U,'{0}.{1}'.format(obj_name,G),E+t,Y+1);H=E+'    def __init__(self, *argv, **kwargs) -> None:\n';H+=E+'        ...\n\n';S.write(H)
			elif any(A in T for A in[A4,A3,'closure']):
				l=A5;x=C
				if Y>0:x=h
				f=B;m=B;y=B
				if V._use_inspect:
					try:f=a.iscoroutinefunction(U)
					except R:pass
					if not f:
						try:m=d(a,'isasyncgenfunction',lambda _:B)(U)
						except R:pass
					if not f and not m:
						try:y=a.isgeneratorfunction(U)
						except R:pass
				W=K
				if V._use_inspect:
					try:
						q=a.signature(U);A=[];I=B;Z=B
						for(M,r)in q.parameters.items():
							Q=d(r,'kind',K)
							if Q==0:I=N;A.append(M)
							elif Q==1:
								if I:A.append(F);I=B
								A.append(M)
							elif Q==2:
								if I:A.append(F);I=B
								Z=N;A.append(X+M)
							elif Q==3:
								if I:A.append(F);I=B
								if not Z:A.append(X);Z=N
								A.append(M)
							elif Q==4:
								if I:A.append(F);I=B
								A.append('**'+M)
							else:A.append(M)
						if I:A.append(F)
						if Y>0 and A and A[0]not in(X,F):A=A[1:]
						if Y>0:W=h+i.join(A)if A else'self'
						else:W=i.join(A)
					except R:pass
				if W is K:W=A6.format(x)
				if A7 in T or A7 in O:H='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,G,l)
				elif f:H='{}async def {}({}) -> {}:\n'.format(E,G,W,l)
				elif m:H='{}async def {}({}) -> AsyncGenerator:\n'.format(E,G,W)
				elif y:H='{}def {}({}) -> Generator:\n'.format(E,G,W)
				else:H='{}def {}({}) -> {}:\n'.format(E,G,W,l)
				if V._capture_docstrings:
					try:
						L=U.__doc__
						if L and A1(L,e):
							L=L.strip().replace('"""',A0).replace(g,g+E+t)
							if L:H+=E+A2.format(L)
					except R:pass
				H+=E+'    ...\n\n';S.write(H)
			elif T=="<class 'module'>":0
			elif T.startswith("<class '"):
				P=T[8:-2];H=C
				if P in('str','int','float','bool','bytearray','bytes'):
					if G.upper()==G:H='{0}{1}: Final[{3}] = {2}\n'.format(E,G,O,P)
					else:H=A8.format(E,G,O,P)
				elif P in(p,o,n):AC={p:'{}',o:'[]',n:'()'};H=A8.format(E,G,AC[P],P)
				elif P in('object','set','frozenset','Pin'):H='{0}{1}: {2} ## = {4}\n'.format(E,G,P,T,O)
				elif P=='generator':
					AD=h if Y>0 else C;b=K;z=B
					if V._use_inspect:
						try:z=a.iscoroutinefunction(U)
						except R:pass
						try:
							q=a.signature(U);A=[];I=B;Z=B
							for(M,r)in q.parameters.items():
								Q=d(r,'kind',K)
								if Q==0:I=N;A.append(M)
								elif Q==1:
									if I:A.append(F);I=B
									A.append(M)
								elif Q==2:
									if I:A.append(F);I=B
									Z=N;A.append(X+M)
								elif Q==3:
									if I:A.append(F);I=B
									if not Z:A.append(X);Z=N
									A.append(M)
								elif Q==4:
									if I:A.append(F);I=B
									A.append('**'+M)
								else:A.append(M)
							if I:A.append(F)
							if Y>0 and A and A[0]not in(X,F):A=A[1:]
							if Y>0:b=h+i.join(A)if A else'self'
							else:b=i.join(A)
						except R:pass
					if b is K:b=A6.format(AD)
					if z:H='{0}async def {1}({2}) -> Incomplete:\n{0}    ...\n\n'.format(E,G,b)
					else:H='{0}def {1}({2}) -> Generator:  ## = {4}\n{0}    ...\n\n'.format(E,G,b,P,O)
				else:
					P=A5
					if j in O:O=O.split(j)[0]+A9
					if j in O:O=O.split(j)[0]+A9
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
			A='{}/{}'.format(path,F)
			try:os.remove(A)
			except E:
				try:B.clean(A);os.rmdir(A)
				except E:pass
	def report_start(B,filename='modules.json'):
		'Start a report of the modules that have been stubbed\n        "create json with list of exported modules';F='firmware';B._json_name='{}/{}'.format(B.path,filename);B._json_first=N;h(B._json_name);D.info('Report file: {}'.format(B._json_name));J.collect()
		try:
			with U(B._json_name,'w')as C:C.write('{');C.write(dumps({F:B.info})[1:-1]);C.write(q);C.write(dumps({A2:{A:__version__},'stubtype':F})[1:-1]);C.write(q);C.write('"modules" :[\n')
		except E as G:D.error(A5);B._json_name=K;raise G
	def report_add(A,module_name,stub_file):
		'Add a module to the report'
		if not A._json_name:raise R(A6)
		try:
			with U(A._json_name,'a')as C:
				if not A._json_first:C.write(q)
				else:A._json_first=B
				G='{{"module": "{}", "file": "{}"}}'.format(module_name,stub_file.replace('\\',F));C.write(G)
		except E:D.error(A5)
	def report_end(A):
		if not A._json_name:raise R(A6)
		with U(A._json_name,'a')as B:B.write('\n]}')
		D.info('Path: {}'.format(A.path))
def h(path):
	'Create nested folders if needed';A=C=0
	while A!=-1:
		A=path.find(F,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:I=os.stat(B)
			except E as G:
				if G.args[0]in[A8,A9]:
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
	if not b in s:return C
	A=s.split(b)[1].split(O)[1];return A
def AC():
	'Get basic system implementation details.'
	try:B=sys.implementation[0]
	except k:B=sys.implementation.name
	D=t({Z:B,A:C,P:C,'ver':C,I:sys.platform,W:'UNKNOWN',Y:C,r:C,'cpu':C,Q:C,s:C});return D
def AD(info):
	'Normalize port names to be consistent with the repo.';A=info
	if A[I].startswith('pyb'):A[I]='stm32'
	elif A[I]=='win32':A[I]='windows'
	elif A[I]=='linux':A[I]='unix'
def AE(info):
	'Extract version information from sys.implementation.'
	try:info[A]=AL(sys.implementation.version)
	except H:pass
def AF(info):
	'Extract board, CPU, and machine details.';A=info
	try:
		D=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[W]=D.strip();B=sys.implementation._build if'_build'in M(sys.implementation)else C
		if B:A[W]=B.split(G)[0];A[r]=B.split(G)[1]if G in B else C
		A[Y]=B;A['cpu']=D.split('with')[-1].strip();A[Q]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if Q in M(sys.implementation)else C
	except(H,V):pass
	if not A[Y]:AM(A)
def AG(info):
	'Extract build information from various system sources.';B=info
	try:
		if'uname'in M(os):
			B[P]=i(os.uname()[3])
			if not B[P]:B[P]=i(os.uname()[2])
		elif A in M(sys):B[P]=i(sys.version)
	except(H,V,k):pass
	if B[A]==C and sys.platform not in('unix','win32'):
		try:D=os.uname();B[A]=D.release
		except(V,H,k):pass
def AH(info):
	'Detect special firmware families (pycopy, pycom, ev3-pybricks).';D='ev3-pybricks';C='pycom';B='pycopy';A=info
	for(E,F,G)in[(B,B,'const'),(C,C,'FAT'),(D,'pybricks.hubs','EV3Brick')]:
		try:H=__import__(F,K,K,G);A[Z]=E;del H;break
		except(S,A0):pass
	if A[Z]==D:A['release']='2.0.0'
def AI(info):
	'Process MicroPython-specific version formatting.';B=info
	if B[Z]==l:
		if B[A]and B[A].endswith('.0')and B[A]>='1.10.0'and B[A]<='1.19.9':B[A]=B[A][:-2]
def AJ(info):
	'Process MPY architecture and version information.';A=info
	if Q in A and A[Q]:
		B=int(A[Q])
		try:
			C=[K,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin','rv32imc'][B>>10]
			if C:A[s]=C
		except V:A[s]='unknown'
		A[Q]='v{}.{}'.format(B&255,B>>8&3)
def AK(info):
	'Handle final version string formatting.';B=info
	if B[P]and not B[A].endswith(b):B[A]=B[A]+b
	B['ver']=f"{B[A]}-{B[P]}"if B[P]else f"{B[A]}"
def _info():'\n    Gather comprehensive system information for MicroPython stubbing.\n\n    Returns a dictionary containing family, version, port, board, and other\n    system details needed for stub generation.\n    ';A=AC();AD(A);AE(A);AF(A);AG(A);AH(A);AI(A);AJ(A);AK(A);return A
def AL(version):
	A=version;B=O.join([e(A)for A in A[:3]])
	if c(A)>3 and A[3]:B+=G+A[3]
	return B
def AM(info):
	'Read the board_id from the boardname.py file that may have been created upfront';B=info
	try:from boardname import BOARD_ID as A;D.info('Found BOARD_ID: {}'.format(A))
	except S:D.warning('BOARD_ID not found');A=C
	B[Y]=A;B[W]=A.split(G)[0]if G in A else A;B[r]==A.split(G)[1]if G in A else C
def get_root():
	'Determine the root folder of the device'
	try:A=os.getcwd()
	except(E,H):A=O
	B=A
	for B in['/remote','/sd','/flash',F,A,O]:
		try:C=os.stat(B);break
		except E:continue
	return B
def v(filename):
	try:
		if os.stat(filename)[0]>>14:return N
		return B
	except E:return B
def w():T("-p, --path   path to store the stubs in, defaults to '.'");sys.exit(1)
def read_path():
	'get --path from cmdline. [unix/win]';path=C
	if c(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:w()
	elif c(sys.argv)==2:w()
	return path
def x():
	'runtime test to determine full or micropython'
	try:A=bytes('abc',encoding='utf8');C=x.__module__;return B
	except(y,H):return N
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	def A(stubber):
		J.collect();stubber.modules=[]
		for C in AB:
			B=C+'/modulelist.txt'
			if not v(B):continue
			with U(B)as D:
				while N:
					A=D.readline().strip()
					if not A:break
					if c(A)>0 and A[0]!='#':stubber.modules.append(A)
				J.collect();T('BREAK');break
		if not stubber.modules:stubber.modules=[l]
		J.collect()
	stubber.modules=[];A(stubber);J.collect();stubber.create_all_stubs()
if __name__=='__main__'or x():
	if not v('no_auto_stubber.txt'):
		T(f"createstubs.py: {__version__}")
		try:J.threshold(4096);J.enable()
		except BaseException:pass
		main()