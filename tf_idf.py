# %%
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import lightgbm as lgb
from mail import mail
# %%
user = pd.read_csv(
    'data/train_preliminary/user.csv').sort_values(['user_id'], ascending=(True,))
Y_train_gender = user.gender
Y_train_age = user.age
corpus = []
f = open('word2vec/userid_creativeids.txt', 'r')
# train_examples = 100
# test_examples = 200
# train_test = 300
train_test = 1900000
train_examples = 900000
test_examples = 1000000
flag = 0
for row in f:
    # row = [[int(e) for e in seq] for seq in row.strip().split(' ')]
    row = row.strip()
    corpus.append(row)
    flag += 1
    if flag == train_test:
        break
# %%
Y_train_gender = Y_train_gender.iloc[:train_examples]-1
Y_train_age = Y_train_age.iloc[:train_examples]-1
# %%
min_df = 30
max_df = 0.001
vectorizer = TfidfVectorizer(
    token_pattern=r"(?u)\b\w+\b",
    min_df=min_df,
    # max_df=max_df,
    # max_features=128,
    dtype=np.float32,
)
all_data = vectorizer.fit_transform(corpus)
print('(examples, features)', all_data.shape)
print('train tfidf done! min_df={}, max_df={} shape is {}'.format(
    min_df, max_df, all_data.shape[1]))
mail('train tfidf done! min_df={}, max_df={} shape is {}'.format(
    min_df, max_df, all_data.shape[1]))
# %%
train_val = all_data[:train_examples, :]
# %%
X_test = all_data[train_examples:(train_examples+test_examples), :]
# %%
test_user_id = pd.read_csv(
    'data/test/click_log.csv').sort_values(['user_id'], ascending=(True)).user_id.unique()
# %%
test_user_id = test_user_id[:test_examples]
# %%
X_train_gender, X_val_gender, Y_train_gender, Y_val_gender = train_test_split(
    train_val, Y_train_gender, train_size=0.9, random_state=1)
lgb_train_gender = lgb.Dataset(X_train_gender, Y_train_gender)
lgb_eval_gender = lgb.Dataset(
    X_val_gender, Y_val_gender, reference=lgb_train_gender)

X_train_age, X_val_age, Y_train_age, Y_val_age = train_test_split(
    train_val, Y_train_age, train_size=0.9, random_state=1)
lgb_train_age = lgb.Dataset(X_train_age, Y_train_age)
lgb_eval_age = lgb.Dataset(
    X_val_age, Y_val_age, reference=lgb_train_age)
# %%


def LGBM_gender(epoch, early_stopping_rounds):
    params_gender = {
        'task': 'train',
        'boosting_type': 'gbdt',
        'objective': 'binary',
        'metric': {'binary_logloss', 'binary_error'},  # evaluate指标
        'max_depth': -1,             # 不限制树深度
        # 更高的accuracy
        'max_bin': 2**10-1,

        'num_leaves': 2**10,
        'min_data_in_leaf': 1,
        'learning_rate': 0.01,
        # 'feature_fraction': 0.9,
        # 'bagging_fraction': 0.8,
        # 'bagging_freq': 5,
        # 'is_provide_training_metric': True,
        'verbose': 1
    }
    print('Start training...')
    # train
    gbm = lgb.train(params_gender,
                    lgb_train_gender,
                    num_boost_round=epoch,
                    valid_sets=lgb_eval_gender,
                    early_stopping_rounds=early_stopping_rounds,
                    )
    print('training done!')
    print('Saving model...')
    # save model to file
    gbm.save_model('tmp/model_gender_dfmin_30.txt')
    print('save model done!')
    return gbm
# %%


def LGBM_age(epoch, early_stopping_rounds):
    params_age = {
        'boosting_type': 'gbdt',
        'objective': 'multiclass',
        "num_class": 10,
        # fine-tuning最重要的三个参数
        'num_leaves': 2**10-1,
        'max_depth': -1,             # 不限制树深度
        'min_data_in_leaf': 1,
        # 更高的accuracy
        # 'max_bin': 2**9-1,
        # 'num_iterations': 50,  # epoch
        'metric': {'multi_logloss', 'multi_error'},
        'learning_rate': 0.01,

        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        # 'bagging_freq': 5,
        'verbose': 1
    }
    print('Start training...')
    # train
    gbm = lgb.train(params_age,
                    lgb_train_age,
                    num_boost_round=epoch,
                    valid_sets=lgb_eval_age,
                    early_stopping_rounds=early_stopping_rounds,
                    )
    print('Saving model...')
    # save model to file
    gbm.save_model('tmp/model_age_dfmin_30.txt')
    print('save model done!')
    return gbm


# %%
# gbm_gender = lgb.Booster(model_file='tmp/model_gender.txt')
# gbm_age = lgb.Booster(model_file='tmp/model_age.txt')
# %%
gbm_gender = LGBM_gender(epoch=2000, early_stopping_rounds=500)
# %%
mail('train gender done!')
gbm_age = LGBM_age(epoch=2000, early_stopping_rounds=500)
mail('train age done!')
# %%


def test():
    print('Start predicting test gender data ...')
    y_pred_gender_probability = gbm_gender.predict(
        X_test, num_iteration=gbm_gender.best_iteration)
    threshold = 0.5
    y_pred_gender = np.where(y_pred_gender_probability > threshold, 1, 0)

    print('Start predicting test age data ...')
    y_pred_age_probability = gbm_age.predict(
        X_test, num_iteration=gbm_age.best_iteration)
    y_pred_age = np.argmax(y_pred_age_probability, axis=1)

    print('start voting...')
    y_pred_gender = y_pred_gender+1
    y_pred_age = y_pred_age+1
    d = {'user_id': test_user_id.tolist(),
         'predicted_age': y_pred_age.tolist(),
         'predicted_gender': y_pred_gender.tolist(),
         }
    ans_df = pd.DataFrame(data=d)
    columns_order = ['user_id', 'predicted_age', 'predicted_gender']
    ans_df[columns_order].to_csv(
        'data/ans/tf_idf.csv', header=True, columns=['user_id', 'predicted_age', 'predicted_gender'], index=False)
    print('Done!!!')


test()
# %%
