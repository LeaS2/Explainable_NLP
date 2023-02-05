#! /bin/bash

set -ex

python scripts/fact_verification.py \
  --model_name_or_path tals/albert-base-vitaminc-fever \
  --tasks_names feverous \
  --data_dir data \
  --do_test \
  --max_seq_length 256 \
  --per_device_train_batch_size 8 \
  --per_device_eval_batch_size 128 \
  --learning_rate 2e-5 \
  --max_steps 50000 \
  --save_step 10000 \
  --overwrite_cache \
  --output_dir results/feverous_2 \
  --eval_all_checkpoints \
  #--test_on_best_ckpt \
  #--do_train
  "$@"

  #--fp16 \
  #--test_tasks vitc_real vitc_synthetic \
  #--do_predict \
  
  #--model_name_or_path albert-base-v2 \
  #--do_eval \

