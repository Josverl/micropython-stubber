w='stubber'
v='{}/{}'
u='method'
t='function'
s='bool'
r='str'
q='float'
p='int'
o=NameError
n=sorted
m=NotImplementedError
d=',\n'
c='dict'
b='list'
a='tuple'
Z='micropython'
Y=str
X=repr
V='cpu'
U='_'
T=KeyError
S=open
R=IndexError
Q=dir
P=ImportError
O='with'
N='family'
M=len
L=print
K=True
J='.'
I='board'
H=AttributeError
A=False
G='/'
E=None
D='version'
F=OSError
C=''
import gc as B,os,sys
from ujson import dumps as e
try:from machine import reset
except P:pass
try:from collections import OrderedDict as f
except P:from ucollections import OrderedDict as f
__version__='v1.16.2'
x=2
y=2
g=[J,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		C=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise m('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();B.collect()
		if C:A._fwid=C.lower()
		elif A.info[N]==Z:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=B.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:h(path+G)
		except F:L('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		I=item_instance;D=[];J=[]
		for A in Q(I):
			if A.startswith(U)and not A in L.modules:continue
			try:
				E=getattr(I,A)
				try:F=X(type(E)).split("'")[1]
				except R:F=C
				if F in{p,q,r,s,a,b,c}:G=1
				elif F in{t,u}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,X(E),X(type(E)),E,G))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,I,K))
			except MemoryError as K:sleep(1);reset()
		D=n([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);B.collect();return D,J
	def add_modules(A,modules):A.modules=n(set(A.modules)|set(modules))
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
		if H is E:N=D.replace(J,U)+'.py';H=I.path+G+N
		else:N=H.split(G)[-1]
		if G in D:D=D.replace(G,J)
		L=E
		try:L=__import__(D,E,E,'*');R=B.mem_free()
		except P:return A
		h(H)
		with S(H,'w')as M:O=Y(I.info).replace('OrderedDict(',C).replace('})','}');Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,I._fwid,O,__version__);M.write(Q);M.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(M,L,D,C)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del L
			except(F,T):pass
			try:del sys.modules[D]
			except T:pass
		B.collect();return K
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';Z='bound_method';Y='Incomplete';Q=in_class;P=object_expr;O='Exception';H=fp;D=indent;B.collect()
		if P in K.problematic:return
		R,N=K.get_obj_attributes(P)
		if N:L(N)
		for(E,J,G,S,f)in R:
			if E in['classmethod','staticmethod','BaseException',O]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and M(D)<=y*4:
				U=C;V=E.endswith(O)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);K.write_object_stub(H,S,'{0}.{1}'.format(obj_name,E),D+'    ',Q+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif any(A in G for A in[u,t,'closure']):
				W=Y;X=C
				if Q>0:X='self, '
				if Z in G or Z in J:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,X,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=C
				if I in[r,p,q,s,'bytearray','bytes']:A=d.format(D,E,J,I)
				elif I in[c,b,a]:e={c:'{}',b:'[]',a:'()'};A=d.format(D,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=Y
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,I,G,J)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+E+' # type: Incomplete\n')
		del R;del N
		try:del E,J,G,S
		except(F,T,o):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,U)
		return A
	def clean(B,path=E):
		if path is E:path=B.path
		try:os.stat(path);C=os.listdir(path)
		except(F,H):return
		for D in C:
			A=v.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(C,filename='modules.json'):
		G=v.format(C.path,filename);B.collect()
		try:
			with S(G,'w')as D:
				C.write_json_header(D);E=K
				for H in C._report:C.write_json_node(D,H,E);E=A
				C.write_json_end(D)
			I=C._start_free-B.mem_free()
		except F:L('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(e({A:B.info})[1:-1]);f.write(d);f.write(e({w:{D:__version__},'stubtype':A})[1:-1]);f.write(d);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(d)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def h(path):
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
def W(s):
	A=' on '
	if not s:return C
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else C
def _info():
	g='ev3-pybricks';e='pycom';d='pycopy';c='unix';b='win32';a='arch';X='ver';K='mpy';G='port';F='build';A=f({N:sys.implementation.name,D:C,F:C,X:C,G:sys.platform,I:'UNKNOWN',V:C,K:C,a:C})
	if A[G].startswith('pyb'):A[G]='stm32'
	elif A[G]==b:A[G]='windows'
	elif A[G]=='linux':A[G]=c
	try:A[D]=J.join([Y(A)for A in sys.implementation.version])
	except H:pass
	try:S=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[I]=O.join(S.split(O)[:-1]).strip();A[V]=S.split(O)[-1].strip();A[K]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if K in Q(sys.implementation)else C
	except(H,R):pass
	B.collect();z(A);B.collect()
	try:
		A[F]=W(os.uname()[3])
		if not A[F]:A[F]=W(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=W(sys.version.split(';')[1])
	except(H,R):pass
	if A[F]and M(A[F])>5:A[F]=C
	if A[D]==C and sys.platform not in(c,b):
		try:h=os.uname();A[D]=h.release
		except(R,H,TypeError):pass
	for(i,j,k)in[(d,d,'const'),(e,e,'FAT'),(g,'pybricks.hubs','EV3Brick')]:
		try:l=__import__(j,E,E,k);A[N]=i;del l;break
		except(P,T):pass
	if A[N]==g:A['release']='2.0.0'
	if A[N]==Z:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if K in A and A[K]:
		L=int(A[K]);U=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][L>>10]
		if U:A[a]=U
		A[K]='v{}.{}'.format(L&255,L>>8&3)
	A[X]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def z(info,desc=C):
	G='with ';D=info;E=A
	for F in[A+'/board_info.csv'for A in g]:
		if j(F):
			C=desc or D[I].strip()
			if i(D,C,F):E=K;break
			if O in C:
				C=C.split(O)[0].strip()
				if i(D,C,F):E=K;break
	if not E:
		C=desc or D[I].strip()
		if G+D[V].upper()in C:C=C.split(G+D[V].upper())[0].strip()
		D[I]=C
	D[I]=D[I].replace(' ',U);B.collect()
def i(info,board_descr,filename):
	with S(filename,'r')as C:
		while 1:
			B=C.readline()
			if not B:break
			D,E=B.split(',')[0].strip(),B.split(',')[1].strip()
			if D==board_descr:info[I]=E;return K
	return A
def get_root():
	try:A=os.getcwd()
	except(F,H):A=J
	B=A
	for B in[A,'/sd','/flash',G,J]:
		try:C=os.stat(B);break
		except F:continue
	return B
def j(filename):
	try:
		if os.stat(filename)[0]>>14:return K
		return A
	except F:return A
def k():sys.exit(1)
def read_path():
	path=C
	if M(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:k()
	elif M(sys.argv)==2:k()
	return path
def l():
	try:B=bytes('abc',encoding='utf8');C=l.__module__;return A
	except(m,H):return K
def main():
	E='/modulelist.txt';stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[]
	for C in g:
		try:
			F=B.mem_free()
			with S(C+E)as D:
				L('Debug: List of modules: '+C+E);A=D.readline()
				while A:
					A=A.strip()
					if M(A)>0 and A[0]!='#':stubber.modules.append(A)
					A=D.readline()
				B.collect();L('Debug: Used memory to load modulelist.txt: '+Y(F-B.mem_free())+' bytes');break
		except Exception:pass
	if not stubber.modules:stubber.modules=[Z]
	B.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or l():
	try:A0=logging.getLogger(w);logging.basicConfig(level=logging.INFO)
	except o:pass
	if not j('no_auto_stubber.txt'):
		try:B.threshold(4*1024);B.enable()
		except BaseException:pass
		main()