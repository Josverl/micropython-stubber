h='modulelist.txt'
g='utf8'
f='stubber'
e='{}/{}'
d='_thread'
c=IndexError
b=NameError
a=print
Z=NotImplementedError
T='modulelist.db'
S='version'
R='__init__'
P=True
O=KeyError
N=ImportError
L='.'
K='_'
J=len
I=open
H=''
G=False
F=AttributeError
E=None
D='/'
A=OSError
import sys,gc as C,machine as i,uos as os
from utime import sleep_us as j
from ujson import dumps as Q
U='1.4.2'
V=2
k=2
try:from machine import resetWDT as W
except N:
	def W():0
class Stubber:
	def __init__(B,path=E,firmware_id=E):
		G=firmware_id;E=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise Z('MicroPython 1.13.0 cannot be stubbed')
		except F:pass
		B._report=[];B.info=l();C.collect()
		if G:B._fwid=str(G).lower()
		else:B._fwid='{family}-{port}-{ver}'.format(**B.info).lower()
		B._start_free=C.mem_free()
		if E:
			if E.endswith(D):E=E[:-1]
		else:E=m()
		B.path='{}/stubs/{}'.format(E,B.flat_fwid).replace('//',D)
		try:X(E+D)
		except A:pass
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=[];B.modules=[]
	def get_obj_attributes(L,item_instance):
		J="Couldn't get attribute '{}' from object '{}', Err: {}";A=item_instance;B=[];G=[];M=E
		try:
			for D in dir(A):
				try:H=getattr(A,D);B.append((D,repr(H),repr(type(H)),H))
				except F as I:G.append(J.format(D,A,I))
		except F as I:G.append(J.format(D,A,I))
		B=[A for A in B if not(A[0].startswith(K)and A[0]!=R)];C.collect();return B,G
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		A.modules=[B for B in A.modules if D in B]+[B for B in A.modules if D not in B];C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(E,module_name):
		B=module_name
		if B.startswith(K)and B!=d:return G
		if B in E.problematic:return G
		if B in E.excluded:return G
		F='{}/{}.py'.format(E.path,B.replace(L,D));C.collect();H=C.mem_free();a('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(B,F,H))
		try:E.create_module_stub(B,F)
		except A:return G
		C.collect();return P
	def create_module_stub(F,module_name,file_name=E):
		G=file_name;B=module_name
		if B.startswith(K)and B!=d:return
		if B in F.problematic:return
		if G is E:G=F.path+D+B.replace(L,K)+'.py'
		if D in B:B=B.replace(D,L)
		J=E
		try:J=__import__(B,E,E,'*')
		except N:return
		X(G)
		with I(G,'w')as M:P='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(B,F._fwid,F.info,U);M.write(P);M.write('from typing import Any\n\n');F.write_object_stub(M,J,B,H);F._report.append({'module':B,'file':G})
		if not B in['os','sys','logging','gc']:
			try:del J
			except (A,O):pass
			try:del sys.modules[B]
			except O:pass
			C.collect()
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		a='tuple';Z='list';Y='dict';X='{0}{1} = {2} # type: {3}\n';V='bound_method';U='Any';P=in_class;N=object_expr;I=fp;B=indent;C.collect()
		if N in L.problematic:return
		Q,c=L.get_obj_attributes(N)
		for (D,K,F,S) in Q:
			if D in['classmethod','staticmethod']:continue
			W();j(1)
			if F=="<class 'type'>"and J(B)<=k*4:E='\n'+B+'class '+D+':\n';E+=B+"    ''\n";I.write(E);L.write_object_stub(I,S,'{0}.{1}'.format(obj_name,D),B+'    ',P+1)
			elif'method'in F or'function'in F or D==R:
				M=U;T=H
				if P>0:
					T='self, '
					if D==R:M='None'
				if V in F or V in K:E='{}@classmethod\n'.format(B);E+='{}def {}(cls, *args) -> {}:\n'.format(B,D,M)
				else:E='{}def {}({}*args) -> {}:\n'.format(B,D,T,M)
				E+=B+'    ...\n\n';I.write(E)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				G=F[8:-2];E=H
				if G in['str','int','float','bool','bytearray','bytes']:E=X.format(B,D,K,G)
				elif G in[Y,Z,a]:d={Y:'{}',Z:'[]',a:'()'};E=X.format(B,D,d[G],G)
				else:
					if not G in['object','set','frozenset']:G=U
					E='{0}{1} : {2} ## {3} = {4}\n'.format(B,D,G,F,K)
				I.write(E)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(B+D+' # type: Any\n')
		del Q;del c
		try:del D,K,F,S
		except (A,O,b):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,K)
		return A
	def clean(D,path=E):
		B=path
		if B is E:B=D.path
		a('Clean/remove files in folder: {}'.format(B))
		try:G=os.listdir(B)
		except (A,F):return
		for H in G:
			C=e.format(B,H)
			try:os.remove(C)
			except A:
				try:D.clean(C);os.rmdir(C)
				except A:pass
	def report(D,filename='modules.json'):
		E=',\n';H=e.format(D.path,filename);C.collect()
		try:
			with I(H,'w')as B:
				B.write('{');B.write(Q({'firmware':D.info})[1:-1]);B.write(E);B.write(Q({f:{S:U}})[1:-1]);B.write(E);B.write('"modules" :[\n');F=P
				for J in D._report:
					if F:F=G
					else:B.write(E)
					B.write(Q(J))
				B.write('\n]}')
			K=D._start_free-C.mem_free()
		except A:pass
