# %%
# 生成词嵌入文件
from tqdm import tqdm
import numpy as np
import pandas as pd
from tensorflow.keras.callbacks import ModelCheckpoint, LearningRateScheduler
from gensim.models import Word2Vec, KeyedVectors
from tensorflow.keras.layers import Input, LSTM, Embedding, Dense
from tensorflow.keras.models import Model, Sequential
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from mail import mail
import os
from keras.utils import to_categorical
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
# %%
# f = open('tmp/userid_creative_ids.txt')
f = open('word2vec/userid_creative_ids.txt')
num_creative_id = 2481135+1
tokenizer = Tokenizer(num_words=num_creative_id)
tokenizer.fit_on_texts(f)
f.close()


# %%
path = "word2vec/wordvectors_creative_id.kv"
wv = KeyedVectors.load(path, mmap='r')


# %%
f = open('word2vec/userid_creative_ids.txt')
max_len_creative_id = -1
for line in f:
    current_line_len = len(line.strip().split(' '))
    max_len_creative_id = max(max_len_creative_id, current_line_len)
f.close()


# %%
creative_id_tokens = list(wv.vocab.keys())
embedding_dim = 128
embedding_matrix = np.random.randn(len(creative_id_tokens)+1, 128)
cnt = 0
for creative_id in creative_id_tokens:
    embedding_vector = wv[creative_id]
    if embedding_vector is not None:
        index = tokenizer.texts_to_sequences([creative_id])[0][0]
        embedding_matrix[index] = embedding_vector


# %%
debug = True
if debug:
    max_len_creative_id = 200
# shape：(sequence长度,)
input_x = Input(shape=(None,))
# cpus = tf.config.experimental.list_logical_devices('CPU')
# with tf.device('cpu'):
#     emb =  Embedding(input_dim=num_creative_id,
#                 output_dim=128,
#                 weights=[embedding_matrix],
#                 trainable=False,
#                 input_length=max_len_creative_id,
#                 mask_zero=True)
# x = emb(input_x)
x = Embedding(input_dim=num_creative_id,
              output_dim=128,
              weights=[embedding_matrix],
              trainable=False,
              input_length=max_len_creative_id,
              mask_zero=True)(input_x)
x = LSTM(1024)(x)
output_y = Dense(10, activation='softmax')(x)

model = Model([input_x], output_y)

# model = Sequential([
#     Embedding(num_creative_id, 128,
#               weights=[embedding_matrix],
#               trainable=False,
#               input_length=None),
#     LSTM(1024),
#     Dense(1, activation='sigmoid')
# ])
model.summary()
model.compile(loss='categorical_crossentropy',
              optimizer='adam', metrics=['accuracy'])


# %%
# 测试数据格式(batch_size, sequence长度)
test_data = np.array([1, 2, 3, 4]).reshape(1, -1)
model.predict(test_data)


# %%
X_train = []
with open('word2vec/userid_creative_ids.txt')as f:
    for text in f:
        X_train.append(text.strip())


# %%
if debug:
    sequences = tokenizer.texts_to_sequences(X_train[:90000//1])
    X_train = pad_sequences(sequences, maxlen=max_len_creative_id)
else:
    sequences = tokenizer.texts_to_sequences(X_train)


# %%
# 使用迭代器实现
# X_train = pad_sequences(sequences, maxlen=max_len_creative_id)
# %%
user_train = pd.read_csv(
    'data/train_preliminary/user.csv').sort_values(['user_id'], ascending=(True,))
Y_gender = user_train['gender'].values
Y_age = user_train['age'].values

Y_age = Y_age-1
Y_gender = Y_gender - 1
# %%
if debug:
    Y_gender = Y_gender[:90000//1]
    Y_age = Y_age[:90000//1]
    Y_age = to_categorical(Y_age)
# %%
checkpoint = ModelCheckpoint("tmp/epoch_{epoch:02d}.hdf5", monitor='val_loss', verbose=0,
                             save_best_only=False, mode='auto', period=20)
# %%
try:
    model.fit(X_train,
              Y_age,
              validation_split=0.1,
              epochs=100,
              batch_size=256,
              callbacks=[checkpoint],
              )
    mail('train lstm for age done!!!')
except Exception as e:
    e = str(e)
    mail('train lstm for age failed!!! ' + e)
# %%
