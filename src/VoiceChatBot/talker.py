import sys
import os
import socket
import subprocess
import threading
import random
import datetime
import time
from collections import deque

# 自作signalユーティリティモジュールを参照
sys.path.append('./src')
from packages.util_signal import util_signal



_modulename = os.path.basename(__file__)

# 格助詞
#pos_case = ('や', 'で', 'より', 'から', 'へ','と','に','を','が')
# 終助詞
#pos_post = ('な', 'ぞ', 'よ', 'ね', 'な','の','か')
# は, が, の, と, ね, を, 

reactions0 = ("はい？","うん？","なに？","はいよ","え？")
reactions1 = ("うーんとね","えっとね","うーん","そうねえ","ちょいまち")
reactions2 = ("もういちどいって","もっかいいって","あんだってぇ？、もっかいいって","ききとれなかった","なんていってるの？","わんもあぷりーず")
reactions3 = ("うんうん","へー","ほう","なるほど","そうだねえ","そうなんだ")

replies0 = (
        ("そそそ、そうなんよねー。","、なんよねー。"), 
        ("これこれ、こういう。","、ということ。"),
        ("それな。","、まじ、それな。"),
        ("うける。","、まじ、うける。"),
        ("かわいい。","、まじ、かわいい。"),
    )

# cwd_str = os.getcwd()
module_dir = os.path.dirname(__file__)
dictationkit_path = module_dir + "/" + "../../../dictation-kit/"
talk_module = module_dir + "/" + "../../../aquestalkpi/AquesTalkPi"

play_module = "aplay"
python_module = 'python3'

# julius -C main.jconf -C am-dnn.jconf -demo -dnnconf julius.dnnconf -input adinnet -module
julius_module = 'julius'
julius_opt = ''
julius_opt = julius_opt + ' -C ' + dictationkit_path + 'main.jconf'
julius_opt = julius_opt + ' -C ' + dictationkit_path + 'am-dnn.jconf'
julius_opt = julius_opt + ' -demo '
julius_opt = julius_opt + ' -dnnconf ' + dictationkit_path + 'julius.dnnconf'
julius_opt = julius_opt + ' -input ' + 'adinnet'
julius_opt = julius_opt + ' -module '

julius_cmd = julius_module + julius_opt

deliverer_module = module_dir + "/deliverer-juliuscli.py"
listener_module = module_dir + "/listener-adinsvr.py"
timefiller_module = module_dir + "/timefiller.py"

deliverer_cmd = python_module + " " + deliverer_module
timefiller_cmd = python_module + " " + timefiller_module
listener_cmd = python_module + " " + listener_module + " " + module_dir + "/listener-adinsvr.conf"

talkserver_host = 'localhost'
talkserver_port = 5533

date_format = '%Y/%m/%d %H:%M:%S'



