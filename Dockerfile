# telecharge l'image de l'OS depuis docker_hub
FROM opensuse/leap:15

# copie l'application dans l'image
COPY . /smartsolman/

# definit le repertoire courant
WORKDIR /smartsolman

# installe le contexte
RUN zypper install -y python3 gcc python3-devel python3-pip sqlite3 zip
RUN pip install -r requirements.txt

# lance l'application a la creation du conteneur
CMD ["/smartsolman/app/dev/delta.sh"]
ENTRYPOINT [ "/bin/bash" ]
