from src.feverous.database.feverous_db import FeverousDB
from src.feverous.utils.wiki_page import WikiPage
import json
#
#db =  FeverousDB("path_to_the_wiki")
#
#page_json = db.get_doc_json("Anarchism")
#wiki_page = WikiPage("Anarchism", page_json)
#
#context_sentence_14 = wiki_page.get_context('sentence_14')

#set = jsonlines.open("testdata.jsonl",)
import json

data = []
with open('feverous_train_challenges.jsonl', encoding="utf8") as f:
    for i, line in enumerate(f):
        element = json.loads(line)
        evidence = element.get("evidence",[])
        content = evidence[0]
        check = 0
        for content_ele in content["content"]:
            
            if "_cell_" in content_ele:
                check = 1
                
        if check == 0:
            data.append(element.copy())
print(len(data))

# 1. alles raus mit "_cell_" in evidence(list)[content] ____done
# 2. sätze zu strings mit siehe oben
# 3. neue spalte evidence_string 
# 4. 