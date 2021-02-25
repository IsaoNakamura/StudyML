import sys
import signal

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
from packages.util_signal import util_signal
class Hoge:
    def __init__(self):
        util_signal.set_killtrap_handler()
        # 初期化処理

    def __del__(self):
        util_signal.set_killtrap_finallybeg()
        # 後始末処理
        util_signal.set_killtrap_finallyend()
    
    def run_main(self):
        result = -1
        try:
            # メイン処理
            pass
        except Exception as e:
            print(e)
        finally:
            if(result!=0):
                pass
        return result

if __name__ == '__main__':
    # エントリポイント
    sys.exit(Hoge().run_main())