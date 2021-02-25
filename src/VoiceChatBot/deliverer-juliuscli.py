import sys
import os
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

juliusserver_host = 'localhost'
juliusserver_port = 10500

talker_host =  'localhost'
talker_port = 5533

def main():
    result = -1
    juliusserversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    talkersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        if( util_socket.connectSocketRetry(juliusserversock, juliusserver_host, juliusserver_port) != 0):
            return result
        if( util_socket.connectSocketRetry(talkersock, talker_host, talker_host) != 0):
            return result

        buffer = ''
        while True:
            rcvmsg = str(juliusserversock.recv(1024).decode('utf-8'))      
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
                    talkersock.send(recog_text.encode("UTF-8"))
                    
                    buffer=''
                elif '<RECOGFAIL/>\n.' in buffer:
                    print("send to talker for failed.")
                    talkersock.send("/recogfail".encode("UTF-8"))
                    buffer=''
                elif '<REJECTED REASON=' in buffer:
                    print("send to talker for rejected.")
                    talkersock.send("/recogfail".encode("UTF-8"))
                    buffer=''

    except KeyboardInterrupt:
        print('finished')
        juliusserversock.send("DIE".encode('utf-8'))
        juliusserversock.close()
        #talkersock.send("DIE".encode('utf-8'))
        talkersock.close()
    
    return result

if __name__ == '__main__':
    main()