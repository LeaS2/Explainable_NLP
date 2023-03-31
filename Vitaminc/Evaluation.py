import jsonlines
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
with jsonlines.open('evaluationFile_last.json') as reader:
    for i, obj in enumerate(reader):
        evaluation = obj

df = pd.DataFrame(evaluation)
diff = df.diff(axis=1)
diff = diff.drop(["label_ids"], axis=1)
diff = diff.rename(columns={"prediction": "difference"})

df = pd.concat([df, diff], axis=1)
claim_data = []
evidence_data = []
with open("./data/feverous/FEVEROUS_test.jsonl", encoding='utf8') as f:
    for line in f:
        doc = json.loads(line)
        claim = [doc['claim']]
        claim_data.append(claim)
        evidence = [doc["evidence"]]
        evidence_data.append(evidence)
claim_df = pd.DataFrame(claim_data)
claim_df = claim_df.rename(columns={0: "claim"})
final_df = pd.concat([df, claim_df], axis=1)
evidence_df = pd.DataFrame(evidence_data)
evidence_df = evidence_df.rename(columns={0: "evidence"})
final_df = pd.concat([final_df, evidence_df], axis=1)
###
support = final_df.loc[final_df['label_ids'] == 0]
refutes = final_df.loc[final_df['label_ids'] == 1]
not_e_info = final_df.loc[final_df['label_ids'] == 2]

support_right = support.loc[support["difference"] == 0]
support_wrong = support.loc[support["difference"] != 0]
print("support right-wrong")
print(len(support_right))
print(len(support_wrong))
print("\n")
refutes_right = refutes.loc[refutes["difference"] == 0]
refutes_wrong = refutes.loc[refutes["difference"] != 0]
print("refutes right-wrong")
print(len(refutes_right))
print(len(refutes_wrong))
print("\n")
not_e_info_right = not_e_info.loc[not_e_info["difference"] == 0]
not_e_info_wrong = not_e_info.loc[not_e_info["difference"] != 0]
print("no info right-wrong")
print(len(not_e_info_wrong))
print(len(not_e_info_right))
print("\n")


print(len(support))
print(len(refutes))
print(len(not_e_info))
###
right_predict = final_df.loc[final_df['difference'] == 0]
wrong_predict = final_df.loc[final_df['difference'] != 0]

#right_predict.to_json("right_last.json", orient='records', lines=True)
#wrong_predict.to_json("wrong_last.json", orient='records', lines=True)

len_df = len(final_df)
len_all = []
for i in range(0,3):
    pred_mask = final_df["prediction"] == i
    prediction_i = final_df[pred_mask]
    length = len(prediction_i)
    len_all.append(length)


procentual_all_predict = np.array(len_all)/len_df
print(procentual_all_predict)

full_len_right = len(right_predict)
len_right = []
for i in range(0,3):
    pred_mask = right_predict["prediction"] == i
    prediction_i = right_predict[pred_mask]
    length = len(prediction_i)
    len_right.append(length)


full_len_wrong = len(wrong_predict)
len_wrong = []
for i in range(0,3):
    pred_mask = wrong_predict["prediction"] == i
    prediction_i = wrong_predict[pred_mask]
    length = len(prediction_i)
    len_wrong.append(length)
procentual_wrong_predict = np.array(len_wrong)/full_len_wrong
procentual_right_predict = np.array(len_right)/full_len_right
print(full_len_right, "length right predict")
print(procentual_right_predict)
print(full_len_wrong, "length wrong predict")
print(procentual_wrong_predict)
#print(len_df, "length whole data")
print()

mean_string_right = right_predict["evidence"].str.len().mean()
mean_string_wrong = wrong_predict["evidence"].str.len().mean()
mean_string_all = final_df["evidence"].str.len().mean()

claims_right = right_predict["claim"]
#
#print(mean_string_all, "evidence mean all")
#print(mean_string_right, "evidence mean right")
#print(mean_string_wrong, "evidence mean wrong")
#

#durchschnitt länge
#random claim maybe? oder nur lange/nur kurze
#wrong_predict.to_json(r"wrong_predict.json", orient="records")
#right_predict.to_json(r"right_predict.json", orient="records")


#f =  open("results/feverous_real_data/checkpoint-50000/trainer_state.json")
#trainer_state = json.load(f)
#log_history = trainer_state["log_history"]
#log_df = pd.DataFrame(log_history)
#x = log_df["loss"]
#y = log_df["step"]
#
#plt.style.use('ggplot')
#
#fig, ax = plt.subplots()
#ax.plot(y,x, linewidth=1.0)
#ax.set_ylabel("Loss")
#ax.set_xlabel("Steps")
#ax.set_title("Loss while training FEVEROUS model")
#plt.show()