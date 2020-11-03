# Application smartsolman

## Usage

smartsolman est une application python qui recherche des similarites entre les messages solman

## Installation

Pour créer l'image, executez la commande suivante

```bash
docker build -f Dockerfile -t smartsolman:dev_S1 .
```

## Deploiement

Pour lancer le service, creez un conteneur depuis l'image avec la commande suivante

```bash
docker run --sysctl net.ipv6.conf.all.forwarding=1 --sysctl net.ipv4.ip_forward=1 -d -p 5000:5000 <image_id>
```

## Informations

Cette version ne contient que le modèle de développement et son service ODATA. Sans mise-a-jour du delta

https://stackoverflow.com/questions/37458287/how-to-run-a-cron-job-inside-a-docker-container

## exploration VOLUME

1) lier le dossier 'vol3' (sur machine) au dossier /smartsolman/data du conteneur

```bash
docker run -it --mount type=bind,source=/c/Users/AntoineESCOBAR-MESLE/Desktop/vol3,target=/smartsolman/data 293ba5a4d349 bash
```
Dockerfile : pas de creation de VOLUME dans Dockerfile
Problème : supprime toutes les données initialement contenues dans /smartsolman/data 
Idée : avoir déjà tous les éléments du modèle dans le dossier vol3 de la machine


docker run --mount type=bind,source=/home/antoine/Bureau/vol3,target=/smartsolman/data --sysctl net.ipv6.conf.all.forwarding=1 --sysctl net.ipv4.ip_forward=1 -d -p 5000:5000 <image_id>