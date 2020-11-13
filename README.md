# Application smartsolman_delta

smartsolman est une application python qui recherche des similarites entre les messages solman

## Usage

Ce conteneur permet de mettre à jour le modèle de l'application smartSolman

## Connection au serveur d'hébergement

Le déploiement actuel s'effectue sur la VM 178.32.116.200 
User : sapadm
Password: idem que sapdocpy

Une fois connecté, basculer en root depuis un terminal :
```bash
su -
```
Password: idem que root de sapdocpy.pasapas.com

## Connection à Docker

Créer votre compte Docker sur la plateforme [Docker Hub](https://hub.docker.com/) 

Poursuivez depuis un terminal à l'emplacement de l'application /smartsolman/smarsolman_delta
```bash
docker login
```
Saissisez votre Compte et Mot_de_passe Docker

## Installation

Pour créer l'image, executez la commande suivante

```bash
docker build -f Dockerfile -t smartsol:delta .
```

## Deploiement

Pour lancer le service, créez un conteneur depuis l'image avec la commande suivante :

```bash
docker run --mount type=bind,source=/home/sapadm/volume,target=/smartsolman/data -it <image_id> /bin/bash
```

Cette commande va :
- Instancier le conteneur et vous ouvrir un terminal à l'intérieur
- Lier un volume du conteneur à un espace disque du serveur pour la bonne persistance des données

## Commandes docker utiles

Consulter les images
```bash
docker images
```
Consulter les conteneurs
```bash
docker ps -a
```
Supprimer un conteneur
```bash
docker container stop <container_id>
docker container rm <container_id>
```
Supprimer une image
```bash
docker rmi <image_id>
```

https://stackoverflow.com/questions/37458287/how-to-run-a-cron-job-inside-a-docker-container
