#%%
import os
import codecs
import copy
from typing import Text
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
 
from keras.layers import Dense, Activation, SimpleRNN
from keras.models import Sequential
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping
from keras.layers import LSTM

def readCandleFile(filePath):
        candle_list = []
        f = open(filePath,'r', encoding='utf-8-sig')
        for data in f:
                data = data.rstrip('\n')
                data = data.split(",")
                candle = {}
                for col in data:
                        col = col.lstrip(" ")
                        col = col.split("=")
                        if (len(col) >= 2) :
                                candle[col[0]]=float(col[1])
                        else:
                                candle["timestamp"]=col[0]
                candle_list.append(candle)
        f.close()
        return candle_list

def makeNormalizeDataSet(candle_list, seqLen=20, step=1):
        # close値のリスト作成
        close_prices = []
        for candle in candle_list:
                close_prices.append(candle["close"])

        input_prices = []
        label_prices = []
        for i in range(0, len(close_prices) - seqLen, step):
                # SEQLEN個の入力値群の中で最大値を取得
                max_price = max(close_prices[i:i+seqLen])
                min_price = min(close_prices[i:i+seqLen])
                # 入力値とラベル値を最大値で正規化
                input_price = [(n-min_price)/(max_price-min_price) for n in close_prices[i:i+seqLen]]
                label_price = (close_prices[i+seqLen]-min_price) / (max_price-min_price)
                # print("label={:.4f}, input={}".format(label_price, input_price))
                input_prices.append(input_price)
                label_prices.append(label_price)

        return input_prices, label_prices

def makeDataSet(candle_list, seqLen=20, step=1):
        # close値のリスト作成
        close_prices = []
        for candle in candle_list:
                close_prices.append(candle["close"])

        input_prices = []
        label_prices = []
        for i in range(0, len(close_prices) - seqLen, step):
                # SEQLEN個の入力値群の中で最大値を取得
                max_price = max(close_prices[i:i+seqLen])
                min_price = min(close_prices[i:i+seqLen])
                # 入力値とラベル値を最大値で正規化
                input_price = [(n-min_price)/(max_price-min_price) for n in close_prices[i:i+seqLen]]
                label_price = (close_prices[i+seqLen]-min_price) / (max_price-min_price)
                # print("label={:.4f}, input={}".format(label_price, input_price))
                input_prices.append(input_price)
                label_prices.append(label_price)

        return input_prices, label_prices

print("tensorflow version={}".format(tf.__version__))

curDir = os.getcwd()
print("curDir={}".format(curDir))

# from google.colab import drive
# drive.mount('/content/drive')
# TRAIN_FILE = '/content/drive/My Drive/Data/btcfx_candle_1min_00.txt'
# TEST_FILE = '/content/drive/My Drive/Data/btcfx_candle_1min_01.txt'

TRAIN_FILE = "../../data/btc/btcfx_candle_1min_buff.txt"
TEST_FILE = "../../data/btc/btcfx_candle_1min_test.txt"

# 2020/12/27 18:55:00, open=2964665, close=2963041, high=2965587, low=2961189, ema=0
train_candles = readCandleFile(TRAIN_FILE)
test_candles = readCandleFile(TEST_FILE)

SEQLEN = 20
STEP = 1
train_inputs, train_labels = makeNormalizeDataSet(train_candles, SEQLEN, STEP)
test_inputs, test_labels = makeNormalizeDataSet(test_candles, SEQLEN, STEP)
long_inputs, long_labels = makeDataSet(test_candles, SEQLEN, STEP)

IN_OUT_NEURONS=1
x = np.array(train_inputs).reshape(len(train_inputs), SEQLEN, IN_OUT_NEURONS)
y = np.array(train_labels).reshape(len(train_inputs), IN_OUT_NEURONS)

HIDDEN_SIZE = 128
BATCH_SIZE = 256#128
NUM_ITERATIONS = 12#25
NUM_EPOCHS_PER_ITERATION = 1
NUM_PREDS_PER_EPOCH = 10
model = Sequential()

