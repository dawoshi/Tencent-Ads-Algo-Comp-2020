# python Transformer_multi_input.py --load_from_npy --epoch 3 --batch_size 256 --num_transformer 3 --head_transformer 4 --num_lstm 3 --not_train_embedding --examples 300000 > tmp/log_1.txt 2>&1
# sleep 60
# python Transformer_multi_input.py --load_from_npy --epoch 3 --batch_size 256 --num_transformer 6 --head_transformer 4 --num_lstm 3 --not_train_embedding --examples 300000 > tmp/log_2.txt 2>&1
# sleep 60
# python Transformer_multi_input.py --load_from_npy --epoch 3 --batch_size 256 --num_transformer 9 --head_transformer 4 --num_lstm 3 --not_train_embedding --examples 300000 > tmp/log_3.txt 2>&1
# sleep 60
# python Transformer_multi_input.py --load_from_npy --epoch 3 --batch_size 256 --num_transformer 12 --head_transformer 4 --num_lstm 3 --not_train_embedding --examples 300000 > tmp/log_4.txt 2>&1
# sleep 60
python Transformer_multi_input.py --load_from_npy --epoch 3 --batch_size 256 --num_transformer 1 --head_transformer 4 --num_lstm 6 --not_train_embedding --examples 100000 > tmp/log_5.txt 2>&1
sleep 60
python Transformer_multi_input.py --load_from_npy --epoch 3 --batch_size 256 --num_transformer 1 --head_transformer 4 --num_lstm 9 --not_train_embedding --examples 100000 > tmp/log_6.txt 2>&1
sleep 60
# python Transformer_multi_input.py --load_from_npy --epoch 3 --batch_size 256 --num_transformer 1 --head_transformer 4 --num_lstm 12 --not_train_embedding --examples 300000 > tmp/log_7.txt 2>&1
# sleep 60
python Transformer_multi_input.py --load_from_npy --epoch 3 --batch_size 256 --num_transformer 1 --head_transformer 4 --num_lstm 3 --examples 100000 > tmp/log_8.txt 2>&1
sleep 60
# python Transformer_multi_input.py --load_from_npy --epoch 3 --batch_size 256 --num_transformer 12 --head_transformer 4 --num_lstm 3 --examples 300000 > tmp/log_9.txt 2>&1
# sleep 60
# python Transformer_multi_input.py --load_from_npy --epoch 3 --batch_size 256 --num_transformer 1 --head_transformer 4 --num_lstm 12 --examples 300000 > tmp/log_10.txt 2>&1
