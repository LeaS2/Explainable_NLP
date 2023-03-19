#! /bin/bash

set -ex
export PYTHONPATH="${PYTHONPATH}:${PWD}/Explainable_NLP/"
pip install -r requirements.txt
python scripts/fact_verification.py \
  --model_name_or_path tals/albert-base-vitaminc-fever \
  --tasks_names feverous \
  --data_dir data \
  --max_seq_length 256 \
  --per_device_train_batch_size 8 \
  --per_device_eval_batch_size 128 \
  --learning_rate 2e-5 \
  --max_steps 20000 \
  --save_step 4000 \
  --overwrite_cache \
  --do_test \
  --test_on_best_ckpt\
  --output_dir results/feverous_less_steps \
  --eval_all_checkpoints \
  --do_train\
  --do_eval\
  "$@"
#--do_train
  #--fp16 \
  #--test_tasks vitc_real vitc_synthetic \
  #--do_predict \
  
  #--model_name_or_path albert-base-v2 \
  #--do_eval \

