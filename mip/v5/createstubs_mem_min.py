v='with'
u='stubber'
t='{}/{}'
s='method'
r='function'
q='bool'
p='str'
o='float'
n='int'
m=NameError
l=sorted
k=NotImplementedError
c=',\n'
b='dict'
a='list'
Z='tuple'
Y='micropython'
X=str
W=repr
U='cpu'
T='_'
S=KeyError
R=open
Q=IndexError
P=dir
O=ImportError
N='family'
M=len
L=print
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
from ujson import dumps as d
try:from machine import reset
except O:pass
try:from collections import OrderedDict as e
except O:from ucollections import OrderedDict as e
__version__='v1.16.2'
w=2
x=2
f=[J,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise k('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();C.collect()
		if B:A._fwid=B.lower()
		elif A.info[N]==Y:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:g(path+G)
		except F:L('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;D=[];J=[]
		for A in P(H):
			if A.startswith(T)and not A in L.modules:continue
			try:
				E=getattr(H,A)
				try:F=W(type(E)).split("'")[1]
				except Q:F=B
				if F in{n,o,p,q,Z,a,b}:G=1
				elif F in{r,s}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,W(E),W(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,K))
			except MemoryError as K:sleep(1);reset()
		D=l([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);C.collect();return D,J
	def add_modules(A,modules):A.modules=l(set(A.modules)|set(modules))
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
		if H is E:N=D.replace(J,T)+'.py';H=I.path+G+N
		else:N=H.split(G)[-1]
		if G in D:D=D.replace(G,J)
		L=E
		try:L=__import__(D,E,E,'*');U=C.mem_free()
		except O:return A
		g(H)
		with R(H,'w')as M:P=X(I.info).replace('OrderedDict(',B).replace('})','}');Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,I._fwid,P,__version__);M.write(Q);M.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(M,L,D,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del L
			except(F,S):pass
			try:del sys.modules[D]
			except S:pass
		C.collect();return K
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';Y='Incomplete';Q=in_class;P=object_expr;O='Exception';H=fp;D=indent;C.collect()
		if P in K.problematic:return
		R,N=K.get_obj_attributes(P)
		if N:L(N)
		for(E,J,G,T,f)in R:
			if E in['classmethod','staticmethod','BaseException',O]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and M(D)<=x*4:
				U=B;V=E.endswith(O)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),D+'    ',Q+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif any(A in G for A in[s,r,'closure']):
				W=Y;X=B
				if Q>0:X='self, '
				if c in G or c in J:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,X,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[p,n,o,q,'bytearray','bytes']:A=d.format(D,E,J,I)
				elif I in[b,a,Z]:e={b:'{}',a:'[]',Z:'()'};A=d.format(D,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=Y
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,I,G,J)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+E+' # type: Incomplete\n')
		del R;del N
		try:del E,J,G,T
		except(F,S,m):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,T)
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
		G=t.format(B.path,filename);C.collect()
		try:
			with R(G,'w')as D:
				B.write_json_header(D);E=K
				for H in B._report:B.write_json_node(D,H,E);E=A
				B.write_json_end(D)
			I=B._start_free-C.mem_free()
		except F:L('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(d({A:B.info})[1:-1]);f.write(c);f.write(d({u:{D:__version__},'stubtype':A})[1:-1]);f.write(c);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(c)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def g(path):
	A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except F as D:
				if D.args[0]==w:
					try:os.mkdir(B)
					except F as E:L('failed to create folder {}'.format(B));raise E
		C=A+1
def V(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	f='ev3-pybricks';d='pycom';c='pycopy';b='unix';a='win32';Z='arch';W='ver';K='mpy';G='port';F='build';A=e({N:sys.implementation.name,D:B,F:B,W:B,G:sys.platform,H:'UNKNOWN',U:B,K:B,Z:B})
	if A[G].startswith('pyb'):A[G]='stm32'
	elif A[G]==a:A[G]='windows'
	elif A[G]=='linux':A[G]=b
	try:A[D]=J.join([X(A)for A in sys.implementation.version]).rstrip(J)
	except I:pass
	try:R=sys.implementation._machine if'_machine'in P(sys.implementation)else os.uname().machine;A[H]=R;A[U]=R.split(v)[-1].strip();A[K]=sys.implementation._mpy if'_mpy'in P(sys.implementation)else sys.implementation.mpy if K in P(sys.implementation)else B
	except(I,Q):pass
	C.collect();y(A);C.collect()
	try:
		A[F]=V(os.uname()[3])
		if not A[F]:A[F]=V(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=V(sys.version.split(';')[1])
	except(I,Q):pass
	if A[F]and M(A[F])>5:A[F]=B
	if A[D]==B and sys.platform not in(b,a):
		try:g=os.uname();A[D]=g.release
		except(Q,I,TypeError):pass
	for(h,i,j)in[(c,c,'const'),(d,d,'FAT'),(f,'pybricks.hubs','EV3Brick')]:
		try:k=__import__(i,E,E,j);A[N]=h;del k;break
		except(O,S):pass
	if A[N]==f:A['release']='2.0.0'
	if A[N]==Y:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if K in A and A[K]:
		L=int(A[K]);T=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][L>>10]
		if T:A[Z]=T
		A[K]='v{}.{}'.format(L&255,L>>8&3)
	A[W]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def y(info,desc=B):
	L='with ';D=info;F=A
	for G in[A+'/board_info.csv'for A in f]:
		if h(G):
			E=desc or D[H].strip();I=E.rfind(' with')
			if I!=-1:J=E[:I].strip()
			else:J=B
			if z(D,E,G,J):F=K;break
	if not F:
		E=desc or D[H].strip()
		if L+D[U].upper()in E:E=E.split(L+D[U].upper())[0].strip()
		D[H]=E
	D[H]=D[H].replace(' ',T);C.collect()
def z(info,descr,filename,short_descr):
	D=short_descr;C=info;E=B
	with R(filename,'r')as J:
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
def h(filename):
	try:
		if os.stat(filename)[0]>>14:return K
		return A
	except F:return A
def i():sys.exit(1)
def read_path():
	path=B
	if M(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:i()
	elif M(sys.argv)==2:i()
	return path
def j():
	try:B=bytes('abc',encoding='utf8');C=j.__module__;return A
	except(k,I):return K
def main():
	E='/modulelist.txt';stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[]
	for B in f:
		try:
			F=C.mem_free()
			with R(B+E)as D:
				L('Debug: List of modules: '+B+E);A=D.readline()
				while A:
					A=A.strip()
					if M(A)>0 and A[0]!='#':stubber.modules.append(A)
					A=D.readline()
				C.collect();L('Debug: Used memory to load modulelist.txt: '+X(F-C.mem_free())+' bytes');break
		except Exception:pass
	if not stubber.modules:stubber.modules=[Y]
	C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or j():
	try:A0=logging.getLogger(u);logging.basicConfig(level=logging.INFO)
	except m:pass
	if not h('no_auto_stubber.txt'):
		try:C.threshold(4*1024);C.enable()
		except BaseException:pass
		main()