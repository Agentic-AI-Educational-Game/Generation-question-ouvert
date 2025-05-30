
# 🧠 Évaluateur de Réponses d'Étudiants avec RAG

Une application **Flask** simple utilisant **LangChain**, **Groq LLM**, le stockage vectoriel **FAISS** et les embeddings **SentenceTransformer** pour :
- Générer des réponses à partir de textes fournis via la Génération Augmentée par Récupération (RAG)
- Évaluer les réponses d'étudiants avec des retours détaillés et une notation

---

## 🖼️ Stack Technologique

| Technologie | Description |
|-----------|-------------|
| **Python** | Langage principal de la logique backend |
| **Flask** | Framework web léger pour construire des APIs |
| **LangChain** | Framework pour créer des applications basées sur des LLMs |
| **Groq LLM** | Fournisseur de LLM à inférence rapide (utilise DeepSeek-LLaMA) |
| **FAISS** | Moteur de recherche vectorielle pour une récupération rapide |
| **SentenceTransformer** | Génère des embeddings pour le texte |

---

## 🚀 Fonctionnement

### Étapes :

1. **📂 Chargement des données** :  
   Charge un fichier `.jsonl` contenant les documents texte.

2. **🔍 Création des embeddings** :  
   Utilise `SentenceTransformer` (`all-MiniLM-L6-v2`) pour vectoriser les textes.

3. **📚 Construction du stockage FAISS** :  
   Stocke ces vecteurs dans un index FAISS pour une recherche sémantique rapide.

4. **🧠 Configuration de la chaîne RAG** :  
   Utilise `RetrievalQA` de **LangChain** avec le modèle **LLaMA de Groq** pour générer des réponses basées sur des questions.

5. **📈 Évaluation des réponses** :  
   Prend une réponse d'étudiant et :
   - Trouve la réponse correcte via RAG
   - Utilise Groq pour évaluer la réponse
   - Retourne une correction, une analyse des erreurs et une note sur 10

---

## 📮 Point de Terminaison API

### `POST /evaluate_answer`

**Requête JSON :**
```json
{
  "text": "The water cycle has three main stages...",
  "question": "What are the stages of the water cycle?",
  "student_answer": "Evaporation and precipitation only"
}
```

**Réponse JSON :**

```json
{
  "correction": "The student forgot to mention condensation.",
  "error": "Missing stage: condensation.",
  "evaluation": "6/10"
}
```

---

## ⚙️ Configuration

Créez un fichier `.env` :

```bash
GROQ_API_KEY=votre_clé_api_groq_ici
```

Installez les dépendances :

```bash
pip install -r requirements.txt
```

Lancez le serveur :

```bash
python app.py
```

---

## 📁 Structure des Fichiers

```
.
├── app.py                # Application Flask principale
├── data.jsonl            # Données textuelles sources
├── .env                  # Stockage des clés API
└── requirements.txt      # Dépendances
```

---

## 📌 Notes

* Requiert une `GROQ_API_KEY` valide.
* Vérifiez que `data.jsonl` existe et contient au moins une entrée JSON avec un champ `"text"`.

---

## 💡 Cas d'Usage

**Éducation** : Les enseignants peuvent automatiser la correction de réponses, générer des retours et garantir l'équité grâce aux LLMs.
