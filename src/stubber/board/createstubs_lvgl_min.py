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
A=',\n'
Z='dict'
Y='list'
X='tuple'
W=open
V=repr
U=ImportError
S='_'
R=KeyError
Q=dir
P=True
O='family'
N=len
M=IndexError
L='.'
K='board'
J=print
I=False
G='/'
H=AttributeError
F=None
E='version'
D=OSError
B=''
import gc as C,sys,uos as os
from ujson import dumps as a
try:from collections import OrderedDict as b
except U:from ucollections import OrderedDict as b
__version__='v1.12.2'
t=2
u=2
class Stubber:
	def __init__(A,path=F,firmware_id=F):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise h('MicroPython 1.13.0 cannot be stubbed')
		except H:pass
		A._report=[];A.info=_info();C.collect()
		if B:A._fwid=B.lower()
		elif A.info[O]==l:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:c(path+G)
		except D:J('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		G=item_instance;A=[];J=[]
		for I in Q(G):
			try:
				D=getattr(G,I)
				try:E=V(type(D)).split("'")[1]
				except M:E=B
				if E in{m,n,o,p,X,Y,Z}:F=1
				elif E in{q,r}:F=2
				elif E in'class':F=3
				else:F=4
				A.append((I,V(D),V(type(D)),D,F))
			except H as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(I,G,K))
		A=i([A for A in A if not A[0].startswith(S)],key=lambda x:x[4]);C.collect();return A,J
	def add_modules(A,modules):A.modules=i(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(A,module_name):
		B=module_name
		if B in A.problematic:return I
		if B in A.excluded:return I
		F='{}/{}.py'.format(A.path,B.replace(L,G));C.collect();E=I
		try:E=A.create_module_stub(B,F)
		except D:return I
		C.collect();return E
	def create_module_stub(H,module_name,file_name=F):
		E=file_name;A=module_name
		if E is F:E=H.path+G+A.replace(L,S)+'.py'
		if G in A:A=A.replace(G,L)
		K=F
		try:K=__import__(A,F,F,'*');J('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,E,C.mem_free()))
		except U:return I
		c(E)
		with W(E,'w')as M:N='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,H._fwid,H.info,__version__);M.write(N);M.write('from typing import Any\n\n');H.write_object_stub(M,K,A,B)
		H._report.append('{{"module": "{}", "file": "{}"}}'.format(A,E.replace('\\',G)))
		if A not in{'os','sys','logging','gc'}:
			try:del K
			except (D,R):pass
			try:del sys.modules[A]
			except R:pass
		C.collect();return P
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';Q=in_class;P=object_expr;O='Exception';H=fp;E=indent;C.collect()
		if P in L.problematic:return
		S,M=L.get_obj_attributes(P)
		if M:J(M)
		for (F,K,G,T,f) in S:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if G=="<class 'type'>"and N(E)<=u*4:
				U=B;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(E,F,U)
				if V:A+=E+'    ...\n';H.write(A);return
				H.write(A);L.write_object_stub(H,T,'{0}.{1}'.format(obj_name,F),E+'    ',Q+1);A=E+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=E+'        ...\n\n';H.write(A)
			elif r in G or q in G:
				W=b;a=B
				if Q>0:a='self, '
				if c in G or c in K:A='{}@classmethod\n'.format(E)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(E,F,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(E,F,a,W)
				A+=E+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[o,m,n,p,'bytearray','bytes']:A=d.format(E,F,K,I)
				elif I in[Z,Y,X]:e={Z:'{}',Y:'[]',X:'()'};A=d.format(E,F,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(E,F,I,G,K)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(E+F+' # type: Any\n')
		del S;del M
		try:del F,K,G,T
		except (D,R,j):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,S)
		return A
	def clean(B,path=F):
		if path is F:path=B.path
		J('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except (D,H):return
		for E in C:
			A=s.format(path,E)
			try:os.remove(A)
			except D:
				try:B.clean(A);os.rmdir(A)
				except D:pass
	def report(A,filename='modules.json'):
		J('Created stubs for {} modules on board {}\nPath: {}'.format(N(A._report),A._fwid,A.path));F=s.format(A.path,filename);C.collect()
		try:
			with W(F,'w')as B:
				A.write_json_header(B);E=P
				for G in A._report:A.write_json_node(B,G,E);E=I
				A.write_json_end(B)
			H=A._start_free-C.mem_free()
		except D:J('Failed to create the report.')
	def write_json_header(C,f):B='firmware';f.write('{');f.write(a({B:C.info})[1:-1]);f.write(A);f.write(a({'stubber':{E:__version__},'stubtype':B})[1:-1]);f.write(A);f.write('"modules" :[\n')
	def write_json_node(B,f,n,first):
		if not first:f.write(A)
		f.write(n)
	def write_json_end(A,f):f.write('\n]}')
def c(path):
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
def T(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	i='ev3-pybricks';h='pycom';g='pycopy';f='GENERIC';c='arch';a='cpu';Z='ver';W='with';I='mpy';G='build';A=b({O:sys.implementation.name,E:B,G:B,Z:B,'port':'stm32'if sys.platform.startswith('pyb')else sys.platform,K:f,a:B,I:B,c:B})
	try:A[E]=L.join([str(A)for A in sys.implementation.version])
	except H:pass
	try:X=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[K]=X.strip();A[a]=X.split(W)[1].strip();A[I]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if I in Q(sys.implementation)else B
	except (H,M):pass
	C.collect()
	try:
		for P in ['board_info.csv','lib/board_info.csv']:
			if e(P):
				J=A[K].strip()
				if d(A,J,P):break
				if W in J:
					J=J.split(W)[0].strip()
					if d(A,J,P):break
				A[K]=f
	except (H,M,D):pass
	A[K]=A[K].replace(' ',S);C.collect()
	try:
		A[G]=T(os.uname()[3])
		if not A[G]:A[G]=T(os.uname()[2])
		if not A[G]and';'in sys.version:A[G]=T(sys.version.split(';')[1])
	except (H,M):pass
	if A[G]and N(A[G])>5:A[G]=B
	if A[E]==B and sys.platform not in('unix','win32'):
		try:j=os.uname();A[E]=j.release
		except (M,H,TypeError):pass
	for (k,m,n) in [(g,g,'const'),(h,h,'FAT'),(i,'pybricks.hubs','EV3Brick')]:
		try:o=__import__(m,F,F,n);A[O]=k;del o;break
		except (U,R):pass
	if A[O]==i:A['release']='2.0.0'
	if A[O]==l:
		if A[E]and A[E].endswith('.0')and A[E]>='1.10.0'and A[E]<='1.20.0':A[E]=A[E][:-2]
	if I in A and A[I]:
		V=int(A[I]);Y=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][V>>10]
		if Y:A[c]=Y
		A[I]='v{}.{}'.format(V&255,V>>8&3)
	A[Z]=f"v{A[E]}-{A[G]}"if A[G]else f"v{A[E]}";return A
def d(info,board_descr,filename):
	with W(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[K]=D;return P
	return I
def get_root():
	try:A=os.getcwd()
	except (D,H):A=L
	B=A
	for B in [A,'/sd','/flash',G,L]:
		try:C=os.stat(B);break
		except D:continue
	return B
def e(filename):
	try:os.stat(filename);return P
	except D:return I
def f():sys.exit(1)
def read_path():
	path=B
	if N(sys.argv)==3:
		A=sys.argv[1].lower()
		if A in('--path','-p'):path=sys.argv[2]
		else:f()
	elif N(sys.argv)==2:f()
	return path
def g():
	try:A=bytes('abc',encoding='utf8');B=g.__module__;return I
	except (h,H):return P
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
	try:logging.basicConfig(level=logging.INFO)
	except j:pass
	if not e('no_auto_stubber.txt'):main()