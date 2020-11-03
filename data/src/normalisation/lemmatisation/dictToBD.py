import json, sys, sqlite3, time, pickle, re

al = "abcdefghijklmnopqrstuvwxyz"
ALPHABET = [l for l in al]

lemma = json.load(open("frLemmaBase_unicode_val_in_keys.json"))
lemma_eng = json.load(open("EngLemmaBase_unicode.json"))
with open("../sap/SAPtables","rb") as f:
    SAPtables = pickle.load(f)

# stopwords fr
with open("../stopwords/stopwords_v1.4","rb") as f:
    stopwords_fr = pickle.load(f)

# stopwords eng
with open("../stopwords/english_stopwords_merge_of_nltk_spacy_gensim","r") as f:
    eng_stopwords = json.load(f)

with open("../../../dev/SparseMatrixSimilarity/full_model2/full_dico_unique","r") as u:
    dico_unique = json.load(u)

conn = sqlite3.connect("../../lemma.db")

c = conn.cursor()

c.executemany("INSERT INTO mots_uniques VALUES(?,?)", dico_unique.items())
conn.commit()
# zou = 0
# for item in stopwords_fr:
#     c.execute("INSERT INTO stopwords_fr VALUES (?)", (item,))
#     conn.commit()
#     if zou % 1000 == 0:
#         print(zou)
#     zou += 1

conn.close()



# t = 0
# d = time.time()
# for row in c.execute("SELECT * FROM fr"):
#     t += 1
# f = time.time()
# conn.close()
# print("BD", f-d)
# t = 0
# d = time.time()
# for a, b in lemma.items():
#     t += 1
# f = time.time()
# print("Dict", f-d)