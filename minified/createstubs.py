e='utf8'
d='{}/{}'
c='_thread'
b=IndexError
a=NameError
Z=print
Y=NotImplementedError
S='.db'
R='version'
Q='__init__'
O='modulelist'
N=True
M=KeyError
L=ImportError
K='.'
J='_'
I=len
G=open
H=''
F=AttributeError
B=False
E='/'
D=None
A=OSError
import sys,gc as C,uos as os
from utime import sleep_us as f
from ujson import dumps as P
__version__='1.4.3'
T=2
g=2
try:from machine import resetWDT as U
except L:
	def U():0
class Stubber:
	def __init__(B,path=D,firmware_id=D):
		G=firmware_id;D=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise Y('MicroPython 1.13.0 cannot be stubbed')
		except F:pass
		B._report=[];B.info=_info();C.collect()
		if G:B._fwid=str(G).lower()
		else:B._fwid='{family}-{port}-{ver}'.format(**B.info).lower()
		B._start_free=C.mem_free()
		if D:
			if D.endswith(E):D=D[:-1]
		else:D=get_root()
		B.path='{}/stubs/{}'.format(D,B.flat_fwid).replace('//',E)
		try:V(D+E)
		except A:pass
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[]
	def get_obj_attributes(L,item_instance):
		K="Couldn't get attribute '{}' from object '{}', Err: {}";A=item_instance;B=[];G=[];M=D
		try:
			for E in dir(A):
				try:H=getattr(A,E);B.append((E,repr(H),repr(type(H)),H))
				except F as I:G.append(K.format(E,A,I))
		except F as I:G.append(K.format(E,A,I))
		B=[A for A in B if not(A[0].startswith(J)and A[0]!=Q)];C.collect();return B,G
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(F,module_name):
		D=module_name
		if D.startswith(J)and D!=c:return B
		if D in F.problematic:return B
		if D in F.excluded:return B
		G='{}/{}.py'.format(F.path,D.replace(K,E));C.collect();H=C.mem_free();Z('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(D,G,H))
		try:F.create_module_stub(D,G)
		except A:return B
		C.collect();return N
	def create_module_stub(F,module_name,file_name=D):
		I=file_name;B=module_name
		if B.startswith(J)and B!=c:return
		if B in F.problematic:return
		if I is D:I=F.path+E+B.replace(K,J)+'.py'
		if E in B:B=B.replace(E,K)
		N=D
		try:N=__import__(B,D,D,'*')
		except L:return
		V(I)
		with G(I,'w')as O:P='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(B,F._fwid,F.info,__version__);O.write(P);O.write('from typing import Any\n\n');F.write_object_stub(O,N,B,H)
		F._report.append({'module':B,'file':I})
		if not B in['os','sys','logging','gc']:
			try:del N
			except (A,M):pass
			try:del sys.modules[B]
			except M:pass
		C.collect()
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		b='tuple';Z='list';Y='dict';X='{0}{1} = {2} # type: {3}\n';W='bound_method';V='Any';P=in_class;O=object_expr;J=fp;B=indent;C.collect()
		if O in L.problematic:return
		R,c=L.get_obj_attributes(O)
		for (D,K,F,S) in R:
			if D in['classmethod','staticmethod']:continue
			U();f(1)
			if F=="<class 'type'>"and I(B)<=g*4:E='\n'+B+'class '+D+':\n';E+=B+"    ''\n";J.write(E);L.write_object_stub(J,S,'{0}.{1}'.format(obj_name,D),B+'    ',P+1)
			elif'method'in F or'function'in F or D==Q:
				N=V;T=H
				if P>0:
					T='self, '
					if D==Q:N='None'
				if W in F or W in K:E='{}@classmethod\n'.format(B);E+='{}def {}(cls, *args) -> {}:\n'.format(B,D,N)
				else:E='{}def {}({}*args) -> {}:\n'.format(B,D,T,N)
				E+=B+'    ...\n\n';J.write(E)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				G=F[8:-2];E=H
				if G in['str','int','float','bool','bytearray','bytes']:E=X.format(B,D,K,G)
				elif G in[Y,Z,b]:d={Y:'{}',Z:'[]',b:'()'};E=X.format(B,D,d[G],G)
				else:
					if not G in['object','set','frozenset']:G=V
					E='{0}{1} : {2} ## {3} = {4}\n'.format(B,D,G,F,K)
				J.write(E)
			else:J.write("# all other, type = '{0}'\n".format(F));J.write(B+D+' # type: Any\n')
		del R;del c
		try:del D,K,F,S
		except (A,M,a):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,J)
		return A
	def clean(E,path=D):
		B=path
		if B is D:B=E.path
		Z('Clean/remove files in folder: {}'.format(B))
		try:G=os.listdir(B)
		except (A,F):return
		for H in G:
			C=d.format(B,H)
			try:os.remove(C)
			except A:
				try:E.clean(C);os.rmdir(C)
				except A:pass
	def report(E,filename='modules.json'):
		F=',\n';I=d.format(E.path,filename);C.collect()
		try:
			with G(I,'w')as D:
				D.write('{');D.write(P({'firmware':E.info})[1:-1]);D.write(F);D.write(P({'stubber':{R:__version__}})[1:-1]);D.write(F);D.write('"modules" :[\n');H=N
				for J in E._report:
					if H:H=B
					else:D.write(F)
					D.write(P(J))
				D.write('\n]}')
			K=E._start_free-C.mem_free()
		except A:pass
