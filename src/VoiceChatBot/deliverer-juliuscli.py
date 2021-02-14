import sys
import socket
#import struct
import subprocess

juliusserver_host = 'localhost'
juliusserver_port = 10500

talker_host =  'localhost'
talker_port = 5533

juliusserversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
talkersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    juliusserversock.connect((juliusserver_host,juliusserver_port))
    talkersock.connect((talker_host, talker_port))

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
