import json, Levenshtein, re, pickle, sys, multiprocessing, functools, time, csv, unidecode, marshal, numpy as np


with open("dict_fautes_orthographes.json","r") as f:
    corrections = json.load(f)

new_ration_correction = {}
c = 0
for i, info in corrections.items():
    if info['lev'] >= 0.92:
        c += 1
        new_ration_correction[i] = info

print(c)

with open("dict_fautes_orthographes_92.json","w") as f:
    json.dump(new_ration_correction, f)

with open('dict_fautes_orthographes_92.csv', 'w') as csv_file:  
    writer = csv.writer(csv_file)
    for key, value in new_ration_correction.items():
        writer.writerow([key, value.get('corr'), value.get('lev') ])
