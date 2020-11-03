import requests, json 
from unidecode import unidecode

url = "https://support.pasapas.com/sap/opu/odata/sap/ZBOW_SRV/DistinctLastNames?$format=json"

user = "i000000275"
pwd = "RapidPareto001!"

r = requests.get(url, auth=(user, pwd))

result = r.json()

# nom_famille= result.values()

names = set()
c = 0
for row in result['d']['results']:
    tmp = unidecode(row['Name'].lower())
    names.add(tmp)

print(len(names))
save = {x:0 for x in names}
print(type(save))

with open("nomfamilleSolman.json","w") as f:
    json.dump(save, f)