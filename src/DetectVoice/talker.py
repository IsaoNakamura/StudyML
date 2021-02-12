import sys
import socket
import subprocess
import threading
import random
import datetime
from collections import deque

reactions0 = ("はい？","うん？","なに？","はいよ","え？")
reactions1 = ("うーんとね","えっとね","うーん","そうねえ","ちょいまち")
reactions2 = ("もういちどいって","もっかいいって","あんだってぇ？もっかいいって","ききとれなかった","なんていってるの？","わんもあぷりーず")
reactions3 = ("うんうん","へー","ほう","なるほど","そうだねえ","そうなんだ")

talk_module = "../../../aquestalkpi/AquesTalkPi"
play_module = "aplay"

talkserver_host = 'localhost'
talkserver_port = 5533

date_format = '%Y/%m/%d %H:%M:%S'

# 音声解析タスク
recognition_tasks = deque()
# リアクションタスク
reaction_tasks = deque()
# 間つなぎタスク
keeper_tasks = deque()
# 返答タスク
reply_tasks = deque()
# 聞き直しタスク
again_tasks = deque()

clients = []

def talk_handler():
    try:
        while True:
            talk_text=''
            if( len(reply_tasks)>0):
                talk_text = reply_tasks.popleft()
                
                if( len(recognition_tasks)==0):
                    # 音声解析タスクがない場合
                    print("send to client for cancel timekeeper")
                    # 間つなぎをキャンセルさせる
                    keeper_tasks.clear()
                    for value in clients:
                        # クライアントに発信する
                        value[0].send("/cancel_timekeeper ".encode("UTF-8"))
                else:
                    # 音声解析タスクがある場合
                    # 間つなぎを依頼する
                    now = datetime.datetime.now()
                    now_str = now.strftime(date_format)
                    print("notification for replied. {}".format(now_str))
                    for value in clients:
                        # クライアントに通知する
                        value[0].send(now_str.encode("UTF-8"))

            if( len(again_tasks)>0):
                again_tasks.popleft()
                
                if( len(recognition_tasks)==0):
                    # 音声解析タスクがない場合
                    react_idx = random.randint(0,len(reactions2)-1)
                    talk_text = reactions2[react_idx]

                    print("send to client for ask again")
                    # 間つなぎをキャンセルさせる
                    keeper_tasks.clear()
                    for value in clients:
                        # クライアントに発信する
                        value[0].send("/cancel_timekeeper ".encode("UTF-8"))
                else:
                    # 音声解析タスクがある場合
                    # 間つなぎを依頼する
                    now = datetime.datetime.now()
                    now_str = now.strftime(date_format)
                    print("notification for replied. {}".format(now_str))
                    for value in clients:
                        # クライアントに通知する
                        value[0].send(now_str.encode("UTF-8"))

            elif( len(reaction_tasks)>0):
                reaction_tasks.popleft()
                react_idx = random.randint(0,len(reactions0)-1)
                talk_text = reactions0[react_idx]
               
                now = datetime.datetime.now()
                now_str = now.strftime(date_format)
                print("notification for reacted. {}".format(now_str))
                for value in clients:
                    # クライアントに通知する
                    value[0].send(now_str.encode("UTF-8"))
                    pass

            elif( len(keeper_tasks)>0):
                keeper_tasks.popleft()
                react_idx = random.randint(0,len(reactions1)-1)
                talk_text = reactions1[react_idx]

                now = datetime.datetime.now()
                now_str = now.strftime(date_format)
                print("notification for keeper. {}".format(now_str))
                for value in clients:
                    # クライアントに通知する
                    value[0].send(now_str.encode("UTF-8"))
                    pass

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
                now = datetime.datetime.now()
                now_str = now.strftime(date_format)
                if( '/detection' in rcvmsg):
                    # マイクから音を検出した場合
                    print("recieve /detection {}".format(now_str))
                    
                    # 音声認識タスクを追加
                    recognition_tasks.append(now_str)

                    # リアクションタスクを追加
                    reaction_tasks.append(now_str)

                elif( '/timekeeper' in rcvmsg):
                    print("recieve /timekeeper {}".format(now_str))
                    # 間つなぎタスクを追加
                    keeper_tasks.append(now_str)

                elif( '/recogfail' in rcvmsg):
                    print("recieve /recogfail {}".format(now_str))
                    # 聞き直しタスクを追加
                    again_tasks.append(now_str)
                    # 音声認識タスクを古いものからPOP
                    recognition_tasks.popleft()

                else:
                    print("recieve recognized text={}".format(rcvmsg))
                    # 返信タスクを追加
                    reply_tasks.append(rcvmsg)
                    # 音声認識タスクを古いものからPOP
                    recognition_tasks.popleft()

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