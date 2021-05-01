import sys
import time
import threading
import multiprocessing

# 自作signalユーティリティモジュールを参照
sys.path.append('./src')
from packages.util_signal import util_signal

class SubProc():
    proc_name = 'SuperSubProc'
    # コンストラクタ
    def __init__(self):
        #self.proc_name = __class__.__name__
        print("{} : init beg.".format(self.proc_name))
        util_signal.set_killtrap_handler()
        # 初期化処理
        self.subthread = None
        self.subthread_alive = True
        print("{} : init end.".format(self.proc_name))
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
            self.proc_name = multiprocessing.current_process().name

            # スレッドをdaemonとして作成
            self.subthread = threading.Thread(target=self.subthread_handler, daemon=True)
            # スレッドスタート
            self.subthread.start()
            print("{} : subthread started. ".format(__class__.__name__))
            # メインループ
            print("{} : mainthread-roop starting. ".format(__class__.__name__))
            counter = 0
            while True:
                print("{} : mainthred counter={} ".format(__class__.__name__, counter))
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
            util_signal.pause_kill()
            print("{} : finally beg.".format(__class__.__name__))
            # スレッドのループを終了させるフラグをOFFにする
            self.subthread_alive = False
            # スレッドをジョインさせる
            self.subthread.join()
            #print("{} : subthread is joined.".format(__class__.__name__))
            if(result!=0):
                pass
            util_signal.resume_kill()
            print("{} : finally end.".format(__class__.__name__))
        return result

def run():
    proc_obj1 = SubProc()
    proc_obj2 = SubProc()
    proc_obj2.proc_name = 'proc_obj2'
    print (proc_obj1.proc_name)
    print (proc_obj2.proc_name)
    print (SubProc.proc_name)
    proc_obj.run_main()

if __name__ == '__main__':
    # エントリポイント
    #sys.exit(SubProc().run_main())
    sys.exit(run())