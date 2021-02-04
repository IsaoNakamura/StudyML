#! /bin/sh

# julius -C main.jconf -C am-dnn.jconf -demo -input vecnet $* &
# sleep 10
python3 ./bin/common/dnnclient-rpi.py dnnclient.conf &
sleep 5
adintool -in mic -out vecnet -server 127.0.0.1 -paramtype FBANK_D_A_Z -veclen 120 -htkconf model/dnn/config.lmfb -port 5532 -cvn -cmnload model/dnn/norm -cmnnoupdate

kill 0
