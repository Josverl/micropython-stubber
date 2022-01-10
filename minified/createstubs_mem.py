b='micropython'
a='{}/{}'
Z='_thread'
Y=IndexError
X=NameError
W=print
V=NotImplementedError
R=True
Q='__init__'
P=open
O='version'
N=KeyError
M=ImportError
K='_'
J=len
I='.'
G=False
H=''
F=AttributeError
E='/'
D=None
A=OSError
import sys,gc as C,uos as os
from utime import sleep_us as c
from ujson import dumps as L
__version__='1.5.1'
d=2
e=2
try:from machine import resetWDT as S
except M:
	def S():0
class Stubber:
	def __init__(B,path=D,firmware_id=D):
		G=firmware_id;D=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise V('MicroPython 1.13.0 cannot be stubbed')
		except F:pass
		B._report=[];B.info=_info();C.collect()
		if G:B._fwid=str(G).lower()
		else:B._fwid='{family}-{ver}-{port}'.format(**B.info).lower()
		B._start_free=C.mem_free()
		if D:
			if D.endswith(E):D=D[:-1]
		else:D=get_root()
		B.path='{}/stubs/{}'.format(D,B.flat_fwid).replace('//',E)
		try:T(D+E)
		except A:pass
		B.problematic=['upip','upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];B.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];B.modules=[]
	def get_obj_attributes(I,item_instance):
		B=item_instance;A=[];G=[]
		for D in dir(B):
			try:E=getattr(B,D);A.append((D,repr(E),repr(type(E)),E))
			except F as H:G.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(D,B,H))
		A=[B for B in A if not(B[0].startswith(K)and B[0]!=Q)];C.collect();return A,G
	def add_modules(A,modules):A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		C.collect()
		for B in A.modules:A.create_one_stub(B)
	def create_one_stub(D,module_name):
		B=module_name
		if B.startswith(K)and B!=Z:return G
		if B in D.problematic:return G
		if B in D.excluded:return G
		F='{}/{}.py'.format(D.path,B.replace(I,E));C.collect();H=C.mem_free();W('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(B,F,H))
		try:D.create_module_stub(B,F)
		except A:return G
		C.collect();return R
	def create_module_stub(F,module_name,file_name=D):
		G=file_name;B=module_name
		if B.startswith(K)and B!=Z:return
		if B in F.problematic:return
		if G is D:G=F.path+E+B.replace(I,K)+'.py'
		if E in B:B=B.replace(E,I)
		J=D
		try:J=__import__(B,D,D,'*')
		except M:return
		T(G)
		with P(G,'w')as L:O='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(B,F._fwid,F.info,__version__);L.write(O);L.write('from typing import Any\n\n');F.write_object_stub(L,J,B,H)
		F._report.append({'module':B,'file':G})
		if not B in['os','sys','logging','gc']:
			try:del J
			except (A,N):pass
			try:del sys.modules[B]
			except N:pass
		C.collect()
	def write_object_stub(L,fp,object_expr,obj_name,indent,in_class=0):
		b='tuple';a='list';Z='dict';Y='{0}{1} = {2} # type: {3}\n';W='bound_method';V='Any';P=in_class;O=object_expr;I=fp;B=indent;C.collect()
		if O in L.problematic:return
		R,d=L.get_obj_attributes(O)
		for (D,K,F,T) in R:
			if D in['classmethod','staticmethod']:continue
			S();c(1)
			if F=="<class 'type'>"and J(B)<=e*4:E='\n'+B+'class '+D+':\n';E+=B+"    ''\n";I.write(E);L.write_object_stub(I,T,'{0}.{1}'.format(obj_name,D),B+'    ',P+1)
			elif'method'in F or'function'in F or D==Q:
				M=V;U=H
				if P>0:
					U='self, '
					if D==Q:M='None'
				if W in F or W in K:E='{}@classmethod\n'.format(B);E+='{}def {}(cls, *args) -> {}:\n'.format(B,D,M)
				else:E='{}def {}({}*args) -> {}:\n'.format(B,D,U,M)
				E+=B+'    ...\n\n';I.write(E)
			elif F=="<class 'module'>":0
			elif F.startswith("<class '"):
				G=F[8:-2];E=H
				if G in['str','int','float','bool','bytearray','bytes']:E=Y.format(B,D,K,G)
				elif G in[Z,a,b]:f={Z:'{}',a:'[]',b:'()'};E=Y.format(B,D,f[G],G)
				else:
					if not G in['object','set','frozenset']:G=V
					E='{0}{1} : {2} ## {3} = {4}\n'.format(B,D,G,F,K)
				I.write(E)
			else:I.write("# all other, type = '{0}'\n".format(F));I.write(B+D+' # type: Any\n')
		del R;del d
		try:del D,K,F,T
		except (A,N,X):pass
	@property
	def flat_fwid(self):
		A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,K)
		return A
	def clean(E,path=D):
		B=path
		if B is D:B=E.path
		W('Clean/remove files in folder: {}'.format(B))
		try:G=os.listdir(B)
		except (A,F):return
		for H in G:
			C=a.format(B,H)
			try:os.remove(C)
			except A:
				try:E.clean(C);os.rmdir(C)
				except A:pass
	def report(D,filename='modules.json'):
		H='firmware';E=',\n';I=a.format(D.path,filename);C.collect()
		try:
			with P(I,'w')as B:
				B.write('{');B.write(L({H:D.info})[1:-1]);B.write(E);B.write(L({'stubber':{O:__version__},'stubtype':H})[1:-1]);B.write(E);B.write('"modules" :[\n');F=R
				for J in D._report:
					if F:F=G
					else:B.write(E)
					B.write(L(J))
				B.write('\n]}')
			K=D._start_free-C.mem_free()
		except A:pass
