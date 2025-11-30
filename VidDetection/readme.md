# Real-Time Object Detection & Tracking System
## vrsion english                             
## Overview
This project implements a **real-time object detection and tracking system** using **YOLOv8** for object detection and **Deep SORT** for multi-object tracking. It provides a **FastAPI backend** for video processing and an optional visualization workflow.

## Features

### Real-time Video Analysis
- Frame-by-frame object detection
- Multi-object tracking
- Extraction of object statistics (count, position, movement)
- JSON and CSV export of tracked objects and metrics

### Annotated Video Generation
- Generates a new video with bounding boxes and tracking IDs
- Color-coded annotations for easier identification
- Downloadable annotated video for visualization or presentation

### Supported Classes
- People, vehicles, animals, sports objects, furniture, electronics, and more (COCO dataset classes)

## Difference Between Video Analysis and Annotated Video
### Video Analysis
- **Purpose**: Extract and process information from video without modifying it visually  
- **Output**: JSON files containing object IDs, positions, and tracking data  
- **Use case**: Statistical analysis, automated processing, model evaluation  

### Annotated Video
- **Purpose**: Visualize the detected objects and tracking in the video  
- **Output**: A video with bounding boxes, IDs, and color-coded trajectories  
- **Use case**: Validation, presentation, and easy verification of detection/tracking performance  

## Project Structure
- `app.py` — FastAPI application for backend video processing  
- `evaluation.py` — Evaluate detection and tracking performance  
- `object_tracing.py` — Tracking utilities for Deep SORT  
- `main.py` — Entry point for processing videos  
- `venv/` — Python virtual environment  
- `.gitignore` — Git ignore file  
- `requirements.txt` — Python dependencies  
- `yolo_maatrics.pg` — YOLO evaluation metrics data  
- `confusion_matrix_example.png` — Sample confusion matrix image  
- `yolov8n.pt` — YOLOv8 pre-trained model weights  

## Installation
1. Clone the repository:
   ```bash
   git clone <repo_url>
   cd <repo_folder>

## Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


### Install dependencies:

pip install -r requirements.txt

Running the Backend
uvicorn app:app --reload

The backend will run at http://127.0.0.1:8000

Running Evaluation
python evaluation.py  
--> the output is the matrices & confusio matrix

Running Object Tracking on a Video
python main.py 

Generating Annotated Video

The main.py script outputs a video file with bounding boxes and tracking IDs for visualization.

## Notes

Make sure YOLOv8 weights (yolov8n.pt) are present in the project directory.

The evaluation metrics and annotated outputs help assess model performance.

## License

This project is released under the MIT License.

## version francais
# Système de Détection et de Suivi d'Objets en Temps Réel

## Vue d'ensemble
Ce projet implémente un **système de détection et de suivi d'objets en temps réel** utilisant **YOLOv8** pour la détection et **Deep SORT** pour le suivi multi-objets. Il fournit un **backend FastAPI** pour le traitement vidéo et un flux de visualisation optionnel.

## Fonctionnalités

### Analyse Vidéo en Temps Réel
- Détection d'objets image par image
- Suivi multi-objets
- Extraction de statistiques sur les objets (nombre, position, mouvement)
- Export JSON/CSV des objets suivis et des métriques

### Génération de Vidéo Annotée
- Génère une nouvelle vidéo avec des boîtes englobantes et des IDs de suivi
- Annotations colorées pour une identification facile
- Vidéo téléchargeable pour visualisation ou présentation

### Classes Supportées
- Personnes, véhicules, animaux, objets de sport, meubles, électronique, etc. (classes du dataset COCO)

## Différence Entre Analyse Vidéo et Vidéo Annotée
### Analyse Vidéo
- **Objectif** : Extraire et traiter les informations de la vidéo sans modification visuelle  
- **Sortie** : Fichiers JSON contenant les IDs d'objets, positions et données de suivi  
- **Cas d'utilisation** : Analyse statistique, traitement automatisé, évaluation du modèle  

### Vidéo Annotée
- **Objectif** : Visualiser les objets détectés et le suivi dans la vidéo  
- **Sortie** : Une vidéo avec boîtes englobantes, IDs et trajectoires colorées  
- **Cas d'utilisation** : Validation, présentation et vérification facile des performances de détection/suivi  

## Structure du Projet
- `app.py` — Application FastAPI pour le traitement vidéo backend  
- `evaluation.py` — Évaluation des performances de détection et de suivi  
- `object_tracing.py` — Utilitaires de suivi pour Deep SORT  
- `main.py` — Point d'entrée pour le traitement des vidéos  
- `venv/` — Environnement virtuel Python  
- `.gitignore` — Fichier d’ignore Git  
- `requirements.txt` — Dépendances Python  
- `yolo_maatrics.pg` — Données des métriques YOLO  
- `confusion_matrix_example.png` — Exemple d’image de matrice de confusion  
- `yolov8n.pt` — Poids du modèle pré-entraîné YOLOv8  

## Installation
1. Cloner le dépôt :
   ```bash
   git clone <url_du_depot>
   cd <dossier_du_projet>

### Créer un environnement virtuel et l’activer :

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


### Installer les dépendances :

pip install -r requirements.txt

### Utilisation
Lancer le Backend
uvicorn app:app --reload


Le backend sera accessible à http://127.0.0.1:8000

Lancer le Suivi d'Objets sur une Vidéo
python main.py 

Génération de Vidéo Annotée

Le script main.py produit un fichier vidéo avec boîtes englobantes et IDs de suivi pour visualisation.

## Remarques

Assurez-vous que les poids YOLOv8 (yolov8n.pt) sont présents dans le répertoire du projet.

Les métriques d’évaluation et les vidéos annotées permettent de mesurer la performance du modèle.

## Licence

Ce projet est publié sous la licence MIT.