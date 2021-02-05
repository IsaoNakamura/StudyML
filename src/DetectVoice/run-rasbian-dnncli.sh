#! /bin/sh

dictationkit_path=../../../dictation-kit

# julius -C main.jconf -C am-dnn.jconf -demo -input vecnet $* &
# sleep 10
#python3 ./dnnclient-rpi.py dnnclient.conf &

#python3 ./talker.py &
#sleep 3
python3 ./listener.py dnnclient.conf &
sleep 5
adintool -in mic -out vecnet -server 127.0.0.1 -paramtype FBANK_D_A_Z -veclen 120 -htkconf $dictationkit_path/model/dnn/config.lmfb -port 5532 -cvn -cmnload $dictationkit_path/model/dnn/norm -cmnnoupdate

kill 0
