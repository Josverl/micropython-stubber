s='{}/{}'
r='method'
q='function'
p='bool'
o='str'
n='float'
m='int'
l='port'
k=NameError
j=sorted
i=NotImplementedError
A=',\n'
a='dict'
Z='list'
Y='tuple'
X='micropython'
W=repr
U=KeyError
T=open
S=IndexError
R=dir
Q=ImportError
P=True
O='_'
N='family'
M=len
L='.'
K='board'
J=print
I=AttributeError
H=False
G='/'
F=None
E='version'
D=OSError
B=''
import gc as C,sys,uos as os
from ujson import dumps as b
try:from machine import reset
except Q:pass
try:from collections import OrderedDict as c
except Q:from ucollections import OrderedDict as c
__version__='v1.12.2'
t=2
u=2
v=[L,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=F,firmware_id=F):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise i('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();J('Port: {}'.format(A.info[l]));J('Board: {}'.format(A.info[K]));C.collect()
		if B:A._fwid=B.lower()
		elif A.info[N]==X:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:d(path+G)
		except D:J('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;A=[];J=[]
		for D in R(H):
			if D.startswith(O):continue
			try:
				E=getattr(H,D)
				try:F=W(type(E)).split("'")[1]
				except S:F=B
				if F in{m,n,o,p,Y,Z,a}:G=1
				elif F in{q,r}:G=2
				elif F in'class':G=3
				else:G=4
				A.append((D,W(E),W(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(D,H,K))
			except MemoryError as K:sleep(1);reset()
		A=j([A for A in A if not A[0].startswith(O)],key=lambda x:x[4]);C.collect();return A,J
	def add_modules(A,modules):A.modules=j(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(A,module_name):
		B=module_name
		if B in A.problematic:return H
		if B in A.excluded:return H
		F='{}/{}.py'.format(A.path,B.replace(L,G));C.collect();E=H
		try:E=A.create_module_stub(B,F)
		except D:return H
		C.collect();return E
	def create_module_stub(I,module_name,file_name=F):
		E=file_name;A=module_name
		if E is F:K=A.replace(L,O)+'.py';E=I.path+G+K
		else:K=E.split(G)[-1]
		if G in A:A=A.replace(G,L)
		M=F
		try:M=__import__(A,F,F,'*');R=C.mem_free();J('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,K,R))
		except Q:return H
		d(E)
		with T(E,'w')as N:S='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,I._fwid,I.info,__version__);N.write(S);N.write('from typing import Any\n\n');I.write_object_stub(N,M,A,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(A,E.replace('\\',G)))
		if A not in{'os','sys','logging','gc'}:
			try:del M
			except (D,U):pass
			try:del sys.modules[A]
			except U:pass
		C.collect();return P
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';Q=in_class;P=object_expr;O='Exception';H=fp;E=indent;C.collect()
		if P in L.problematic:return
		R,N=L.get_obj_attributes(P)
		if N:J(N)
		for (F,K,G,S,f) in R:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if G=="<class 'type'>"and M(E)<=u*4:
				T=B;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:T=O
				A='\n{}class {}({}):\n'.format(E,F,T)
				if V:A+=E+'    ...\n';H.write(A);return
				H.write(A);L.write_object_stub(H,S,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);A=E+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=E+'        ...\n\n';H.write(A)
			elif r in G or q in G:
				W=b;X=B
				if Q>0:X='self, '
				if c in G or c in K:A='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,X,W)
				A+=E+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[o,m,n,p,'bytearray','bytes']:A=d.format(E,F,K,I)
				elif I in[a,Z,Y]:e={a:'{}',Z:'[]',Y:'()'};A=d.format(E,F,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,I,G,K)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(E+F+' # type: Any\n')
		del R;del N
		try:del F,K,G,S
		except (D,U,k):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,O)
		return A
	def clean(B,path=F):
		if path is F:path=B.path
		J('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except (D,I):return
		for E in C:
			A=s.format(path,E)
			try:os.remove(A)
			except D:
				try:B.clean(A);os.rmdir(A)
				except D:pass
	def report(A,filename='modules.json'):
		J('Created stubs for {} modules on board {}\nPath: {}'.format(M(A._report),A._fwid,A.path));F=s.format(A.path,filename);C.collect()
		try:
			with T(F,'w')as B:
				A.write_json_header(B);E=P
				for G in A._report:A.write_json_node(B,G,E);E=H
				A.write_json_end(B)
			I=A._start_free-C.mem_free()
		except D:J('Failed to create the report.')
	def write_json_header(C,f):B='firmware';f.write('{');f.write(b({B:C.info})[1:-1]);f.write(A);f.write(b({'stubber':{E:__version__},'stubtype':B})[1:-1]);f.write(A);f.write('"modules" :[\n')
	def write_json_node(B,f,n,first):
		if not first:f.write(A)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def d(path):
	A=C=0
	while A!=-1:
		A=path.find(G,C)
		if A!=-1:
			B=path[0]if A==0 else path[:A]
			try:H=os.stat(B)
			except D as E:
				if E.args[0]==t:
					try:os.mkdir(B)
					except D as F:J('failed to create folder {}'.format(B));raise F
		C=A+1
def V(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	i='ev3-pybricks';h='pycom';g='pycopy';d='GENERIC';b='arch';a='cpu';Z='ver';T='with';G='mpy';D='build';A=c({N:sys.implementation.name,E:B,D:B,Z:B,l:'stm32'if sys.platform.startswith('pyb')else sys.platform,K:d,a:B,G:B,b:B})
	try:A[E]=L.join([str(A)for A in sys.implementation.version])
	except I:pass
	try:W=sys.implementation._machine if'_machine'in R(sys.implementation)else os.uname().machine;A[K]=W.strip();A[a]=W.split(T)[1].strip();A[G]=sys.implementation._mpy if'_mpy'in R(sys.implementation)else sys.implementation.mpy if G in R(sys.implementation)else B
	except (I,S):pass
	C.collect()
	for J in [A+'/board_info.csv'for A in v]:
		if f(J):
			H=A[K].strip()
			if e(A,H,J):break
			if T in H:
				H=H.split(T)[0].strip()
				if e(A,H,J):break
			A[K]=d
	A[K]=A[K].replace(' ',O);C.collect()
	try:
		A[D]=V(os.uname()[3])
		if not A[D]:A[D]=V(os.uname()[2])
		if not A[D]and';'in sys.version:A[D]=V(sys.version.split(';')[1])
	except (I,S):pass
	if A[D]and M(A[D])>5:A[D]=B
	if A[E]==B and sys.platform not in('unix','win32'):
		try:j=os.uname();A[E]=j.release
		except (S,I,TypeError):pass
	for (k,m,n) in [(g,g,'const'),(h,h,'FAT'),(i,'pybricks.hubs','EV3Brick')]:
		try:o=__import__(m,F,F,n);A[N]=k;del o;break
		except (Q,U):pass
	if A[N]==i:A['release']='2.0.0'
	if A[N]==X:
		if A[E]and A[E].endswith('.0')and A[E]>='1.10.0'and A[E]<='1.20.0':A[E]=A[E][:-2]
	if G in A and A[G]:
		P=int(A[G]);Y=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][P>>10]
		if Y:A[b]=Y
		A[G]='v{}.{}'.format(P&255,P>>8&3)
	A[Z]=f"v{A[E]}-{A[D]}"if A[D]else f"v{A[E]}";return A
def e(info,board_descr,filename):
	with T(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[K]=D;return P
	return H
def get_root():
	try:A=os.getcwd()
	except (D,I):A=L
	B=A
	for B in [A,'/sd','/flash',G,L]:
		try:C=os.stat(B);break
		except D:continue
	return B
def f(filename):
	try:
		if os.stat(filename)[0]>>14:return P
		return H
	except D:return H
def g():sys.exit(1)
def read_path():
	path=B
	if M(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:g()
	elif M(sys.argv)==2:g()
	return path
def h():
	try:A=bytes('abc',encoding='utf8');B=h.__module__;return H
	except (i,I):return P
def main():
	stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[X]
	for A in [B,G,'/lib/']:
		try:
			with T(A+'modulelist'+'.txt')as E:stubber.modules=[A.strip()for A in E.read().split('\n')if M(A.strip())and A.strip()[0]!='#'];break
		except D:pass
	C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or h():
	try:logging.basicConfig(level=logging.INFO)
	except k:pass
	if not f('no_auto_stubber.txt'):C.threshold(4*1024);C.enable();main()