def T(path):
	C=path;B=F=0
	while B!=-1:
		B=C.find(E,F)
		if B!=-1:
			if B==0:D=C[0]
			else:D=C[0:B]
			try:I=os.stat(D)
			except A as G:
				if G.args[0]==d:
					try:os.mkdir(D)
					except A as H:raise H
				else:raise G
		F=B+1
def _info():
	g=' on ';f='0.0.0';e='port';d='platform';c='machine';a='nodename';Z='name';T='mpy';S='unknown';R='-';Q='sysname';L='v';K='family';G='build';C='ver';B='release';U=sys.implementation.name;V=sys.platform;A={Z:U,B:f,O:f,G:H,Q:S,a:S,c:S,K:U,d:V,e:V,C:H}
	try:A[B]=I.join([str(A)for A in sys.implementation.version]);A[O]=A[B];A[Z]=sys.implementation.name;A[T]=sys.implementation.mpy
	except F:pass
	if sys.platform not in('unix','win32'):
		try:
			E=os.uname();A[Q]=E.sysname;A[a]=E.nodename;A[B]=E.release;A[c]=E.machine
			if g in E.version:
				P=E.version.split(g)[0]
				if A[Q]=='esp8266':
					if R in P:W=P.split(R)[0]
					else:W=P
					A[O]=A[B]=W.lstrip(L)
				try:A[G]=P.split(R)[1]
				except Y:pass
		except (Y,F,TypeError):pass
	try:from pycopy import const;A[K]='pycopy';del const
	except (M,N):pass
	if A[d]=='esp32_LoBo':A[K]='loboris';A[e]='esp32'
	elif A[Q]=='ev3':
		A[K]='ev3-pybricks';A[B]='1.0.0'
		try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
		except M:pass
	if A[B]:A[C]=L+A[B].lstrip(L)
	if A[K]==b:
		if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[C]=A[B][:-2]
		else:A[C]=A[B]
		if A[G]!=H and J(A[G])<4:A[C]+=R+A[G]
	if A[C][0]!=L:A[C]=L+A[C]
	if T in A:
		h=int(A[T]);X=[D,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][h>>10]
		if X:A['arch']=X
	return A
def get_root():
	try:B=os.getcwd()
	except (A,F):B=I
	for C in [B,'/sd','/flash',E,I]:
		try:D=os.stat(C);break
		except A as G:continue
	return C
def B():sys.exit(1)
def read_path():
	A=H
	if J(sys.argv)==3:
		C=sys.argv[1].lower()
		if C in('--path','-p'):A=sys.argv[2]
		else:B()
	elif J(sys.argv)==2:B()
	return A
def U():
	try:A=bytes('abc',encoding='utf8');B=U.__module__;return G
	except (V,F):return R
def main():
	stubber=Stubber(path=read_path());stubber.clean()
	try:stubber.modules=[A.strip()for A in P('modulelist'+'.txt')if J(A.strip())and A.strip()[0]!='#']
	except A:stubber.modules=[b]
	C.collect();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or U():
	try:logging.basicConfig(level=logging.INFO)
	except X:pass
	main()