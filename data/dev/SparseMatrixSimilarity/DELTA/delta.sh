#!/bin/bash

killServerPID () {
    ps aux | grep "python3 ../../../../app/dev/full_model/server_DF.py" | head -n 1 | awk '{print $2}' | xargs kill -9
}

getServerPID () {
    while read -r line
    do
        pid_to_stop=$line
    done < server_PID
}

# recupere le modele actuel
cp -r ../full_model2/ .

# execute la mise à jour du modele
python3 maj_model.py

# remplace le modele par sa mise-a-jour
cp -a ./full_model_buffer/. ../full_model2/

# libère espace disque
find ./full_model_buffer/ -type f -delete 
find ./full_model2/ -type f -delete

# autorise le modèle en lecture/ecriture
chmod -R 777 ../full_model2

touch ../full_model2/zorototo