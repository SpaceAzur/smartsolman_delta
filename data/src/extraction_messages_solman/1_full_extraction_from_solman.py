import requests, json, os, sys, marshal, pickle, time
from collections import defaultdict

'''
ABSTRACT

Le programme extrait par paquets l'ensemble des messages contenus dans la base SOLMAN 
(commence par message plus anciens)
=> il stocke les messages du paquet dans un dictionnaire
=> le dictionnaire contient : 
    - le N° de chaque message
    - l'en-tête (ShortText) et le corps (LongText) de chaque message, concaténés
=> Il sauvegarde le dictionnaire dans le répertoire "bow_tmp/" 
=> le programme "fusion_en_un_seul_BOW.py" s'occupera de l'étape suivante
'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
statut = 200
identifiant = 'i000000275'  # VOTRE IDENTIFIANT SOLMAN
pwd = 'RapidPareto001!'     # VOTRE MOT DE PASSE SOLMAN

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FONCTION : connection à un service ODATA pour récupérer un dictionnaire JSON
# PARAM : TYPE      NOM             CONTENU
#         string    url             adresse_HTML
#         string    identifiant     identifiant (ex: i000000234)
#         string    pwd             mot_de_passe
# RETURN : dict (dictionnaire de donnees)
def getDictFromOdata(url, identifiant, pwd):
    donnees = requests.get(url, auth=(identifiant,pwd))
    global statut 
    statut = donnees.status_code
    if (donnees.status_code != 200):
        print("erreur de connection", donnees.status_code)
        sys.exit(1)
    dict_json = donnees.json()  
    del donnees
    del url
    del identifiant
    del pwd
    return dict_json

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# REQUETAGE / EXTRACTION SEQUENTIELLE DE SOLMAN
u = "http://support.pasapas.com/sap/opu/odata/sap/zbow_srv/Messages?$top="
r = "&$skip="
l = "&$format=json"
# la variable "top" indique le nb de message qui sera extrait dans chaque paquet
top = 1
skip = 0
fi = 'bow'
chier = '.json'
count = 1
repertoire = 'bow_tmp/'
repertoire2 = 'bow_tmp2/'

while True :  
    
    # initialisation d'un dictionnaire vierge
    dico = defaultdict(dict)

    #requête ODATA
    requete = u+str(top)+r+str(skip)+l
    data = getDictFromOdata(requete,identifiant, pwd)
    fichier = fi+str(count)+chier
    # composition du dictionnaire 
    for message in data['d']['results']:
        dico[message['Number']]['texte'] = message.get('ShortText') + ' ' + message.get('LongText')
    dico = dict(dico)

    # monitoring de l'extraction
    print(count, skip)
    
    # sauvegarde du fichier sur disk
    with open(repertoire+fichier,'w') as f:
        json.dump(dico, f)

    # with open(repertoire2+fichier,'w') as f:
    #     json.dump(dico2, f)

    count += 1
    skip = skip + top
    del dico
    del requete
    del data
    del fichier
    del message

'''
Service TREX
http://support.pasapas.com/sap/opu/odata/sap/ZBOW_SRV/TrexSearch?Terms=%27livraison%20entrante%27&$format=json
'''
