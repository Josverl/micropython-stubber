v='with'
u='stubber'
t='{}/{}'
s='method'
r='function'
q='bool'
p='str'
o='float'
n='int'
m='micropython'
l=Exception
k=TypeError
j=NameError
i=sorted
h=NotImplementedError
b='-'
a=',\n'
Z='dict'
Y='list'
X='tuple'
W=open
V=repr
T='cpu'
S='_'
R=len
Q=KeyError
P=IndexError
O=print
N=ImportError
M='family'
L=dir
K=True
J='.'
I=AttributeError
H='board'
A=False
G='/'
E=None
F=OSError
C='version'
B=''
import gc as D,os,sys
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except N:pass
try:from collections import OrderedDict as c
except N:from ucollections import OrderedDict as c
__version__='v1.16.2'
w=2
x=2
y=[J,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise h('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();D.collect()
		if B:A._fwid=B.lower()
		elif A.info[M]==m:A._fwid='{family}-v{version}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=D.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:d(path+G)
		except F:O('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(M,item_instance):
		H=item_instance;C=[];J=[]
		for A in L(H):
			if A.startswith(S)and not A in M.modules:continue
			try:
				E=getattr(H,A)
				try:F=V(type(E)).split("'")[1]
				except P:F=B
				if F in{n,o,p,q,X,Y,Z}:G=1
				elif F in{r,s}:G=2
				elif F in'class':G=3
				else:G=4
				C.append((A,V(E),V(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,K))
			except MemoryError as K:sleep(1);reset()
		C=i([A for A in C if not A[0].startswith('__')],key=lambda x:x[4]);D.collect();return C,J
	def add_modules(A,modules):A.modules=i(set(A.modules)|set(modules))
	def create_all_stubs(A):
		D.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(B,module_name):
		C=module_name
		if C in B.problematic:return A
		if C in B.excluded:return A
		H='{}/{}.py'.format(B.path,C.replace(J,G));D.collect();E=A
		try:E=B.create_module_stub(C,H)
		except F:return A
		D.collect();return E
	def create_module_stub(I,module_name,file_name=E):
		H=file_name;C=module_name
		if H is E:O=C.replace(J,S)+'.py';H=I.path+G+O
		else:O=H.split(G)[-1]
		if G in C:C=C.replace(G,J)
		L=E
		try:L=__import__(C,E,E,'*');T=D.mem_free()
		except N:return A
		d(H)
		with W(H,'w')as M:P=str(I.info).replace('OrderedDict(',B).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(C,I._fwid,P,__version__);M.write(R);M.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(M,L,C,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(C,H.replace('\\',G)))
		if C not in{'os','sys','logging','gc'}:
			try:del L
			except(F,Q):pass
			try:del sys.modules[C]
			except Q:pass
		D.collect();return K
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Incomplete';P=in_class;N=object_expr;M='Exception';H=fp;C=indent;D.collect()
		if N in K.problematic:return
		S,L=K.get_obj_attributes(N)
		if L:O(L)
		for(E,J,G,T,f)in S:
			if E in['classmethod','staticmethod','BaseException',M]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and R(C)<=x*4:
				U=B;V=E.endswith(M)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=M
				A='\n{}class {}({}):\n'.format(C,E,U)
				if V:A+=C+'    ...\n';H.write(A);return
				H.write(A);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),C+'    ',P+1);A=C+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=C+'        ...\n\n';H.write(A)
			elif any(A in G for A in[s,r,'closure']):
				W=b;a=B
				if P>0:a='self, '
				if c in G or c in J:A='{}@classmethod\n'.format(C)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(C,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(C,E,a,W)
				A+=C+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[p,n,o,q,'bytearray','bytes']:A=d.format(C,E,J,I)
				elif I in[Z,Y,X]:e={Z:'{}',Y:'[]',X:'()'};A=d.format(C,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(C,E,I,G,J)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(C+E+' # type: Incomplete\n')
		del S;del L
		try:del E,J,G,T
		except(F,Q,j):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,S)
		return A
	def clean(B,path=E):
		if path is E:path=B.path
		try:os.stat(path);C=os.listdir(path)
		except(F,I):return
		for D in C:
			A=t.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(B,filename='modules.json'):
		G=t.format(B.path,filename);D.collect()
		try:
			with W(G,'w')as C:
				B.write_json_header(C);E=K
				for H in B._report:B.write_json_node(C,H,E);E=A
				B.write_json_end(C)
			I=B._start_free-D.mem_free()
		except F:O('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(dumps({A:B.info})[1:-1]);f.write(a);f.write(dumps({u:{C:__version__},'stubtype':A})[1:-1]);f.write(a);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(a)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def d(path):
	A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except F as D:
				if D.args[0]==w:
					try:os.mkdir(B)
					except F as E:O('failed to create folder {}'.format(B));raise E
		C=A+1
def U(s):
	A=' on '
	if not s:return B
	s=s.split(A,1)[0]if A in s else s;s=s.split('; ',1)[1]if'; 'in s else s;C=s.split(b)[1]if s.startswith('v')else s.split(b,1)[-1].split(J)[1];return C
def _info():
	b='-preview';a='ev3-pybricks';Z='pycom';Y='pycopy';X='unix';W='win32';V='arch';S='ver';J='mpy';G='port';F='build';A=c({M:sys.implementation.name,C:B,F:B,S:B,G:sys.platform,H:'UNKNOWN',T:B,J:B,V:B})
	if A[G].startswith('pyb'):A[G]='stm32'
	elif A[G]==W:A[G]='windows'
	elif A[G]=='linux':A[G]=X
	try:A[C]=z(sys.implementation.version)
	except I:pass
	try:O=sys.implementation._machine if'_machine'in L(sys.implementation)else os.uname().machine;A[H]=O;A[T]=O.split(v)[-1].strip();A[J]=sys.implementation._mpy if'_mpy'in L(sys.implementation)else sys.implementation.mpy if J in L(sys.implementation)else B
	except(I,P):pass
	D.collect();A0(A);D.collect()
	try:
		if'uname'in L(os):
			A[F]=U(os.uname()[3])
			if not A[F]:A[F]=U(os.uname()[2])
		elif C in L(sys):A[F]=U(sys.version)
	except(I,P,k):pass
	if A[C]==B and sys.platform not in(X,W):
		try:d=os.uname();A[C]=d.release
		except(P,I,k):pass
	for(e,f,g)in[(Y,Y,'const'),(Z,Z,'FAT'),(a,'pybricks.hubs','EV3Brick')]:
		try:h=__import__(f,E,E,g);A[M]=e;del h;break
		except(N,Q):pass
	if A[M]==a:A['release']='2.0.0'
	if A[M]==m:
		A[C]
		if A[C]and A[C].endswith('.0')and A[C]>='1.10.0'and A[C]<='1.19.9':A[C]=A[C][:-2]
	if J in A and A[J]:
		K=int(A[J]);R=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][K>>10]
		if R:A[V]=R
		A[J]='v{}.{}'.format(K&255,K>>8&3)
	if A[F]and not A[C].endswith(b):A[C]=A[C]+b
	A[S]=f"{A[C]}-{A[F]}"if A[F]else f"{A[C]}";return A
def z(version):
	A=version;B=J.join([str(A)for A in A[:3]])
	if R(A)>3 and A[3]:B+=b+A[3]
	return B
def A0(info,desc=B):
	L='with ';C=info;F=A
	for G in[A+'/board_info.csv'for A in y]:
		if e(G):
			E=desc or C[H].strip();I=E.rfind(' with')
			if I!=-1:J=E[:I].strip()
			else:J=B
			if A1(C,E,G,J):F=K;break
	if not F:
		E=desc or C[H].strip()
		if L+C[T].upper()in E:E=E.split(L+C[T].upper())[0].strip()
		C[H]=E
	C[H]=C[H].replace(' ',S);D.collect()
def A1(info,descr,filename,short_descr):
	D=short_descr;C=info;E=B
	with W(filename,'r')as J:
		while 1:
			F=J.readline()
			if not F:break
			I,G=F.split(',')[0].strip(),F.split(',')[1].strip()
			if I==descr:C[H]=G;return K
			elif D and I==D:
				if v in D:C[H]=G;return K
				E=G
	if E:C[H]=E;return K
	return A
def get_root():
	try:A=os.getcwd()
	except(F,I):A=J
	B=A
	for B in[A,'/sd','/flash',G,J]:
		try:C=os.stat(B);break
		except F:continue
	return B
def e(filename):
	try:
		if os.stat(filename)[0]>>14:return K
		return A
	except F:return A
def f():sys.exit(1)
def read_path():
	path=B
	if R(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:f()
	elif R(sys.argv)==2:f()
	return path
def g():
	try:B=bytes('abc',encoding='utf8');C=g.__module__;return A
	except(h,I):return K
def main():
	C='lvgl'
	try:import lvgl as A
	except l:return
	B=C
	try:B='lvgl-{0}_{1}_{2}-{3}-{4}'.format(A.version_major(),A.version_minor(),A.version_patch(),A.version_info(),sys.platform)
	except l:B='lvgl-{0}_{1}_{2}_{3}-{4}'.format(8,1,0,'dev',sys.platform)
	finally:stubber=Stubber(firmware_id=B)
	stubber.clean();stubber.modules=['io','lodepng','rtch',C];D.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or g():
	try:A2=logging.getLogger(u);logging.basicConfig(level=logging.INFO)
	except j:pass
	if not e('no_auto_stubber.txt'):
		try:D.threshold(4*1024);D.enable()
		except BaseException:pass
		main()