class Talker:
    def __init__(self):
        print("{} : init.".format(_modulename))
        util_signal.set_killtrap_handler()
        # 初期化処理
        
        # 音声解析タスク
        self.recognition_tasks = deque()
        # リアクションタスク
        self.reaction_tasks = deque()
        # 間つなぎタスク
        self.keeper_tasks = deque()
        # 返答タスク
        self.reply_tasks = deque()
        # 聞き直しタスク
        self.again_tasks = deque()

        self.clients = []
        self.client_thread = None
        self.client_alive = True

        self.julius_proc = None
        self.deliverer_proc = None
        self.listener_proc = None
        self.timefiller_proc = None

        self.talker_sock = None

        self.talk_thread = None
        self.talk_alive = True

    def __del__(self):
        util_signal.set_killtrap_finallybeg()
        print("{} : del beg.".format(_modulename))

        # 後始末処理
        if(self.deliverer_proc is not None):
            self.deliverer_proc.kill()
        if(self.listener_proc is not None):
            self.listener_proc.kill()
        if(self.timefiller_proc is not None):
            self.timefiller_proc.kill()
        if(self.julius_proc is not None):
            self.julius_proc.kill()
        if(self.talker_sock is not None):
            #self.talker_sock.send("DIE".encode('utf-8'))
            self.talker_sock.close()

        print("{} : del end.".format(_modulename))
        util_signal.set_killtrap_finallyend()

    def genReplyText(self, recog_text):
        reply_text = ''
        try:
            reply_idx = random.randint(0,len(replies0)-1)
            pre_text = replies0[reply_idx][0]
            post_text = replies0[reply_idx][1]
            main_text = ''
            
            words = [ word.split('+') for word in recog_text.split(' ') ]
            for i, cur_word in enumerate(words):
                if(len(cur_word)>=2):
                    cur_value = cur_word[0]
                    cur_type = cur_word[1]
                    if( cur_type=='助詞'):
                        if( (i+1) < len(words) ):
                            next_word = words[i+1]
                            if(len(next_word)>=2):
                                next_value = next_word[0]
                                next_type = next_word[1]
                                if(next_value=='。'):
                                    # 終助詞と判定
                                    # 追加しない
                                    pass
                                else:
                                    # 追加する
                                    main_text+=cur_value
                                    pass
                        else:
                            # 終助詞と判定
                            # 追加しない
                            pass
                    #elif( cur_type=='助動詞'):
                    #    # 追加しない
                    #    pass
                    else:
                        # 追加する
                        main_text+=cur_value
            
            reply_text = pre_text + main_text + post_text
        except Exception as err:
            pass
        finally:
            pass
        return reply_text

    def test_genReplyText(self):
        try:
            recog_text = '今日+名詞 は+助詞 、+補助記号 天気+名詞 が+助詞 いい+形容詞 です+助動詞 ね+助詞 '
            reply_text = self.genReplyText(recog_text)
            print('reply_text={}'.format(reply_text))
            pass
        except Exception as err:
            pass
        finally:
            pass

    def talk_handler(self):
        result = -1
        try:
            while self.talk_alive:
                talk_text=''
                if( len(self.reply_tasks)>0):
                    if( len(self.recognition_tasks)>0):
                        # 音声解析タスクがある場合
                        talk_text = self.genReplyText(self.reply_tasks.popleft())
                        # 音声認識タスクを古いものからPOP
                        self.recognition_tasks.popleft()

                        if( len(self.recognition_tasks)>0):
                            # 音声解析タスクがまだある場合
                            # 間つなぎを依頼する
                            now = datetime.datetime.now()
                            now_str = now.strftime(date_format)
                            print("notification for replied. {}".format(now_str))
                            for value in self.clients:
                                # クライアントに通知する
                                value[0].send(now_str.encode("UTF-8"))
                        else:
                            # 音声解析タスクがもうない場合
                            print("send to client for cancel timekeeper")
                            # 間つなぎをキャンセルさせる
                            self.keeper_tasks.clear()
                            for value in self.clients:
                                # クライアントに発信する
                                value[0].send("/cancel_timekeeper ".encode("UTF-8"))   
                    else:
                        # 音声解析タスクがない場合
                        print("send to client for cancel timekeeper")
                        # 間つなぎをキャンセルさせる
                        self.keeper_tasks.clear()
                        for value in self.clients:
                            # クライアントに発信する
                            value[0].send("/cancel_timekeeper ".encode("UTF-8"))

                elif( len(self.again_tasks)>0):
                    self.again_tasks.popleft()
                    #again_tasks.clear()
                    react_idx = random.randint(0,len(reactions2)-1)
                    talk_text = reactions2[react_idx]
                    print("send to client for ask again")

                    # 音声認識タスクを古いものからPOP
                    if(len(self.recognition_tasks)>0):
                        self.recognition_tasks.popleft()
                        # 音声解析タスクをクリアする
                        #recognition_tasks.clear()

                    # 間つなぎをキャンセルさせる
                    self.keeper_tasks.clear()
                    for value in self.clients:
                        # クライアントに発信する
                        value[0].send("/cancel_timekeeper ".encode("UTF-8"))

                elif( len(self.reaction_tasks)>0):
                    self.reaction_tasks.popleft()
                    react_idx = random.randint(0,len(reactions0)-1)
                    talk_text = reactions0[react_idx]
                
                    now = datetime.datetime.now()
                    now_str = now.strftime(date_format)
                    print("notification for reacted. {}".format(now_str))
                    for value in self.clients:
                        # クライアントに通知する
                        value[0].send(now_str.encode("UTF-8"))
                        pass

                elif( len(self.keeper_tasks)>0):
                    self.keeper_tasks.popleft()
                    react_idx = random.randint(0,len(reactions1)-1)
                    talk_text = reactions1[react_idx]

                    now = datetime.datetime.now()
                    now_str = now.strftime(date_format)
                    print("notification for keeper. {}".format(now_str))
                    for value in self.clients:
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
            print("{} : talk_handler end. ".format(_modulename))
        except KeyboardInterrupt:
            # Ctrl+Cで止められるのが前提
            print("{} : talk_handler except KeyboardInterrupt.".format(_modulename))
            result = 0
        except Exception as e:
            print("{} : talk_handler except Exception. except={}".format(_modulename, e))
        finally:
            if(result!=0):
                pass
        return result

    # 接続済みクライアントは読み込みおよび書き込みを繰り返す
    def client_handler(self, connection, address):
        try:
            while self.client_alive:
                #クライアント側から受信する
                rcvmsg = str(connection.recv(4096).decode('utf-8'))
                if len(rcvmsg)>0:
                    now = datetime.datetime.now()
                    now_str = now.strftime(date_format)
                    if( '/detection' in rcvmsg):
                        # マイクから音を検出した場合
                        print("recieve /detection {}".format(now_str))
                        
                        # 音声認識タスクを追加
                        self.recognition_tasks.append(now_str)

                        # リアクションタスクを追加
                        self.reaction_tasks.append(now_str)

                    elif( '/timekeeper' in rcvmsg):
                        print("recieve /timekeeper {}".format(now_str))
                        # 間つなぎタスクを追加
                        self.keeper_tasks.append(now_str)

                    elif( '/recogfail' in rcvmsg):
                        print("recieve /recogfail {}".format(now_str))
                        # 聞き直しタスクを追加
                        self.again_tasks.append(now_str)

                    else:
                        print("recieve recognized text={}".format(rcvmsg))

                        if( len(self.recognition_tasks) > 0):
                            # 返信タスクを追加
                            self.reply_tasks.append(rcvmsg)
                        #else:
                        #    reply_tasks.clear()
            print("{} : client_handler end. ".format(_modulename))
        except Exception as e:
            print(e)

    def run_main(self):
        result = -1
        try:
            # juliusプロセススタート
            # self.julius_proc = subprocess.Popen(julius_cmd.split(),stdin=None,stdout=None)
            # time.sleep(5.0)
        
            self.talker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.talker_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.talker_sock.bind((talkserver_host, talkserver_port))
            self.talker_sock.listen(1)

            # スレッド作成
            self.talk_thread = threading.Thread(target=self.talk_handler, daemon=True)
            # スレッドスタート
            self.talk_thread.start()

            # サブプロセススタート
            self.deliverer_proc = subprocess.Popen(deliverer_cmd.split(),stdin=None,stdout=None)
            self.listener_proc = subprocess.Popen(listener_cmd.split(),stdin=None,stdout=None)
            self.timefiller_proc = subprocess.Popen(timefiller_cmd.split(),stdin=None,stdout=None)

            while True:
                # 接続要求を受信
                conn, addr = self.talker_sock.accept()
                # アドレス確認
                print("{} : connected from ip={} port={}".format(_modulename, addr[0], addr[1]))
                # 待受中にアクセスしてきたクライアントを追加
                self.clients.append((conn, addr))
                if self.client_thread is None:
                    # スレッド作成
                    self.client_thread = threading.Thread(target=self.client_handler, args=(conn, addr), daemon=True)
                    # スレッドスタート
                    self.client_thread.start()

        except KeyboardInterrupt:
            print("{} : except KeyboardInterrupt. ".format(_modulename))
        except Exception as e:
            print("{} : except Exception. except={}".format(_modulename, e))
        finally:
            self.talk_alive = False
            self.talk_thread.join()
            self.client_alive = False
            if self.client_thread is not None:
                self.client_thread.join()
            if(result!=0):
                pass
        return result

if __name__ == '__main__':
    sys.exit(abs(Talker().run_main()))