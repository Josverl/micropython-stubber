q='machine'
p='nodename'
o='{}/{}'
n='method'
m='function'
l='bool'
k='str'
j='float'
i='int'
h=Exception
g=NameError
f=sorted
e=NotImplementedError
A=',\n'
Z='_'
Y='dict'
X='list'
W='tuple'
V=IndexError
U=repr
T='-'
S='sysname'
R='version'
Q=True
P='v'
O='build'
N=len
M=KeyError
L=ImportError
K='.'
J=print
I=AttributeError
H=False
G=''
F='/'
D=None
C=OSError
B='release'
import gc as E,sys,uos as os
from ujson import dumps as a
try:from collections import OrderedDict
except L:from ucollections import OrderedDict
__version__='v1.12.2'
r=2
s=2
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise e('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();E.collect()
		if B:A._fwid=B.lower()
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info).lower()
		A._start_free=E.mem_free()
		if path:
			if path.endswith(F):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',F)
		try:b(path+F)
		except C:J('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		F=item_instance;A=[];J=[]
		for H in dir(F):
			try:
				B=getattr(F,H)
				try:C=U(type(B)).split("'")[1]
				except V:C=G
				if C in{i,j,k,l,W,X,Y}:D=1
				elif C in{m,n}:D=2
				elif C in'class':D=3
				else:D=4
				A.append((H,U(B),U(type(B)),B,D))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(H,F,K))
		A=f([A for A in A if not A[0].startswith(Z)],key=lambda x:x[4]);E.collect();return A,J
	def add_modules(A,modules):A.modules=f(set(A.modules)|set(modules))
	def create_all_stubs(A):
		E.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(A,module_name):
		B=module_name
		if B in A.problematic:return H
		if B in A.excluded:return H
		G='{}/{}.py'.format(A.path,B.replace(K,F));E.collect();D=H
		try:D=A.create_module_stub(B,G)
		except C:return H
		E.collect();return D
	def create_module_stub(I,module_name,file_name=D):
		B=file_name;A=module_name
		if B is D:B=I.path+F+A.replace(K,Z)+'.py'
		if F in A:A=A.replace(F,K)
		N=D
		try:N=__import__(A,D,D,'*');J('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,B,E.mem_free()))
		except L:return H
		b(B)
		with open(B,'w')as O:P='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,I._fwid,I.info,__version__);O.write(P);O.write('from typing import Any\n\n');I.write_object_stub(O,N,A,G)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(A,B.replace('\\',F)))
		if A not in{'os','sys','logging','gc'}:
			try:del N
			except (C,M):pass
			try:del sys.modules[A]
			except M:pass
		E.collect();return Q
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';R=in_class;Q=object_expr;P='Exception';H=fp;B=indent;E.collect()
		if Q in L.problematic:return
		S,O=L.get_obj_attributes(Q)
		if O:J(O)
		for (D,K,F,T,f) in S:
			if D in['classmethod','staticmethod','BaseException',P]:continue
			if F=="<class 'type'>"and N(B)<=s*4:
				U=G;V=D.endswith(P)or D.endswith('Error')or D in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=P
				A='\n{}class {}({}):\n'.format(B,D,U)
				if V:A+=B+'    ...\n';H.write(A);return
				H.write(A);L.write_object_stub(H,T,'{0}.{1}'.format(obj_name,D),B+'    ',R+1);A=B+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=B+'        ...\n\n';H.write(A)
			elif n in F or m in F:
				Z=b;a=G
				if R>0:a='self, '
				if c in F or c in K:A='{}@classmethod\n'.format(B)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(B,D,Z)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(B,D,a,Z)
				A+=B+'    ...\n\n';H.write(A)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				I=F[8:-2];A=G
				if I in[k,i,j,l,'bytearray','bytes']:A=d.format(B,D,K,I)
				elif I in[Y,X,W]:e={Y:'{}',X:'[]',W:'()'};A=d.format(B,D,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(B,D,I,F,K)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(F));H.write(B+D+' # type: Any\n')
		del S;del O
		try:del D,K,F,T
		except (C,M,g):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,Z)
		return A
	def clean(B,path=D):
		if path is D:path=B.path
		J('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);E=os.listdir(path)
		except (C,I):return
		for F in E:
			A=o.format(path,F)
			try:os.remove(A)
			except C:
				try:B.clean(A);os.rmdir(A)
				except C:pass
	def report(A,filename='modules.json'):
		J('Created stubs for {} modules on board {}\nPath: {}'.format(N(A._report),A._fwid,A.path));F=o.format(A.path,filename);E.collect()
		try:
			with open(F,'w')as B:
				A.write_json_header(B);D=Q
				for G in A._report:A.write_json_node(B,G,D);D=H
				A.write_json_end(B)
			I=A._start_free-E.mem_free()
		except C:J('Failed to create the report.')
	def write_json_header(C,f):B='firmware';f.write('{');f.write(a({B:C.info})[1:-1]);f.write(A);f.write(a({'stubber':{R:__version__},'stubtype':B})[1:-1]);f.write(A);f.write('"modules" :[\n')
	def write_json_node(B,f,n,first):
		if not first:f.write(A)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def b(path):
	A=D=0
	while A!=-1:
		A=path.find(F,D)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except C as E:
				if E.args[0]==r:
					try:os.mkdir(B)
					except C as G:J('failed to create folder {}'.format(B));raise G
		D=A+1
def _info():
	a='0.0.0';Z='port';Y='platform';X='name';J='mpy';H='unknown';E='family';C='ver';Q=sys.implementation.name;U='stm32'if sys.platform.startswith('pyb')else sys.platform;A={X:Q,B:a,R:a,O:G,S:H,p:H,q:H,E:Q,Y:U,Z:U,C:G}
	try:A[B]=K.join([str(A)for A in sys.implementation.version]);A[R]=A[B];A[X]=sys.implementation.name;A[J]=sys.implementation.mpy
	except I:pass
	if sys.platform not in('unix','win32'):
		try:t(A)
		except (V,I,TypeError):pass
	try:from pycopy import const as F;A[E]='pycopy';del F
	except (L,M):pass
	try:from pycom import FAT as F;A[E]='pycom';del F
	except (L,M):pass
	if A[Y]=='esp32_LoBo':A[E]='loboris';A[Z]='esp32'
	elif A[S]=='ev3':
		A[E]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except L:pass
	if A[B]:A[C]=P+A[B].lstrip(P)
	if A[E]=='micropython':
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[O]!=G and N(A[O])<4:A[C]+=T+A[O]
	if A[C][0]!=P:A[C]=P+A[C]
	if J in A:
		b=int(A[J]);W=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][b>>10]
		if W:A['arch']=W
	return A
