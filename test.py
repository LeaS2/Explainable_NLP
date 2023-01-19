import json
import jsonlines

from src.feverous.database.feverous_db import FeverousDB
from src.feverous.database.wiki_page import WikiPage

db = FeverousDB("feverous_wikiv1.db")

page_json = db.get_doc_json("Anarchism")

wiki_page = WikiPage("Anarchism", page_json)

data = []
with open('feverous_dev_challenges.jsonl', encoding="utf8") as f:
    for i, line in enumerate(f):
        if i == 0:
            continue
        element = json.loads(line)
        evidence = element.get("evidence", [])
        evidence_list = evidence[0]
        content = evidence_list["content"]
        context = evidence_list["context"]
        check = 0
        for content_ele in content:

            if "_cell_" in content_ele:
                check = 1
            elif "_item_" in content_ele:
                check = 1
            elif "_table_" in content_ele:
                check = 1

        if check == 0:
            evidence_string = ""

            for j, cont in enumerate(context):
                title_str = context[cont][0].removesuffix("_title")
                page_json = db.get_doc_json(title_str)
                wiki_page = WikiPage(title_str, page_json)
                sentence_idx = int(cont[-1])

                curr_sentence = wiki_page.get_sentences()[sentence_idx]

                evidence_string += curr_sentence.__str__() + " "
            element.pop("annotator_operations")
            element.pop("challenge")
            element.pop("evidence")
            element.update({"evidence": evidence_string})
            if element.get("label") == 1:
                element.pop("label")
                element.update({"label": "REFUTES"})
            elif element.get("label") == 0:
                element.pop("label")
                element.update({"label": "SUPPORTS"})
            else:
                element.pop("label")
                element.update({"label": "NOT ENOUGH INFO"})

            data.append(element.copy())
with jsonlines.open('new_dev_FEVEROUS.jsonl', mode='w') as writer:
    writer.write_all(data)

# 1. alles raus mit "_cell_" in evidence(list)[content] ____done

# next
# labels zu 0=SUPPORTS 1=REFUTES, default=NOT ENOUGH INFO
# Evidence list durchgehen 

# 2. sätze zu strings mit siehe oben
# 3. neue spalte evidence_string 
# 4.
