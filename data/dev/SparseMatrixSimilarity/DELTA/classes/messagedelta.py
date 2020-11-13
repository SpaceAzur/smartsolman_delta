import requests, json, marshal, pickle, datetime, re, os
from collections import defaultdict

class MessageDelta(object):

    # variable d'authentification service SOLMAN
    USER = "i000000275"   
    PWD = "RapidPareto001!" 

    def __init__(self):
        self.status = "The night is dark and full of terrors"
        self.derniere_maj = self.getLastDate()
        self.jour_extract_delta = datetime.date.today().strftime("%Y-%m-%d")
        self.heure_extract_delta = os.popen("TZ=Europe/Paris date +'%H:%M:%S'").read().rstrip()

    def getLastDate(self):
        with open("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/date_delta","r") as f:
            last_maj = json.load(f)
        dat = last_maj['date']
        heure = last_maj['horaire']
        return dat, heure

    def saveDeltaDate(self):
        # maj_date = dict.fromkeys({ self.jour_extract_delta, self.heure_extract_delta }, 0)
        maj_date = {"date": self.jour_extract_delta,"horaire": self.heure_extract_delta}
        with open("/smartsolman/data/dev/SparseMatrixSimilarity/DELTA/date_delta","w") as f:
            json.dump(maj_date,f)

    def getMessageDeltaFromSolman(self):

        user = MessageDelta.USER
        pwd = MessageDelta.PWD

        last_jour, last_heure = self.derniere_maj

        src = "http://support.pasapas.com//sap/opu/odata/sap/zbow_srv/Messages?$filter=LastChange%20gt%20datetime%27"
        u_date = last_jour
        u_heure = "T"+last_heure
        u_format = "%27&$format=json"

        url = src+u_date+u_heure+u_format

        r = requests.get(url, auth=(user, pwd))
        result = r.json()

        delta = defaultdict(dict)
        for message in result['d']['results']:
            delta[message['Number']]['texte'] = message.get('ShortText') + ' ' + message.get('LongText')

        return delta

    def saveDeltaMessages(self, delta: dict):
        last_date, last_heure = self.derniere_maj
        date = self.jour_extract_delta
        with open("messagesDeltaTo"+date,"w") as f:
            json.dump(delta, f)
