import sys
import socket
import struct

talkserver_host = 'localhost'
talkserver_port = 5533

talkserversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
talkserversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
talkserversock.bind((talkserver_host, talkserver_port))
talkserversock.listen(1)

print('Waiting for connections...')
talkclientsock, talkclient_address = talkserversock.accept()

fnum = 0

while True:

    rcvmsg = talkclientsock.recv(4)
    #nbytes = struct.unpack('=i', rcvmsg)[0]

    if len(rcvmsg)>0:
        #print(format("nbytes={}, rcvmsg={} ", nbytes, rcvmsg))
        #print(format("rcvmsg={} ", str(rcvmsg)))
        print(rcvmsg)
        fnum = fnum + 1
    elif len(rcvmsg) == 0:
        fnum = 0

talkclientsock.close()
