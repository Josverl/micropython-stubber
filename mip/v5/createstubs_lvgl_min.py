t='{}/{}'
s='method'
r='function'
q='bool'
p='str'
o='float'
n='int'
m='micropython'
l='port'
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
T='_'
S=KeyError
R=IndexError
Q=dir
P=True
O='family'
N=len
M=ImportError
L='.'
K='board'
J=print
I=AttributeError
H=False
G='/'
F=None
D='version'
E=OSError
B=''
import gc as C,sys,uos as os
from ujson import dumps as a
try:from machine import reset
except M:pass
try:from collections import OrderedDict as b
except M:from ucollections import OrderedDict as b
__version__='v1.12.2'
u=2
v=2
w=[L,'/lib','/flash/lib','lib']
class Stubber:
	def __init__(A,path=F,firmware_id=F):
		B=firmware_id
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise h('MicroPython 1.13.0 cannot be stubbed')
		except I:pass
		A._report=[];A.info=_info();J('Port: {}'.format(A.info[l]));J('Board: {}'.format(A.info[K]));C.collect()
		if B:A._fwid=B.lower()
		elif A.info[O]==m:A._fwid='{family}-{ver}-{port}-{board}'.format(**A.info)
		else:A._fwid='{family}-{ver}-{port}'.format(**A.info)
		A._start_free=C.mem_free()
		if path:
			if path.endswith(G):path=path[:-1]
		else:path=get_root()
		A.path='{}/stubs/{}'.format(path,A.flat_fwid).replace('//',G)
		try:c(path+G)
		except E:J('error creating stub folder {}'.format(path))
		A.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=[]
	def get_obj_attributes(L,item_instance):
		G=item_instance;A=[];J=[]
		for H in Q(G):
			try:
				D=getattr(G,H)
				try:E=V(type(D)).split("'")[1]
				except R:E=B
				if E in{n,o,p,q,X,Y,Z}:F=1
				elif E in{r,s}:F=2
				elif E in'class':F=3
				else:F=4
				A.append((H,V(D),V(type(D)),D,F))
			except I as K:J.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(H,G,K))
		A=i([A for A in A if not A[0].startswith(T)],key=lambda x:x[4]);C.collect();return A,J
	def add_modules(A,modules):A.modules=i(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(A,module_name):
		B=module_name
		if B in A.problematic:return H
		if B in A.excluded:return H
		F='{}/{}.py'.format(A.path,B.replace(L,G));C.collect();D=H
		try:D=A.create_module_stub(B,F)
		except E:return H
		C.collect();return D
	def create_module_stub(I,module_name,file_name=F):
		D=file_name;A=module_name
		if C.mem_free()<8500:
			try:from machine import reset;reset()
			except M:pass
		if D is F:K=A.replace(L,T)+'.py';D=I.path+G+K
		else:K=D.split(G)[-1]
		if G in A:A=A.replace(G,L)
		N=F
		try:N=__import__(A,F,F,'*');J('Stub module: {:<25} to file: {:<70} mem:{:>5}'.format(A,K,C.mem_free()))
		except M:return H
		c(D)
		with W(D,'w')as O:Q='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,I._fwid,I.info,__version__);O.write(Q);O.write('from typing import Any\n\n');I.write_object_stub(O,N,A,B)
		I._report.append('{{"module": "{}", "file": "{}"}}'.format(A,D.replace('\\',G)))
		if A not in{'os','sys','logging','gc'}:
			try:del N
			except (E,S):pass
			try:del sys.modules[A]
			except S:pass
		C.collect();return P
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		d='{0}{1} = {2} # type: {3}\n';c='bound_method';b='Any';Q=in_class;P=object_expr;O='Exception';H=fp;D=indent;C.collect()
		if P in L.problematic:return
		R,M=L.get_obj_attributes(P)
		if M:J(M)
		for (F,K,G,T,f) in R:
			if F in['classmethod','staticmethod','BaseException',O]:continue
			if G=="<class 'type'>"and N(D)<=v*4:
				U=B;V=F.endswith(O)or F.endswith('Error')or F in['KeyboardInterrupt','StopIteration','SystemExit']
				if V:U=O
				A='\n{}class {}({}):\n'.format(D,F,U)
				if V:A+=D+'    ...\n';H.write(A);return
				H.write(A);L.write_object_stub(H,T,'{0}.{1}'.format(obj_name,F),D+'    ',Q+1);A=D+'    def __init__(self, *argv, **kwargs) -> None:\n';A+=D+'        ...\n\n';H.write(A)
			elif s in G or r in G:
				W=b;a=B
				if Q>0:a='self, '
				if c in G or c in K:A='{}@classmethod\n'.format(D)+'{}def {}(cls, *args, **kwargs) -> {}:\n'.format(D,F,W)
				else:A='{}def {}({}*args, **kwargs) -> {}:\n'.format(D,F,a,W)
				A+=D+'    ...\n\n';H.write(A)
			elif G=="<class 'module'>":0
			elif G.startswith("<class '"):
				I=G[8:-2];A=B
				if I in[p,n,o,q,'bytearray','bytes']:A=d.format(D,F,K,I)
				elif I in[Z,Y,X]:e={Z:'{}',Y:'[]',X:'()'};A=d.format(D,F,e[I],I)
				else:
					if I not in['object','set','frozenset']:I=b
					A='{0}{1} : {2} ## {3} = {4}\n'.format(D,F,I,G,K)
				H.write(A)
			else:H.write("# all other, type = '{0}'\n".format(G));H.write(D+F+' # type: Any\n')
		del R;del M
		try:del F,K,G,T
		except (E,S,j):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,T)
		return A
	def clean(B,path=F):
		if path is F:path=B.path
		J('Clean/remove files in folder: {}'.format(path))
		try:os.stat(path);C=os.listdir(path)
		except (E,I):return
		for D in C:
			A=t.format(path,D)
			try:os.remove(A)
			except E:
				try:B.clean(A);os.rmdir(A)
				except E:pass
	def report(A,filename='modules.json'):
		J('Created stubs for {} modules on board {}\nPath: {}'.format(N(A._report),A._fwid,A.path));F=t.format(A.path,filename);C.collect()
		try:
			with W(F,'w')as B:
				A.write_json_header(B);D=P
				for G in A._report:A.write_json_node(B,G,D);D=H
				A.write_json_end(B)
			I=A._start_free-C.mem_free()
		except E:J('Failed to create the report.')
	def write_json_header(C,f):B='firmware';f.write('{');f.write(a({B:C.info})[1:-1]);f.write(A);f.write(a({'stubber':{D:__version__},'stubtype':B})[1:-1]);f.write(A);f.write('"modules" :[\n')
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
			except E as D:
				if D.args[0]==u:
					try:os.mkdir(B)
					except E as F:J('failed to create folder {}'.format(B));raise F
		C=A+1
