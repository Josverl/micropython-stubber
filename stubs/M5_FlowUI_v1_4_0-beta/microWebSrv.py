"""
Module: 'microWebSrv' on M5 FlowUI v1.4.0-beta
"""
# MCU: (sysname='esp32', nodename='esp32', release='1.11.0', version='v1.11-284-g5d8e1c867 on 2019-08-30', machine='ESP32 module with ESP32')
# Stubber: 1.3.1

class MicroWebSocket:
    ''
    def Close():
        pass

    def IsClosed():
        pass

    def SendBinary():
        pass

    def SendText():
        pass

    def _handshake():
        pass

    _handshakeSign = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    _msgTypeBin = 2
    _msgTypeText = 1
    _opBinFrame = 2
    _opCloseFrame = 8
    _opContFrame = 0
    _opPingFrame = 9
    _opPongFrame = 10
    _opTextFrame = 1
    def _receiveFrame():
        pass

    def _sendFrame():
        pass

    def _tryAllocByteArray():
        pass

    def _tryStartThread():
        pass

    def _wsProcess():
        pass

    def threadID():
        pass


class MicroWebSrv:
    ''
    def GetMimeTypeFromFilename():
        pass

    def GetRouteHandler():
        pass

    def HTMLEscape():
        pass

    def IsStarted():
        pass

    def SetNotFoundPageUrl():
        pass

    def Start():
        pass

    def State():
        pass

    def Stop():
        pass

    _client = None
    _docoratedRouteHandlers = None
    def _fileExists():
        pass

    _html_escape_chars = None
    _indexPages = None
    def _isPyHTMLFile():
        pass

    _mimeTypes = None
    def _physPathFromURLPath():
        pass

    _pyhtmlPagesExt = '.pyhtml'
    _response = None
    def _serverProcess():
        pass

    def _tryAllocByteArray():
        pass

    def _tryStartThread():
        pass

    def _unquote():
        pass

    def _unquote_plus():
        pass

    def route():
        pass

    def threadID():
        pass


class MicroWebSrvRoute:
    ''

class MicroWebTemplate:
    ''
    def Execute():
        pass

    INSTRUCTION_ELIF = 'elif'
    INSTRUCTION_ELSE = 'else'
    INSTRUCTION_END = 'end'
    INSTRUCTION_FOR = 'for'
    INSTRUCTION_IF = 'if'
    INSTRUCTION_INCLUDE = 'include'
    INSTRUCTION_PYTHON = 'py'
    TOKEN_CLOSE = '}}'
    TOKEN_CLOSE_LEN = 2
    TOKEN_OPEN = '{{'
    TOKEN_OPEN_LEN = 2
    def Validate():
        pass

    def _parseBloc():
        pass

    def _parseCode():
        pass

    def _processInstructionELIF():
        pass

    def _processInstructionELSE():
        pass

    def _processInstructionEND():
        pass

    def _processInstructionFOR():
        pass

    def _processInstructionIF():
        pass

    def _processInstructionINCLUDE():
        pass

    def _processInstructionPYTHON():
        pass

    def _processToken():
        pass

_thread = None
def dumps():
    pass

gc = None
def loads():
    pass

network = None
re = None
socket = None
def stat():
    pass

time = None
