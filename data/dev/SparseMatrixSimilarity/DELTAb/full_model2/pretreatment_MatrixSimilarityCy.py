# -*- coding: utf-8 -*-
from gensim import corpora, models, similarities
from collections import defaultdict
import scipy
import os, sys, pandas as pd, numpy as np, time, json, pickle, marshal, csv, re, unidecode, Levenshtein
from operator import itemgetter
import heapq, scipy.sparse, math, random

# ratio de Levenshtein
RATIO = 0.9

al = "abcdefghijklmnopqrstuvwxyz"
ALPHABET = [l for l in al]

# base de lemmatisation francaise
lemma = json.load(open("../../../frLemmaBase_unicode_val_in_keys.json"))
lemma_values = set(lemma.values())

# base de lemmatisation anglaise
lemma_eng = json.load(open("../../../EngLemmaBase_unicode.json"))

# stopwords fr
with open("../../../stopwords_v1.2","rb") as f:
    stopwords_fr = pickle.load(f)

# stopwords eng
with open("../../../english_stopwords_merge_of_nltk_spacy_gensim","r") as f:
    eng_stopwords = json.load(f)

# termes spécifiques SAP
with open("../../../SAPtables","rb") as f:
    SAPtables = pickle.load(f)

# dictionnaire de mot unique
with open("full_dico_unique","r") as u:
    dico_unique = json.load(u).keys()

with open("../../../src/fautes_orthographe/dev/dict_fautes_orthographes_92.json","r") as f:
    correction_ortho = json.load(f)

with open("../../../src/traductions/sap_sterm/monogram/fr_monogram.json","r") as f:
    fr_monogram = json.load(f)

with open("../../../src/traductions/sap_sterm/monogram/eng_monogram.json","r") as f:
    eng_monogram = json.load(f)


# Création du dictionnaire de mot unique à un message
def getUniqueWords(corpus_normalized: list, numbers: list):
    compteur = 0
    inventaire = {}

    # compte le nombre de message solman où apparait chaque token
    for i, texte in enumerate(corpus_normalized):                              
        for token in set(texte):
            if token in inventaire.keys():
                inventaire[token] = {"count": inventaire[token].get("count") + 1 , "orig": numbers[i]}
            else:
                inventaire[token] = {"count": 1, "orig": numbers[i]}                                                       

    # sauvegarde le dictionnaire total du modele en JSON 
    with open("full_dico",'w') as f:      # je sauvegarde le dictionnaire du corpus
        json.dump(inventaire,f)

    # identifie les token qui n'apparaissent que dans un seul message solman
    unique = {}
    for i, val in inventaire.items():                                        
        if val.get('count') == 1:
            unique[i] = val.get('orig')

    # sauvegarde les mots uniques en JSON
    with open("full_dico_unique",'w') as f:     # je sauvegarde le dictionnaire de mot unique du corpus
        json.dump(unique,f)

    # sauvegarde en CSV
    with open("dict_unique.csv", "w") as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in unique.items():
            writer.writerow([key, value])
    
    return unique
    

# décompose et recompose les termes contenant certains type de metacaractere
def transformMeta(token: str):
    global lemma
    global lemma_eng
    global SAPtables

    tmp = [ re.split(r'[\-\_]',x) for x in token.split() ]
    tmp = [ item for sublist in tmp for item in sublist ]
    lemmaRemoved = [ lemma[y] if y in lemma.keys() else y for y in tmp ]
    recompose_without_digit = "".join([ t for t in lemmaRemoved if t not in lemma.values() and not t.isdigit() and not t in SAPtables ])    
    saptable = " ".join([ x for x in lemmaRemoved if x in SAPtables ]) # recupere nom de table si inclus dans le mot (postule qu'il ne peut y avoir qu'un seul nom de table dans un mot composé)
    if saptable:
        return recompose_without_digit, saptable
    else:
        return recompose_without_digit


