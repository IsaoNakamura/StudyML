import sys
import os
_modulename = os.path.basename(__file__)

# sys.path.append('./src')
# module_dirpath = /home/pi/GitHub/StudyML/src/VoiceChatBot
# srcディレクトリ内に自作モジュールが格納されている
module_dirpath = os.path.dirname(os.path.abspath(__file__))
dirlist = module_dirpath.split('/')
dirlist_rvs = dirlist[::-1]
src_diridx = dirlist_rvs.index('src')
src_dirlist = [dir for dir in dirlist_rvs[:src_diridx-1:-1]]
src_dirpath = '/'.join(src_dirlist)
sys.path.append(src_dirpath)

import socket
from packages.util_socket import util_socket
from packages.util_signal import util_signal

class DelivererJuliusCli:
    def __init__(
        self
        , _juliusmodule_host:str='localhost'
        , _juliusmodule_port:int=10500
        , _talker_host:str='localhost'
        , _talker_port:int=5533
    ):
        """コンストラクタ"""
        print("{} : init.".format(_modulename))
        util_signal.set_killtrap_handler()
        self.juliusmodule_host = _juliusmodule_host
        self.juliusmodule_port = _juliusmodule_port
        self.talker_host =  _talker_host
        self.talker_port = _talker_port
        self.juliusmodule_sock = None
        self.talker_sock = None
    
    def __del__(self):
        """デストラクタ"""

        util_signal.set_killtrap_finallybeg()
        print("{} : del beg.".format(_modulename))

        if(self.talker_sock is not None):
            self.talker_sock.close()
        if(self.juliusmodule_sock is not None):
            #juliusserversock.send("DIE".encode('utf-8'))
            self.juliusmodule_sock.close()

        print("{} : del end.".format(_modulename))
        util_signal.set_killtrap_finallyend()

    def run_main(self):
        result = -1
        try:
            self.juliusmodule_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if( self.juliusmodule_sock is None ):
                return result

            self.talker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if( self.talker_sock is None ):
                return result

            if( util_socket.connectSocketRetry(self.juliusmodule_sock, self.juliusmodule_host, self.juliusmodule_port) != 0):
                return result
            if( util_socket.connectSocketRetry(self.talker_sock, self.talker_host, self.talker_port) != 0):
                return result

            buffer = ''
            while True:
                rcvmsg = str(self.juliusmodule_sock.recv(1024).decode('utf-8'))      
                if len(rcvmsg)>0:
                    buffer+=rcvmsg
                    if '</RECOGOUT>\n.' in buffer:
                        recog_text = ''
                        #for line in buffer.split('\n'):
                        #    index = line.find('WORD="')
                        #    if index != -1:
                        #        line = line[index+6:line.find('"',index+6)]
                        #        recog_text = recog_text + line
                        #print("send to talker for recognition. text={}".format(recog_text))
                        #talkersock.send(recog_text.encode("UTF-8"))
                        
                        for line in buffer.split('\n'):
                            index = line.find('CLASSID="')
                            if index != -1:
                                line = line[index+9:line.find('"',index+9)]
                                if '&lt;s&gt;' not in line and '&lt;/s&gt;' not in line :
                                    recog_text = recog_text + line + ' '
                        print("send to talker for recognition. text={}".format(recog_text))
                        self.talker_sock.send(recog_text.encode("UTF-8"))
                        
                        buffer=''
                    elif '<RECOGFAIL/>\n.' in buffer:
                        print("send to talker for failed.")
                        self.talker_sock.send("/recogfail".encode("UTF-8"))
                        buffer=''
                    elif '<REJECTED REASON=' in buffer:
                        print("send to talker for rejected.")
                        self.talker_sock.send("/recogfail".encode("UTF-8"))
                        buffer=''
        except KeyboardInterrupt:
            # Ctrl+Cで止められるのが前提
            print("{} : except KeyboardInterrupt.".format(_modulename))
            result = 0
        except Exception as e:
            print("{} : except Exception. except={}".format(_modulename, e))
        finally:
            if(result!=0):
                pass
        return result


if __name__ == '__main__':
    sys.exit(abs(DelivererJuliusCli().run_main()))

    