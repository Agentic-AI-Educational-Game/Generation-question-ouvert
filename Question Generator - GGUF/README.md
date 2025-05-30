# 🧠 Question Generation API with Hugging Face Models

Une application **Flask** qui utilise des modèles GGUF de Hugging Face pour générer des questions pertinentes à partir d'un texte fourni.

---

## 🖼️ Stack Technologique

| Technologie | Description |
|-------------|-------------|
| **Python** | Langage principal de l'application |
| **Flask** | Framework web pour créer des API REST |
| **llama_cpp** | Bibliothèque pour exécuter des modèles GGUF localement |
| **Hugging Face Hub** | Téléchargement de modèles depuis le Hub HF |
| **SentencePiece** | Tokenizer pour modèles LLaMA (inclus dans llama_cpp) |

---

## 🚀 Fonctionnement

### Étapes du processus :

1. **📥 Téléchargement du modèle** :  
   Au premier démarrage, l'application télécharge le modèle GGUF depuis Hugging Face Hub.

2. **⚙️ Initialisation** :  
   Le modèle est chargé en mémoire avec une configuration optimisée pour la génération de questions.

3. **📝 Génération de questions** :  
   Quand l'API reçoit un texte :
   - Prépare un prompt structuré en français
   - Exécute le modèle avec un stream de tokens
   - Extrait la question du format de réponse spécifié

4. **📤 Retour du résultat** :  
   Renvoie la question générée au format JSON avec :
   - La question extraite
   - La réponse brute du modèle

---

## 📮 Point de Terminaison API

### `POST /generate_question`

**Requête JSON :**
```json
{
  "text": "Le cycle de l'eau comprend trois étapes principales : évaporation, condensation et précipitation. L'évaporation se produit lorsque l'eau des océans se transforme en vapeur..."
}
```

**Réponse JSON :**
```json
{
  "question": "Quelles sont les trois étapes principales du cycle de l'eau ?",
  "raw": "**Question :** Quelles sont les trois étapes principales du cycle de l'eau ?"
}
```

---

## ⚙️ Configuration & Exécution

1. Installez les dépendances :
```bash
pip install flask huggingface-hub llama-cpp-python
```

2. Exécutez l'application :
```bash
python app.py
```

3. L'application sera accessible sur :
```
http://localhost:5000
```

---

## 📁 Structure des Fichiers

```
.
├── app.py                # Application principale
├── models/               # Dossier des modèles téléchargés
│   └── finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf
```

---

## ⚠️ Notes Importantes

- **Téléchargement initial** : Le premier démarrage peut prendre plusieurs minutes pour télécharger le modèle (~2-4GB)
- **Mémoire requise** : L'application nécessite au moins 4GB de RAM
- **Modèle utilisé** : `zinec/finetuned-qwen-fr` (Qwen 0.5B quantifié en 8-bit)
- **Langue** : Spécialement conçu pour générer des questions en français

---

## 💡 Cas d'Usage

**Éducation** :  
- Génération automatique de questions d'évaluation  
- Création de questionnaires à partir de contenus pédagogiques  
- Outil d'aide à la préparation d'examens  

**Contenu** :  
- Génération de FAQ à partir d'articles  
- Création de quiz interactifs  
- Augmentation de datasets pour NLP
