# -*- coding: utf-8 -*-
from gensim import corpora, models, similarities
from collections import defaultdict
import scipy
import os, sys, pandas as pd, numpy as np, time, json, pickle, marshal, csv, re, unidecode, Levenshtein
from operator import itemgetter
import heapq, scipy.sparse, math, random
sys.path.append('.')
from modules.normalisationdatabase import NormalisationDataBase

# # ratio de Levenshtein
# RATIO = 0.92

# # pourcentage du corpus dans lequel apparait un token et au dessus duquel le token est considéré comme trop fréquent, et évacuer 
# SEUIL_FREQUENCE = 12.0

# al = "abcdefghijklmnopqrstuvwxyz"
# ALPHABET = [l for l in al]

# with open("/smartsolman/data/src/fautes_orthographe/dev/dict_fautes_orthographes_92.json","r") as f:
#     CORRECTION_ORTHOGRAPHE = json.load(f)

# db  = NormalisationDataBase()

class Normalisation2(object):

    # ratio de Levenshtein
    RATIO = 0.92

    # pourcentage du corpus dans lequel apparait un token et au dessus duquel le token est considéré comme trop fréquent, et évacuer 
    SEUIL_FREQUENCE = 12.0

    al = "abcdefghijklmnopqrstuvwxyz"
    ALPHABET = [l for l in al]

    with open("/smartsolman/data/src/fautes_orthographe/dev/dict_fautes_orthographes_92.json","r") as f:
        CORRECTION_ORTHOGRAPHE = json.load(f)


    def __init__(self, db):
        self.db = db

    # Création du dictionnaire de mot unique à un message
    def getUniqueWords(self, corpus_normalized: list, numbers: list):
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
    def transformMeta(self, token: str):
        # global lemma
        # global lemma_eng
        # global SAPtables

        tmp = [ re.split(r'[\-\_]',x) for x in token.split() ] # produit une liste de list
        tmp = [ item for sublist in tmp for item in sublist ] # reconverti en liste simple
        
        # lemmaRemoved = [ lemma[y] if y in lemma.keys() else y for y in tmp ]
        
        lemmaRemoved = []
        for element in tmp:
            q = self.db.frLemmatisation(element)
            if q:
                lemmaRemoved.append(q)
            else:
                lemmaRemoved.append(element)

        del element, q

        # recompose_without_digit = "".join([ t for t in lemmaRemoved if t not in lemma.values() and not t.isdigit() and not t in SAPtables ])    

        recompose = []
        for element in lemmaRemoved:
            q = self.db.isSAPterm(element)
            p = self.db.frLemmatisation(element)
            if (not q
                and not p
                and not element.isdigit() ):
                recompose.append(element)
            else:
                continue
        
        del q, p

        recompose_without_digit = "".join(recompose)

        saptable = " ".join([ x for x in lemmaRemoved if self.db.isSAPterm(x) ]) # recupere nom de table si inclus dans le mot (postule qu'il ne peut y avoir qu'un seul nom de table dans un mot composé)
        
        if saptable:
            return recompose_without_digit, saptable
        else:
            return recompose_without_digit



    def apostropheX92(self, message: str):
        res = { re.sub(r'[\x92\n\t\r]', ' ', message) }
        res = str(res)
        res = res[2:-2]
        return res


    def pap_normalize(self, message: str):

        ALPHABET = Normalisation2.ALPHABET
        CORRECTION_ORTHOGRAPHE = Normalisation2.CORRECTION_ORTHOGRAPHE


        # regex: suppression du format apostrophe r'\x92' <=> u'\u0092' (apparait comme un mini rectangle)
        x92 = re.compile(r'[\x92\']')
        if x92.search(message):
            message0 = self.apostropheX92(message)
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
                deux = [ e for e in un if not e in ALPHABET if not self.db.isFrenchStopword(e) if not self.db.isEnglishStopword(e) ]
                if len(deux) == 0:
                    pass
                else:
                    # print(m, un, deux, len(deux))
                    message5bis.append(deux[0])
            else:
                message5bis.append(m)

        meta = re.compile(r'[-_]')
        message6 = [ self.transformMeta(x) if meta.search(x) else x for x in message5bis ]

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
        message8 = [ x for x in message7bis if not self.db.isFrenchStopword(x) if not self.db.isEnglishStopword(x) ]

        # lemmatisation, sauf si token contient un metacaractere recomposé ou commence par 'z'
        message9 = []
        for m in message8:

            q = self.db.frLemmatisation(m)
            p = self.db.engLemmatisation(m)

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
        message10 = [ t for t in message9 if not self.db.isFrenchStopword(t) if not self.db.isEnglishStopword(t) ]

        # nettoyage des tokens vides
        while '' in message10:
            message10.remove('')

        # ????????????????? pourquoi encore
        message11 = []
        for m in message10:
            message11.append(re.sub(r'\W', '', str(m)))

        return message11

