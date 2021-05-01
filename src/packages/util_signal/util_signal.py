import sys
import os
import signal
import threading

_modulename = os.path.basename(__file__)

def killtrap_handler(signum, frame) -> None:
    print("trapped. signum={} frame={}".format(signum, frame))
    sys.exit(1)

def set_killtrap_handler() -> None:
   signal.signal(signal.SIGTERM, killtrap_handler)

def pause_kill() -> None:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def resume_kill() -> None:
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

def set_killtrap_finallybeg() -> None:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def set_killtrap_finallyend() -> None:
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

# 自作signalユーティリティモジュールを参照
sys.path.append('./src')
from packages.util_signal import util_signal

class TestUtilSignal():
    # コンストラクタ
    def __init__(self):
        print("{} : init.".format(_modulename))
        util_signal.set_killtrap_handler()
        # 初期化処理
        self.subthread = None
        self.subthread_alive = True
    # デストラクタ
    def __del__(self):
        try:
            print("{} : del beg.".format(_modulename))
            util_signal.pause_kill()
            # 後始末処理
        finally:
            util_signal.resume_kill()
            print("{} : del end.".format(_modulename))

    # スレッドハンドラ
    def subthread_handler(self):
        while self.subthread_alive:
            pass
        print("subthread is end.")
    # メイン処理実行
    def run_test(self):
        result = -1
        try:
            # スレッドをdaemonとして作成
            self.subthread = threading.Thread(target=self.subthread_handler, daemon=True)
            # スレッドスタート
            self.subthread.start()
            print("{} : subthread started. ".format(_modulename))
            # メインループ
            print("{} : mainthread-roop starting. ".format(_modulename))
            while True:
                pass
        except KeyboardInterrupt:
            print("{} : except KeyboardInterrupt. ".format(_modulename))
        except Exception as e:
            print("{} : except Exception. except={}".format(_modulename, e))
        finally:
            print("{} : finally beg.".format(_modulename))
            # スレッドのループを終了させるフラグをOFFにする
            self.subthread_alive = False
            # スレッドをジョインさせる
            self.subthread.join()
            if(result!=0):
                pass
            print("{} : finally end.".format(_modulename))
        return result

if __name__ == '__main__':
    # エントリポイント
    sys.exit(TestUtilSignal().run_test())