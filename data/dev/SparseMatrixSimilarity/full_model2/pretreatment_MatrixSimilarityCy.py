# -*- coding: utf-8 -*-
from gensim import corpora, models, similarities
from collections import defaultdict
import scipy
import os, sys, pandas as pd, numpy as np, time, json, pickle, marshal, csv, re, unidecode, Levenshtein
from operator import itemgetter
import heapq, scipy.sparse, math, random
from classes.normalisationdatabase import NormalisationDataBase

# ratio de Levenshtein
RATIO = 0.92

# pourcentage du corpus dans lequel apparait un token et au dessus duquel le token est considéré comme trop fréquent, et évacuer 
SEUIL_FREQUENCE = 12.0

al = "abcdefghijklmnopqrstuvwxyz"
ALPHABET = [l for l in al]

with open("/smartsolman/data/src/fautes_orthographe/recette/dict_fautes_orthographes_92.json","r") as f:
    CORRECTION_ORTHOGRAPHE = json.load(f)

db  = NormalisationDataBase()

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
    # global lemma
    # global lemma_eng
    # global SAPtables

    tmp = [ re.split(r'[\-\_]',x) for x in token.split() ] # produit une liste de list
    tmp = [ item for sublist in tmp for item in sublist ] # reconverti en liste simple
    
    # lemmaRemoved = [ lemma[y] if y in lemma.keys() else y for y in tmp ]
    
    lemmaRemoved = []
    for element in tmp:
        q = db.frLemmatisation(element)
        if q:
            lemmaRemoved.append(q)
        else:
            lemmaRemoved.append(element)

    del element, q

    # recompose_without_digit = "".join([ t for t in lemmaRemoved if t not in lemma.values() and not t.isdigit() and not t in SAPtables ])    

    recompose = []
    for element in lemmaRemoved:
        q = db.isSAPterm(element)
        p = db.frLemmatisation(element)
        if (not q
            and not p
            and not element.isdigit() ):
            recompose.append(element)
        else:
            continue
    
    del q, p

    recompose_without_digit = "".join(recompose)

    saptable = " ".join([ x for x in lemmaRemoved if db.isSAPterm(x) ]) # recupere nom de table si inclus dans le mot (postule qu'il ne peut y avoir qu'un seul nom de table dans un mot composé)
    
    if saptable:
        return recompose_without_digit, saptable
    else:
        return recompose_without_digit



def apostropheX92(message: str):
    res = { re.sub(r'[\x92\n\t\r]', ' ', message) }
    res = str(res)
    res = res[2:-2]
    return res


def pap_normalize(message: str):

    # global lemma
    # global lemma_eng
    # global stopwords_fr
    # global SAPtables
    # global eng_stopwords
    # global dico_unique
    global ALPHABET
    global CORRECTION_ORTHOGRAPHE

    # lemma_fr_values = set(lemma.values())
    # lemma_eng_values = set(lemma_eng.values())

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
    negligeable = re.compile(r'[§!@`]')
    message5 = [ i for i in message4 if not negligeable.search(i) and not non_alfanum.search(i) ]

    # 2eme traitement des apostrophes ayant pu échapper au 1er traitement 
    apostr = re.compile(r"'")
    message5bis = []
    for m in message5:
        if apostr.search(m):
            un = re.sub(apostr, ' ', m).split()
            deux = [ e for e in un if not e in ALPHABET if not db.isFrenchStopword(e) if not db.isEnglishStopword(e) ]
            if len(deux) == 0:
                pass
            else:
                # print(m, un, deux, len(deux))
                message5bis.append(deux[0])
        else:
            message5bis.append(m)

    meta = re.compile(r'[-_]')
    message6 = [ transformMeta(x) if meta.search(x) else x for x in message5bis ]

    # suite à 'transformMeta', des caratères peuvent être renvoyés comme termes (term) ou tuple_de_terme (term1,term2)
    # ici au besoin, nous re-splitons les tuples_de_terme en terme
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
    message8 = [ x for x in message7bis if not db.isFrenchStopword(x) if not db.isEnglishStopword(x) ]

    # lemmatisation, sauf si token contient un metacaractere recomposé ou commence par 'z'
    message9 = []
    for m in message8:

        q = db.frLemmatisation(m)
        p = db.engLemmatisation(m)

        if ( meta.search(m) or start_with_z.search(m) ):
            message9.append(m)
        elif q:
            message9.append(q)
        elif p:
            message9.append(p)
        elif m in CORRECTION_ORTHOGRAPHE.keys():
            message9.append(CORRECTION_ORTHOGRAPHE[m].get('corr'))
        else:
            message9.append(m)


    # pour être sûr, seconde suppression des stopwords 
    message10 = [ t for t in message9 if not db.isFrenchStopword(t) if not db.isEnglishStopword(t) ]

    # nettoyage des tokens vides
    while '' in message10:
        message10.remove('')

    # ????????????????? pourquoi encore
    message11 = []
    for m in message10:
        message11.append(re.sub(r'\W', '', str(m)))

    return message11