def V(path):
	C=path;B=F=0
	while B!=-1:
		B=C.find(E,F)
		if B!=-1:
			if B==0:D=C[0]
			else:D=C[0:B]
			try:I=os.stat(D)
			except A as G:
				if G.args[0]==T:
					try:os.mkdir(D)
					except A as H:raise H
				else:raise G
		F=B+1
def _info():
	W='loboris';V='0.0.0';U='port';T='platform';S='machine';Q='nodename';P='name';J='unknown';I='sysname';G='build';E='ver';D='family';B='release';N=sys.implementation.name;O=sys.platform;A={P:N,B:V,R:V,G:H,I:J,Q:J,S:J,D:N,T:O,U:O,E:H}
	try:A[B]=K.join([str(A)for A in sys.implementation.version]);A[R]=A[B];A[P]=sys.implementation.name;A['mpy']=sys.implementation.mpy
	except F:pass
	if sys.platform not in('unix','win32'):
		try:
			C=os.uname();A[I]=C.sysname;A[Q]=C.nodename;A[B]=C.release;A[S]=C.machine
			if' on 'in C.version:
				X=C.version.split('on ')[0]
				try:A[G]=X.split('-')[1]
				except b:pass
		except (b,F,TypeError):pass
	try:from pycopy import const;A[D]='pycopy';del const
	except (L,M):pass
	if A[T]=='esp32_LoBo':A[D]=W;A[U]='esp32'
	elif A[I]=='ev3':
		A[D]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except L:pass
	if A[B]:A[E]='v'+A[B]
	if A[D]!=W:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[E]=A[B][:-2]
		else:A[E]=A[B]
		if A[G]!=H:A[E]+='-'+A[G]
	return A
def get_root():
	B='/flash'
	try:D=os.stat(B)
	except A as C:
		if C.args[0]==T:
			try:B=os.getcwd()
			except (A,F):B=K
		else:B=E
	return B
def W():sys.exit(1)
def read_path():
	A=H
	if I(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):A=sys.argv[2]
		else:W()
	elif I(sys.argv)==2:W()
	return A
def X():
	try:A=bytes('abc',encoding=e);C=X.__module__;return B
	except (Y,F):return N
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[A.strip()for A in G('modulelist.txt')if I(A.strip())];C.collect();stubber.create_all_stubs();stubber.report()
h=B
def i():os.remove(O+S)
def j():
	K=b'todo';import btree
	try:E=G(O+S,'r+b');F=N
	except A:E=G(O+S,'w+b');F=B
	stubber=Stubber(path=read_path())
	if not F:stubber.clean()
	C=btree.open(E)
	if not F or I(list(C.keys()))==0:
		for L in G(O+'.txt'):
			D=L.strip()
			if I(D)and D[0]!='#':C[D]=K
		C.flush()
	for D in C.keys():
		if C[D]!=K:continue
		H=B
		try:H=stubber.create_one_stub(D.decode(e))
		except MemoryError:C.close();E.close();import machine as M;M.reset()
		if H:J='good, I guess'
		else:J=b'skipped'
		C[D]=J;C.flush()
	C.close();E.close()
if __name__=='__main__'or X():
	try:logging.basicConfig(level=logging.INFO)
	except a:pass
	main()