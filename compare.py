import json
import pandas as pd

cols = ['claim', 'label']
fev_data = []
vitc_data = []
with open("fev_test.jsonl", encoding='utf8') as f:
    for line in f:
        doc = json.loads(line)
        lst = [doc['claim'], doc['label']]
        fev_data.append(lst)

df_fev = pd.DataFrame(data=fev_data, columns=cols)

with open("vitc_test.jsonl", encoding='utf8') as f:
    for line in f:
        doc = json.loads(line)
        lst = [doc['claim'], doc['label']]
        vitc_data.append(lst)

df_vitc = pd.DataFrame(data=vitc_data, columns=cols)

count = 0
for ind in df_fev.index:
    fev_claim = df_fev['claim'][ind]
    #for idx in df_vitc.index:
    #    vitc_claim = df_vitc['claim'][idx]
    #    if vitc_claim in fev_claim:
    #        print("hi")
    x = df_vitc['claim'].str.contains(fev_claim)
    if True in x.tolist():
        count += 1
print(count)

