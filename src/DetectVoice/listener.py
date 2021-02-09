import sys
import numpy as np
import socket
import struct

talker_host =  'localhost'
talker_port = 5533
adinserver_host = 'localhost'
adinserver_port = 5532
julius_host = 'localhost'
julius_port = 5531
num_raw = 120
num_input = 1320
num_hid = 2048
num_output = 2004
num_context = 11 # 1320 / 120
batchsize = 32

dictationkit_path = "../../../dictation-kit/"

w_filename = ["dnn_sample/W_l1.npy", "dnn_sample/W_l2.npy", "dnn_sample/W_l3.npy", "dnn_sample/W_l4.npy", "dnn_sample/W_l5.npy", "dnn_sample/W_l6.npy", "dnn_sample/W_l7.npy", "dnn_sample/W_output.npy"]
b_filename = ["dnn_sample/bias_l1.npy", "dnn_sample/bias_l2.npy", "dnn_sample/bias_l3.npy", "dnn_sample/bias_l4.npy", "dnn_sample/bias_l5.npy", "dnn_sample/bias_l6.npy", "dnn_sample/bias_l7.npy", "dnn_sample/bias_output.npy"]

prior_filename = "dnn_sample/seedhmm.cluster.prior"

if len(sys.argv) > 1:
    conffile = sys.argv[1]
    f = open(conffile)
    for line in f:
        linebuf = line.strip().split(' ')
        if linebuf[0] == "--adinserver_host":adinserver_host = linebuf[1]
        elif linebuf[0] == "--adinserver_port":adinserver_port = int(linebuf[1])
        elif linebuf[0] == "--julius_host":julius_host = linebuf[1]
        elif linebuf[0] == "--julius_port":julius_port = int(linebuf[1])
        elif linebuf[0] == "--num_raw":num_raw = int(linebuf[1])
        elif linebuf[0] == "--num_input":num_input = int(linebuf[1])
        elif linebuf[0] == "--num_hid":num_hid = int(linebuf[1])
        elif linebuf[0] == "--num_output":num_output = int(linebuf[1])
        elif linebuf[0] == "--num_context":num_context = int(linebuf[1])
        elif linebuf[0] == "--batchsize":batchsize = int(linebuf[1])
        elif linebuf[0] == "--prior_filename":prior_filename = dictationkit_path + linebuf[1]
        elif linebuf[0] == "--w_filename":
            for i in range(1, len(linebuf)):
                w_filename[i - 1] = dictationkit_path + linebuf[i]
        elif linebuf[0] == "--b_filename":
            for i in range(1, len(linebuf)):
                b_filename[i - 1] = dictationkit_path + linebuf[i]
        elif linebuf[0] == "#":
            pass
        else:
            print("unkown switch")
            sys.exit()
    f.close()                                                            

w1 = np.load(w_filename[0])
w2 = np.load(w_filename[1])
w3 = np.load(w_filename[2])
w4 = np.load(w_filename[3])
w5 = np.load(w_filename[4])
w6 = np.load(w_filename[5])
w7 = np.load(w_filename[6])
wo = np.load(w_filename[7])

b1 = np.load(b_filename[0])
b2 = np.load(b_filename[1])
b3 = np.load(b_filename[2])
b4 = np.load(b_filename[3])
b5 = np.load(b_filename[4])
b6 = np.load(b_filename[5])
b7 = np.load(b_filename[6])
bo = np.load(b_filename[7])

state_prior = np.zeros((bo.shape[0], 1))
prior_factor = 1.0
for line in open(prior_filename):
    state_id, state_p = line[:-1].split(' ')
    state_id = int(state_id)
    state_p = float(state_p) * prior_factor
    state_prior[state_id][0] = state_p

def ff(x0):
    x1 = 1. / (1 + np.exp(-(np.dot(w1.T, x0) + b1)))
    x2 = 1. / (1 + np.exp(-(np.dot(w2.T, x1) + b2)))
    x3 = 1. / (1 + np.exp(-(np.dot(w3.T, x2) + b3)))
    x4 = 1. / (1 + np.exp(-(np.dot(w4.T, x3) + b4)))
    x5 = 1. / (1 + np.exp(-(np.dot(w5.T, x4) + b5)))
    x6 = 1. / (1 + np.exp(-(np.dot(w6.T, x5) + b6)))
    x7 = 1. / (1 + np.exp(-(np.dot(w7.T, x6) + b7)))
    tmp = np.dot(wo.T, x7) + bo
    np.exp(tmp, tmp)
    tmp /= np.sum(tmp, axis=0)
    tmp /= state_prior
    np.log10(tmp, tmp)
    return tmp

adinserversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
adinserversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
adinserversock.bind((adinserver_host, adinserver_port))
adinserversock.listen(1)


talkersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
talkersock.connect((talker_host, talker_port))

juliusclientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
juliusclientsock.connect((julius_host, julius_port))

sendconf = 0

print('Waiting for connections...')
adinclientsock, adinclient_address = adinserversock.accept()

splice_feature = np.zeros(num_input)
buf_splice_feature = None
fnum = 0
is_session_julius = False
is_wait = True
while True:
    if is_wait:
        print("wait message from adinserver.")
    rcvmsg = adinclientsock.recv(4)
    nbytes = struct.unpack('=i', rcvmsg)[0]
    if is_wait:
        print("recieve message from adinserver.")
        is_wait = False

    if nbytes == 12:
        rcvmsg = adinclientsock.recv(12)
        fbank_vecdim, fbank_shift, fbank_outprob_p = struct.unpack('=iii', rcvmsg)
        c_msg = struct.pack('=iiii', 12, num_output, 10, 1)
        print("#SPLIT C_MSG:{}".format(c_msg))
        juliusclientsock.sendall(c_msg)
        sendconf = 1

    elif nbytes == num_raw * 4:
        buffer = b''
        while len(buffer) < nbytes:
            # tmpdata = str(adinclientsock.recv(nbytes - len(buffer)).decode('utf-8'))
            # print("buffer length is {}".format(len(buffer)))
            tmpdata = adinclientsock.recv( nbytes - len(buffer) )
            if not tmpdata:
                # print(" #RECIEVE break")
                break
            buffer += tmpdata

        rcvmsg = buffer
        #print(" #RECIEVE from adin")

        val = struct.unpack("=" + "f" * num_raw, rcvmsg)
        splice_feature = np.r_[splice_feature[num_raw:num_input], val]
        if fnum >= num_context:
            
            if buf_splice_feature is not None:
                buf_splice_feature = np.hstack((buf_splice_feature, splice_feature[:, np.newaxis]))
            else:
                #print("fnum={} num_context={}".format(fnum, num_context))
                buf_splice_feature = splice_feature[:, np.newaxis]

        if buf_splice_feature is not None and buf_splice_feature.shape[1] == batchsize:
            if is_session_julius == False:
                talkersock.send("/reaction".encode("UTF-8"))
                is_session_julius = True            
            
            print("  #BEG send to julius nbyte={}".format(nbytes))
            #xo = ff(buf_splice_feature)
            #for i in range(xo.shape[1]):
            #    r_feature = xo[:, i]
            for i in range(buf_splice_feature.shape[1]):
                r_feature = buf_splice_feature[:, i]
                r_msg = struct.pack('=i', num_output * 4)
                juliusclientsock.sendall(r_msg)
                r_msg = struct.pack("=" + "f" * num_output, *r_feature)
                juliusclientsock.sendall(r_msg)

            print("  #END send to julius nbyte={}".format(nbytes))


            buf_splice_feature = None
        fnum = fnum + 1

    elif nbytes == 0:
        if buf_splice_feature is not None:
            print("  #BEG send to julius nbyte={}".format(nbytes))
            #xo = ff(buf_splice_feature)
            #for i in range(xo.shape[1]):
            #    r_feature = xo[:, i]
            for i in range(buf_splice_feature.shape[1]):
                r_feature = buf_splice_feature[:, i]
                r_msg = struct.pack('=i', num_output * 4)
                juliusclientsock.sendall(r_msg)
                r_msg = struct.pack("=" + "f" * num_output, *r_feature)
                juliusclientsock.sendall(r_msg)
            print("  #END send to julius nbyte={}".format(nbytes))

        r_msg = struct.pack('=i', 0)
        juliusclientsock.sendall(r_msg)
        print("#SPLIT R_MSG:{}".format(r_msg))
        #talkersock.sendall(b' end')
        splice_feature = np.zeros(num_input)
        buf_splice_feature = None
        fnum = 0
        is_session_julius = False
        is_wait = True
    elif len(rcvmsg) == 0:
        print("  rcvmsg's length is 0.")


r_msg = struct.pack('=i', 0)
juliusclientsock.sendall(r_msg)

r_msg = struct.pack('=i', -1)
juliusclientsock.sendall(r_msg)

adinclientsock.close()
