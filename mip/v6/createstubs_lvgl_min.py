u='with'
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
O=dir
N=print
M=ImportError
L='family'
K=True
J='.'
I=AttributeError
H='board'
A=False
G='/'
E=None
D='version'
F=OSError
B=''
import gc as C,os,sys
from ujson import dumps as b
try:from machine import reset
except M:pass
try:from collections import OrderedDict as c
except M:from ucollections import OrderedDict as c
__version__='v1.16.2'
v=2
w=2
x=[J,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise h('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();C.collect()
		if B:A._fwid=B.lower()
		elif A.info[L]==l:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:d(path+G)
		except F:N('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;D=[];J=[]
		for A in O(H):
			if A.startswith(S)and not A in L.modules:continue
			try:
				E=getattr(H,A)
				try:F=V(type(E)).split("'")[1]
				except P:F=B
				if F in{m,n,o,p,X,Y,Z}:G=1
				elif F in{q,r}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,V(E),V(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,K))
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
		H='{}/{}.py'.format(B.path,D.replace(J,G));C.collect();E=A
		try:E=B.create_module_stub(D,H)
		except F:return A
		C.collect();return E
	def create_module_stub(I,module_name,file_name=E):
		H=file_name;D=module_name
		if H is E:O=D.replace(J,S)+'.py';H=I.path+G+O
		else:O=H.split(G)[-1]
		if G in D:D=D.replace(G,J)
		L=E
		try:L=__import__(D,E,E,'*');T=C.mem_free()
		except M:return A
		d(H)
		with W(H,'w')as N:P=str(I.info).replace('OrderedDict(',B).replace('})','}');R='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,I._fwid,P,__version__);N.write(R);N.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(N,L,D,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del L
			except(F,Q):pass
			try:del sys.modules[D]
			except Q:pass
		C.collect();return K
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Incomplete';P=in_class;O=object_expr;M='Exception';H=fp;D=indent;C.collect()
		if O in K.problematic:return
		S,L=K.get_obj_attributes(O)
		if L:N(L)
		for(E,J,G,T,f)in S:
			if E in['classmethod','staticmethod','BaseException',M]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and R(D)<=w*4:
				U=B;V=E.endswith(M)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=M
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),D+'    ',P+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif any(A in G for A in[r,q,'closure']):
				W=b;a=B
				if P>0:a='self, '
				if c in G or c in J:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,a,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[o,m,n,p,'bytearray','bytes']:A=d.format(D,E,J,I)
				elif I in[Z,Y,X]:e={Z:'{}',Y:'[]',X:'()'};A=d.format(D,E,e[I],I)
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
		except(F,I):return
		for D in C:
			A=s.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(B,filename='modules.json'):
		G=s.format(B.path,filename);C.collect()
		try:
			with W(G,'w')as D:
				B.write_json_header(D);E=K
				for H in B._report:B.write_json_node(D,H,E);E=A
				B.write_json_end(D)
			I=B._start_free-C.mem_free()
		except F:N('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(b({A:B.info})[1:-1]);f.write(a);f.write(b({t:{D:__version__},'stubtype':A})[1:-1]);f.write(a);f.write('"modules" :[\n')
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
				if D.args[0]==v:
					try:os.mkdir(B)
					except F as E:N('failed to create folder {}'.format(B));raise E
		C=A+1
def U(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	d='ev3-pybricks';b='pycom';a='pycopy';Z='unix';Y='win32';X='arch';W='ver';K='mpy';G='port';F='build';A=c({L:sys.implementation.name,D:B,F:B,W:B,G:sys.platform,H:'UNKNOWN',T:B,K:B,X:B})
	if A[G].startswith('pyb'):A[G]='stm32'
	elif A[G]==Y:A[G]='windows'
	elif A[G]=='linux':A[G]=Z
	try:A[D]=J.join([str(A)for A in sys.implementation.version]).rstrip(J)
	except I:pass
	try:S=sys.implementation._machine if'_machine'in O(sys.implementation)else os.uname().machine;A[H]=S;A[T]=S.split(u)[-1].strip();A[K]=sys.implementation._mpy if'_mpy'in O(sys.implementation)else sys.implementation.mpy if K in O(sys.implementation)else B
	except(I,P):pass
	C.collect();y(A);C.collect()
	try:
		A[F]=U(os.uname()[3])
		if not A[F]:A[F]=U(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=U(sys.version.split(';')[1])
	except(I,P):pass
	if A[F]and R(A[F])>5:A[F]=B
	if A[D]==B and sys.platform not in(Z,Y):
		try:e=os.uname();A[D]=e.release
		except(P,I,TypeError):pass
	for(f,g,h)in[(a,a,'const'),(b,b,'FAT'),(d,'pybricks.hubs','EV3Brick')]:
		try:i=__import__(g,E,E,h);A[L]=f;del i;break
		except(M,Q):pass
	if A[L]==d:A['release']='2.0.0'
	if A[L]==l:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if K in A and A[K]:
		N=int(A[K]);V=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][N>>10]
		if V:A[X]=V
		A[K]='v{}.{}'.format(N&255,N>>8&3)
	A[W]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def y(info,desc=B):
	L='with ';D=info;F=A
	for G in[A+'/board_info.csv'for A in x]:
		if e(G):
			E=desc or D[H].strip();I=E.rfind(' with')
			if I!=-1:J=E[:I].strip()
			else:J=B
			if z(D,E,G,J):F=K;break
	if not F:
		E=desc or D[H].strip()
		if L+D[T].upper()in E:E=E.split(L+D[T].upper())[0].strip()
		D[H]=E
	D[H]=D[H].replace(' ',S);C.collect()
def z(info,descr,filename,short_descr):
	D=short_descr;C=info;E=B
	with W(filename,'r')as J:
		while 1:
			F=J.readline()
			if not F:break
			I,G=F.split(',')[0].strip(),F.split(',')[1].strip()
			if I==descr:C[H]=G;return K
			elif D and I==D:
				if u in D:C[H]=G;return K
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
	D='lvgl'
	try:import lvgl as A
	except k:return
	B=D
	try:B='lvgl-{0}_{1}_{2}-{3}-{4}'.format(A.version_major(),A.version_minor(),A.version_patch(),A.version_info(),sys.platform)
	except k:B='lvgl-{0}_{1}_{2}_{3}-{4}'.format(8,1,0,'dev',sys.platform)
	finally:stubber=Stubber(firmware_id=B)
	stubber.clean();stubber.modules=['io','lodepng','rtch',D];C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or g():
	try:A0=logging.getLogger(t);logging.basicConfig(level=logging.INFO)
	except j:pass
	if not e('no_auto_stubber.txt'):
		try:C.threshold(4*1024);C.enable()
		except BaseException:pass
		main()