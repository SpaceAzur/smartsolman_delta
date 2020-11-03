import scipy.sparse, json, re, numpy as np, pickle, unidecode, Levenshtein, os, itertools 
import unidecode
from gensim import corpora, models, similarities

texte = '''
L'électricité est une richese inestimable dont on ne peut plus se passé aujourd'hui.
C'est la découverte de l'électricité, il y a plus d'un siècle, qui a permise au progrès de
faire des bond prodigieux.
Autrefois, bien avant la découverte de l'électricité, les hommes s'éclairait à la lampe
ou à la chandelle, les déplacements se fesaient en voiture tiré par des animau. Il y
avait des moulins à vent et des usines dont les machines fonctionnait par la force de
l'eau. Pour écrir, on ce servait d'une plume d'oie et on imprimmait les journaux ou les
livres avec la seule forse des muscles.
Il n'y avait pas de circuits intégré et les ordinateurs n'existait pas.
Il y a eut, en 150 ans, plus de progrès tecnologiques que depuis les débuts de
l'hummanité.
Les chercheurs saves beaucoup de choses à propos de l'électricité.
Ils fouilles sans cessent les mystères de l'électricité pour trouvé de nouvelles
applications et de nouvelles invantions.
'''

lemma = json.load(open("../frLemmaBase_unicode_val_in_keys.json"))
old = len(lemma)
with open("../stopwords_v1.2","rb")as f:
    stopwords_fr = pickle.load(f)

# source https://infolingu.univ-mlv.fr/DonneesLinguistiques/Dictionnaires/telechargement.html
dico_public =  open("../dela-fr-public.dic",'r', encoding="utf-16le").readlines()
print("dico public", len(dico_public))

def splitnonalpha(s):
   pos = 1
   while pos < len(s) and s[pos].isalpha():
      pos+=1
   return (s[:pos], s[pos:])

all_nonal = re.compile(r'[^a-zA-Z]')

#==========================================================================
# dictionnaire_unitaire = {}
# analyse = {}
# dictionnaire_compose = set()
# espace = re.compile(r' +')
# t = 0
# #pour chaque mot du dictionnaire public
# for mot in dico_public:
#     # je sépare l'expression de ses attributs
#     expression = mot.split(",",1)
#     # je récupère l'expression (pouvant être simple ouo composée)
#     terme = expression[0].strip()
#     #
#     lemme = expression[1].split(".",1)

#     if espace.search(terme):
#         compose = terme.split(" ")
#         print(terme, lemme, "COMPOSEEEEEEEEEEE", compose)
#         for f in compose:
#             if all_nonal.search(f):
#                 my_sub = all_nonal.sub(' ', f)
#                 if espace.search(my_sub):
#                     my_split = my_sub.split(" ")
#                     # print(f, my_split)
#                     for sp in my_split:
#                         if sp in stopwords_fr:
#                             continue
#                         else:
#                             dictionnaire_unitaire[unidecode.unidecode(sp)] = None
#             dictionnaire_compose.add(unidecode.unidecode(f.lower()))
#     else:
#         terme = unidecode.unidecode(terme)
#         lem = unidecode.unidecode(lemme[0])
#         print(terme, lem, 'lemme', lem == '')
#         dictionnaire_unitaire[terme] = lem


def decompose(terme): # converti au format unicode
    global stopwords_fr
    all_nonal = re.compile(r'[^a-zA-Z]')
    espace = re.compile(r' +')
    nonalpha_out = all_nonal.sub(" ", unidecode.unidecode(terme)) 
    my_split = nonalpha_out.split(" ")
    ok = [ o for o in my_split if not o in stopwords_fr ]
    while '' in ok:
        ok.remove('')
    return ok

def decompose2(terme): 
    global stopwords_fr
    all_nonal = re.compile(r'[^a-zA-Z]')
    espace = re.compile(r' +')
    nonalpha_out = all_nonal.sub(" ", terme) 
    my_split = nonalpha_out.split(" ")
    ok = [ o for o in my_split if not o in stopwords_fr ]
    while '' in ok:
        ok.remove('')
    return ok

