import sys
import socket
import datetime
import time
import threading

talker_host =  'localhost'
talker_port = 5533

talkersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

date_format = '%Y/%m/%d %H:%M:%S'
#date_format = '%H時%M分%S秒'
interval_sec = 3

rcvdate = [] # datetime.datetime.now()

def recv_handler(sock):
    try:
        while True:
            rcvmsg = sock.recv(4096)
            if len(rcvmsg)>0:
                rcvstr = str(rcvmsg.decode('utf-8'))
                if( '/cancel' in rcvstr):
                    rcvdate.clear()
                    print("recv from talker for cancel.")
                    pass
                else:
                    #print("読み込んだバイト数:({})".format(len(rcvmsg)))
                    rcvdate.clear()
                    rcvdate.append(datetime.datetime.strptime(rcvstr, date_format))
                    print("recv from talker for timekeep. rcvdate={}".format(rcvdate[0]))

                    #if (len(rcvmsg) < 4096) :
                    #    continue
    except Exception as e:
        print(e)



try:
    talkersock.connect((talker_host, talker_port))

    thread = threading.Thread(target = recv_handler, args= (talkersock,), daemon= True)
    thread.start()

    #last = datetime.datetime.now()
    while True:
        now = datetime.datetime.now()
        now_str = now.strftime(date_format)
        #delta = now - last
        if( len(rcvdate) > 0 ):
            delta = now - rcvdate[0]
            #print("rcvdate={} now={} delta={}".format(rcvdate[0],now_str,delta.seconds ))
            if delta.seconds == interval_sec:
                #rcvdate = now
                #last = now
                
                #talkersock.send(now_str.encode("UTF-8"))
                talkersock.send('/timekeeper'.encode("UTF-8"))
                print("send msg to talker. rcv(from talker)={} now={} delta={}".format(rcvdate,now_str,delta.seconds ))
                rcvdate.clear()
        time.sleep(1)

except KeyboardInterrupt:
    print('finished')
    #talkersock.send("DIE".encode('utf-8'))
    talkersock.close()
