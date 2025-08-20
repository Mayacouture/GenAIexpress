#!/usr/bin/env python3
"""
Démonstration de Lectio Divina IA
Simule le fonctionnement de l'application sans dépendances externes
"""

import json
from datetime import datetime

def demo_meditation_generation():
    """Démonstration de la génération d'une méditation"""
    
    print("🙏 LECTIO DIVINA IA - DÉMONSTRATION")
    print("=" * 50)
    
    # Simulation d'une émotion utilisateur
    emotion = "peur et anxiété"
    print(f"🎯 Émotion/Blessure: {emotion}")
    
    # Simulation de la recherche RAG
    print("\n🔍 Recherche de passages pertinents...")
    rag_results = [
        {
            "source": "bible",
            "content": "N'ayez pas peur, car je suis avec vous; ne vous inquiétez pas, car je suis votre Dieu. Je vous fortifierai, je vous aiderai, je vous soutiendrai de ma droite triomphante.",
            "score": 0.95,
            "reference": "Isaïe 41:10"
        },
        {
            "source": "bible", 
            "content": "Venez à moi, vous tous qui êtes fatigués et chargés, et je vous donnerai du repos.",
            "score": 0.92,
            "reference": "Matthieu 11:28"
        },
        {
            "source": "valtorta",
            "content": "Dans les moments de plus grande détresse, quand l'âme se sent abandonnée et que les ténèbres semblent l'envahir, c'est alors que la lumière divine se manifeste avec le plus d'éclat.",
            "score": 0.88,
            "reference": "Tome 1, Chapitre 5"
        }
    ]
    
    for i, result in enumerate(rag_results, 1):
        print(f"  Source {i}: {result['reference']} (Score: {result['score']:.2f})")
    
    # Simulation de la génération de méditation
    print("\n✍️ Génération de la méditation...")
    
    meditation = {
        "session_id": "demo_123",
        "emotion": emotion,
        "meditation_text": """## LECTIO

« N'ayez pas peur, car je suis avec vous; ne vous inquiétez pas, car je suis votre Dieu. Je vous fortifierai, je vous aiderai, je vous soutiendrai de ma droite triomphante. » (Isaïe 41:10)

« Venez à moi, vous tous qui êtes fatigués et chargés, et je vous donnerai du repos. » (Matthieu 11:28)

## MEDITATIO

Chère âme qui traverse l'épreuve de la peur et de l'anxiété, sache que tu n'es pas seule. Le Seigneur lui-même te parle à travers ces paroles d'Isaïe, te rappelant qu'Il est présent à tes côtés, même dans les moments les plus sombres.

La peur est une émotion humaine naturelle, mais elle ne doit pas nous paralyser. Jésus nous invite à venir à Lui avec nos fardeaux, nos inquiétudes, nos angoisses. Il ne promet pas de nous épargner les difficultés, mais Il nous assure de Sa présence et de Sa force.

## ORATIO

Seigneur Jésus, je viens à Toi avec mon cœur lourd de peur et d'anxiété. Tu connais mes inquiétudes, mes doutes, mes moments de faiblesse. Je Te confie tout cela, sachant que Tu es mon refuge et ma force.

Aide-moi à me souvenir que Tu es toujours avec moi, même quand je ne Te sens pas. Donne-moi la paix qui dépasse toute compréhension, cette paix que seul Tu peux offrir. Fortifie ma foi et aide-moi à Te faire confiance en toutes circonstances.

## CONTEMPLATIO

Prends un moment pour te laisser bercer par ces paroles... Respire profondément et laisse la paix du Christ envahir ton cœur... Sache que tu es aimé(e) et que tu n'es jamais seul(e)...

## ACTIO

1. Prends 5 minutes chaque jour pour prier et méditer ces versets
2. Note tes peurs dans un journal et confie-les au Seigneur
3. Partage tes inquiétudes avec une personne de confiance
4. Pratique la respiration consciente quand l'anxiété monte
5. Remplace les pensées négatives par des versets bibliques

## RÉFÉRENCES

- Isaïe 41:10
- Matthieu 11:28
- Tome 1, Chapitre 5 (Maria Valtorta)""",
        "references": ["Isaïe 41:10", "Matthieu 11:28", "Tome 1, Chapitre 5 (Maria Valtorta)"],
        "rag_sources": rag_results,
        "session_info": {
            "date": datetime.now().strftime('%d/%m/%Y %H:%M'),
            "style": "standard",
            "length": "moyen",
            "voice": "alloy",
            "speed": 1.0
        }
    }
    
    print("✅ Méditation générée avec succès !")
    
    # Affichage de la méditation
    print("\n📖 MÉDITATION GÉNÉRÉE")
    print("-" * 30)
    
    sections = meditation["meditation_text"].split("## ")
    for section in sections[1:]:  # Ignorer la première section vide
        lines = section.strip().split("\n")
        title = lines[0]
        content = "\n".join(lines[1:])
        
        print(f"\n🔸 {title}")
        print("-" * 20)
        print(content[:200] + "..." if len(content) > 200 else content)
    
    # Simulation de l'export
    print("\n📤 EXPORT")
    print("-" * 15)
    print("✅ Audio MP3 généré: meditation_demo_123.mp3")
    print("✅ PDF généré: meditation_demo_123.pdf")
    print("✅ Markdown généré: meditation_demo_123.md")
    
    # Simulation du feedback
    print("\n💭 FEEDBACK UTILISATEUR")
    print("-" * 25)
    feedback = {
        "score": 5,
        "comment": "Cette méditation m'a vraiment aidé à trouver la paix. Les passages bibliques étaient parfaitement choisis pour ma situation."
    }
    print(f"Note: {feedback['score']}/5")
    print(f"Commentaire: {feedback['comment']}")
    
    # Sauvegarde de la session
    session_data = {
        "timestamp": datetime.now().isoformat(),
        "session_id": meditation["session_id"],
        "emotion": emotion,
        "style": "standard",
        "length": "moyen",
        "feedback_score": feedback["score"],
        "feedback_text": feedback["comment"]
    }
    
    with open("demo_session.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    print("\n💾 Session sauvegardée dans demo_session.json")
    
    return meditation

def demo_interface():
    """Simulation de l'interface utilisateur"""
    
    print("\n🖥️ SIMULATION DE L'INTERFACE STREAMLIT")
    print("=" * 45)
    
    print("""
┌─────────────────────────────────────────────────────────┐
│                    LECTIO DIVINA IA                     │
│              Méditations sonores personnalisées         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ ⚙️ CONFIGURATION (Sidebar)                              │
│                                                         │
│ 🔄 Indexer / Mettre à jour le corpus                   │
│                                                         │
│ 🎛️ Options de génération:                              │
│    • Longueur: Moyen (~6 min)                          │
│    • Style: Standard                                   │
│    • Inclure Valtorta: ✓                               │
│    • Intention: Trouver la paix                        │
│                                                         │
│ 🔊 Options audio:                                       │
│    • Voix: alloy - Voix neutre                         │
│    • Débit: Normal                                     │
│    • Fond sonore: ✗                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🎯 VOTRE MÉDITATION PERSONNALISÉE                      │
│                                                         │
│ Ton émotion / blessure: [peur et anxiété]              │
│                                                         │
│ [🎵 Générer la méditation sonore]                      │
│                                                         │
│ 📖 MÉDITATION GÉNÉRÉE                                  │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🎵 [Lecteur audio]                                  │ │
│ │ [📥 Télécharger MP3]                                │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 📖 LECTIO [▼]                                          │
│ 📖 MEDITATIO [▼]                                       │
│ 📖 ORATIO [▼]                                          │
│ 📖 CONTEMPLATIO [▼]                                    │
│ 📖 ACTIO [▼]                                           │
│                                                         │
│ 💭 Comment te sens-tu après la méditation ?            │
│ Note: [●●●●●] 5/5                                      │
│ Commentaire: [Zone de texte]                           │
│                                                         │
│ [💾 Enregistrer] [🙏 Déposer dans le Christ]           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 📊 HISTORIQUE                                           │
│                                                         │
│ peur et anxiété - 2024-01-15 [▼]                       │
│   Style: Standard | Longueur: Moyen | Feedback: 5/5    │
│   [🔄 Re-générer] [▶️ Rejouer]                         │
└─────────────────────────────────────────────────────────┘
""")

def main():
    """Fonction principale de démonstration"""
    
    # Génération de la méditation
    meditation = demo_meditation_generation()
    
    # Simulation de l'interface
    demo_interface()
    
    print("\n🎉 DÉMONSTRATION TERMINÉE")
    print("=" * 30)
    print("""
Pour utiliser l'application complète :

1. Installez les dépendances :
   pip install -r requirements.txt

2. Configurez votre clé OpenAI dans .env

3. Lancez l'application :
   streamlit run app.py

4. Ajoutez vos textes bibliques et Valtorta dans data/

5. Indexez le corpus et générez vos méditations !
""")

if __name__ == "__main__":
    main()