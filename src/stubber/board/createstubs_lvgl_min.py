t='stubber'
s='{}/{}'
r='method'
q='function'
p='bool'
o='str'
n='float'
m='int'
l='micropython'
k=Exception
j=NameError
i=sorted
h=NotImplementedError
Z=',\n'
Y='dict'
X='list'
W='tuple'
V=open
U=repr
S='_'
R=len
Q=KeyError
P=IndexError
O=dir
M=print
N=ImportError
K=True
L='family'
J='board'
I='.'
H=AttributeError
A=False
G='/'
E=None
D='version'
F=OSError
B=''
import gc as C,os,sys
from ujson import dumps as a
try:from machine import reset
except N:pass
try:from collections import OrderedDict as b
except N:from ucollections import OrderedDict as b
__version__='v1.16.1'
u=2
v=2
w=[I,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise h('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();C.collect()
		if B:A._fwid=B.lower()
		elif A.info[L]==l:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:c(path+G)
		except F:M('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		I=item_instance;D=[];J=[]
		for A in O(I):
			if A.startswith(S)and not A in L.modules:continue
			try:
				E=getattr(I,A)
				try:F=U(type(E)).split("'")[1]
				except P:F=B
				if F in{m,n,o,p,W,X,Y}:G=1
				elif F in{q,r}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,U(E),U(type(E)),E,G))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,I,K))
			except MemoryError as K:sleep(1);reset()
		D=i([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);C.collect();return D,J
	def add_modules(A,modules):A.modules=i(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(B,module_name):
		D=module_name
		if D in B.problematic:return A
		if D in B.excluded:return A
		H='{}/{}.py'.format(B.path,D.replace(I,G));C.collect();E=A
		try:E=B.create_module_stub(D,H)
		except F:return A
		C.collect();return E
	def create_module_stub(J,module_name,file_name=E):
		H=file_name;D=module_name
		if H is E:O=D.replace(I,S)+'.py';H=J.path+G+O
		else:O=H.split(G)[-1]
		if G in D:D=D.replace(G,I)
		L=E
		try:L=__import__(D,E,E,'*');T=C.mem_free()
		except N:return A
		c(H)
		with V(H,'w')as M:P=str(J.info).replace('OrderedDict(',B).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,J._fwid,P,__version__);M.write(R);M.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(M,L,D,B)
		J._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del L
			except(F,Q):pass
			try:del sys.modules[D]
			except Q:pass
		C.collect();return K
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Incomplete';P=in_class;O=object_expr;N='Exception';H=fp;D=indent;C.collect()
		if O in K.problematic:return
		S,L=K.get_obj_attributes(O)
		if L:M(L)
		for(E,J,G,T,f)in S:
			if E in['classmethod','staticmethod','BaseException',N]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and R(D)<=v*4:
				U=B;V=E.endswith(N)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=N
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),D+'    ',P+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif any(A in G for A in[r,q,'closure']):
				Z=b;a=B
				if P>0:a='self, '
				if c in G or c in J:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,Z)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,a,Z)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[o,m,n,p,'bytearray','bytes']:A=d.format(D,E,J,I)
				elif I in[Y,X,W]:e={Y:'{}',X:'[]',W:'()'};A=d.format(D,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,I,G,J)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+E+' # type: Incomplete\n')
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
		except(F,H):return
		for D in C:
			A=s.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(B,filename='modules.json'):
		G=s.format(B.path,filename);C.collect()
		try:
			with V(G,'w')as D:
				B.write_json_header(D);E=K
				for H in B._report:B.write_json_node(D,H,E);E=A
				B.write_json_end(D)
			I=B._start_free-C.mem_free()
		except F:M('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(a({A:B.info})[1:-1]);f.write(Z);f.write(a({t:{D:__version__},'stubtype':A})[1:-1]);f.write(Z);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(Z)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def c(path):
	A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except F as D:
				if D.args[0]==u:
					try:os.mkdir(B)
					except F as E:M('failed to create folder {}'.format(B));raise E
		C=A+1
def T(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	k='ev3-pybricks';j='pycom';i='pycopy';h='unix';g='win32';f='GENERIC';c='arch';a='cpu';Z='ver';W='with';K='mpy';G='port';F='build';A=b({L:sys.implementation.name,D:B,F:B,Z:B,G:sys.platform,J:f,a:B,K:B,c:B})
	if A[G].startswith('pyb'):A[G]='stm32'
	elif A[G]==g:A[G]='windows'
	elif A[G]=='linux':A[G]=h
	try:A[D]=I.join([str(A)for A in sys.implementation.version])
	except H:pass
	try:X=sys.implementation._machine if'_machine'in O(sys.implementation)else os.uname().machine;A[J]=X.strip();A[a]=X.split(W)[1].strip();A[K]=sys.implementation._mpy if'_mpy'in O(sys.implementation)else sys.implementation.mpy if K in O(sys.implementation)else B
	except(H,P):pass
	C.collect()
	for U in[A+'/board_info.csv'for A in w]:
		if e(U):
			M=A[J].strip()
			if d(A,M,U):break
			if W in M:
				M=M.split(W)[0].strip()
				if d(A,M,U):break
			A[J]=f
	A[J]=A[J].replace(' ',S);C.collect()
	try:
		A[F]=T(os.uname()[3])
		if not A[F]:A[F]=T(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=T(sys.version.split(';')[1])
	except(H,P):pass
	if A[F]and R(A[F])>5:A[F]=B
	if A[D]==B and sys.platform not in(h,g):
		try:m=os.uname();A[D]=m.release
		except(P,H,TypeError):pass
	for(n,o,p)in[(i,i,'const'),(j,j,'FAT'),(k,'pybricks.hubs','EV3Brick')]:
		try:q=__import__(o,E,E,p);A[L]=n;del q;break
		except(N,Q):pass
	if A[L]==k:A['release']='2.0.0'
	if A[L]==l:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if K in A and A[K]:
		V=int(A[K]);Y=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][V>>10]
		if Y:A[c]=Y
		A[K]='v{}.{}'.format(V&255,V>>8&3)
	A[Z]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def d(info,board_descr,filename):
	with V(filename,'r')as C:
		while 1:
			B=C.readline()
			if not B:break
			D,E=B.split(',')[0].strip(),B.split(',')[1].strip()
			if D==board_descr:info[J]=E;return K
	return A
def get_root():
	try:A=os.getcwd()
	except(F,H):A=I
	B=A
	for B in[A,'/sd','/flash',G,I]:
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
	except(h,H):return K
def main():
	D='lvgl'
	try:import lvgl as A
	except k:return
	B=D
	try:B='lvgl-{0}_{1}_{2}-{3}-{4}'.format(A.version_major(),A.version_minor(),A.version_patch(),A.version_info(),sys.platform)
	except k:B='lvgl-{0}_{1}_{2}_{3}-{4}'.format(8,1,0,'dev',sys.platform)
	finally:stubber=Stubber(firmware_id=B)
	stubber.clean();stubber.modules=['io','lodepng','rtch',D];C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or g():
	try:x=logging.getLogger(t);logging.basicConfig(level=logging.INFO)
	except j:pass
	if not e('no_auto_stubber.txt'):
		try:C.threshold(4*1024);C.enable()
		except BaseException:pass
		main()