def X(path):
	C=path;B=F=0
	while B!=-1:
		B=C.find(D,F)
		if B!=-1:
			if B==0:E=C[0]
			else:E=C[0:B]
			try:I=os.stat(E)
			except A as G:
				if G.args[0]==V:
					try:os.mkdir(E)
					except A as H:raise H
				else:raise G
		F=B+1
def l():
	W='loboris';V='0.0.0';U='port';T='platform';R='machine';Q='nodename';P='name';J='unknown';I='sysname';G='build';E='ver';D='family';B='release';K=sys.implementation.name;M=sys.platform;A={P:K,B:V,S:V,G:H,I:J,Q:J,R:J,D:K,T:M,U:M,E:H}
	try:A[B]=L.join([str(A)for A in sys.implementation.version]);A[S]=A[B];A[P]=sys.implementation.name;A['mpy']=sys.implementation.mpy
	except F:pass
	if sys.platform not in('unix','win32'):
		try:
			C=os.uname();A[I]=C.sysname;A[Q]=C.nodename;A[B]=C.release;A[R]=C.machine
			if' on 'in C.version:
				X=C.version.split('on ')[0]
				try:A[G]=X.split('-')[1]
				except c:pass
		except (c,F,TypeError):pass
	try:from pycopy import const;A[D]='pycopy';del const
	except (N,O):pass
	if A[T]=='esp32_LoBo':A[D]=W;A[U]='esp32'
	elif A[I]=='ev3':
		A[D]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except N:pass
	if A[B]:A[E]='v'+A[B]
	if A[D]!=W:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[E]=A[B][:-2]
		else:A[E]=A[B]
		if A[G]!=H:A[E]+='-'+A[G]
	return A
def m():
	B='/flash'
	try:E=os.stat(B)
	except A as C:
		if C.args[0]==V:
			try:B=os.getcwd()
			except (A,F):B=L
		else:B=D
	return B
def B():sys.exit(1)
def read_path():
	A=H
	if J(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):A=sys.argv[2]
		else:B()
	elif J(sys.argv)==2:B()
	return A
def Y():
	try:A=bytes('abc',encoding=g);B=Y.__module__;return G
	except (Z,F):return P
def main():stubber=Stubber(path=read_path());stubber.clean();stubber.modules=[A.strip()for A in I(h)if J(A.strip())];C.collect();stubber.create_all_stubs();stubber.report()
M=logging.getLogger(f)
o=G
def p():os.remove(T)
def n():
	H=b'todo';import btree
	try:D=I(T,'r+b');E=P;M.info('Opened existing db')
	except A:D=I(T,'w+b');M.info('created new db');E=G
	stubber=Stubber(path=read_path())
	if not E:stubber.clean()
	B=btree.open(D)
	if not E or J(list(B.keys()))==0:
		M.info('load modulelist into db')
		for K in I(h):
			C=K.strip()
			if J(C)and C[0]!='#':B[C]=H
		B.flush()
	for C in B.keys():
		if B[C]!=H:continue
		try:L=stubber.create_one_stub(C.decode(g))
		except MemoryError:B.close();D.close();i.reset()
		if L:F=bytearray(stubber._report[-1])
		else:F=b'skipped'
		B[C]=F;B.flush();M.info(F)
	B.close();D.close()
if __name__=='__main__'or Y():
	try:logging.basicConfig(level=logging.INFO)
	except b:pass
	n()