#model.add(SimpleRNN(HIDDEN_SIZE, return_sequences=False, input_shape=(SEQLEN, IN_OUT_NEURONS), unroll=True))
model.add(LSTM(HIDDEN_SIZE, batch_input_shape=(None, SEQLEN, IN_OUT_NEURONS), return_sequences=False))

model.add(Dense(IN_OUT_NEURONS))

#model.add(Activation("softmax"))
#model.compile(loss="categorical_crossentropy", optimizer="rmsprop")

model.add(Activation("linear"))

optimizer = Adam(lr=0.001)
model.compile(loss="mean_squared_error", optimizer=optimizer)

#model.compile(loss="mean_squared_error", optimizer="adam",)

early_stopping = EarlyStopping(monitor='val_loss', mode='auto', patience=0)
history = model.fit(x, y, batch_size=BATCH_SIZE, epochs=10, validation_split=0.1, callbacks=[early_stopping])

#for iteration in range(NUM_ITERATIONS):
#  print("="*50)
#  print("Iteration #: %d" % (iteration))
#  model.fit(x, y, batch_size=BATCH_SIZE, epochs=NUM_EPOCHS_PER_ITERATION)

for i in range(1):
  test_idx = 0#np.random.randint(len(test_inputs))
  x_prices = test_inputs[test_idx]
  y_prices = copy.copy(x_prices)
  z_prices = copy.copy(x_prices)
  y_prices.append(test_labels[test_idx])

  Xtest = np.array(x_prices).reshape(1, len(x_prices), IN_OUT_NEURONS)
  ypred = model.predict(Xtest, verbose=0)
  z_prices.append(ypred[0][0])

  plt.figure()
  plt.plot(range(0,len(y_prices)),y_prices, color="r", label="label_data")
  plt.plot(range(0,len(z_prices)),z_prices, color="g", label="predict_data")
  plt.plot(range(0,len(x_prices)),x_prices, color="b", label="input_data")
  plt.legend()
  plt.show()


long_idx = 0#np.random.randint(len(long_inputs))
long_prices = long_inputs[long_idx]
test_prices = copy.copy(long_prices)
label_prices = copy.copy(long_prices)
pred_prices = copy.copy(long_prices)

for i in range(NUM_PREDS_PER_EPOCH):
  # SEQLEN個の入力値群の中で最大値を取得
  #max_price = max(test_prices[i:i+len(test_prices)])
  #min_price = min(test_prices[i:i+len(test_prices)])
  max_price = max(test_prices)
  min_price = min(test_prices)
  # 入力値とラベル値を最大値で正規化
  #x_prices = [(n-min_price)/(max_price-min_price) for n in test_prices[i:i+len(test_prices)]]
  x_prices = [(n-min_price)/(max_price-min_price) for n in test_prices]
  # 推論用の入力データを作成
  Xtest = np.array(x_prices).reshape(1, len(x_prices), IN_OUT_NEURONS)
  # 推論を実行
  ypred = model.predict(Xtest, verbose=0)
  # 推論結果を実値に戻す
  ypred_real = (max_price - min_price)*ypred[0][0] + min_price
  # 最初のデータを取り除いて推論結果の実値を追加する
  test_prices = test_prices[1:]
  test_prices.append(ypred_real)
  # 結果配列に推論結果の実値を追加する
  pred_prices.append(ypred_real)
  label_prices.append(long_labels[long_idx+i])

# 入力値群の中で最大値を取得
max_price = max(pred_prices)
min_price = min(pred_prices)
# 入力値とラベル値を最大値で正規化
label_plot = [(n-min_price)/(max_price-min_price) for n in label_prices]
pred_plot = [(n-min_price)/(max_price-min_price) for n in pred_prices]
input_plot = [(n-min_price)/(max_price-min_price) for n in long_prices]
plt.figure()
plt.plot(range(0,len(label_plot)),label_plot, color="r", label="label_data")
plt.plot(range(0,len(pred_plot)),pred_plot, color="g", label="predict_data")
plt.plot(range(0,len(input_plot)),input_plot, color="b", label="input_data")
plt.legend()
plt.show()
# %%
