# -*- coding: utf-8 -*-
from gensim import corpora, models, similarities
from pprint import pprint
from collections import defaultdict
from gensim.similarities import Similarity
import json, string, gensim, time, sys, pickle, marshal, csv, codecs, re, gc, unidecode, numpy as np
import scipy, pathlib
# ajout du chemin des modules à la variable d'environnement PYTHON
sys.path.append('../../../../app/dev/full_model/modules')
import normalisation

# debut compteur temps execution
start = time.time()

SEUIL_FREQUENCE = 12

# chargement fichiers requis pour traitement de texte
lemma = json.load(open("../../../frLemmaBase_unicode_val_in_keys.json"))
with open("../../../stopwords_v1.2","rb")as f:
    stopwords_fr = pickle.load(f)
with open("../../../SAPtables","rb") as f:
    SAPtables = pickle.load(f)

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
with open('../../../src/base_de_donnees/full/BOW_082020.json', encoding='utf8') as f:
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

# num_list = []
# for num in numbers:
#     num_list.append(num)

# sauvegarde de la liste "numéros de message" dans le fichier 'list_numbers'
marshal.dump(numbers, open("list_numbers", 'wb'))

# normalisation de chaque message du sac de mot
a = 0
doc = []
for m in message:
    treated = normalisation.pap_normalize(m)
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
mot_unique = normalisation.getUniqueWords(corpus_normalized=doc, numbers=numbers)
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
texts = [[token for token in texte if frequency[token] < SEUIL_FREQUENCE if not token in mot_unique.keys() if not token in stopwords_fr] for texte in doc]

# Crée un dictionnaire GENSIM (mapping de chaque mot avec un id)
dictionary = corpora.Dictionary(texts)
print("len du dictionnaire ", len(dictionary))
print("nb de mot unique à 1 message ", len(mot_unique))
# sauvegarde dans fichier 'specifiques.dict'
dictionary.save('specifiques.dict')     

# sauvegarde dictionnaire gensim en format texte
dictionary.save_as_text('dictionnaire_format_texte/dictionnaire_du_corpus.txt')
 
# création et sauvegarde du dictionnaire contenant les termes absents des lemmes, des stopwords, du dico_unique et sans candidat à la correction d'une potentielle faute d'orthographe
dico_intermediaire = normalisation.dictionnaire_intermediaire(texts)
# j'enregistre en JSON
with open('dictionnaire_intermediaire.json', 'w') as f:  
    json.dump(dico_intermediaire,f)
# j'enregistre en CSV
with open('dictionnaire_intermediaire.csv', 'w') as csv_file:  
    writer = csv.writer(csv_file)
    for key, value in dico_intermediaire.items():
        writer.writerow([key])

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
