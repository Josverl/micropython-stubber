b='{}/{}'
a='_thread'
Z=IndexError
Y=NameError
X=print
W=NotImplementedError
R='version'
Q=True
P='__init__'
O=open
M=len
L=KeyError
K=ImportError
J='.'
I='_'
G=False
H=''
F=AttributeError
E='/'
D=None
A=OSError
import sys,gc as C,uos as os
from utime import sleep_us as c
from ujson import dumps as N
__version__='1.4.3'
S=2
d=2
try:from machine import resetWDT as T
except K:
	def T():0
class Stubber:
	def __init__(B,path=D,firmware_id=D):
		G=firmware_id;D=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise W('MicroPython 1.13.0 cannot be stubbed')
		except F:pass
		B._report=[];B.info=_info();C.collect()
		if G:B._fwid=str(G).lower()
		else:B._fwid='{family}-{port}-{ver}'.format(**B.info).lower()
		B._start_free=C.mem_free()
		if D:
			if D.endswith(E):D=D[:-1]
		else:D=get_root()
		B.path='{}/stubs/{}'.format(D,B.flat_fwid).replace('//',E)
		try:U(D+E)
		except A:pass
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[]
	def get_obj_attributes(L,item_instance):
		K="Couldn't get attribute '{}' from object '{}', Err: {}";A=item_instance;B=[];G=[];M=D
		try:
			for E in dir(A):
				try:H=getattr(A,E);B.append((E,repr(H),repr(type(H)),H))
				except F as J:G.append(K.format(E,A,J))
		except F as J:G.append(K.format(E,A,J))
		B=[A for A in B if not(A[0].startswith(I)and A[0]!=P)];C.collect();return B,G
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(D,module_name):
		B=module_name
		if B.startswith(I)and B!=a:return G
		if B in D.problematic:return G
		if B in D.excluded:return G
		F='{}/{}.py'.format(D.path,B.replace(J,E));C.collect();H=C.mem_free();X('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(B,F,H))
		try:D.create_module_stub(B,F)
		except A:return G
		C.collect();return Q
	def create_module_stub(F,module_name,file_name=D):
		G=file_name;B=module_name
		if B.startswith(I)and B!=a:return
		if B in F.problematic:return
		if G is D:G=F.path+E+B.replace(J,I)+'.py'
		if E in B:B=B.replace(E,J)
		M=D
		try:M=__import__(B,D,D,'*')
		except K:return
		U(G)
		with O(G,'w')as N:P='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(B,F._fwid,F.info,__version__);N.write(P);N.write('from typing import Any\n\n');F.write_object_stub(N,M,B,H)
		F._report.append({'module':B,'file':G})
		if not B in['os','sys','logging','gc']:
			try:del M
			except (A,L):pass
			try:del sys.modules[B]
			except L:pass
		C.collect()
	def write_object_stub(K,fp,object_expr,obj_name,indent,in_class=0):
		b='tuple';a='list';Z='dict';X='{0}{1} = {2} # type: {3}\n';W='bound_method';V='Any';Q=in_class;O=object_expr;I=fp;B=indent;C.collect()
		if O in K.problematic:return
		R,e=K.get_obj_attributes(O)
		for (D,J,F,S) in R:
			if D in['classmethod','staticmethod']:continue
			T();c(1)
			if F=="<class 'type'>"and M(B)<=d*4:E='\n'+B+'class '+D+':\n';E+=B+"    ''\n";I.write(E);K.write_object_stub(I,S,'{0}.{1}'.format(obj_name,D),B+'    ',Q+1)
			elif'method'in F or'function'in F or D==P:
				N=V;U=H
				if Q>0:
					U='self, '
					if D==P:N='None'
				if W in F or W in J:E='{}@classmethod\n'.format(B);E+='{}def {}(cls, *args) -> {}:\n'.format(B,D,N)
				else:E='{}def {}({}*args) -> {}:\n'.format(B,D,U,N)
				E+=B+'    ...\n\n';I.write(E)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				G=F[8:-2];E=H
				if G in['str','int','float','bool','bytearray','bytes']:E=X.format(B,D,J,G)
				elif G in[Z,a,b]:f={Z:'{}',a:'[]',b:'()'};E=X.format(B,D,f[G],G)
				else:
					if not G in['object','set','frozenset']:G=V
					E='{0}{1} : {2} ## {3} = {4}\n'.format(B,D,G,F,J)
				I.write(E)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(B+D+' # type: Any\n')
		del R;del e
		try:del D,J,F,S
		except (A,L,Y):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,I)
		return A
	def clean(E,path=D):
		B=path
		if B is D:B=E.path
		X('Clean/remove files in folder: {}'.format(B))
		try:G=os.listdir(B)
		except (A,F):return
		for H in G:
			C=b.format(B,H)
			try:os.remove(C)
			except A:
				try:E.clean(C);os.rmdir(C)
				except A:pass
	def report(D,filename='modules.json'):
		E=',\n';H=b.format(D.path,filename);C.collect()
		try:
			with O(H,'w')as B:
				B.write('{');B.write(N({'firmware':D.info})[1:-1]);B.write(E);B.write(N({'stubber':{R:__version__}})[1:-1]);B.write(E);B.write('"modules" :[\n');F=Q
				for I in D._report:
					if F:F=G
					else:B.write(E)
					B.write(N(I))
				B.write('\n]}')
			J=D._start_free-C.mem_free()
		except A:pass
def U(path):
	C=path;B=F=0
	while B!=-1:
		B=C.find(E,F)
		if B!=-1:
			if B==0:D=C[0]
			else:D=C[0:B]
			try:I=os.stat(D)
			except A as G:
				if G.args[0]==S:
					try:os.mkdir(D)
					except A as H:raise H
				else:raise G
		F=B+1
def _info():
	W='loboris';V='0.0.0';U='port';T='platform';S='machine';Q='nodename';P='name';M='unknown';I='sysname';G='build';E='ver';D='family';B='release';N=sys.implementation.name;O=sys.platform;A={P:N,B:V,R:V,G:H,I:M,Q:M,S:M,D:N,T:O,U:O,E:H}
	try:A[B]=J.join([str(A)for A in sys.implementation.version]);A[R]=A[B];A[P]=sys.implementation.name;A['mpy']=sys.implementation.mpy
	except F:pass
	if sys.platform not in('unix','win32'):
		try:
			C=os.uname();A[I]=C.sysname;A[Q]=C.nodename;A[B]=C.release;A[S]=C.machine
			if' on 'in C.version:
				X=C.version.split('on ')[0]
				try:A[G]=X.split('-')[1]
				except Z:pass
		except (Z,F,TypeError):pass
	try:from pycopy import const;A[D]='pycopy';del const
	except (K,L):pass
	if A[T]=='esp32_LoBo':A[D]=W;A[U]='esp32'
	elif A[I]=='ev3':
		A[D]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except K:pass
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
		if C.args[0]==S:
			try:B=os.getcwd()
			except (A,F):B=J
		else:B=E
	return B
def B():sys.exit(1)
def read_path():
	A=H
	if M(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):A=sys.argv[2]
		else:B()
	elif M(sys.argv)==2:B()
	return A
def V():
	try:A=bytes('abc',encoding='utf8');B=V.__module__;return G
	except (W,F):return Q
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	try:stubber.modules=[A.strip()for A in O('modulelist'+'.txt')if M(A.strip())and A.strip()[0]!='#']
	except A:stubber.modules=['micropython']
	C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or V():
	try:logging.basicConfig(level=logging.INFO)
	except Y:pass
	main()