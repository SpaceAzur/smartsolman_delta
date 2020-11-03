import os, sys
# récupère les arguments saisis par l'utilisateur
try:           
    if sys.argv[1] and sys.argv[2]:
        num_message = sys.argv[1]
        mode = sys.argv[2]
        print(num_message)
        print(mode)
except:      
    print("\nUsage : Saisir des arguments : \n argument_1 : votre_numero_de_message \n argument_2  \n\t -> saisir i (version initial) \n\t -> saisir c (version custom) \n exemple : python3 client.py 67439 i\n")
    sys.exit(1)

# try:
#     if sys.argv[3]:
#         keyword = sys.argv[3]
#         print("keyword", keyword)
# except:
#     pass

if mode == 'i':
    url2 = "http://localhost:5000/tfidf_classic/"
    for_save = 'initial'
elif mode == 'c':
    url2 = "http://localhost:5000/tfidf_custom/"
    for_save = 'custom'
else:
    print("Argument {} incorrect !\n\tChoisir 'i' pour initial ou 'c' pour custom".format(mode))
    sys.exit(1)

keywords = sys.argv
keys = keywords[3:]

some_text = "liubq iqufhdiuf nqineg"
# some_text = some_text.split(" ")

print(some_text)
for k in keys:
    some_text += ' ' + k

print(some_text)