# debut compteur temps execution
start = time.time()

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
with open('/data/src/base_de_donnees/full/BOW_2020_10_17.json', encoding='utf8') as f:
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
'''
# normalisation de chaque message du sac de mot
a = 0
doc = []
for m in message:
    treated = pap_normalize(m)
    if a % 1000 == 0:                                                                        # pour monitoring lors de la génération
        with open("monitor"+str(a),'w') as f:                                               #
            json.dump(treated,f)                                                            #
    doc.append(treated)
    a += 1
    print("norm ",a)
    del treated

# sauvegarde du corpus normalisés
with open("docNormalized","w") as f:
    json.dump(doc,f)
'''
# chargement du corpus normalisé (étape qq peu inutile)
with open("docNormalized","r") as f:
    doc = json.load(f)

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
    # if IF_compteur % 1000 == 0:
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

# traitement des doc normalisés : suppression des mots < à une certaine fréquence. Suppression des mots uniques. 3ème suppression des stopwords (les 2 premières suppressions s'effectuent dans normalize())
texts = [[token for token in texte if frequency[token] < SEUIL_FREQUENCE if not token in mot_unique.keys() if not db.isFrenchStopword(token) if not db.isEnglishStopword(token) ] for texte in doc]

# Crée un dictionnaire GENSIM (mapping de chaque mot avec un id)
dictionary = corpora.Dictionary(texts)

collection_frequencies = dictionary.cfs
document_frequencies = dictionary.dfs
reverse_dictionary = { v: k for k, v in dictionary.token2id.items() }
global_tokens = {}
for i, val in reverse_dictionary.items():
    global_tokens[i] = {"token": val,"freq": collection_frequencies[i],"docs": document_frequencies[i]}

with open("frequence_by_gensim","w") as f:
    json.dump(global_tokens,f)

print("len du dictionnaire ", len(dictionary))
print("nb de mot unique à 1 message ", len(mot_unique))
# sauvegarde dans fichier 'specifiques.dict'
dictionary.save('specifiques.dict')     

# # sauvegarde dictionnaire gensim en format texte
# dictionary.save_as_text('dictionnaire_format_texte/dictionnaire_du_corpus.txt')
 

# creation du corpus : objet gensim contenant l'id de chaque mot et sa fréquence d'apparition dans chaque corps de message
corpus = [dictionary.doc2bow(text) for text in texts]

# sérialisation et sauvegarde dans le fichier 'specifiques.mm'
corpora.MmCorpus.serialize('specifiques.mm', corpus)

# SMARTIRS acronymes : consulter https://radimrehurek.com/gensim/models/tfidfmodel.html
# ECRIRE L'ACRONYME SOUHAITE DANS LE FICHIER "parametresSMARTIRS" du dossier courant
param = open("parametresSMARTIRS","r").read()

# Gréation duu modèle TFIDF 
tfidf_classic = models.TfidfModel(corpus=corpus, normalize=True)                                             # VERSION INITIALE
tfidf_custom = models.TfidfModel(corpus=corpus, dictionary=dictionary, smartirs=param)      # VERSION CUSTOM

# sauvegarde du modèle
tfidf_classic.save("tfidf_classic.model")
tfidf_custom.save("tfidf_custom.model")

# Génère l'indice matricielle du modèle
index_classic = similarities.SparseMatrixSimilarity(tfidf_classic[corpus], num_features=len(dictionary))
index_custom = similarities.SparseMatrixSimilarity(tfidf_custom[corpus], num_features=len(dictionary))

# # je créé le repertoire du modele custom s'il n'existe pas
# if pathlib.Path.exists("./custom_model/{}".format(MY_CUSTOM)):
#     pass
# else:
#     os.makedirs("./custom_model/{}".format(MY_CUSTOM))
    
# sauvegarde la matrice 
index_classic.save('classic_model/full_sparse.index', separately=["index"])
index_custom.save('custom_model/{}/full_sparse.index'.format(param), separately=["index"])

# calcul et affichage des temps d'exécution
end = time.time()
hours, rem = divmod(end-start, 3600)
minutes, seconds = divmod(rem, 60)
print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
db.close()
