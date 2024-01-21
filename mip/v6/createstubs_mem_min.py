w='with'
v='stubber'
u='{}/{}'
t='method'
s='function'
r='bool'
q='str'
p='float'
o='int'
n=TypeError
m=NameError
l=sorted
k=NotImplementedError
d='-'
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
P=ImportError
O='family'
N=len
M=dir
L=print
K=True
J='.'
I=AttributeError
H='board'
A=False
G='/'
E=None
F=OSError
D='version'
C=''
import gc as B,os,sys
try:from ujson import dumps
except:from json import dumps
try:from machine import reset
except P:pass
try:from collections import OrderedDict as e
except P:from ucollections import OrderedDict as e
__version__='v1.16.2'
x=2
y=2
f=[J,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise k('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();B.collect()
		if C:A._fwid=C.lower()
		elif A.info[O]==Y:A._fwid='{family}-v{version}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-v{version}-{port}'.format(**A.info)
		A._start_free=B.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:g(path+G)
		except F:L('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;D=[];J=[]
		for A in M(H):
			if A.startswith(T)and not A in L.modules:continue
			try:
				E=getattr(H,A)
				try:F=W(type(E)).split("'")[1]
				except Q:F=C
				if F in{o,p,q,r,Z,a,b}:G=1
				elif F in{s,t}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,W(E),W(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,K))
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
		H='{}/{}.py'.format(C.path,D.replace(J,G));B.collect();E=A
		try:E=C.create_module_stub(D,H)
		except F:return A
		B.collect();return E
	def create_module_stub(I,module_name,file_name=E):
		H=file_name;D=module_name
		if H is E:N=D.replace(J,T)+'.py';H=I.path+G+N
		else:N=H.split(G)[-1]
		if G in D:D=D.replace(G,J)
		L=E
		try:L=__import__(D,E,E,'*');U=B.mem_free()
		except P:return A
		g(H)
		with R(H,'w')as M:O=X(I.info).replace('OrderedDict(',C).replace('})','}');Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,I._fwid,O,__version__);M.write(Q);M.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(M,L,D,C)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del L
			except(F,S):pass
			try:del sys.modules[D]
			except S:pass
		B.collect();return K
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';Y='Incomplete';Q=in_class;P=object_expr;O='Exception';H=fp;D=indent;B.collect()
		if P in K.problematic:return
		R,M=K.get_obj_attributes(P)
		if M:L(M)
		for(E,J,G,T,f)in R:
			if E in['classmethod','staticmethod','BaseException',O]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and N(D)<=y*4:
				U=C;V=E.endswith(O)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),D+'    ',Q+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif any(A in G for A in[t,s,'closure']):
				W=Y;X=C
				if Q>0:X='self, '
				if c in G or c in J:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,X,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=C
				if I in[q,o,p,r,'bytearray','bytes']:A=d.format(D,E,J,I)
				elif I in[b,a,Z]:e={b:'{}',a:'[]',Z:'()'};A=d.format(D,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=Y
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,I,G,J)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+E+' # type: Incomplete\n')
		del R;del M
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
			A=u.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(C,filename='modules.json'):
		G=u.format(C.path,filename);B.collect()
		try:
			with R(G,'w')as D:
				C.write_json_header(D);E=K
				for H in C._report:C.write_json_node(D,H,E);E=A
				C.write_json_end(D)
			I=C._start_free-B.mem_free()
		except F:L('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(dumps({A:B.info})[1:-1]);f.write(c);f.write(dumps({v:{D:__version__},'stubtype':A})[1:-1]);f.write(c);f.write('"modules" :[\n')
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
				if D.args[0]==x:
					try:os.mkdir(B)
					except F as E:L('failed to create folder {}'.format(B));raise E
		C=A+1
def V(s):
	A=' on '
	if not s:return C
	s=s.split(A,1)[0]if A in s else s;s=s.split('; ',1)[1]if'; 'in s else s;B=s.split(d)[1]if s.startswith('v')else s.split(d,1)[-1].split(J)[1];return B
def _info():
	c='-preview';b='ev3-pybricks';a='pycom';Z='pycopy';X='unix';W='win32';T='arch';R='ver';J='mpy';G='port';F='build';A=e({O:sys.implementation.name,D:C,F:C,R:C,G:sys.platform,H:'UNKNOWN',U:C,J:C,T:C})
	if A[G].startswith('pyb'):A[G]='stm32'
	elif A[G]==W:A[G]='windows'
	elif A[G]=='linux':A[G]=X
	try:A[D]=z(sys.implementation.version)
	except I:pass
	try:L=sys.implementation._machine if'_machine'in M(sys.implementation)else os.uname().machine;A[H]=L;A[U]=L.split(w)[-1].strip();A[J]=sys.implementation._mpy if'_mpy'in M(sys.implementation)else sys.implementation.mpy if J in M(sys.implementation)else C
	except(I,Q):pass
	B.collect();A0(A);B.collect()
	try:
		if'uname'in M(os):
			A[F]=V(os.uname()[3])
			if not A[F]:A[F]=V(os.uname()[2])
		elif D in M(sys):A[F]=V(sys.version)
	except(I,Q,n):pass
	if A[D]==C and sys.platform not in(X,W):
		try:d=os.uname();A[D]=d.release
		except(Q,I,n):pass
	for(f,g,h)in[(Z,Z,'const'),(a,a,'FAT'),(b,'pybricks.hubs','EV3Brick')]:
		try:i=__import__(g,E,E,h);A[O]=f;del i;break
		except(P,S):pass
	if A[O]==b:A['release']='2.0.0'
	if A[O]==Y:
		A[D]
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if J in A and A[J]:
		K=int(A[J]);N=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][K>>10]
		if N:A[T]=N
		A[J]='v{}.{}'.format(K&255,K>>8&3)
	if A[F]and not A[D].endswith(c):A[D]=A[D]+c
	A[R]=f"{A[D]}-{A[F]}"if A[F]else f"{A[D]}";return A
def z(version):
	A=version;B=J.join([X(A)for A in A[:3]])
	if N(A)>3 and A[3]:B+=d+A[3]
	return B
def A0(info,desc=C):
	L='with ';D=info;F=A
	for G in[A+'/board_info.csv'for A in f]:
		if h(G):
			E=desc or D[H].strip();I=E.rfind(' with')
			if I!=-1:J=E[:I].strip()
			else:J=C
			if A1(D,E,G,J):F=K;break
	if not F:
		E=desc or D[H].strip()
		if L+D[U].upper()in E:E=E.split(L+D[U].upper())[0].strip()
		D[H]=E
	D[H]=D[H].replace(' ',T);B.collect()
def A1(info,descr,filename,short_descr):
	D=short_descr;B=info;E=C
	with R(filename,'r')as J:
		while 1:
			F=J.readline()
			if not F:break
			I,G=F.split(',')[0].strip(),F.split(',')[1].strip()
			if I==descr:B[H]=G;return K
			elif D and I==D:
				if w in D:B[H]=G;return K
				E=G
	if E:B[H]=E;return K
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
	path=C
	if N(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:i()
	elif N(sys.argv)==2:i()
	return path
def j():
	try:B=bytes('abc',encoding='utf8');C=j.__module__;return A
	except(k,I):return K
def main():
	E='/modulelist.txt';stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[]
	for C in f:
		try:
			F=B.mem_free()
			with R(C+E)as D:
				L('Debug: List of modules: '+C+E);A=D.readline()
				while A:
					A=A.strip()
					if N(A)>0 and A[0]!='#':stubber.modules.append(A)
					A=D.readline()
				B.collect();L('Debug: Used memory to load modulelist.txt: '+X(F-B.mem_free())+' bytes');break
		except Exception:pass
	if not stubber.modules:stubber.modules=[Y]
	B.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or j():
	try:A2=logging.getLogger(v);logging.basicConfig(level=logging.INFO)
	except m:pass
	if not h('no_auto_stubber.txt'):
		try:B.threshold(4*1024);B.enable()
		except BaseException:pass
		main()