import json, pickle, marshal, re, sys, unidecode

numbers = marshal.load(open("list_numbers", "rb"))

with open("docNormalized","r") as f:
    doc = json.load(f)

with open('../../../src/base_de_donnees/full/BOW_082020.json', encoding='utf8') as f:
    bow = json.load(f)

with open("../../../EngLemmaBase_unicode.json","r") as f:
    lemma_eng = json.load(f)

with open("../../../english_stopwords_merge_of_nltk_spacy_gensim","r") as f:
    eng_stopwords = json.load(f)

with open("../../../frLemmaBase_unicode_val_in_keys.json","r") as f:
    lemma = json.load(f)

with open("../../../SAPtables","rb") as f:
    SAPtables = pickle.load(f)

with open("full_dico_unique","r") as f:
    dico_unique = json.load(f).keys()

with open("../../../stopwords_v1.2","rb") as f:
    stopwords_fr = pickle.load(f)

al = "abcdefghijklmnopqrstuvwxyz"
ALPHABET = [l for l in al]

# u0092 = []
# symbol = re.compile(u'\u0092')

# f = 0
# c = 0
# for i, msg in bow.items():
#     # print(msg['texte'])
#     # breakpoint()
#     x = symbol.search(msg['texte']) 
#     if x != None:
#         d = x.span()[0]
#         f = x.span()[1]
#         u0092.append(i)
#         mot = msg['texte']
#         n = mot[:d].split()[-1]
#         m = mot[f:].split()[0]
#         o = mot[d:f]
#         # print(f, n, m, o)
#     # print(c)
#     c += 1
#     try:
#         del f
#     except:
#         pass
# print("u0092 =>", len(u0092))

x92 = []
symbol = re.compile(r'\x92')

f = 0
c = 0
anomalies = {}
for i, msg in bow.items():
    # print(msg['texte'])
    # breakpoint()
    x = symbol.search(msg['texte']) 
    if x != None:
        anomalies[i] = msg
        d = x.span()[0]
        f = x.span()[1]
        x92.append(i)
        mot = msg['texte']
        n = mot[:d].split()[-1]
        m = mot[f:].split()[0]
        o = mot[d:f]
        w = msg['texte'][d-1:f]
        dic = { "a":mot[d-5:f+5],"b":re.sub(r"[\x92\']", ' ', mot[d-5:f+5]) }
        # if not unidecode.unidecode(o).lower() in stopwords_fr:
            # print(f, n, m, o, "".join("{:x}".format(ord(t)) for t in w), dic)
    # print(c)
        c += 1
    try:
        del f
    except:
        pass

print("nb mesg concerné", c, len(anomalies))

def transformMeta(token: str):
    global lemma
    global lemma_eng
    global SAPtables
    # with open("../../../../data/SAPtables","rb") as f:
    #     SAPtables = pickle.load(f)
    # lemma = json.load(open("../../../../data/frLemmaBase_unicode.json"))
    tmp = [ re.split(r'[\-\_]',x) for x in token.split() ]
    tmp = [ item for sublist in tmp for item in sublist ]
    lemmaRemoved = [ lemma[y] if y in lemma.keys() else y for y in tmp ]
    recompose_without_digit = "".join([ t for t in lemmaRemoved if t not in lemma.values() and not t.isdigit() and not t in SAPtables ])    
    saptable = " ".join([ x for x in lemmaRemoved if x in SAPtables ]) # recupere nom de table si inclus dans le mot (postule qu'il ne peut y avoir qu'un seul nom de table dans un mot composé)
    if saptable:
        return recompose_without_digit, saptable
    else:
        return recompose_without_digit

def apostropheX92(message: str):
    res = { re.sub(r'[\x92\n\t\r]', ' ', message) }
    res = str(res)
    res = res[2:-2]
    return res

