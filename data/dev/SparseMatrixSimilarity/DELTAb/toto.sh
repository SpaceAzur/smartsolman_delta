#!/bin/bash

run_maj () {

    # recupere le modele actuel
    cp -r ../full_model2/ .

    # execute la mise à jour du modele
    python3 maj_model.py

    # remplace le modele par sa mise-a-jour
    cp -a ./full_model_buffer/. ../full_model2/

    # archive le modèle de la veille
    zip -r ./last_model.zip ./full_model2

    # libère espace disque
    rm -r ./full_model2/*
    rm -r ./full_model_buffer/*
}

# execute la maj du modele tous les jours à 1h du matin
while true
do 
    timy=$(date +%H)
    if [ "$timy" -eq 01 ]
    then 
        run_maj
        sleep 1h 1m
    fi 
done