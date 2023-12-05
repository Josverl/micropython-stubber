u='{}/{}'
t='method'
s='function'
r='bool'
q='str'
p='float'
o='int'
n='micropython'
m='port'
l=Exception
k=NameError
j=sorted
i=NotImplementedError
A=',\n'
a='dict'
Z='list'
Y='tuple'
X='stubber'
W=open
V=repr
T='_'
S=KeyError
R=IndexError
Q=dir
P=ImportError
O=True
N='family'
M=len
L='.'
K='board'
J=print
I=AttributeError
H=False
G='/'
E='version'
D=None
F=OSError
B=''
import gc as C,os,sys
from ujson import dumps as b
try:from machine import reset
except P:pass
try:from collections import OrderedDict as c
except P:from ucollections import OrderedDict as c
__version__='v1.15.0'
v=2
w=2
x=[L,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=D,firmware_id=D):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise i('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A.log=D;A.log=logging.getLogger(X);A._report=[];A.info=_info();J('Port: {}'.format(A.info[m]));J('Board: {}'.format(A.info[K]));C.collect()
		if B:A._fwid=B.lower()
		elif A.info[N]==n:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:d(path+G)
		except F:J('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		H=item_instance;D=[];J=[]
		for A in Q(H):
			if A.startswith(T)and not A in L.modules:continue
			try:
				E=getattr(H,A)
				try:F=V(type(E)).split("'")[1]
				except R:F=B
				if F in{o,p,q,r,Y,Z,a}:G=1
				elif F in{s,t}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,V(E),V(type(E)),E,G))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,H,K))
			except MemoryError as K:sleep(1);reset()
		D=j([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);C.collect();return D,J
	def add_modules(A,modules):A.modules=j(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(A,module_name):
		B=module_name
		if B in A.problematic:return H
		if B in A.excluded:return H
		E='{}/{}.py'.format(A.path,B.replace(L,G));C.collect();D=H
		try:D=A.create_module_stub(B,E)
		except F:return H
		C.collect();return D
	def create_module_stub(I,module_name,file_name=D):
		E=file_name;A=module_name
		if E is D:K=A.replace(L,T)+'.py';E=I.path+G+K
		else:K=E.split(G)[-1]
		if G in A:A=A.replace(G,L)
		M=D
		try:M=__import__(A,D,D,'*');Q=C.mem_free();J('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,K,Q))
		except P:return H
		d(E)
		with W(E,'w')as N:R=str(I.info).replace('OrderedDict(',B).replace('})','}');U='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,I._fwid,R,__version__);N.write(U);N.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(N,M,A,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(A,E.replace('\\',G)))
		if A not in{'os','sys','logging','gc'}:
			try:del M
			except (F,S):pass
			try:del sys.modules[A]
			except S:pass
		C.collect();return O
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Incomplete';Q=in_class;P=object_expr;O='Exception';H=fp;D=indent;C.collect()
		if P in L.problematic:return
		R,N=L.get_obj_attributes(P)
		if N:J(N)
		for (E,K,G,T,f) in R:
			if E in['classmethod','staticmethod','BaseException',O]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and M(D)<=w*4:
				U=B;V=E.endswith(O)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);L.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),D+'    ',Q+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif any((A in G for A in[t,s,'closure'])):
				W=b;X=B
				if Q>0:X='self, '
				if c in G or c in K:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,X,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[q,o,p,r,'bytearray','bytes']:A=d.format(D,E,K,I)
				elif I in[a,Z,Y]:e={a:'{}',Z:'[]',Y:'()'};A=d.format(D,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,I,G,K)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+E+' # type: Incomplete\n')
		del R;del N
		try:del E,K,G,T
		except (F,S,k):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,T)
		return A
	def clean(B,path=D):
		if path is D:path=B.path
		J('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except (F,I):return
		for E in C:
			A=u.format(path,E)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(A,filename='modules.json'):
		J('Created stubs for {} modules on board {}\nPath: {}'.format(M(A._report),A._fwid,A.path));E=u.format(A.path,filename);C.collect()
		try:
			with W(E,'w')as B:
				A.write_json_header(B);D=O
				for G in A._report:A.write_json_node(B,G,D);D=H
				A.write_json_end(B)
			I=A._start_free-C.mem_free()
		except F:J('Failed to create the report.')
	def write_json_header(C,f):B='firmware';f.write('{');f.write(b({B:C.info})[1:-1]);f.write(A);f.write(b({X:{E:__version__},'stubtype':B})[1:-1]);f.write(A);f.write('"modules" :[\n')
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
			except F as D:
				if D.args[0]==v:
					try:os.mkdir(B)
					except F as E:J('failed to create folder {}'.format(B));raise E
		C=A+1
def U(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	h='ev3-pybricks';g='pycom';d='pycopy';b='GENERIC';a='arch';Z='cpu';Y='ver';V='with';G='mpy';F='build';A=c({N:sys.implementation.name,E:B,F:B,Y:B,m:'stm32'if sys.platform.startswith('pyb')else sys.platform,K:b,Z:B,G:B,a:B})
	try:A[E]=L.join([str(A)for A in sys.implementation.version])
	except I:pass
	try:W=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[K]=W.strip();A[Z]=W.split(V)[1].strip();A[G]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if G in Q(sys.implementation)else B
	except (I,R):pass
	C.collect()
	for J in [A+'/board_info.csv'for A in x]:
		if f(J):
			H=A[K].strip()
			if e(A,H,J):break
			if V in H:
				H=H.split(V)[0].strip()
				if e(A,H,J):break
			A[K]=b
	A[K]=A[K].replace(' ',T);C.collect()
	try:
		A[F]=U(os.uname()[3])
		if not A[F]:A[F]=U(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=U(sys.version.split(';')[1])
	except (I,R):pass
	if A[F]and M(A[F])>5:A[F]=B
	if A[E]==B and sys.platform not in('unix','win32'):
		try:i=os.uname();A[E]=i.release
		except (R,I,TypeError):pass
	for (j,k,l) in [(d,d,'const'),(g,g,'FAT'),(h,'pybricks.hubs','EV3Brick')]:
		try:o=__import__(k,D,D,l);A[N]=j;del o;break
		except (P,S):pass
	if A[N]==h:A['release']='2.0.0'
	if A[N]==n:
		if A[E]and A[E].endswith('.0')and A[E]>='1.10.0'and A[E]<='1.19.9':A[E]=A[E][:-2]
	if G in A and A[G]:
		O=int(A[G]);X=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][O>>10]
		if X:A[a]=X
		A[G]='v{}.{}'.format(O&255,O>>8&3)
	A[Y]=f"v{A[E]}-{A[F]}"if A[F]else f"v{A[E]}";return A
def e(info,board_descr,filename):
	with W(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[K]=D;return O
	return H
def get_root():
	try:A=os.getcwd()
	except (F,I):A=L
	B=A
	for B in [A,'/sd','/flash',G,L]:
		try:C=os.stat(B);break
		except F:continue
	return B
def f(filename):
	try:
		if os.stat(filename)[0]>>14:return O
		return H
	except F:return H
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
	except (i,I):return O
def main():
	D='lvgl'
	try:import lvgl as A
	except l:return
	B=D
	try:B='lvgl-{0}_{1}_{2}-{3}-{4}'.format(A.version_major(),A.version_minor(),A.version_patch(),A.version_info(),sys.platform)
	except l:B='lvgl-{0}_{1}_{2}_{3}-{4}'.format(8,1,0,'dev',sys.platform)
	finally:stubber=Stubber(firmware_id=B)
	stubber.clean();stubber.modules=['io','lodepng','rtch',D];C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or h():
	try:y=logging.getLogger(X);logging.basicConfig(level=logging.INFO)
	except k:pass
	if not f('no_auto_stubber.txt'):
		try:C.threshold(4*1024);C.enable()
		except BaseException:pass
		main()