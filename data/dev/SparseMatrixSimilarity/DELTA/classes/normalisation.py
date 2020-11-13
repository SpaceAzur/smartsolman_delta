# -*- coding: utf-8 -*-
import os, sys, requests, time, json, pickle, marshal, csv, re, unidecode, Levenshtein, progressbar
from gensim import corpora
from collections import defaultdict

class Normalisation(object):

    RATIO = 0.92
    LEMMA_FR = json.load(open("/smartsolman/data/frLemmaBase_unicode_val_in_keys.json"))
    LEMMA_ENG = json.load(open("/smartsolman/data/EngLemmaBase_unicode.json"))

    ALPHABET = [ h for h in "abcdefghijklmnopqrstuvwxyz"]

    with open("/smartsolman/data/stopwords_v1.2","rb") as f:
        STOPWORDS_FR = pickle.load(f)

    with open("/smartsolman/data/english_stopwords_merge_of_nltk_spacy_gensim","r") as f:
        STOPWORDS_ENG = json.load(f)

    with open("/smartsolman/data/SAPtables","rb") as f:
        SAPTABLES = pickle.load(f)

    with open("full_model2/full_dico_unique","r") as u:
        UNIQUE = json.load(u).keys()

    with open("full_model2/full_dico","r") as u:
        FULL_DICT = json.load(u).keys()

    with open("/smartsolman/data/src/fautes_orthographe/dev/dict_fautes_orthographes_92.json","r") as f:
        CORRECTION_ORTHOGRAPHE = json.load(f)

    with open("/smartsolman/data/src/traductions/sap_sterm/monogram/fr_monogram.json","r") as f:
        FR_MONOGRAM = json.load(f)

    with open("/smartsolman/data/src/traductions/sap_sterm/monogram/eng_monogram.json","r") as f:
        ENG_MONOGRAM = json.load(f)


    NUMBERS = marshal.load(open("full_model2/list_numbers", "rb")) 


    def __init__(self):
        # self.db = db from atributes
        self.status = "You know nothing John Snow"

    def getUniqueWords(self, corpus_normalized: list, numbers: list):
        compteur = 0
        inventaire = {}

        bar = progressbar.ProgressBar(maxval=len(corpus_normalized), \
            widgets=[progressbar.Bar('=', 'Unique [', ']'), ' ', progressbar.Percentage()] )
        c = 0
        bar.start()

        # compte le nombre de message solman où apparait chaque token
        for i, texte in enumerate(corpus_normalized):  
            bar.update(c)                            
            for token in set(texte):
                if token in inventaire.keys():
                    inventaire[token] = {"count": inventaire[token].get("count") + 1 , "orig": numbers[i]}
                else:
                    inventaire[token] = {"count": 1, "orig": numbers[i]}                                                       
            c += 1
        bar.finish()
        # sauvegarde le dictionnaire total du modele en JSON 
        with open("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/full_dico",'w') as f:      # je sauvegarde le dictionnaire du corpus
            json.dump(inventaire,f)

        # identifie les token qui n'apparaissent que dans un seul message solman
        unique = {}
        for i, val in inventaire.items():                                        
            if val.get('count') == 1:
                unique[i] = val.get('orig')

        # sauvegarde les mots uniques en JSON
        with open("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/full_dico_unique",'w') as f:     # je sauvegarde le dictionnaire de mot unique du corpus
            json.dump(unique,f)

        # sauvegarde en CSV
        with open("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/dict_unique.csv", "w") as csv_file:  
            writer = csv.writer(csv_file)
            for key, value in unique.items():
                writer.writerow([key, value])
        
        return unique
        
    def transformMeta(self, token: str):
        lemma = Normalisation.LEMMA_FR
        lemma_eng = Normalisation.LEMMA_ENG
        SAPtables = Normalisation.SAPTABLES

        tmp = [ re.split(r'[\-\_]',x) for x in token.split() ]
        tmp = [ item for sublist in tmp for item in sublist ]
        lemmaRemoved = [ lemma[y] if y in lemma.keys() else y for y in tmp ]
        recompose_without_digit = "".join([ t for t in lemmaRemoved if t not in lemma.values() and not t.isdigit() and not t in SAPtables ])    
        saptable = " ".join([ x for x in lemmaRemoved if x in SAPtables ]) # recupere nom de table si inclus dans le mot (postule qu'il ne peut y avoir qu'un seul nom de table dans un mot composé)
        if saptable:
            return recompose_without_digit, saptable
        else:
            return recompose_without_digit

    def apostropheX92(self, message: str):
        res = { re.sub(r'[\x92\n\t\r]', ' ', message) }
        res = str(res)
        res = res[2:-2]
        return res

    def pasapasLemmatisation(self, message: list):

        fr_monogram = Normalisation.FR_MONOGRAM
        eng_monogram = Normalisation.ENG_MONOGRAM
        correction_ortho = Normalisation.CORRECTION_ORTHOGRAPHE
        lemma = Normalisation.LEMMA_FR
        lemma_eng = Normalisation.LEMMA_ENG
        stopwords_fr = Normalisation.STOPWORDS_FR
        eng_stopwords = Normalisation.STOPWORDS_ENG
        SAPtables = Normalisation.SAPTABLES
        dico_unique = Normalisation.UNIQUE

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

    def distanceLevenshtein(self, token):
        lemma = Normalisation.LEMMA_FR
        fautes_deja_corrigees = Normalisation.CORRECTION_ORTHOGRAPHE
        best_distance = 0.0

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
        
        return save

    def pap_normalize(self, message: str):

        lemma = Normalisation.LEMMA_FR
        lemma_eng = Normalisation.LEMMA_ENG
        stopwords_fr = Normalisation.STOPWORDS_FR
        SAPtables = Normalisation.SAPTABLES
        eng_stopwords = Normalisation.STOPWORDS_ENG
        dico_unique = Normalisation.UNIQUE
        CORRECTION_ORTHOGRAPHE = Normalisation.CORRECTION_ORTHOGRAPHE

        lemma_fr_values = set(lemma.values())
        lemma_eng_values = set(lemma_eng.values())

        x92 = re.compile(r'[\x92\']')
        if x92.search(message):
            message0 = self.apostropheX92(message)
        else:
            message0 = message

        # supprime \t\n\r supprime ponctuation + split les mots contenant des metacaractere qui bascule alors dans le "traitement standard"
        ponctu = re.compile(r"[\s\.,:\';°\*%'><\<\>=\+\?&~#\$£€\{\}\(\)\[\]\|/\\]") 
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
        message3 = re.sub(r"[\n\r\t\a]",' ', message2bis).lower() # doublon avec ligne 230 => '\s' s'en occupe déjà
        message4 = message3.split()

        # nettoyage
        while '' in message4:
            message4.remove('')

        # enlève les mots composés exclusivement de caractère non alpha-numérique (ex: "--->", "==>", "*%__") OK
        non_alfanum = re.compile(r'^\W+$')

        # supprime les mots contenant meta ["!", "§", "@", "`"]
        bob = re.compile(r'[§!@`]')
        message5 = [ i for i in message4 if not bob.search(i) and not non_alfanum.search(i) ]

        # suppression des apostrophes et double-quote rémanantes aux traitements précédents (pre-split)
        # regex : définit le pattern apostrophe
        apostr = re.compile(r"'")
        message5bis = []
        for m in message5:
            if apostr.search(m):
                un = re.sub(apostr, ' ', m).split()
                deux = [ e for e in un if not e in Normalisation.ALPHABET if not e in stopwords_fr if not e in eng_stopwords]
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
        message8 = [ x for x in message7bis if not x in stopwords_fr if not x in eng_stopwords ]

        # lemmatisation, sauf si token contient un metacaractere recomposé ou commence par 'z'
        message9 = self.pasapasLemmatisation(message8)

        # pour être sûr, seconde suppression des stopwords 
        message10 = [ t for t in message9 if not t in stopwords_fr if not t in eng_stopwords ]

        # nettoyage des tokens vides
        while '' in message10:
            message10.remove('')

        # ????????????????? pourquoi encore
        message11 = []
        for m in message10:
            message11.append(re.sub(r'\W', '', str(m)))

        return message11

    def inUnique(self, token):
        unique = Normalisation.UNIQUE
        verif = token in unique.keys()
        return verif

    def isUnique(self, token):
        unique = Normalisation.UNIQUE
        full_dict = Normalisation.FULL_DICT
        a = 0
        return None

    def getMessageIndex(self, num_message):
        return None

    def yieldFromJSON(self, fichier):
        with open(fichier,'r', encoding='utf8') as f:
            tmp_base = json.load(f)
            for w in tmp_base:
                yield w
