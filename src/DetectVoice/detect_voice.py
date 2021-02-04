import socket

host = 'localhost'
# host = '10.0.1.21'
port = 10500

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host,port))

data=""
try:
    data = ""
    while True:
        if '</RECOGOUT>\n.' in data:
            recog_text = ""
            for line in data.split('\n'):
                index = line.find('WORD="')
                if index != -1:
                    line = line[index+6:line.find('"',index+6)]
                    recog_text = recog_text + line
            print("result: " + recog_text)
            data = ""
        else:
            data += str(sock.recv(1024).decode('utf-8'))
            #print('Not Found')
except KeyboardInterrupt:
    print('finished')
    sock.send("DIE".encode('utf-8'))
    sock.close()
