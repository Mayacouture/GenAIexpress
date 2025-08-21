# 🙏 Lectio Divina IA

**Méditations sonores personnalisées pour la guérison des blessures de l'âme**

Une application Streamlit qui génère des méditations audio personnalisées de type Lectio Divina, enracinées dans l'Écriture Sainte et les écrits de Maria Valtorta, pour accompagner spirituellement les personnes dans leurs moments de difficulté.

## ✨ Fonctionnalités

- 🎯 **Méditations personnalisées** basées sur l'émotion/blessure de l'utilisateur
- 🔍 **Recherche RAG** dans un corpus biblique et les écrits de Maria Valtorta
- 🎵 **Génération audio** via OpenAI TTS avec différentes voix
- 📖 **Structure Lectio Divina** : Lectio, Meditatio, Oratio, Contemplatio, Actio
- 📤 **Exports multiples** : MP3, PDF, Markdown
- 💭 **Feedback utilisateur** et historique des sessions
- ⚠️ **Détection de contenu à risque** avec ressources d'aide
- 🎛️ **Options personnalisables** : longueur, style, voix, fond sonore

## 🚀 Installation

### Prérequis

- Python 3.8+
- Clé API OpenAI

### 1. Cloner le repository

```bash
git clone <repository-url>
cd lectio-divina-ia
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration

1. Copier le fichier d'exemple :
```bash
cp .env.example .env
```

2. Éditer `.env` avec votre clé API OpenAI :
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING=text-embedding-3-large
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=alloy
```

### 4. Préparer les données

Placez vos textes bibliques dans `./data/bible/` et vos textes de Maria Valtorta dans `./data/valtorta/` au format `.txt`.

**Structure recommandée :**
```
data/
├── bible/
│   ├── psaume_23.txt
│   ├── matthieu_11_28.txt
│   └── ...
└── valtorta/
    ├── tome_1_chapitre_5.txt
    └── ...
```

### 5. Lancer l'application

```bash
streamlit run app.py
```

L'application sera accessible à l'adresse : http://localhost:8501

## 📖 Utilisation

### 1. Indexation du corpus

- Cliquez sur "🔄 Indexer / Mettre à jour le corpus" dans la sidebar
- Attendez que l'indexation soit terminée
- Vérifiez les statistiques affichées

### 2. Génération d'une méditation

1. **Saisissez votre émotion/blessure** dans le champ principal
2. **Configurez les options** dans la sidebar :
   - Longueur (Court/Moyen/Long)
   - Style (Simple/Standard/Contemplatif)
   - Inclure Maria Valtorta (oui/non)
   - Intention de prière (optionnel)
   - Voix TTS et débit
   - Fond sonore (optionnel)

3. **Cliquez sur "🎵 Générer la méditation sonore"**

### 3. Écoute et feedback

- **Écoutez** la méditation audio générée
- **Lisez** la transcription dans les accordéons
- **Consultez** les références et sources utilisées
- **Donnez votre feedback** (note + commentaire)
- **Déposez ce moment dans le Christ** si vous le souhaitez

### 4. Export

- **Téléchargez l'audio** en MP3
- **Exportez en PDF** ou **Markdown** via la sidebar
- **Consultez l'historique** de vos sessions

## 🏗️ Architecture

```
lectio-divina-ia/
├── app.py              # Application principale Streamlit
├── rag.py              # Système RAG (indexation et recherche)
├── tts.py              # Génération audio (OpenAI TTS)
├── export.py           # Export PDF/Markdown
├── utils.py            # Fonctions utilitaires
├── prompts.py          # Templates de prompts IA
├── requirements.txt    # Dépendances Python
├── .env.example        # Configuration d'exemple
├── data/               # Corpus de textes
│   ├── bible/          # Textes bibliques
│   └── valtorta/       # Écrits de Maria Valtorta
└── README.md           # Ce fichier
```

## 🔧 Configuration avancée

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Clé API OpenAI | Requis |
| `OPENAI_MODEL` | Modèle de génération | `gpt-4o-mini` |
| `OPENAI_EMBEDDING` | Modèle d'embedding | `text-embedding-3-large` |
| `OPENAI_TTS_MODEL` | Modèle TTS | `tts-1` |
| `OPENAI_TTS_VOICE` | Voix TTS | `alloy` |
| `CHUNK_SIZE` | Taille des chunks | `1000` |
| `CHUNK_OVERLAP` | Overlap des chunks | `150` |
| `TOP_K_RESULTS` | Nombre de résultats RAG | `12` |
| `TOP_K_FINAL` | Nombre final de résultats | `5` |

### Voix TTS disponibles

- `alloy` : Voix neutre et équilibrée
- `echo` : Voix masculine chaleureuse
- `fable` : Voix féminine douce
- `onyx` : Voix masculine profonde
- `nova` : Voix féminine claire
- `shimmer` : Voix féminine mélodieuse

## 🛡️ Sécurité et éthique

### Détection de contenu à risque

L'application détecte automatiquement les contenus sensibles (suicide, violence, désespoir) et propose :
- Des ressources d'aide appropriées
- Une prière de soutien personnalisée
- Des contacts d'urgence

### Ressources d'aide

- **SOS Amitié** : 09 72 39 40 50 (24h/24)
- **Croix-Rouge Écoute** : 0800 858 858
- **SOS Suicide Phénix** : 01 40 44 46 45

### Avertissement

⚠️ **Cette application ne remplace pas un avis médical ou psychologique.** En cas de détresse, consultez un professionnel de santé.

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **OpenAI** pour les API de génération et TTS
- **Streamlit** pour le framework d'interface
- **Maria Valtorta** pour ses écrits spirituels
- **La communauté open source** pour les bibliothèques utilisées

## 📞 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Consultez la documentation
- Contactez l'équipe de développement

---

*Que cette application vous aide à trouver la paix et la consolation dans votre cheminement spirituel.* 🙏
