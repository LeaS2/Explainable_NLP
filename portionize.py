import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def counter(data):
    support = 0
    refutes = 0
    no_info = 0

    with open(data, encoding="utf8") as f:
        for i, line in enumerate(f):
            element = json.loads(line)
            if element["label"] == "SUPPORTS":
                support += 1
            elif element["label"] == "REFUTES":
                refutes += 1
            else:
                no_info += 1

    return [support, refutes, no_info]


train = counter("FEVEROUS_train.jsonl")
test = counter("FEVEROUS_test.jsonl")

fig, ax = plt.subplots()

ax.axis("off")
ax.axis("tight")

df = pd.DataFrame([train, test], columns=["Supports", "Refutes", "Not Enough Info"])
table = ax.table(cellText=df.values, colLabels=df.columns, rowLabels=["Train-Split", "Test-Split"], loc='center')

fig.tight_layout()
plt.show()
