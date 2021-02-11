import sys
import socket
import subprocess
import threading
import random
import datetime

reactions0 = ("はい？","うん？","なに？","はいよ","え？")
reactions1 = ("うーんとね","えっとね","そうだねえ","うーん","えっとぉ","そうねえ","ちょいまち")
reactions2 = ("うんうん","へー","ほう","なるほど","そうだねえ","そうなんだ")

talk_module = "../../../aquestalkpi/AquesTalkPi"
play_module = "aplay"

talkserver_host = 'localhost'
talkserver_port = 5533

date_format = '%Y/%m/%d %H:%M:%S'

reaction_talks = []
keeper_talks = []
detect_talks = []

clients = []

def talk_handler():
    try:
        while True:
            talk_text=''
            if( len(detect_talks)>0):
                talk_text = detect_talks.pop()
                
                now = datetime.datetime.now()
                now_str = now.strftime(date_format)
                print("notification for detect. {}".format(now_str))
                for value in clients:
                    # クライアントに発信する
                    value[0].send("/cancel ".encode("UTF-8"))
                    pass

                detect_talks.clear()
                reaction_talks.clear()
                keeper_talks.clear()

            if( len(reaction_talks)>0):
                talk_text = reaction_talks.pop()

                now = datetime.datetime.now()
                now_str = now.strftime(date_format)
                print("notification for reaction. {}".format(now_str))
                for value in clients:
                    # クライアントに発信する
                    value[0].send(now_str.encode("UTF-8"))
                    pass

                reaction_talks.clear()
                keeper_talks.clear()

            if( len(keeper_talks)>0):
                talk_text = keeper_talks.pop()

                now = datetime.datetime.now()
                now_str = now.strftime(date_format)
                print("notification for keeper. {}".format(now_str))
                for value in clients:
                    # クライアントに発信する
                    value[0].send(now_str.encode("UTF-8"))
                    pass
                
                keeper_talks.clear()

            if(len(talk_text)>0):
                cmd1 = talk_module + " " + talk_text
                cmd2 = play_module
                process1=subprocess.Popen(cmd1.split(),stdout=subprocess.PIPE)
                ##process2=subprocess.Popen(cmd2.split(),stdin=process1.stdout)
                process2=subprocess.run(cmd2.split(),stdin=process1.stdout)
                print(cmd1.split())


    except Exception as e:
        print(e)

# 接続済みクライアントは読み込みおよび書き込みを繰り返す
def client_handler(connection, address):
    try:
        while True:
            #クライアント側から受信する
            rcvmsg = str(connection.recv(4096).decode('utf-8'))
            if len(rcvmsg)>0:
                if( '/reaction' in rcvmsg):
                    react_idx = random.randint(0,len(reactions0)-1)
                    print("recieve /reaction idx={}".format(react_idx))
                    reaction_talks.clear()
                    reaction_talks.append(reactions0[react_idx])
                elif( '/timekeeper' in rcvmsg):
                    if(len(detect_talks)<=0):
                        react_idx = random.randint(0,len(reactions1)-1)
                        print("recieve /timekeeper idx={}".format(react_idx))
                        keeper_talks.clear()
                        keeper_talks.append(reactions1[react_idx])
                    pass
                else:
                    detect_talks.clear()
                    detect_talks.append(rcvmsg)

    except Exception as e:
        print(e)


talkserversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    talkserversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    talkserversock.bind((talkserver_host, talkserver_port))
    talkserversock.listen(1)

    # スレッド作成
    talk_thread = threading.Thread(target=talk_handler, daemon=True)
    # スレッドスタート
    talk_thread.start()

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
        client_thread = threading.Thread(target=client_handler, args=(conn, addr), daemon=True)
        # スレッドスタート
        client_thread.start()

except KeyboardInterrupt:
    print('finished')
    talkserversock.send("DIE".encode('utf-8'))
    talkserversock.close()