import json, pickle, marshal, time, asyncio


with open("../../../stopwords_v1.2","rb") as f:
    stopwords_fr = pickle.load(f)

with open("nomfamilleSolman.json","r") as f:
    nfamille = set(json.load(f).keys())

print(len(stopwords_fr))

new = stopwords_fr | nfamille

print(len(new), len(new) - len(stopwords_fr))

with open("stopwords_v1.4","wb") as f:
    pickle.dump(new, f)

f = [ a for a in range(100) ]
print(f[0:11])

