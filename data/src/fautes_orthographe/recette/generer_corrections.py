import json, Levenshtein, re, pickle, sys, multiprocessing, functools, time, csv
sys.path.append("../../../../app/dev/full_model/modules")

RATIO = 0.9

lemma = json.load(open("../../../frLemmaBase_unicode_val_in_keys.json"))
lemma_eng = json.load(open("../../../EngLemmaBase_unicode.json"))

with open("../../../SAPtables","rb") as f:
    SAPtables = pickle.load(f)

with open("../../../dev/SparseMatrixSimilarity/full_model2/docNormalized","r") as f:
    doc = json.load(f)

with open("../../traductions/sap_sterm/monogram/fr_monogram.json", "r") as f:
    fr_monogram = json.load(f).keys()

with open("../../traductions/sap_sterm/monogram/eng_monogram.json", "r") as f:
    eng_monogram = json.load(f).keys()


# définition des ensembles de comparaison
keylemfr = set(lemma.keys())
vallemfr = set(lemma.values())
keylemen = set(lemma_eng.keys())
vallemnen = set(lemma_eng.values())
sap = set(SAPtables)

with open("dict_fautes_orthographes.json","r") as f:
    correction = json.load(f)

# nb de token dans coprus
nb_token = sum([ len(x) for x in doc ])
print("nb_token", nb_token)

# FONCTION  : correction en français par calcul de la distance de Levenshtein 
#             sur les clés du dictionnaire de lemmatisation français
# PARAM     : string
# RETURN    : tuple(string, string, float)    
def multiLevenshtein(token):
    global RATIO
    global keylemfr
    global vallemfr
    global keylemen
    global vallemnen
    global sap
    global fr_monogram
    global eng_monogram
    global correction

    # regex pour si token contient un chiffre
    dig = re.compile(r'\d')
    # regex pour si token contient un "-" ou "_"
    meta = re.compile(r'[-_]')
    # regex pour mot commençant par 'z'
    z = re.compile(r'^z.+')

    if token in correction.keys():
        save = (token, 0.0, 0.0)
        return save


    if ( token in keylemfr
        or token in vallemfr
        or token in keylemen
        or token in vallemnen
        or token in sap
        or token.isdigit()
        or z.search(token) 
        or dig.search(token)
        or meta.search(token) 
        or token in fr_monogram
        or token in eng_monogram):

        save = (token, token, 0.0)

        return save

    best_distance = 0.0
    for lem in keylemfr:
        currentz = Levenshtein.ratio(token, lem)
        current = round(currentz,5)
        # sauvegarde de la meilleure distance (itératif)
        if current >= best_distance:
            best_distance = current
            save = (token, lem, best_distance)
        else:
            continue

    return save

# nombre de processeurs utilisé
CORES = 30

d = time.time()
c = 0

for texte in doc:
    pool = multiprocessing.Pool(CORES)
    message = pool.map(multiLevenshtein,(tok for tok in set(texte)))
    pool.close()
    pool.join()
    for token in message:
        if token[2] <= RATIO :
            continue
        elif token[0] in correction.keys():
            continue
        else:
            correction[token[0]] = {"corr": token[1], "lev": token[2] }
    print(c)
    c += 1
    
f = time.time()
print("multiproc", len(correction), f-d)

# sauvegarde en JSON
with open('dict_fautes_orthographes.json', 'w') as f:  
    json.dump(correction,f)

# sauvegarde en CSV
with open('dict_fautes_orthographes.csv', 'w') as csv_file:  
    writer = csv.writer(csv_file)
    for key, value in correction.items():
        writer.writerow([key, value.get('corr'), value.get('lev') ])
