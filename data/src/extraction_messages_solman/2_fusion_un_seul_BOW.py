import requests, json, os, sys, marshal, pickle, time, datetime
from collections import defaultdict

'''
ABSTRACT

Le programme fusionne tous les paquets en un seul bag_of_word (BOW)
=> paquets contenus dans le dossier "bow_tmp"
=> sauvegarde du BOW dans dossier courant
=> quand terminé, à vous de supprimer manuellement les fichiers du dossier "bow_tmp"
'''
# repertoire contenant les bow à fusionner
bow_tmp = "bow_tmp/"
# liste des fichiers
repertoire = os.listdir(bow_tmp)
# initialise un dictionnaire vide
global_dict = defaultdict(dict)

# LOOP : ouverture/lecture des fichiers n et n+1 du répertoire
# fusion des dictionnaires contenus dans fichier n et n+1 
#               => jusqu'à n'avoir qu'un seul dictionnaire
for i, val in enumerate(repertoire):
    with open(bow_tmp+repertoire[i],'r') as f:
        bow_a = json.load(f)
        f.close()
    try:
        with open(bow_tmp+repertoire[i+1],'r') as f:
            bow_b = json.load(f)
            f.close()
    except:
        global_dict = {**global_dict, **bow_a} 
    global_dict = {**global_dict,**bow_a, **bow_b}

print(len(global_dict))
d = "_".join(str(datetime.date.today()).split("-"))

# ecriture/sauvegarde gros dictionnaire unique (dans dossier courant)
with open('BOW_'+d+'.json','w') as f:
    json.dump(global_dict, f)
