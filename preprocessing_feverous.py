import json
import jsonlines

from src.feverous.database.feverous_db import FeverousDB
from src.feverous.database.wiki_page import WikiPage

db = FeverousDB("../feverous_wikiv1.db")

# page_json = db.get_doc_json("Anarchism")

# wiki_page = WikiPage("Anarchism", page_json)
from datasets import load_dataset

dataset = load_dataset("fever/feverous", split="train")
for i, elem in enumerate(dataset):
    evidence = elem.get("evidence", [])
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
    # test thingy
    for j, cont in enumerate(context):
        evidence_string = ""
        title_str = cont[0].removesuffix("_title")
        page_json = db.get_doc_json(title_str)
        wiki_page = WikiPage(title_str, page_json)
        sentence_idx = int(content[j][-1])
        if len(wiki_page.get_sentences()) > sentence_idx:
            curr_sentence = wiki_page.get_sentences()[sentence_idx]

            evidence_string += curr_sentence.__str__() + " "
        else:
            print(elem)
    '''if check == 0:
            evidence_string = ""

            for j, cont in enumerate(context):
                title_str = cont[0].removesuffix("_title")
                page_json = db.get_doc_json(title_str)
                wiki_page = WikiPage(title_str, page_json)
                sentence_idx = int(content[j][-1])

                curr_sentence = wiki_page.get_sentences()[sentence_idx]

                evidence_string += curr_sentence.__str__() + " " '''
    elem.pop("annotator_operations")
    elem.pop("challenge")
    elem.pop("evidence")
    elem.pop("expected_challenge")
    elem.update({"evidence": evidence_string})



# with jsonlines.open('new_FEVEROUS.jsonl', mode='w') as writer:
#  writer.write_all(data)

# 1. alles raus mit "_cell_" in evidence(list)[content] ____done

# next
# labels zu 0=SUPPORTS 1=REFUTES, default=NOT ENOUGH INFO
# Evidence list durchgehen 

# 2. sätze zu strings mit siehe oben
# 3. neue spalte evidence_string 
# 4.
