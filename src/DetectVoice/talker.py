import sys
import socket
import struct

talkserver_host = 'localhost'
talkserver_port = 5532

talkserversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
talkserversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
talkserversock.bind((talkserver_host, talkserver_port))
talkserversock.listen(1)

print('Waiting for connections...')
talkclientsock, talkclient_address = talkserversock.accept()

fnum = 0

while True:

    rcvmsg = talkclientsock.recv(4)
    nbytes = struct.unpack('=i', rcvmsg)[0]

    if nbytes > 0:
        print(format("nbytes={}, rcvmsg={} ", nbytes, rcvmsg))
        fnum = fnum + 1
    elif nbytes == 0:
        fnum = 0

talkclientsock.close()
