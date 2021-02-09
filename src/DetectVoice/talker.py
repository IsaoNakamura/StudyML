import sys
import socket
import subprocess
import threading
import random
import datetime

reactions0 = ("はい？","うん？","なに？","はいよ","え？")
reactions1 = ("うんうん","へー","ほう","なるほど","そうだねえ","そうなんだ")

talk_module = "../../../aquestalkpi/AquesTalkPi"
play_module = "aplay"

talkserver_host = 'localhost'
talkserver_port = 5533

date_format = '%Y/%m/%d %H:%M:%S'

clients = []

# 接続済みクライアントは読み込みおよび書き込みを繰り返す
def loop_handler(connection, address):
    try:
        buffer = ''
        while True:
            #クライアント側から受信する
            rcvmsg = str(connection.recv(4096).decode('utf-8'))
            if len(rcvmsg)>0:
                talk_text=''
                if( '/reaction' in rcvmsg):
                    react_idx = random.randint(0,len(reactions0)-1)
                    print("recieve /reaction idx={}".format(react_idx))
                    talk_text = reactions0[react_idx]
                elif( '/timekeeper' in rcvmsg):
                    talk_text='うーんとね'
                    pass
                else:
                    talk_text = rcvmsg
                
                if( len(talk_text)>0):
                    cmd1 = talk_module + " " + talk_text
                    cmd2 = play_module
                    process1=subprocess.Popen(cmd1.split(),stdout=subprocess.PIPE)
                    process2=subprocess.Popen(cmd2.split(),stdin=process1.stdout)
                    #process2=subprocess.run(cmd2.split(),stdin=process1.stdout)
                    print(cmd1.split())

                    for value in clients:
                        if value[1][0] == address[0] and value[1][1] == address[1] :
                            # 当該ループであるクライアントには発信しない
                            #print("クライアント{}:{}から{}というメッセージを受信完了".format(value[1][0], value[1][1], rcvmsg))
                            pass
                        else:
                            # 当該ループでないクライアントには発信する
                            now = datetime.datetime.now()
                            now_str = now.strftime(date_format)
                            value[0].send(now_str.encode("UTF-8"))
                            #value[0].send("クライアント{}:{}から{}を受信".format(value[1][0], value[1][1], rcvmsg.decode()).encode("UTF-8"))
                            pass
    except Exception as e:
        print(e)


talkserversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    talkserversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    talkserversock.bind((talkserver_host, talkserver_port))
    talkserversock.listen(1)    
    while True:
        try:
            # 接続要求を受信
            conn, addr = talkserversock.accept()

        except KeyboardInterrupt:
            talkserversock.close()
            exit()
            break
        # アドレス確認
        print("[アクセス元アドレス]=>{}".format(addr[0]))
        print("[アクセス元ポート]=>{}".format(addr[1]))
        print("\r\n")
        # 待受中にアクセスしてきたクライアントを追加
        clients.append((conn, addr))
        # スレッド作成
        thread = threading.Thread(target=loop_handler, args=(conn, addr), daemon=True)
        # スレッドスタート
        thread.start()

except KeyboardInterrupt:
    print('finished')
    talkserversock.send("DIE".encode('utf-8'))
    talkserversock.close()