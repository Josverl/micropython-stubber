'\nCreate stubs for (all) modules on a MicroPython board\nCopyright (c) 2019-2021 Jos Verlinde\n'
_I='__init__'
_H='logging'
_G=False
_F='version'
_E='machine'
_D='_thread'
_C='.'
_B='/'
_A=None
import sys,gc,uos as os
from utime import sleep_us
from ujson import dumps
ENOENT=2
stubber_version='1.4.0.beta'
MAX_CLASS_LEVEL=2
try:from machine import resetWDT
except ImportError:
	def resetWDT():0
class Stubber:
	'Generate stubs for modules in firmware'
	def __init__(A,path=_A,firmware_id=_A):
		C=firmware_id;B=path
		try:
			if os.uname().release=='1.13.0'and os.uname().version<'v1.13-103':raise NotImplementedError('MicroPython 1.13.0 cannot be stubbed')
		except AttributeError:pass
		A._report=[];A.info=A._info()
		if C:A._fwid=str(C).lower()
		else:A._fwid='{family}-{port}-{ver}'.format(**A.info).lower()
		A._start_free=gc.mem_free()
		if B:
			if B.endswith(_B):B=B[:-1]
		else:B=A.get_root()
		A.path='{}/stubs/{}'.format(B,A.flat_fwid).replace('//',_B)
		try:A.ensure_folder(B+_B)
		except OSError:pass
		A.problematic=['upysh','webrepl_setup','http_client','http_client_ssl','http_server','http_server_ssl'];A.excluded=['webrepl','_webrepl','port_diag','example_sub_led.py','example_pub_button.py'];A.modules=['_onewire',_D,'_uasyncio','ak8963','apa102','apa106','array','binascii','btree','builtins','cmath','collections','crypto','curl','dht','display','display_driver_utils','ds18x20','errno','esp','esp32','espidf','flashbdev','framebuf','freesans20','fs_driver','functools','gc','gsm','hashlib','heapq','ili9XXX','imagetools','inisetup','io','json','lcd160cr','lodepng',_H,'lv_colors','lv_utils','lvgl','lwip',_E,'math','microWebSocket','microWebSrv','microWebTemplate','micropython','mpu6500','mpu9250','neopixel','network','ntptime','onewire','os','pyb','pycom','pye','queue','random','re','requests','rtch','select','socket','ssd1306','ssh','ssl','stm','struct','sys','time','tpcalib','uarray','uasyncio/__init__','uasyncio/core','uasyncio/event','uasyncio/funcs','uasyncio/lock','uasyncio/stream','ubinascii','ubluetooth','ucollections','ucrypto','ucryptolib','uctypes','uerrno','uftpd','uhashlib','uheapq','uio','ujson','ulab','ulab/approx','ulab/compare','ulab/fft','ulab/filter','ulab/linalg','ulab/numerical','ulab/poly','ulab/user','ulab/vector','umachine','umqtt/robust','umqtt/simple','uos','upip','upip_utarfile','uqueue','urandom','ure','urequests','urllib/urequest','uselect','usocket','ussl','ustruct','usys','utelnetserver','utime','utimeq','uwebsocket','uzlib','websocket','websocket_helper','writer','xpt2046','ymodem','zlib'];A.include_nested=gc.mem_free()>3200
	@staticmethod
	def _info():
		'collect base information on this runtime';R='loboris';Q='0.0.0';P='port';O='platform';N='nodename';M='name';I='mpy';H='unknown';G='sysname';F='build';E='ver';D='family';B='release';J=sys.implementation.name;K=sys.platform;A={M:J,B:Q,_F:Q,F:'',G:H,N:H,_E:H,D:J,O:K,P:K,E:''}
		try:A[B]=_C.join([str(A)for A in sys.implementation.version]);A[_F]=A[B];A[M]=sys.implementation.name;A[I]=sys.implementation.mpy
		except AttributeError:pass
		if sys.platform not in('unix','win32'):
			try:
				C=os.uname();A[G]=C.sysname;A[N]=C.nodename;A[B]=C.release;A[_E]=C.machine
				if' on 'in C.version:
					S=C.version.split('on ')[0]
					try:A[F]=S.split('-')[1]
					except IndexError:pass
			except (IndexError,AttributeError,TypeError):pass
		try:from pycopy import const;A[D]='pycopy';del const
		except (ImportError,KeyError):pass
		if A[O]=='esp32_LoBo':A[D]=R;A[P]='esp32'
		elif A[G]=='ev3':
			A[D]='ev3-pybricks';A[B]='1.0.0'
			try:from pybricks.hubs import EV3Brick;A[B]='2.0.0'
			except ImportError:pass
		if A[B]:A[E]='v'+A[B]
		if A[D]!=R:
			if A[B]and A[B]>='1.10.0'and A[B].endswith('.0'):A[E]=A[B][:-2]
			else:A[E]=A[B]
			if A[F]!='':A[E]+='-'+A[F]
		if I in A:
			T=int(A[I]);L=[_A,'x86','x64','armv6','armv6m','armv7m','armv7em','armv7emsp','armv7emdp','xtensa','xtensawin'][T>>10]
			if L:A['arch']=L
		return A
	def get_obj_attributes(H,obj):
		'extract information of the objects members and attributes';G="Couldn't get attribute '{}' from object '{}', Err: {}";B=obj;C=[];D=[];A=_A
		try:
			for A in dir(B):
				try:E=getattr(B,A);C.append((A,repr(E),repr(type(E)),E))
				except AttributeError as F:D.append(G.format(A,B,F))
		except AttributeError as F:D.append(G.format(A,B,F))
		C=[A for A in C if not(A[0].startswith('_')and A[0]!=_I)];gc.collect();return C,D
	def add_modules(A,modules):'Add additional modules to be exported';A.modules=sorted(set(A.modules)|set(modules))
	def create_all_stubs(A):
		'Create stubs for all configured modules';A.modules=[B for B in A.modules if _B in B]+[B for B in A.modules if _B not in B];gc.collect()
		for B in A.modules:
			if A.include_nested:A.include_nested=gc.mem_free()>3200
			if B.startswith('_')and B!=_D:continue
			if B in A.problematic:continue
			if B in A.excluded:continue
			C='{}/{}.py'.format(A.path,B.replace(_C,_B));gc.collect();D=gc.mem_free();print('Stub module: {:<20} to file: {:<55} mem:{:>5}'.format(B,C,D))
			try:A.create_module_stub(B,C)
			except OSError:pass
			gc.collect()
	def create_module_stub(B,module_name,file_name=_A):
		'Create a Stub of a single python module';C=file_name;A=module_name
		if A.startswith('_')and A!=_D:return
		if A in B.problematic:return
		if C is _A:C=B.path+_B+A.replace(_C,'_')+'.py'
		if _B in A:
			A=A.replace(_B,_C)
			if not B.include_nested:return
		F=_G;D=_A
		try:D=__import__(A,_A,_A,'*')
		except ImportError:
			F=True
			if not _C in A:return
		if F and _C in A:
			G=A.split(_C)
			for H in range(1,len(G)):
				I=_C.join(G[0:H])
				try:J=__import__(I);del J
				except (ImportError,KeyError):pass
			try:D=__import__(A,_A,_A,'*')
			except ImportError:return
		B.ensure_folder(C)
		with open(C,'w')as E:K='"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(A,B._fwid,B.info,stubber_version);E.write(K);E.write('from typing import Any\n\n');B.write_object_stub(E,D,A,'');B._report.append({'module':A,'file':C})
		if not A in['os','sys',_H,'gc']:
			try:del D
			except (OSError,KeyError):pass
			try:del sys.modules[A]
			except KeyError:pass
			gc.collect()
	def write_object_stub(G,fp,object_expr,obj_name,indent,in_class=0):
		'Write a module/object stub to an open file. Can be called recursive.';S='tuple';R='list';Q='dict';P='{0}{1} = {2} # type: {3}\n';O='Any';J=object_expr;F=fp;A=indent
		if J in G.problematic:return
		K,T=G.get_obj_attributes(J)
		for (C,L,D,M) in K:
			resetWDT();sleep_us(1);H=["<class 'function'>","<class 'bound_method'>"]
			if D=="<class 'type'>"and len(A)<=MAX_CLASS_LEVEL*4:B='\n'+A+'class '+C+':\n';B+=A+"    ''\n";F.write(B);G.write_object_stub(F,M,'{0}.{1}'.format(obj_name,C),A+'    ',in_class+1)
			elif D in H:
				I=O;N=''
				if D==H[0]:
					N='self, '
					if C==_I:I='None'
				if D==H[1]:B='{}@classmethod\n'.format(A);B+='{}def {}(cls) -> {}:\n'.format(A,C,I)
				else:B='{}def {}({}*args) -> {}:\n'.format(A,C,N,I)
				B+=A+'    ...\n\n';F.write(B)
			elif D.startswith("<class '"):
				E=D[8:-2];B=''
				if E in['str','int','float','bool','bytearray','bytes']:B=P.format(A,C,L,E)
				elif E in[Q,R,S]:U={Q:'{}',R:'[]',S:'()'};B=P.format(A,C,U[E],E)
				else:
					if not E in['object','set','frozenset']:E=O
					B='{0}{1}: {2}\n'.format(A,C,E)
				F.write(B)
			else:F.write("# all other, type = '{0}'\n".format(D));F.write(A+C+' = Any\n')
		del K;del T
		try:del C,L,D,M
		except (OSError,KeyError,NameError):pass
	@property
	def flat_fwid(self):
		"Turn _fwid from 'v1.2.3' into '1_2_3' to be used in filename";A=self._fwid;B=' .()/\\:$'
		for C in B:A=A.replace(C,'_')
		return A
	def clean(C,path=_A):
		'Remove all files from the stub folder';A=path
		if A is _A:A=C.path
		print('Clean/remove files in folder: {}'.format(A))
		try:D=os.listdir(A)
		except (OSError,AttributeError):return
		for E in D:
			B='{}/{}'.format(A,E)
			try:os.remove(B)
			except OSError:
				try:C.clean(B);os.rmdir(B)
				except OSError:pass
	def report(B,filename='modules.json'):
		'create json with list of exported modules';C=',\n';E='{}/{}'.format(B.path,filename);gc.collect()
		try:
			with open(E,'w')as A:
				A.write('{');A.write(dumps({'firmware':B.info})[1:-1]);A.write(C);A.write(dumps({'stubber':{_F:stubber_version}})[1:-1]);A.write(C);A.write('"modules" :[\n');D=True
				for F in B._report:
					if D:D=_G
					else:A.write(C)
					A.write(dumps(F))
				A.write('\n]}')
			G=B._start_free-gc.mem_free()
		except OSError:pass
	def ensure_folder(G,path):
		'Create nested folders if needed';B=path;A=D=0
		while A!=-1:
			A=B.find(_B,D)
			if A!=-1:
				if A==0:C=B[0]
				else:C=B[0:A]
				try:H=os.stat(C)
				except OSError as E:
					if E.args[0]==ENOENT:
						try:os.mkdir(C)
						except OSError as F:raise F
					else:raise E
			D=A+1
	@staticmethod
	def get_root():
		'Determine the root folder of the device'
		try:A='/flash';C=os.stat(A)
		except OSError as B:
			if B.args[0]==ENOENT:
				try:A=os.getcwd()
				except (OSError,AttributeError):A=_C
			else:A=_B
		return A
def show_help():sys.exit(1)
def read_path():
	'get --path from cmdline. [unix/win]';A=''
	if len(sys.argv)==3:
		B=sys.argv[1].lower()
		if B in('--path','-p'):A=sys.argv[2]
		else:show_help()
	elif len(sys.argv)==2:show_help()
	return A
def isMicroPython():
	'runtime test to determine full or micropython'
	try:B=bytes('abc',encoding='utf8');A=1;C=f"aa{A}";return _G
	except (NotImplementedError,SyntaxError):return True
def main():
	try:logging.basicConfig(level=logging.INFO)
	except NameError:pass
	stubber=Stubber(path=read_path());stubber.clean();stubber.create_all_stubs();stubber.report()
if __name__=='__main__'or isMicroPython():main()