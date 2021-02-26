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
 
def set_killtrap_finallybeg() -> None:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def set_killtrap_finallyend() -> None:
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

# 自作signalユーティリティモジュールを参照
sys.path.append('./src')
from packages.util_signal import util_signal
class Hoge:
    # コンストラクタ
    def __init__(self):
        print("{} : init.".format(_modulename))
        util_signal.set_killtrap_handler()
        # 初期化処理
        self.hoge_thread = None
        self.hoge_alive = True
    # デストラクタ
    def __del__(self):
        util_signal.set_killtrap_finallybeg()
        print("{} : del beg.".format(_modulename))
        # 後始末処理
        print("{} : del end.".format(_modulename))
        util_signal.set_killtrap_finallyend()
    # スレッドハンドラ
    def hoge_handler(self):
        while self.hoge_alive:
            pass
    # メイン処理実行
    def run_main(self):
        result = -1
        try:
            # スレッドをdaemonとして作成
            self.hoge_thread = threading.Thread(target=self.hoge_handler, daemon=True)
            # スレッドスタート
            self.hoge_thread.start()
            # メインループ
            while True:
                pass
        except KeyboardInterrupt:
            print("{} : except KeyboardInterrupt. ".format(_modulename))
        except Exception as e:
            print("{} : except Exception. except={}".format(_modulename, e))
        finally:
            print("{} : finally beg.".format(_modulename))
            # スレッドのループを終了させるフラグをOFFにする
            self.hoge_alive = False
            # スレッドをジョインさせる
            self.hoge_thread.join()
            if(result!=0):
                pass
            print("{} : finally end.".format(_modulename))
        return result

if __name__ == '__main__':
    # エントリポイント
    sys.exit(Hoge().run_main())