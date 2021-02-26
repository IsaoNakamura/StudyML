import sys
import os
import socket
import struct
import subprocess
# import time

_modulename = os.path.basename(__file__)

talker_host =  'localhost'
talker_port = 5533
adinserver_host = 'localhost'
adinserver_port = 5532
julius_host = 'localhost'
julius_port = 5530#5531

module_dir = os.path.dirname(__file__)
dictationkit_path = module_dir + "/" + "../../../dictation-kit/"
adintool_module = "adintool"

if len(sys.argv) > 1:
    conffile = sys.argv[1]
    f = open(conffile)
    for line in f:
        linebuf = line.strip().split(' ')
        if linebuf[0] == "--adinserver_host":adinserver_host = linebuf[1]
        elif linebuf[0] == "--adinserver_port":adinserver_port = int(linebuf[1])
        elif linebuf[0] == "--julius_host":julius_host = linebuf[1]
        elif linebuf[0] == "--julius_port":julius_port = int(linebuf[1])
        elif linebuf[0] == "--talker_host":talker_host = linebuf[1]
        elif linebuf[0] == "--talker_port":talker_port = int(linebuf[1])
        elif linebuf[0] == "#":
            pass
        else:
            print("unkown switch")
            sys.exit()
    f.close()

adintool_opt = ''
adintool_opt = adintool_opt + ' -in' + ' ' + 'mic'
adintool_opt = adintool_opt + ' -out' + ' ' + 'adinnet'
adintool_opt = adintool_opt + ' -server' + ' ' + adinserver_host
adintool_opt = adintool_opt + ' -paramtype' + ' ' + 'FBANK_D_A_Z'
adintool_opt = adintool_opt + ' -htkconf' + ' ' + dictationkit_path + '/model/dnn/config.lmfb'
adintool_opt = adintool_opt + ' -port' + ' ' + str(adinserver_port)
adintool_opt = adintool_opt + ' -cvn'
adintool_opt = adintool_opt + ' -cmnload' + ' ' + dictationkit_path + '/model/dnn/norm'
adintool_opt = adintool_opt + ' -cmnnoupdate'

adintool_cmd = adintool_module + adintool_opt
adintool_proc = None

juliusclientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
talkersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
adinserversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    juliusclientsock.connect((julius_host, julius_port))
    talkersock.connect((talker_host, talker_port))

    # サブプロセススタート
    adintool_proc=subprocess.Popen(adintool_cmd.split(),stdin=None,stdout=None)
    # time.sleep(1)

    adinserversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    adinserversock.bind((adinserver_host, adinserver_port))
    adinserversock.listen(1)
    print('Waiting for connections...')
    adinclientsock, adinclient_address = adinserversock.accept()
    print('connected from client.')

    while True:
        rcvmsg = adinclientsock.recv(4)
        nbytes = struct.unpack('=i', rcvmsg)[0]
        #print("nbytes={}".format(nbytes))
        juliusclientsock.sendall(rcvmsg)
        if nbytes > 0:
            buffer = b''
            while len(buffer) < nbytes:
                recv_byte = nbytes - len(buffer)
                tmpdata = adinclientsock.recv( recv_byte )
                if not tmpdata:
                    break
                buffer += tmpdata
                #print(" #recive. recv_byte={}, buffer_len={}".format(recv_byte,len(buffer)))
            if len(buffer)>0 :
                #print(" #send to julius. buffer length is {}".format(len(buffer)))
                juliusclientsock.sendall(buffer)
        elif nbytes == 0:
            r_msg = struct.pack('=i', 0)
            juliusclientsock.sendall(r_msg)
            #print("#SPLIT R_MSG:{}".format(r_msg))
            talkersock.send("/detection".encode("UTF-8"))
            print("send to talker for detection.")

    r_msg = struct.pack('=i', 0)
    juliusclientsock.sendall(r_msg)

    r_msg = struct.pack('=i', -1)
    juliusclientsock.sendall(r_msg)

    adinclientsock.close()

except KeyboardInterrupt:
    print("{} : except KeyboardInterrupt. ".format(_modulename))
    juliusclientsock.close()
    adinserversock.close()
    talkersock.close()
    if(adintool_proc is not None):
        adintool_proc.kill()