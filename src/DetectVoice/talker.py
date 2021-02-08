import sys
import socket
import subprocess
import threading

talk_module = "../../../aquestalkpi/AquesTalkPi"
play_module = "aplay"

talkserver_host = 'localhost'
talkserver_port = 5533

clients = []

# 接続済みクライアントは読み込みおよび書き込みを繰り返す
def loop_handler(connection, address):
    while True:
        try:
            #クライアント側から受信する
            res = connection.recv(4096)
            talk_text = str(res.decode('utf-8'))    
            cmd1 = talk_module + " " + talk_text
            cmd2 = play_module
            process1=subprocess.Popen(cmd1.split(),stdout=subprocess.PIPE)
            process2=subprocess.Popen(cmd2.split(),stdin=process1.stdout)
            print(cmd1.split())

            #for value in clients:
                #if value[1][0] == address[0] and value[1][1] == address[1] :
                #    print("クライアント{}:{}から{}というメッセージを受信完了".format(value[1][0], value[1][1], res))
                #else:
                #    value[0].send("クライアント{}:{}から{}を受信".format(value[1][0], value[1][1], res.decode()).encode("UTF-8"))
                #    pass
        except Exception as e:
            print(e)
            break


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