def paz_normalize(message: str):

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
    # => pour chaque apostrophe, controle si son format hexadecimal est r'\x92' ou si son format unicode est u'\u0092'
    x92 = re.compile(r'[\x92\']')
    if x92.search(message):
        message0 = apostropheX92(message=message)
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
    message3 = re.sub(r"[\n\r\t\a<>]", ' ', message2).lower() # doublon avec ligne 230 => '\s' s'en occupe déjà

    
    # if x92.search(message3) != None:
    #     message3bis = apostropheX92(message3)
    #     print("in function", message3bis)
    # else:
    message3bis = message3

    # message3bis = { 'to': re.sub(r'\x92', ' ', message3) }

    # print(type(message3bis))
    # print(type(message3bis['to']))
    # message3tris = message3bis['to']

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
    message9 = []
    for m in message8:
        if ( meta.search(m) or start_with_z.search(m) ):
            message9.append(m)
        elif m in lemma.keys():
            message9.append(lemma[m])
        elif m in lemma_eng.keys():
            message9.append(lemma_eng[m])
        else:
            message9.append(m)


    # # correction orthographe (par distance de Levenshtein), sauf si le token est un lemme, sauf si le token contient un metacaractere recomposé, sauf si token est un terme SAP
    # message9bis = []
    # for mot in message9:
    #     if (mot in set(lemma.values()) 
    #         # or mot in lemma.keys() 
    #         # or mot in lemma_eng.keys()
    #         or mot in set(lemma_eng.values())
    #         or meta.search(mot) 
    #         or mot in SAPtables 
    #         or mot.isdigit() 
    #         # or mot in stopwords_fr 
    #         # or mot in eng_stopwords 
    #         or digit_in_token.search(mot)
    #         or start_with_z.search(mot) ):

    #         message9bis.append(mot)

    #     elif mot in fautes_deja_corrigees.keys():
    #         message9bis.append(fautes_deja_corrigees[mot].get('corr'))

    #     else:
    #         correction, distance = distanceLevenshtein(mot)
    #         message9bis.append(correction)
    #         fautes_deja_corrigees[mot] = { "corr": correction, "lev": distance }
    #         with open("../../../../data/dev/SparseMatrixSimilarity/very_light/analyse_des_corrections.json","w") as f:
    #             json.dump(fautes_deja_corrigees,f)
    #         del correction, distance

    # pour être sûr, seconde suppression des stopwords 
    message10 = [ t for t in message9 if not t in stopwords_fr if not t in eng_stopwords ]

    # nettoyage des tokens vides
    while '' in message10:
        message10.remove('')

    # ????????????????? pourquoi encore
    message11 = []
    for m in message10:
        message11.append(re.sub(r'\W', '', str(m)))

    # suppression des mots à trop forte frequence | s'execute selon si le modele est déjà créé ou pas (considération pour les appels du client)
    # çàd : cette partie s'exécute pour la normalisation du message query
    try:
        with open("../../../../data/dev/SparseMatrixSimilarity/full_model2/frequence","r") as f:
            frequence = json.load(f)

        messsage12 = []
        for u in message11:
            try:
                z = frequence[u]
                if z < 20:
                    message12.append(u)
                else:
                    continue
            except:
                continue
    except:
        pass

    # regex : sauvegarde du pattern "n°OT"
    # OT = re.compile(r'\w{3}k\d{6}')

    if 'message13' in locals():
        return message12
    else:
        return message11

# cp = 0
# renorma = {}
# for k, item in anomalies.items():
#     norm = paz_normalize(item['texte'])
#     renorma[k] = norm
#     print(cp)
#     cp += 1

# with open("renormaDict2.json","w") as f:
#     json.dump(renorma,f)

with open("renormaDict2.json","r") as f:
    modif = json.load(f)

c = 0
for ke in modif.keys():
    ide = numbers.index(int(ke))

# print(doc[ide],'doc', ke)
# print(modif[ke],'modif')

buwgalett = paz_normalize(bow[ke]['texte'])

print("\nbuwgalett\n", ke, buwgalett)

zu = re.compile(r'\x92')
fdict = bow[ke]['texte']
qq = fdict #json.dumps(fdict)


res = { re.sub(r'[\x92\n\t\r]', ' ', qq) }
# res = { "to": re.sub(r'\x92', ' ', qq) }
res = str(res)
# print("res\n\n", res)
# print("type res", type(res))
res = res[2:-2]
retourne = res
# print("\nretourne",retourne, type(retourne))

