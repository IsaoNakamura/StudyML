import socket
import time

def connectSocket(socket, host, port) -> int:
    result = -1
    try:
        socket.connect((host,port))
        result = 0
    except Exception as e:
        print(e)
    finally:
        pass
    return result

def connectSocketRetry(socket:None, host:str, port:int, retrycnt:int=10, retryinterval_sec:float=1.0) -> int:
    result = -1
    try:
        retry=0
        while True:
            if( connectSocket(socket, host, port) == 0):
                result=0
                break
            
            retry+=1
            if(retry>=retrycnt):
                break

            time.sleep(retryinterval_sec)
            continue
    except Exception as e:
        print(e)
    finally:
        pass
    return result

def hogefunc():
    # 0:正常 !0:異常
    result = -1 
    try:
        #TODO
        # ここまできたら正常終了
        result = 0
    except Exception as e:
        print(e)
    finally:
        if(result!=0):
            # 異常時後始末処理
            pass
    return result