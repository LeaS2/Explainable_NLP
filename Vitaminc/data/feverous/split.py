import numpy as np
import jsonlines
import json
import random

small_train = {}
with jsonlines.open('long_train.jsonl') as reader:
    with jsonlines.open('small_train.jsonl', mode='w') as writer:
        randomize = random.sample(range(29960), k=1000)
        for i, obj in enumerate(reader):
            if i in randomize:
                writer.write(obj)
        print(i)

    