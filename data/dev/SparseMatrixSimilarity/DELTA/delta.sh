#!/bin/bash

run_maj () {
    # recupere le modele actuel
    cp -r ../full_model2/ .

    # execute la mise a jour du modele
    python3 maj_model.py

    # remplace le modele par sa mise-a-jour
    cp -a ./full_model_buffer/. ../full_model2/

    # sauvegarde modele de la veille
    veille="modele_j-1.zip"
    if [ -f "$veille" ]
    then
        rm $veille
    fi
    zip -r modele_j-1.zip ./full_model2

    # libere espace disque (supprime fichiers en preservant dossiers enfants)
    find ./full_model_buffer/ -type f -delete 
    find ./full_model2/ -type f -delete

    # autorise le modele en lecture/ecriture
    chmod -R 777 ../full_model2
}

# s'execute tous les jours a 01h00 du matin
while true
do  
    timy=$(date +%H)
    if [ "$timy" -eq 01 ] 
    then
        run_maj
        sleep 1h 1m
    fi 
done