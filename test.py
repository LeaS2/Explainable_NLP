from src.feverous.database.feverous_db import FeverousDB
from src.feverous.database.wiki_page import WikiPage
import json
#
db =  FeverousDB("D:\ feverous_wikiv1.db")
#
#page_json = db.get_doc_json("Anarchism")
#wiki_page = WikiPage("Anarchism", page_json)
#
#context_sentence_14 = wiki_page.get_context('sentence_14')

data = []
with open('testdata.jsonl', encoding="utf8") as f:
    for i, line in enumerate(f):
        element = json.loads(line)
        evidence = element.get("evidence",[])
        evidence_list = evidence[0]
        content = evidence_list["content"]
        context = evidence_list["context"]
        check = 0
        for content_ele in content:
            
            if "_cell_" in content_ele:
                check = 1
                
        if check == 0:
            evidence_string = ""
            #for i in len(context):
                #page_json = db.get_doc_json(context[i]) 
                #wiki_page = WikiPage(context[i], page_json)
                #
                #context_temp = wiki_page.get_context(content[i])
                #evidence_string += context_temp
                #
            #element.pop("evidence")
            #element.update({"evidence": evidence_string})
            #íf element.get("label") == 1
                #element.pop("label")
                #element.update({"label": "REFUTES"})
            #elif element.get("label") == 0
                #element.pop("label")
                #element.update({"label": "SUPPORTS"})
            #else
                #element.pop("label")
                #element.update({"label": "NOT ENOUGH INFO"})

            data.append(element.copy())


# 1. alles raus mit "_cell_" in evidence(list)[content] ____done

# next
# labels zu 0=SUPPORTS 1=REFUTES, default=NOT ENOUGH INFO
# Evidence list durchgehen 

# 2. sätze zu strings mit siehe oben
# 3. neue spalte evidence_string 
# 4. 