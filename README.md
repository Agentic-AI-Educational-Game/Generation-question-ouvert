![rWPZLgPRTv-CAkI7RbH3KA](https://github.com/user-attachments/assets/a230061d-90e4-46ef-823c-1ddf853fff83)


# Generation-question-ouvert
Generation question ouvert - flask + notebook

**Model used** : ( I use instruct because its smarter and also provide instruction using `<s>[INST][/INST]` read [doc](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1) )
* https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1

Tuto notebook :
* https://colab.research.google.com/drive/11S9gZqGz1VIugw-YJCsJmyAhecbDNHNM#scrollTo=WBWkBQkeIfWN

My notebook solution `<|im_start|> / <|im_end|>` : 
* [OLD](https://colab.research.google.com/drive/1yjNgzQqW48_A9pcppVPOl70LFK_8KnEt?authuser=1#scrollTo=UHDKEHrSMWpV)
* [NEW QWEN 1.5B GGUF](https://colab.research.google.com/drive/1mL0htJXRWE_n-d57aLsE0NyvNUo1xP6o?authuser=4#scrollTo=dZXQSgGQUD6n)

Test GGUF : 
* https://colab.research.google.com/drive/1EbDjglTp9_AQMtiUhX5URaQtTbQcnN1L?authuser=4#scrollTo=GPyUrcH7wCMO

# Requests/Responses :

## Generation des questions ouvert:
**Request:**
```json
{
    "text": "La plage et la montagne offrent des paysages contrastés. Sur la plage, il y a du sable doré, des vagues qui déferlent et des parasols colorés. Tandis qu\u0027\u00e0 la montagne, l\u0027air est frais, les cimes sont enneigées et les sentiers sinueux."
}
```

**Response:**
```json
{
    "question": "Quels sont les caractéristiques des paysages de la plage et de la montagne, respectivement, en fonction du texte ?",
    "raw": "**Question :** Quels sont les caractéristiques des paysages de la plage et de la montagne, respectivement, en fonction du texte ?"
}
```

## Correction des questions ouvert:
**Request:**
```json
{
    "text": "La plage et la montagne offrent des paysages contrastés. Sur la plage, il y a du sable doré, des vagues qui déferlent et des parasols colorés. Tandis qu\u0027\u00e0 la montagne, l\u0027air est frais, les cimes sont enneigées et les sentiers sinueux.",
    "student_answer": "Les paysages de la plage sont typiques avec des plages vert."
}
```
**Responses**
```json
{
    "correction": "Le texte original décrit des paysages contrastés, avec la plage offrant un sable doré, des vagues et des parasols colorés, tandis que la montagne offre un air frais, des cimes enneigées et des sentiers sinueux, ce qui fait de ces deux endroits des paysages très différents.",
    "erreur": "L'étudiant a mal interprété le texte original. Il a mis en avant des détails spécifiques à la plage (sable doré, vagues, parasols) au détriment de la description de la montagne (air frais, cimes enneigées, sentiers sinueux), ce qui n'est pas le contexte du paragraphe. Il a également omis de mentionner les paysages de la plage, ce qui manque de cohérence avec le contexte général.",
    "note": "6/10",
    "raw": "Note : 6/10\n\nErreur : L'étudiant a mal interprété le texte original. Il a mis en avant des détails spécifiques à la plage (sable doré, vagues, parasols) au détriment de la description de la montagne (air frais, cimes enneigées, sentiers sinueux), ce qui n'est pas le contexte du paragraphe. Il a également omis de mentionner les paysages de la plage, ce qui manque de cohérence avec le contexte général. \n\nCorrection : \nLe texte original décrit des paysages contrastés, avec la plage offrant un sable doré, des vagues et des parasols colorés, tandis que la montagne offre un air frais, des cimes enneigées et des sentiers sinueux, ce qui fait de ces deux endroits des paysages très différents."
}
```

## Instruction prompt 
### generation question ouvert 

```python
    prompt = f"""<|im_start|>system
You are an expert question-generation assistant.
When the user gives you a block of text, you must:
1. Generate exactly one relevant question in French based solely on the provided text.
2. Never add any comments, explanations, or additional questions.
3. Use the exact output format:

**Question :** [votre question]

Always follow this layout strictly, with no extra lines or sections.
<|im_end|>
<|im_start|>user
**Instruction :**
À partir *uniquement* du texte fourni, génère une seule question pertinente en français.
Ne dépasse pas une seule question. N’ajoute aucun commentaire ni explication.

Le format de sortie doit être strictement le suivant :
**Question :** [question générée]

**Texte :**
{input_text}
<|im_end|>
<|im_start|>assistant
"""
```


### correction des questions ouverts 

```python
    prompt = f"""<|im_start|>system
You are an expert error-correction assistant.
When the user gives you an original text and a student’s answer, you must:
1. Assign a score out of 10 and display it as
   Note : X/10
2. Point out the single most important mistake in one sentence prefixed with
   Erreur :
3. Provide the corrected statement prefixed with
   Correction :

Always follow this exact layout, with no extra lines or sections.
<|im_end|>
<|im_start|>user
Voici le texte original : {texte}.
Réponse de l’étudiant : {reponse_eleve}.
<|im_end|>
<|im_start|>assistant
"""
```