def t(info):
	E=' on ';A=info;C=os.uname();A[S]=C[0];A[p]=C[1];A[B]=C[2];A[q]=C[4]
	if E in C[3]:
		D=C[3].split(E)[0]
		if A[S]=='esp8266':F=D.split(T)[0]if T in D else D;A[R]=A[B]=F.lstrip(P)
		try:A[O]=D.split(T)[1]
		except V:pass
def get_root():
	try:A=os.getcwd()
	except (C,I):A=K
	B=A
	for B in [A,'/sd','/flash',F,K]:
		try:D=os.stat(B);break
		except C:continue
	return B
def u(filename):
	try:os.stat(filename);return Q
	except C:return H
def c():sys.exit(1)
def read_path():
	path=G
	if N(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:c()
	elif N(sys.argv)==2:c()
	return path
def d():
	try:A=bytes('abc',encoding='utf8');B=d.__module__;return H
	except (e,I):return Q
def main():
	C='lvgl'
	try:import lvgl as A
	except h:return
	B=C
	try:B='lvgl-{0}_{1}_{2}-{3}-{4}'.format(A.version_major(),A.version_minor(),A.version_patch(),A.version_info(),sys.platform)
	except h:B='lvgl-{0}_{1}_{2}_{3}-{4}'.format(8,1,0,'dev',sys.platform)
	finally:stubber=Stubber(firmware_id=B)
	stubber.clean();stubber.modules=['io','lodepng','rtch',C];E.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or d():
	try:logging.basicConfig(level=logging.INFO)
	except g:pass
	if not u('no_auto_stubber.txt'):main()