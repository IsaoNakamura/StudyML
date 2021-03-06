import sys
import threading
import time
import multiprocessing
from multiprocessing import Process, Queue

# 自作signalユーティリティモジュールを参照
sys.path.append('./src')
from packages.util_signal import util_signal
import MultiProc.subproc

class MainProc():
    # コンストラクタ
    def __init__(self):
        print("{} : init beg.".format(__class__.__name__))
        util_signal.set_killtrap_handler()
        # 初期化処理
        self.subthread = None
        self.subthread_alive = True
        self.subprocess = None 
        print("{} : init end.".format(__class__.__name__))
    # デストラクタ
    def __del__(self):
        try:
            print("{} : del beg.".format(__class__.__name__))
            # 後始末処理
        finally:
            print("{} : del end.".format(__class__.__name__))

    # スレッドハンドラ
    def subthread_handler(self):
        counter = 0
        while self.subthread_alive:
            #print("{} : counter={} ".format(multiprocessing.current_process().name, counter))
            print("{} : subthread counter={} ".format(__class__.__name__, counter))
            counter+=1
            time.sleep(1.0)
        print("{} : subthread is ended. ".format(__class__.__name__))
    # メイン処理実行
    def run_main(self):
        result = -1
        try:
            # スレッドをdaemonとして作成
            self.subthread = threading.Thread(target=self.subthread_handler, daemon=True)
            # スレッドスタート
            self.subthread.start()
            print("{} : subthread started. ".format(__class__.__name__))

            self.subprocess = Process(name='SubProcess1', target=MultiProc.subproc.run)
            self.subprocess.start()
            print("{} : subprocess started. ".format(__class__.__name__))

            # メインループ
            print("{} : mainthread-roop starting. ".format(__class__.__name__))
            counter = 0
            while True:
                print("{} : mainthread counter={} ".format(__class__.__name__, counter))
                counter+=1
                time.sleep(1.0)
            print("{} : mainthread-roop is ended. ".format(__class__.__name__))
            result = 0
        except KeyboardInterrupt:
            print("{} : except KeyboardInterrupt. ".format(__class__.__name__))
            result = 0
        except Exception as e:
            print("{} : except Exception. except={}".format(__class__.__name__), e)
        finally:
            print("{} : finally beg.".format(__class__.__name__))
            util_signal.pause_kill()
            # スレッドのループを終了させるフラグをOFFにする
            self.subthread_alive = False
            # スレッドをジョインさせる
            self.subthread.join()
            print("{} : subthread is joined.".format(__class__.__name__))

            if self.subprocess is not None and self.subprocess.is_alive():
                print("{} : call subprocess terminate.".format(__class__.__name__))
                self.subprocess.terminate()
                print("{} : called subprocess terminate.".format(__class__.__name__))

            if(result!=0):
                pass
            util_signal.resume_kill()
            print("{} : finally end.".format(__class__.__name__))
        return result

if __name__ == '__main__':
    # エントリポイント
    sys.exit(MainProc().run_main())