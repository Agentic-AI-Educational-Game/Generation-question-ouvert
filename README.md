# 🧠 Système de Génération de Questions Basé sur l'IA

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![LLM](https://img.shields.io/badge/LLM-FF69B4?style=for-the-badge&logo=tensorflow&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

[eng](README_eng.md) 

## Aperçu du Projet

Ce projet présente un système robuste basé sur l'IA, conçu pour générer des questions ouvertes en français à partir d'un texte fourni, en tirant parti d'un Grand Modèle de Langage (LLM) local. Il offre deux interfaces pour une flexibilité accrue : une application Streamlit conviviale pour le prototypage rapide et les tests, et une application web Flask intégrée à MongoDB pour un stockage persistant et une expérience web plus traditionnelle. Le système est capable de concentrer la génération de questions sur des parties spécifiques du texte d'entrée, ce qui le rend très adaptable à diverses fins éducatives ou analytiques.

![Arch](screenshots/gen-question.png)

## ✨ Fonctionnalités

*   **Intégration LLM Locale :** Utilise un Grand Modèle de Langage local au format GGUF pour la génération de questions, garantissant la confidentialité et la capacité hors ligne.
*   **Deux Interfaces Utilisateur :**
    *   **Application Streamlit :** Une interface web simple et interactive pour la saisie rapide de texte et la génération de questions.
    *   **Application Web Flask :** Une application web plus complète avec un frontend dédié (`index.html`) et un backend pour la génération et le stockage des questions.
*   **Intégration MongoDB :** L'application Flask s'intègre de manière transparente avec MongoDB pour stocker les questions générées, le texte d'entrée original et les horodatages pour un suivi et une analyse historiques.
*   **Génération de Questions Contextuelles :** Capacité à concentrer la génération de questions sur des segments spécifiques du texte d'entrée, permettant des questions précises et pertinentes.
*   **Sortie Structurée :** La sortie du LLM est analysée dans un format JSON structuré pour une consommation et une intégration faciles.
*   **MongoDB Dockerisé :** Inclut une configuration Docker Compose pour un déploiement facile de MongoDB et Mongo Express (une interface d'administration MongoDB basée sur le web).

## 🚀 Démarrage Rapide

Suivez ces étapes pour configurer et exécuter le projet localement.

### Prérequis

*   Python 3.8+
*   `pip` (installateur de paquets Python)
*   Docker et Docker Compose (pour la configuration de MongoDB)

### 1. Cloner le Dépôt

```bash
git clone https://github.com/your-username/Gen-Update.git
cd Gen-Update
```

### 2. Configurer les Variables d'Environnement

Créez un fichier `.env` dans le répertoire racine du projet basé sur le fichier `.env-example` :

```bash
cp .env-example .env
```

Modifiez le fichier `.env` avec vos configurations spécifiques :

```
MONGO_URI=mongodb://root:example@localhost:27017/
MONGO_DB_NAME=question_db
MONGO_COLLECTION_NAME=generated_questions
MODEL_PATH=./models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf
```

*   `MONGO_URI` : Chaîne de connexion pour votre instance MongoDB.
*   `MONGO_DB_NAME` : Nom de la base de données à utiliser.
*   `MONGO_COLLECTION_NAME` : Nom de la collection pour stocker les questions.
*   `MODEL_PATH` : Chemin relatif vers votre fichier de modèle GGUF.

### 3. Télécharger le Modèle LLM

Le projet utilise un modèle GGUF local. Vous devez télécharger le modèle `finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf` et le placer dans le répertoire `models/`.

*(Fournir un lien pour télécharger le modèle ici si disponible, ou des instructions sur la façon de l'obtenir)*

### 4. Installer les Dépendances Python

```bash
pip install -r requirements.txt
```
*(Note : Un fichier `requirements.txt` est supposé. S'il n'est pas présent, j'en créerais un.)*

### 5. Exécuter MongoDB avec Docker Compose

Naviguez jusqu'à la racine du projet et démarrez les services MongoDB et Mongo Express :

```bash
docker-compose -f mongo.yml up -d
```

Cela démarrera MongoDB sur `localhost:27017` et Mongo Express (interface web pour MongoDB) sur `localhost:8081`. Vous pouvez accéder à Mongo Express dans votre navigateur à l'adresse `http://localhost:8081` en utilisant les identifiants définis dans `mongo.yml` (par exemple, `root`/`example`).

![Mongo Express Interface](screenshots/mongo.png)

## 💡 Utilisation

### Application Streamlit

Pour exécuter l'application Streamlit :

```bash
streamlit run app.py
```

Ouvrez votre navigateur web et naviguez vers l'adresse fournie par Streamlit (généralement `http://localhost:8501`).

*   Entrez votre texte dans la zone "Input Text".
*   Optionnellement, spécifiez un "Focus Text" pour guider la génération de questions.
*   Cliquez sur "Generate Question".

![Streamlit App Initial State/Success](screenshots/streamlit-1.png)
![Streamlit App Another View/Error](screenshots/streamlit-2.png)

### Application Web Flask

Pour exécuter l'application web Flask :

```bash
python flask-app.py
```

L'application sera disponible à l'adresse `http://127.0.0.1:5000/`.

*   Accédez à la page principale pour saisir du texte et générer des questions.
*   Les questions générées seront stockées dans votre collection MongoDB configurée.

![Flask App UI](screenshots/flask-app.png)
![Flask App Command Line](screenshots/flask-cmd.png)
