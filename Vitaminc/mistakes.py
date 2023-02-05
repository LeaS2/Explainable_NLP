import jsonlines
import json
import numpy as np
import pandas as pd
with jsonlines.open('evaluationFile_1.json') as reader:
    for i, obj in enumerate(reader):
        evaluation = obj

df = pd.DataFrame(evaluation)
diff = df.diff(axis=1)
diff = diff.drop(["label_ids"], axis=1)
diff = diff.rename(columns={"prediction": "difference"})

df = pd.concat([df, diff], axis=1)
test_data = []

with open("./data/feverous/test.jsonl", encoding='utf8') as f:
    for line in f:
        doc = json.loads(line)
        lst = [doc['claim']]
        test_data.append(lst)
test_df = pd.DataFrame(test_data)
test_df = test_df.rename(columns={0: "claim"})
final_df = pd.concat([df, test_df], axis=1)

right_predict = final_df.loc[final_df['difference'] == 0]
wrong_predict = final_df.loc[final_df['difference'] != 0]

wrong_predict.to_json(r"wrong_predict.json", orient="records")
right_predict.to_json(r"right_predict.json", orient="records")