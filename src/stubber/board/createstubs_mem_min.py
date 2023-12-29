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
b=',\n'
a='dict'
Z='list'
Y='tuple'
X='micropython'
W=str
V=repr
T='_'
S=KeyError
R=open
Q=IndexError
P=dir
O=ImportError
N=True
M='family'
L=len
K=print
J='board'
I='.'
H=AttributeError
A=False
G='/'
E=None
D='version'
F=OSError
C=''
import gc as B,os,sys
from ujson import dumps as c
try:from machine import reset
except O:pass
try:from collections import OrderedDict as d
except O:from ucollections import OrderedDict as d
__version__='v1.16.1'
v=2
w=2
e=[I,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise k('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();B.collect()
		if C:A._fwid=C.lower()
		elif A.info[M]==X:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=B.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:f(path+G)
		except F:K('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		I=item_instance;D=[];J=[]
		for A in P(I):
			if A.startswith(T)and not A in L.modules:continue
			try:
				E=getattr(I,A)
				try:F=V(type(E)).split("'")[1]
				except Q:F=C
				if F in{n,o,p,q,Y,Z,a}:G=1
				elif F in{r,s}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,V(E),V(type(E)),E,G))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,I,K))
			except MemoryError as K:sleep(1);reset()
		D=l([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);B.collect();return D,J
	def add_modules(A,modules):A.modules=l(set(A.modules)|set(modules))
	def create_all_stubs(A):
		B.collect()
		for C in A.modules:A.create_one_stub(C)
	def create_one_stub(C,module_name):
		D=module_name
		if D in C.problematic:return A
		if D in C.excluded:return A
		H='{}/{}.py'.format(C.path,D.replace(I,G));B.collect();E=A
		try:E=C.create_module_stub(D,H)
		except F:return A
		B.collect();return E
	def create_module_stub(J,module_name,file_name=E):
		H=file_name;D=module_name
		if H is E:M=D.replace(I,T)+'.py';H=J.path+G+M
		else:M=H.split(G)[-1]
		if G in D:D=D.replace(G,I)
		K=E
		try:K=__import__(D,E,E,'*');U=B.mem_free()
		except O:return A
		f(H)
		with R(H,'w')as L:P=W(J.info).replace('OrderedDict(',C).replace('})','}');Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,J._fwid,P,__version__);L.write(Q);L.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');J.write_object_stub(L,K,D,C)
		J._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del K
			except(F,S):pass
			try:del sys.modules[D]
			except S:pass
		B.collect();return N
	def write_object_stub(M,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Incomplete';Q=in_class;P=object_expr;O='Exception';H=fp;D=indent;B.collect()
		if P in M.problematic:return
		R,N=M.get_obj_attributes(P)
		if N:K(N)
		for(E,J,G,T,f)in R:
			if E in['classmethod','staticmethod','BaseException',O]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and L(D)<=w*4:
				U=C;V=E.endswith(O)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);M.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),D+'    ',Q+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif any(A in G for A in[s,r,'closure']):
				W=b;X=C
				if Q>0:X='self, '
				if c in G or c in J:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,X,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=C
				if I in[p,n,o,q,'bytearray','bytes']:A=d.format(D,E,J,I)
				elif I in[a,Z,Y]:e={a:'{}',Z:'[]',Y:'()'};A=d.format(D,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
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
		except(F,H):return
		for D in C:
			A=t.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(C,filename='modules.json'):
		G=t.format(C.path,filename);B.collect()
		try:
			with R(G,'w')as D:
				C.write_json_header(D);E=N
				for H in C._report:C.write_json_node(D,H,E);E=A
				C.write_json_end(D)
			I=C._start_free-B.mem_free()
		except F:K('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(c({A:B.info})[1:-1]);f.write(b);f.write(c({u:{D:__version__},'stubtype':A})[1:-1]);f.write(b);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(b)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def f(path):
	A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except F as D:
				if D.args[0]==v:
					try:os.mkdir(B)
					except F as E:K('failed to create folder {}'.format(B));raise E
		C=A+1
def U(s):
	A=' on '
	if not s:return C
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else C
def _info():
	k='ev3-pybricks';j='pycom';i='pycopy';f='GENERIC';c='arch';b='cpu';a='ver';V='with';G='mpy';F='build';A=d({M:sys.implementation.name,D:C,F:C,a:C,'port':'stm32'if sys.platform.startswith('pyb')else sys.platform,J:f,b:C,G:C,c:C})
	try:A[D]=I.join([W(A)for A in sys.implementation.version])
	except H:pass
	try:Y=sys.implementation._machine if'_machine'in P(sys.implementation)else os.uname().machine;A[J]=Y.strip();A[b]=Y.split(V)[1].strip();A[G]=sys.implementation._mpy if'_mpy'in P(sys.implementation)else sys.implementation.mpy if G in P(sys.implementation)else C
	except(H,Q):pass
	B.collect()
	for N in[A+'/board_info.csv'for A in e]:
		if h(N):
			K=A[J].strip()
			if g(A,K,N):break
			if V in K:
				K=K.split(V)[0].strip()
				if g(A,K,N):break
			A[J]=f
	A[J]=A[J].replace(' ',T);B.collect()
	try:
		A[F]=U(os.uname()[3])
		if not A[F]:A[F]=U(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=U(sys.version.split(';')[1])
	except(H,Q):pass
	if A[F]and L(A[F])>5:A[F]=C
	if A[D]==C and sys.platform not in('unix','win32'):
		try:l=os.uname();A[D]=l.release
		except(Q,H,TypeError):pass
	for(m,n,o)in[(i,i,'const'),(j,j,'FAT'),(k,'pybricks.hubs','EV3Brick')]:
		try:p=__import__(n,E,E,o);A[M]=m;del p;break
		except(O,S):pass
	if A[M]==k:A['release']='2.0.0'
	if A[M]==X:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if G in A and A[G]:
		R=int(A[G]);Z=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][R>>10]
		if Z:A[c]=Z
		A[G]='v{}.{}'.format(R&255,R>>8&3)
	A[a]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def g(info,board_descr,filename):
	with R(filename,'r')as C:
		while 1:
			B=C.readline()
			if not B:break
			D,E=B.split(',')[0].strip(),B.split(',')[1].strip()
			if D==board_descr:info[J]=E;return N
	return A
def get_root():
	try:A=os.getcwd()
	except(F,H):A=I
	B=A
	for B in[A,'/sd','/flash',G,I]:
		try:C=os.stat(B);break
		except F:continue
	return B
def h(filename):
	try:
		if os.stat(filename)[0]>>14:return N
		return A
	except F:return A
def i():sys.exit(1)
def read_path():
	path=C
	if L(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:i()
	elif L(sys.argv)==2:i()
	return path
def j():
	try:B=bytes('abc',encoding='utf8');C=j.__module__;return A
	except(k,H):return N
def main():
	E='/modulelist.txt';stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[]
	for C in e:
		try:
			F=B.mem_free()
			with R(C+E)as D:
				K('Debug: List of modules: '+C+E);A=D.readline()
				while A:
					A=A.strip()
					if L(A)>0 and A[0]!='#':stubber.modules.append(A)
					A=D.readline()
				B.collect();K('Debug: Used memory to load modulelist.txt: '+W(F-B.mem_free())+' bytes');break
		except Exception:pass
	if not stubber.modules:stubber.modules=[X]
	B.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or j():
	try:x=logging.getLogger(u);logging.basicConfig(level=logging.INFO)
	except m:pass
	if not h('no_auto_stubber.txt'):
		try:B.threshold(4*1024);B.enable()
		except BaseException:pass
		main()