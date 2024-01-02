v='stubber'
u='{}/{}'
t='method'
s='function'
r='bool'
q='str'
p='float'
o='int'
n='micropython'
m=Exception
l=NameError
k=sorted
j=NotImplementedError
b=',\n'
a='dict'
Z='list'
Y='tuple'
X=open
W=repr
U='cpu'
T='_'
S=len
R=KeyError
Q=IndexError
P=dir
O=print
N=ImportError
M='with'
L='family'
K=True
J='.'
I='board'
H=AttributeError
A=False
G='/'
E=None
D='version'
F=OSError
B=''
import gc as C,os,sys
from ujson import dumps as c
try:from machine import reset
except N:pass
try:from collections import OrderedDict as d
except N:from ucollections import OrderedDict as d
__version__='v1.16.2'
w=2
x=2
y=[J,'/lib','/sd/lib','/flash/lib','lib']
from time import sleep
class Stubber:
	def __init__(A,path=E,firmware_id=E):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise j('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();C.collect()
		if B:A._fwid=B.lower()
		elif A.info[L]==n:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:e(path+G)
		except F:O('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		I=item_instance;D=[];J=[]
		for A in P(I):
			if A.startswith(T)and not A in L.modules:continue
			try:
				E=getattr(I,A)
				try:F=W(type(E)).split("'")[1]
				except Q:F=B
				if F in{o,p,q,r,Y,Z,a}:G=1
				elif F in{s,t}:G=2
				elif F in'class':G=3
				else:G=4
				D.append((A,W(E),W(type(E)),E,G))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(A,I,K))
			except MemoryError as K:sleep(1);reset()
		D=k([A for A in D if not A[0].startswith('__')],key=lambda x:x[4]);C.collect();return D,J
	def add_modules(A,modules):A.modules=k(set(A.modules)|set(modules))
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
		if H is E:O=D.replace(J,T)+'.py';H=I.path+G+O
		else:O=H.split(G)[-1]
		if G in D:D=D.replace(G,J)
		L=E
		try:L=__import__(D,E,E,'*');S=C.mem_free()
		except N:return A
		e(H)
		with X(H,'w')as M:P=str(I.info).replace('OrderedDict(',B).replace('})','}');Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(D,I._fwid,P,__version__);M.write(Q);M.write('from typing import Any\nfrom _typeshed import Incomplete\n\n');I.write_object_stub(M,L,D,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(D,H.replace('\\',G)))
		if D not in{'os','sys','logging','gc'}:
			try:del L
			except(F,R):pass
			try:del sys.modules[D]
			except R:pass
		C.collect();return K
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Incomplete';P=in_class;N=object_expr;M='Exception';H=fp;D=indent;C.collect()
		if N in K.problematic:return
		Q,L=K.get_obj_attributes(N)
		if L:O(L)
		for(E,J,G,T,f)in Q:
			if E in['classmethod','staticmethod','BaseException',M]:continue
			if E[0].isdigit():continue
			if G=="<class 'type'>"and S(D)<=x*4:
				U=B;V=E.endswith(M)or E.endswith('Error')or E in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=M
				A='\n{}class {}({}):\n'.format(D,E,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);K.write_object_stub(H,T,'{0}.{1}'.format(obj_name,E),D+'    ',P+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif any(A in G for A in[t,s,'closure']):
				W=b;X=B
				if P>0:X='self, '
				if c in G or c in J:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,E,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,E,X,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[q,o,p,r,'bytearray','bytes']:A=d.format(D,E,J,I)
				elif I in[a,Z,Y]:e={a:'{}',Z:'[]',Y:'()'};A=d.format(D,E,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,E,I,G,J)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+E+' # type: Incomplete\n')
		del Q;del L
		try:del E,J,G,T
		except(F,R,l):pass
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
			A=u.format(path,D)
			try:os.remove(A)
			except F:
				try:B.clean(A);os.rmdir(A)
				except F:pass
	def report(B,filename='modules.json'):
		G=u.format(B.path,filename);C.collect()
		try:
			with X(G,'w')as D:
				B.write_json_header(D);E=K
				for H in B._report:B.write_json_node(D,H,E);E=A
				B.write_json_end(D)
			I=B._start_free-C.mem_free()
		except F:O('Failed to create the report.')
	def write_json_header(B,f):A='firmware';f.write('{');f.write(c({A:B.info})[1:-1]);f.write(b);f.write(c({v:{D:__version__},'stubtype':A})[1:-1]);f.write(b);f.write('"modules" :[\n')
	def write_json_node(A,f,n,first):
		if not first:f.write(b)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def e(path):
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
def V(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	e='ev3-pybricks';c='pycom';b='pycopy';a='unix';Z='win32';Y='arch';X='ver';K='mpy';G='port';F='build';A=d({L:sys.implementation.name,D:B,F:B,X:B,G:sys.platform,I:'UNKNOWN',U:B,K:B,Y:B})
	if A[G].startswith('pyb'):A[G]='stm32'
	elif A[G]==Z:A[G]='windows'
	elif A[G]=='linux':A[G]=a
	try:A[D]=J.join([str(A)for A in sys.implementation.version])
	except H:pass
	try:T=sys.implementation._machine if'_machine'in P(sys.implementation)else os.uname().machine;A[I]=M.join(T.split(M)[:-1]).strip();A[U]=T.split(M)[-1].strip();A[K]=sys.implementation._mpy if'_mpy'in P(sys.implementation)else sys.implementation.mpy if K in P(sys.implementation)else B
	except(H,Q):pass
	C.collect();z(A);C.collect()
	try:
		A[F]=V(os.uname()[3])
		if not A[F]:A[F]=V(os.uname()[2])
		if not A[F]and';'in sys.version:A[F]=V(sys.version.split(';')[1])
	except(H,Q):pass
	if A[F]and S(A[F])>5:A[F]=B
	if A[D]==B and sys.platform not in(a,Z):
		try:f=os.uname();A[D]=f.release
		except(Q,H,TypeError):pass
	for(g,h,i)in[(b,b,'const'),(c,c,'FAT'),(e,'pybricks.hubs','EV3Brick')]:
		try:j=__import__(h,E,E,i);A[L]=g;del j;break
		except(N,R):pass
	if A[L]==e:A['release']='2.0.0'
	if A[L]==n:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.19.9':A[D]=A[D][:-2]
	if K in A and A[K]:
		O=int(A[K]);W=[E,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][O>>10]
		if W:A[Y]=W
		A[K]='v{}.{}'.format(O&255,O>>8&3)
	A[X]=f"v{A[D]}-{A[F]}"if A[F]else f"v{A[D]}";return A
def z(info,desc=B):
	G='with ';D=info;E=A
	for F in[A+'/board_info.csv'for A in y]:
		if g(F):
			B=desc or D[I].strip()
			if f(D,B,F):E=K;break
			if M in B:
				B=B.split(M)[0].strip()
				if f(D,B,F):E=K;break
	if not E:
		B=desc or D[I].strip()
		if G+D[U].upper()in B:B=B.split(G+D[U].upper())[0].strip()
		D[I]=B
	D[I]=D[I].replace(' ',T);C.collect()
def f(info,board_descr,filename):
	with X(filename,'r')as C:
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
def g(filename):
	try:
		if os.stat(filename)[0]>>14:return K
		return A
	except F:return A
def h():sys.exit(1)
def read_path():
	path=B
	if S(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:h()
	elif S(sys.argv)==2:h()
	return path
def i():
	try:B=bytes('abc',encoding='utf8');C=i.__module__;return A
	except(j,H):return K
def main():
	D='lvgl'
	try:import lvgl as A
	except m:return
	B=D
	try:B='lvgl-{0}_{1}_{2}-{3}-{4}'.format(A.version_major(),A.version_minor(),A.version_patch(),A.version_info(),sys.platform)
	except m:B='lvgl-{0}_{1}_{2}_{3}-{4}'.format(8,1,0,'dev',sys.platform)
	finally:stubber=Stubber(firmware_id=B)
	stubber.clean();stubber.modules=['io','lodepng','rtch',D];C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or i():
	try:A0=logging.getLogger(v);logging.basicConfig(level=logging.INFO)
	except l:pass
	if not g('no_auto_stubber.txt'):
		try:C.threshold(4*1024);C.enable()
		except BaseException:pass
		main()