# LORS DU TRAITEMENT D'UN MESSAGE QUERY
# utilise la distance de Levenshtein sur les clés du dictionnaire de lemmatisation pour potentiellement corriger les fautes d'orthographes de chaque token
# return : type tuple (message corrigé: list, sous_dico_intermediaire: dict)
def checkCorrection(token):
    
    global lemma
    global lemma_eng
    global stopwords_fr
    global eng_stopwords
    global dico_unique
    global RATIO

    # On créé une liste de candidat (distance du candidat > RATIO) pour corriger une potentielle faute d'orthographe
    dis_levenshtein =[]
    for lem in lemma.keys():
        distance = Levenshtein.ratio(token.lower(), lem)
        if distance > RATIO:
            dis_levenshtein.append((lem, distance))
    dis_levenshtein.sort(key=lambda x: x[1], reverse = True)
    
    # si aucune distance > RATIO n'a été trouvé OU que token est un lemme OU que token est unique
    if ( token in lemma.keys() or token in dico_unique or len(dis_levenshtein) == 0 ):
        return token
    else: # Sinon on renvoi la correction ayant la plus courte distance de Levenshtein
        return dis_levenshtein[0] 


# corrige faute d'orthographe par calcul distance de levenshtein, algo itératif sans sauvegarde de liste
def correctionOrthographe(token):
    global lemma
    global lemma_eng

    best_distance = 0.0

    for lem in lemma.values():
        current = Levenshtein.ratio(token, lem)
        if current > best_distance:
            best_distance = current
            save = (lem, best_distance)
    
    if best_distance > RATIO:
        with open("analyse_des_corrections.json","a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow((token, save[0], save[1]))
            f.close()
        return save[0]
    else:
        return token


# SANS SEUIL | recherche la meilleure distance entre toute
# corrige faute d'orthographe par calcul distance de levenshtein, algo itératif sans sauvegarde de liste
def distanceLevenshtein(token):
    global lemma
    global fautes_deja_corrigees
    best_distance = 0.0

    # with open("../../../../data/dev/SparseMatrixSimilarity/full_model2/analyse_des_corrections.json","r") as f:
    #     fautes_deja_corrigees = json.load(f)

    # si token est déjà corrigé, retourne le token
    # if token in fautes_deja_corrigees.keys():
    #     return fautes_deja_corrigees[token].get("corr")

    # pour chaque mot correctement orthographié du dictionnaire de lemmatisation en français (les clés ont été ajouté aux valeurs)
    for lem in lemma.values():
        # je calcule la distance de levenshtein
        currentz = Levenshtein.ratio(token, lem)
        current = round(currentz,5)
        # je sauvegarde la meilleure distance de manière itérative
        if current >= best_distance:
            best_distance = current
            save = (lem, best_distance)
        else:
            continue
    # fautes_deja_corrigees[token] = { "corr": save[0], "lev": save[1] }

    # with open("../../../../data/dev/SparseMatrixSimilarity/full_model2/analyse_des_corrections.json","w") as f:
    #     json.dump(fautes_deja_corrigees,f)
    
    return save
    

# LORS DE GENERATION DU MODELE 
def dictionnaire_intermediaire(corpus_normalized):
    global lemma
    global lemma_eng
    global stopwords_fr
    global eng_stopwords
    global dico_unique
    global SAPtables

    # instanciation des ensembles
    keylemfr = set(lemma.keys())
    vallemfr = set(lemma.values())
    keylemen = set(lemma_eng.keys())
    vallemen = set(lemma_eng.values())
    unique = set(dico_unique)
    sap = set(SAPtables)
    stopwordsfr = set(stopwords_fr)
    stopwordsen = set(eng_stopwords)

    intermediaire = set()
    for message in corpus_normalized:
        mez = set(message)
        for token in mez:
            if (not token in keylemfr
                and not token in vallemfr
                and not token in keylemen
                and not token in vallemen
                and not token in sap
                and not token in stopwordsfr
                and not token in stopwordsen
                and not token in unique):   
                intermediaire.add(token)
            else:
                continue
    
    # caste de set() à dict() en vue de sauvegarde en JSON
    dict_intermediaire = dict.fromkeys(intermediaire,0)

    return dict_intermediaire


def apostropheX92(message: str):
    res = { re.sub(r'[\x92\n\t\r]', ' ', message) }
    res = str(res)
    res = res[2:-2]
    return res


def pasapasLemmatisation(message: list):

    global fr_monogram
    global eng_monogram 
    global correction_ortho 
    global lemma
    global lemma_eng
    global stopwords_fr
    global eng_stopwords
    global SAPtables
    global dico_unique 

    meta = re.compile(r'[-_]')
    start_with_z = re.compile(r'^z.+')
    digit_in_token = re.compile(r'\d')

    message9 = []
    for m in message:

        if m in lemma.keys():
            message9.append(lemma[m])

        elif m in lemma_eng.keys():
            message9.append(lemma_eng[m])

        elif ( meta.search(m) 
            or start_with_z.search(m)
            or digit_in_token.search(m) ):
            message9.append(m)

        elif ( m in fr_monogram.keys() or m in eng_monogram.keys() ):
            message9.append(m)
        
        elif m in correction_ortho.keys():
            correct = correction_ortho[m]['corr']
            if correct in lemma.keys():
                message9.append(lemma[correct])
            elif correct in lemma_eng.keys():
                message9.append(lemma_eng[correct])
            else:
                message9.append(correct)
            message9.append(correct)

    return message9


def pap_normalize(message: str):

    global lemma
    global lemma_eng
    global stopwords_fr
    global SAPtables
    global eng_stopwords
    global dico_unique
    global ALPHABET

    lemma_fr_values = set(lemma.values())
    lemma_eng_values = set(lemma_eng.values())

    # regex: suppression du format apostrophe r'\x92' <=> u'\u0092' (apparait comme un mini rectangle)
    x92 = re.compile(r'[\x92\']')
    if x92.search(message):
        message0 = apostropheX92(message)
    else:
        message0 = message

    # supprime \t\n\r supprime ponctuation + split les mots contenant des metacaractere qui bascule alors dans le "traitement standard"
    ponctu = re.compile(r"[\s\.,:\';°\*%><\<\>=\+\?&~#\$£€\{\}\(\)\[\]\|/\\]") 
    message1 = ponctu.sub(" ", message0)
    
    # regex : definit les mots commençant par un "z"
    start_with_z = re.compile(r'^z.+')

    # regex : définit les mots contenant au moins un chiffre
    digit_in_token = re.compile(r'\d')

    # supprime tous type d'accent (unicode)
    message2 = unidecode.unidecode(message1)

    # regex pour numero de telephone (format français)
    phone_in_token = re.compile(r'\(?(?:^0[1-9]\d{8}$|0[1-9]([\s\.\-\_]\d{2}){4}$)\)?')
    phone_in_string = re.compile(r'(?:(\d{2})?-?(\d{2})[-_\s\.]?)?(\d{2})[-_\s\.]?-?(\d{2})[-_\s\.]?-?(\d{2})[-_\s\.]?(\d{2})\)?')

    # supprime num_telephone du texte avant tokenisation
    message2bis = re.sub(phone_in_string, '', message2)

    # lowercase et tokenise (convertit en liste) OK
    message3 = re.sub(r"[\n\r\t\a<>]", ' ', message2bis).lower() # doublon avec ligne 230 => '\s' s'en occupe déjà

    message3bis = message3

    message4 = message3bis.split(" ")

    # nettoyage
    while '' in message4:
        message4.remove('')

    # enlève les mots composés exclusivement de caractère non alpha-numérique (ex: "--->", "==>", "*%__") OK
    non_alfanum = re.compile(r'^\W+$')

    # supprime les mots contenant meta ["!", "§", "@", "`"]
    bob = re.compile(r'[§!@`]')
    message5 = [ i for i in message4 if not bob.search(i) and not non_alfanum.search(i) ]

    # 2eme traitement des apostrophes ayant pu échapper au 1er traitement 
    apostr = re.compile(r"'")
    message5bis = []
    for m in message5:
        if apostr.search(m):
            un = re.sub(apostr, ' ', m).split()
            deux = [ e for e in un if not e in ALPHABET if not e in stopwords_fr if not e in eng_stopwords]
            if len(deux) == 0:
                pass
            else:
                # print(m, un, deux, len(deux))
                message5bis.append(deux[0])
        else:
            message5bis.append(m)

    meta = re.compile(r'[-_]')
    message6 = [ transformMeta(x) if meta.search(x) else x for x in message5bis ]

    # si transforMeta() a identifié des noms de table SAP, ils sont alors renvoyé en tuples (token, table_sap)
    message7 = []
    for k, token in enumerate(message6):
        if not isinstance(token, tuple):
            message7.append(token)
        else:
            for y in token:
                message7.append(y)

    # suppression des horaires (ex: 4h, 12:50, 15H05)
    horaires = re.compile(r'^\d{1,2}[:hH]\d{0,2}$')
    message7bis = [ z for z in message7 if not horaires.search(z) ]

    # enlève les stopwords
    message8 = [ x for x in message7bis if not x in stopwords_fr if not x in eng_stopwords ]

    message9 = pasapasLemmatisation(message8)

    # pour être sûr, seconde suppression des stopwords 
    message10 = [ t for t in message9 if not t in stopwords_fr if not t in eng_stopwords ]

    # nettoyage des tokens vides
    while '' in message10:
        message10.remove('')

    # ????????????????? pourquoi encore
    message11 = []
    for m in message10:
        message11.append(re.sub(r'\W', '', str(m)))

    # frequence TODO
 
    return message11


# debut compteur temps execution
start = time.time()

SEUIL_FREQUENCE = 12

# cette fonction ne sert à rien ...
def doublons(liste):
    double = True
    while double == True: 
        double = False 
        liste_verif = [] 
        for word in liste:
            try: 
                doublon = liste_verif.index(word) 
                liste.remove(word)  
                double = True 
            except: pass 
            liste_verif.append(word)
    return liste


# chargement du sac de mot : fichier contenant tous les messages solman
with open('../../../src/base_de_donnees/full/BOW_2020_10_07.json', encoding='utf8') as f:
    data = json.load(f)

# structuration du sac de mot
dicti = {}
for things in data:
    num = int(things)
    msg = data[things]['texte'] #+ ' ' + data[things]['corps']  
    u = 0
    while u < len(things):                                          
        dicti[num] = msg
        u += 1

# sauvegarde de la liste des n° de messages solman
numbers = list(dicti.keys())
# sauvegarde de la liste des messages solman
message = dicti.values()


# sauvegarde de la liste "numéros de message" dans le fichier 'list_numbers'
marshal.dump(numbers, open("list_numbers", 'wb'))

# normalisation de chaque message du sac de mot
a = 0
doc = []
for m in message:
    treated = pap_normalize(m)
    if a % 500 == 0:                                                                        # pour monitoring lors de la génération
        with open("monitor"+str(a),'w') as f:                                               #
            json.dump(treated,f)                                                            #
    doc.append(treated)
    a += 1
    print("norm ",a)
    del treated

# sauvegarde du corpus normalisés
with open("docNormalized","w") as f:
    json.dump(doc,f)

# chargement du corpus normalisé (étape qq peu inutile)
with open("docNormalized","r") as f:
    doc = json.load(f)

print("on est bon")
# nb total de document constituant le corpus
counting = len(doc)

# calcul des fréquences de chaque mot dans le corpus
frequency = defaultdict(int)
IF_compteur = 0
for texte in doc:
    doublons(texte)
    for token in texte:
        frequency[token] += (1 * 100)/counting          # calcul de l'indice de frequence
        frequency[token] = round(frequency[token], 3)   # on arrondi l'indice de frequence 
    if IF_compteur % 1000 == 0:
        print("TFIDF ",IF_compteur)
    IF_compteur += 1

# création du dictionnaire de mot unique (la fonction sauvegarde le dictionnaire)
mot_unique = getUniqueWords(corpus_normalized=doc, numbers=numbers)
# sauvegarde les mots uniques en JSON
with open("full_dico_unique.json",'w') as f:     
    json.dump(mot_unique,f)
# sauvegarde en CSV
with open("dict_unique.csv", "w") as csv_file:  
    writer = csv.writer(csv_file)
    for key, value in mot_unique.items():
        writer.writerow([key, value])

# sauvegarde du dictionnaire des frequences
with open("frequence","w") as f:
    json.dump(frequency,f)

# tyxts = [[token for token in texte 
#             if not token in stopwords_fr 
#             if not token in eng_stopwords 
#             if not token in mot_unique.keys()] 
#         for texte in doc]

# dictionario = corpora.Dictionary(tyxts)

# collection_frequencies = dictionario.cfs # occurence token dans corpus
# document_frequencies = dictionario.dfs # nb de document contenant chaque token
# reverse_dictionary = { v: k for k, v in dictionario.token2id.items() }

# global_tokens = {}
# for i, val in reverse_dictionary.items():
#     global_tokens[i] = {"token": val,"occ": collection_frequencies[i],"docs": document_frequencies[i]}

# with open("freq_gensim","w") as f:
#     json.dump(global_tokens,f)

# traitement des doc normalisés : suppression des mots < à une certaine fréquence. Suppression des mots uniques. 3ème suppression des stopwords (les 2 premières suppressions s'effectuent dans normalize())
texts = [[token for token in texte 
            if frequency[token] < SEUIL_FREQUENCE 
            if not token in mot_unique.keys() 
            if not token in stopwords_fr 
            if not token in eng_stopwords
            if not token in mot_unique.keys()] 
        for texte in doc]

# Crée un dictionnaire GENSIM (mapping de chaque mot avec un id)
dictionary = corpora.Dictionary(texts)
print("len du dictionnaire ", len(dictionary))
print("len mot unique au corpus ", len(mot_unique))
# sauvegarde dans fichier 'specifiques.dict'
dictionary.save('specifiques.dict')     



# sauvegarde dictionnaire gensim en format texte
dictionary.save_as_text('dictionnaire_format_texte/dictionnaire_du_corpus.txt')
 
# # création et sauvegarde du dictionnaire contenant les termes absents des lemmes, des stopwords, du dico_unique et sans candidat à la correction d'une potentielle faute d'orthographe
# dico_intermediaire = dictionnaire_intermediaire(texts)
# # j'enregistre en JSON
# with open('dictionnaire_intermediaire.json', 'w') as f:  
#     json.dump(dico_intermediaire,f)
# # j'enregistre en CSV
# with open('dictionnaire_intermediaire.csv', 'w') as csv_file:  
#     writer = csv.writer(csv_file)
#     for key, value in dico_intermediaire.items():
#         writer.writerow([key])

# creation du corpus : objet gensim contenant l'id de chaque mot et sa fréquence d'apparition dans chaque corps de message
corpus = [dictionary.doc2bow(text) for text in texts]

# sérialisation et sauvegarde dans le fichier 'specifiques.mm'
corpora.MmCorpus.serialize('specifiques.mm', corpus)

# SMARTIRS acronymes : consulter https://radimrehurek.com/gensim/models/tfidfmodel.html
# ECRIRE L'ACRONYME SOUHAITE DANS LE FICHIER "parametresSMARTIRS" du dossier courant
param = open("parametresSMARTIRS","r").read()

# Gréation duu modèle TFIDF 
tfidf_classic = models.TfidfModel(corpus=corpus, normalize=True)                            # VERSION INITIALE
tfidf_custom = models.TfidfModel(corpus=corpus, dictionary=dictionary, smartirs=param)      # VERSION CUSTOM

# sauvegarde du modèle
tfidf_classic.save("classic_model/tfidf_classic.model")
tfidf_custom.save("custom_model/{}/tfidf_custom.model".format(param))

# Génère l'indice matricielle du modèle
index_classic = similarities.SparseMatrixSimilarity(tfidf_classic[corpus], num_features=len(dictionary))
index_custom = similarities.SparseMatrixSimilarity(tfidf_custom[corpus], num_features=len(dictionary))

# # je créé le repertoire du modele custom s'il n'existe pas
# if pathlib.Path.exists("./custom_model/{}".format(MY_CUSTOM)):
#     pass
# else:
#     os.makedirs("./custom_model/{}".format(MY_CUSTOM))
    
# sauvegarde la matrice 
index_classic.save('classic_model/sparse.index', separately=["index"])
index_custom.save('custom_model/{}/sparse.index'.format(param), separately=["index"])

# calcul et affichage des temps d'exécution
end = time.time()
hours, rem = divmod(end-start, 3600)
minutes, seconds = divmod(rem, 60)
print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))


lsi_model = models.LsiModel(tfidf_classic, id2word=dictionary, num_topics=300)
corpus_lsi = lsi_model[tfidf_classic]

lsi_model.print_topics()