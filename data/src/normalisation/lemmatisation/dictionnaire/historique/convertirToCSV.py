import json, csv, re, copy

lemma = json.load(open("V3_frLemmaBase_unicode_val_in_keys_merge_with_public.json"))

print(len(lemma))

with open('V3_dictLemmatisationPAP.csv', 'w') as csv_file:  
    writer = csv.writer(csv_file)
    for key, value in lemma.items():
       writer.writerow([key, value])

