import sys
import io
import socket
import subprocess

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

host = 'localhost'
# host = '10.0.1.21'
port = 10500

talk_module = "../aquestalkpi/AquesTalkPi"
play_module = "aplay"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host,port))

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
            cmd1 = talk_module + " " + recog_text
            cmd2 = play_module
            #process1=subprocess.Popen(cmd1.split(),stdout=subprocess.PIPE)
            #process2=subprocess.Popen(cmd2.split(),stdin=process1.stdout)
            print(cmd1.split())
            data = ""
        else:
            data += str(sock.recv(1024).decode('utf-8'))
            # print(data)
except KeyboardInterrupt:
    print('finished')
    sock.send("DIE".encode('utf-8'))
    sock.close()
