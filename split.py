import json
import jsonlines

from src.feverous.database.feverous_db import FeverousDB
from src.feverous.database.wiki_page import WikiPage
import random
import numpy as np
from sklearn.model_selection import train_test_split

data = []
with open('Vitaminc/data/feverous/train.jsonl', encoding="utf8") as f:
    for i, line in enumerate(f):
        element = json.loads(line)


        data.append(element.copy())

random.seed(123)
arr = np.array(data)
train, test = train_test_split(arr, test_size=0.2, shuffle=True)
print(len(train), len(test))

with jsonlines.open('FEVEROUS_train.jsonl', mode='w') as writer:
    writer.write_all(train)

with jsonlines.open('FEVEROUS_test.jsonl', mode='w') as writer:
    writer.write_all(test)