test= 'événements == de \\n force majeure'

non_alpha = re.compile(r'\W')
espace = re.compile(r' +')
simple = set()
compose = set()
simple2 = set()
compose2 = set()
maj_dicionnaire = {}
for mot in dico_public:
    # je sépare l'expression de ses attributs
    expression = mot.split(",",1)
    # je récupère l'expression (pouvant être simple ouo composée)
    terme = expression[0].strip()
    # si fournis, je récupère le lemme du terme
    lemme = expression[1].split(".",1)
    terme = terme.lower()
    if ( espace.search(terme) or non_alpha.search(terme) ):
        temp = decompose(terme)
        temp2 = decompose2(terme)
        for t in temp:
            compose.add(t)
            compose2.add(t)
    else:
        term = unidecode.unidecode(terme)
        simple.add(term)
        simple2.add(terme)
        maj_dicionnaire[term] = None if lemme[0] == '' else unidecode.unidecode(lemme[0])

print("simple", len(simple))
print("compose", len(compose))

# je vérifie qu'il y a bien une valeurs pour chaque clé dans le dictionnaire 'simple'
cc = 0 
ccc = 0
for x, y in maj_dicionnaire.items():
    if y == None:
        cc += 1
        if y in maj_dicionnaire.keys():
            ccc += 1
print(len(maj_dicionnaire),"dont", cc,"clés sans valeur et", ccc)

maj_dicionnaire2 = {}
to_add = set()
for x, y in maj_dicionnaire.items():
    if y != None:
    #     maj_dicionnaire2[y] = y
    # else:
        maj_dicionnaire2[x] = y
    else:
        to_add.add(x)

print(len(maj_dicionnaire2), len(to_add))


cc = 0 
ccc = 0
for x, y in maj_dicionnaire2.items():
    if y == None:
        cc += 1
print(cc)

for t in to_add:
    if t in maj_dicionnaire2.keys():
        print("toto")

for t in to_add:
    maj_dicionnaire2[t] = t

print(len(maj_dicionnaire2))
for x, y in maj_dicionnaire2.items():
    if y == None:
        cc += 1
print(cc)

# with open("lemmaBase_from_public.json","w") as f:
#     json.dump(maj_dicionnaire2,f)

cc = 0
to_stopwords = set()
to_delete_from_maj_dicionnaire2 = set()
for e, f in maj_dicionnaire2.items():
    if espace.search(f):
        cc += 1
        # print(e, f)
        to_delete_from_maj_dicionnaire2.add(e)
        to_stopwords.add(f.lower())
        for w in f.split(" "):
            to_stopwords.add(w.lower())
            to_delete_from_maj_dicionnaire2.add(w.lower())

# # MAJ DES STOPWORDS
# print(cc, len(to_stopwords))
# print("stopword avant maj", len(stopwords_fr))
# for p in to_stopwords:
#     stopwords_fr.add(p)
# print("stopword apres maj", len(stopwords_fr))

# with open("../stopwords_v1.3","wb")as f:
#     pickle.dump(stopwords_fr,f)

with open("../stopwords_v1.3","rb")as f:
    stopwords_fr = pickle.load(f)


# verifie que chaque element de valeur composée est absente ou supprimée des clés du dictionnaire
print(len(maj_dicionnaire2), len(to_delete_from_maj_dicionnaire2))
print("brian" in maj_dicionnaire2.keys())
for to_del in to_delete_from_maj_dicionnaire2:
    if to_del in maj_dicionnaire2.keys():
        del maj_dicionnaire2[to_del]
    else:
        pass

# je vérifie qu'il n'y a aucune expression composé dans les clés du dictionnaire
print(len(maj_dicionnaire2))
cc = 0
for k, l in maj_dicionnaire2.items():
    if espace.search(k):
        cc += 1
        print("aie")

# je vérifie que tous est en lowercase
for i in stopwords_fr:
    if not i.islower():
        print("aie")
    if not isinstance(i, str):
        print("ouille")
cc = 0
for s, t in maj_dicionnaire2.items():
    if (not s.islower()
        or not t.islower()):
        cc += 1
        print("AIE", s, t, cc)

    if (not isinstance(s, str)
        or not isinstance(t, str)):
        print("OUILLE")