def U(s):
	A=' on '
	if not s:return B
	if A in s:s=s.split(A,1)[0]
	return s.split('-')[1]if'-'in s else B
def _info():
	h='ev3-pybricks';g='pycom';f='pycopy';c='GENERIC';a='arch';Z='cpu';Y='ver';V='with';G='mpy';E='build';A=b({O:sys.implementation.name,D:B,E:B,Y:B,l:'stm32'if sys.platform.startswith('pyb')else sys.platform,K:c,Z:B,G:B,a:B})
	try:A[D]=L.join([str(A)for A in sys.implementation.version])
	except I:pass
	try:W=sys.implementation._machine if'_machine'in Q(sys.implementation)else os.uname().machine;A[K]=W.strip();A[Z]=W.split(V)[1].strip();A[G]=sys.implementation._mpy if'_mpy'in Q(sys.implementation)else sys.implementation.mpy if G in Q(sys.implementation)else B
	except (I,R):pass
	C.collect()
	for J in [A+'/board_info.csv'for A in w]:
		if e(J):
			H=A[K].strip()
			if d(A,H,J):break
			if V in H:
				H=H.split(V)[0].strip()
				if d(A,H,J):break
			A[K]=c
	A[K]=A[K].replace(' ',T);C.collect()
	try:
		A[E]=U(os.uname()[3])
		if not A[E]:A[E]=U(os.uname()[2])
		if not A[E]and';'in sys.version:A[E]=U(sys.version.split(';')[1])
	except (I,R):pass
	if A[E]and N(A[E])>5:A[E]=B
	if A[D]==B and sys.platform not in('unix','win32'):
		try:i=os.uname();A[D]=i.release
		except (R,I,TypeError):pass
	for (j,k,n) in [(f,f,'const'),(g,g,'FAT'),(h,'pybricks.hubs','EV3Brick')]:
		try:o=__import__(k,F,F,n);A[O]=j;del o;break
		except (M,S):pass
	if A[O]==h:A['release']='2.0.0'
	if A[O]==m:
		if A[D]and A[D].endswith('.0')and A[D]>='1.10.0'and A[D]<='1.20.0':A[D]=A[D][:-2]
	if G in A and A[G]:
		P=int(A[G]);X=[F,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][P>>10]
		if X:A[a]=X
		A[G]='v{}.{}'.format(P&255,P>>8&3)
	A[Y]=f"v{A[D]}-{A[E]}"if A[E]else f"v{A[D]}";return A
def d(info,board_descr,filename):
	with W(filename,'r')as B:
		while 1:
			A=B.readline()
			if not A:break
			C,D=A.split(',')[0].strip(),A.split(',')[1].strip()
			if C==board_descr:info[K]=D;return P
	return H
def get_root():
	try:A=os.getcwd()
	except (E,I):A=L
	B=A
	for B in [A,'/sd','/flash',G,L]:
		try:C=os.stat(B);break
		except E:continue
	return B
def e(filename):
	try:
		if os.stat(filename)[0]>>14:return P
		return H
	except E:return H
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
	try:A=bytes('abc',encoding='utf8');B=g.__module__;return H
	except (h,I):return P
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