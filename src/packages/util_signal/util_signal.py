import sys
import signal

def killtrap_handler(signum, frame) -> None:
    #print("trapped. signum={} frame={}".format(signum, frame))
    sys.exit(1)

def set_killtrap_handler() -> None:
   signal.signal(signal.SIGTERM, killtrap_handler)
 
def set_killtrap_finallybeg() -> None:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def set_killtrap_finallyend() -> None:
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

