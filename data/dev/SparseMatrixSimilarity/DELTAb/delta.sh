#!/bin/bash

# recupere le modele actuel
cp -r ../full_model2/ .

# execute la mise à jour du modele
python3 maj_model.py

# remplace le modele par sa mise-a-jour
cp -a ./full_model_buffer/. ../full_model2/

# archive le modèle de la veille
FILE="last_model.zip"
if [ -f "$FILE" ]
then
    rm $FILE
fi
zip -r ./last_model.zip ./full_model2

# libère espace disque
find ./full_model_buffer/ -type f -delete 
find ./full_model2/ -type f -delete

# autorise le modèle en lecture/ecriture
chmod -R 777 ../full_model2
