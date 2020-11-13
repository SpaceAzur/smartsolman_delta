#!/bin/bash

run_maj () {
    # recupere le modele actuel
    cp -r /smartsolman/data/dev/SparseMatrixSimilarity/full_model2/ /smartsolman/data/dev/SparseMatrixSimilarity/DELTA/

    # execute la mise a jour du modele
    python3 maj_model.py

    # remplace le modele par sa mise-a-jour
    cp -a /smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/. /smartsolman/data/dev/SparseMatrixSimilarity/full_model2/

    # sauvegarde modele de la veille
    veille="/smartsolman/data/dev/SparseMatrixSimilarity/modele_j-1.zip"
    if [ -f "$veille" ]
    then
        rm $veille
    fi
    echo "compression & sauvegarde modele J-1"
    zip -r /smartsolman/data/dev/SparseMatrixSimilarity/modele_J-1.zip /smartsolman/data/dev/SparseMatrixSimilarity/full_model2

    # libere espace disque (supprime fichiers en preservant dossiers enfants)
    find /smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model_buffer/ -type f -delete
    find /smartsolman/data/dev/SparseMatrixSimilarity/DELTA/full_model2/ -type f -delete

    # autorise le modele en lecture/ecriture
    chmod -R 777 /smartsolman/data/dev/SparseMatrixSimilarity/full_model2

    date +%H:%M:%S > /smartsolman/data/maj_ok

}

run_maj

# # s'execute tous les jours a 01h00 du matin
# while true
# do  
#     timy=$(date +%H)
#     if [ "$timy" -eq 01 ] 
#     then
#         run_maj
#         sleep 1h 1m
#     fi 
# done