print(cc)

# je vérifie qu'il n'y a aucun digit 
for s, t in maj_dicionnaire2.items():
    for caractere in s:
        if caractere.isdigit():
            print("alala", s)
    for caracter in t:
        if caracter.isdigit():
            print("ololo", t)

maj_stopword = set()
cc = 0
for n in stopwords_fr:
    for cara in n:
        if cara.isdigit():
            cc += 1
            print('mille sabor', n, cc)
            maj_stopword.add(n)

print(len(maj_stopword))
print(len(stopwords_fr))
for m in maj_stopword:
    stopwords_fr.remove(m)
print(len(stopwords_fr))

cc = 0
for n in stopwords_fr:
    for cara in n:
        if cara.isdigit():
            cc += 1
            print('ectoplasme', n, cc)

# je corrige des valeurs de maj_dicionnaire2 en lower() et sans digit

maj_dicionnaire3 = {}
cc = 0
for s, t in maj_dicionnaire2.items():
    if not t.islower():
        cc += 1
        # print("tonerre", s, t, cc)
        result = ''.join([i for i in t if not i.isdigit()]).lower()
        maj_dicionnaire3[s] = result
    else:
        maj_dicionnaire3[s] = t
print(len(maj_dicionnaire2) == len(maj_dicionnaire3))

# import googletrans, langdetect

# translator = googletrans.Translator()
# francais = set()
# anglais = set()
# autres = set()
# for c in compose2:
#     if not c in simple2:
#         if translator.detect(c).lang == 'fr':
#             francais.add(c)
#         elif translator.detect(c).lang == 'en':
#             anglais.add(c)
#         else:
#             autres.add(c)
#     else:
#         continue

# print("francais", len(francais))
# print("anglais", len(anglais))
# print("autres", len(autres))

to_stop = ["M.", "monsieur","Messrs.", "messieurs", "Mlle.", "mademoiselle","Mm.", "messieurs", "Mme.", "madame", "Mr.", "monsieur", "Mrs.", "messieurs", "Ms.", "messieurs"]
for t in to_stop:
    stopwords_fr.add(t.lower())


del lemma["7e"]
del lemma["e"]

for t in to_stop:
    if t in lemma.keys():
        del lemma[t]

for s, t in lemma.items():
    for caractere in s:
        if caractere.isdigit():
            print("coucou", s)
    for caracter in t:
        if caracter.isdigit():
            print("hello", s, t)


# lemma2 = {}
# cc = 0
# ccc = 0
# for o, p in lemma.items():
#     if (not o.islower()
#         or not p.islower()):
#         cc += 1
#         result_cle = ''.join([i for i in o if not i.isdigit()]).lower()
#         result_val = ''.join([i for i in p if not i.isdigit()]).lower()
#         print("sapristi", o, p, cc, result_cle, result_val)
#         if unidecode.unidecode(result_cle) in lemma.keys():
#             ccc += 1
#         lemma2[unidecode.unidecode(result_cle)] = unidecode.unidecode(result_val)
#     else:
#         if unidecode.unidecode(result_cle) in lemma.keys():
#             ccc += 1
#         lemma2[unidecode.unidecode(o)] = unidecode.unidecode(p)

# print(len(lemma), len(lemma2), ccc)

lemma3 = {}
cc = 0
ccc = 0
for o, p in lemma.items():
    result_cle = ''.join([i for i in o if not i.isdigit()]).lower()
    result_val = ''.join([i for i in p if not i.isdigit()]).lower()   
    lemma3[unidecode.unidecode(result_cle)] = unidecode.unidecode(result_val)
print(len(lemma3))

# je fusionne le dictionnaire public avec notre dictionnaire de lemme
lemma4 = {**lemma3, **maj_dicionnaire3}
print(len(lemma4), old)

with open("stopwords_v1.3","wb")as f:
    pickle.dump(stopwords_fr,f)

with open("frLemmaBase_unicode_val_in_keys2.json","w") as f:
    json.dump(lemma4, f)