#!/usr/bin/env python3
"""
Script de test pour Lectio Divina IA
Vérifie que tous les modules fonctionnent correctement
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Teste l'import des modules"""
    print("🔍 Test des imports...")
    
    try:
        from utils import load_env_vars, create_session_id
        print("✅ utils.py - OK")
    except Exception as e:
        print(f"❌ utils.py - Erreur: {e}")
        return False
    
    try:
        from rag import RAGSystem
        print("✅ rag.py - OK")
    except Exception as e:
        print(f"❌ rag.py - Erreur: {e}")
        return False
    
    try:
        from tts import TTSSystem
        print("✅ tts.py - OK")
    except Exception as e:
        print(f"❌ tts.py - Erreur: {e}")
        return False
    
    try:
        from export import ExportSystem
        print("✅ export.py - OK")
    except Exception as e:
        print(f"❌ export.py - Erreur: {e}")
        return False
    
    try:
        from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
        print("✅ prompts.py - OK")
    except Exception as e:
        print(f"❌ prompts.py - Erreur: {e}")
        return False
    
    return True

def test_configuration():
    """Teste la configuration"""
    print("\n🔧 Test de la configuration...")
    
    # Vérifier le fichier .env
    if not os.path.exists('.env'):
        print("⚠️  Fichier .env non trouvé. Créez-le à partir de .env.example")
        return False
    
    try:
        from utils import load_env_vars
        config = load_env_vars()
        print("✅ Configuration chargée - OK")
        
        # Vérifier les variables requises
        required_vars = ['openai_api_key', 'openai_model', 'openai_embedding']
        for var in required_vars:
            if not config.get(var):
                print(f"❌ Variable manquante: {var}")
                return False
        
        print("✅ Variables d'environnement - OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        return False

def test_data_directories():
    """Teste les répertoires de données"""
    print("\n📁 Test des répertoires de données...")
    
    bible_dir = Path("./data/bible")
    valtorta_dir = Path("./data/valtorta")
    
    if not bible_dir.exists():
        print("⚠️  Répertoire ./data/bible/ non trouvé")
        return False
    
    if not valtorta_dir.exists():
        print("⚠️  Répertoire ./data/valtorta/ non trouvé")
        return False
    
    # Vérifier qu'il y a des fichiers
    bible_files = list(bible_dir.glob("*.txt"))
    valtorta_files = list(valtorta_dir.glob("*.txt"))
    
    if not bible_files:
        print("⚠️  Aucun fichier biblique trouvé dans ./data/bible/")
    else:
        print(f"✅ {len(bible_files)} fichiers bibliques trouvés")
    
    if not valtorta_files:
        print("⚠️  Aucun fichier Valtorta trouvé dans ./data/valtorta/")
    else:
        print(f"✅ {len(valtorta_files)} fichiers Valtorta trouvés")
    
    return True

def test_rag_system():
    """Teste le système RAG"""
    print("\n🔍 Test du système RAG...")
    
    try:
        from rag import RAGSystem
        rag = RAGSystem()
        print("✅ RAGSystem initialisé - OK")
        
        # Test de chargement d'index existant
        if rag.load_index():
            print("✅ Index existant chargé - OK")
        else:
            print("⚠️  Aucun index existant trouvé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur RAG: {e}")
        return False

def test_tts_system():
    """Teste le système TTS"""
    print("\n🔊 Test du système TTS...")
    
    try:
        from tts import TTSSystem
        tts = TTSSystem()
        print("✅ TTSSystem initialisé - OK")
        
        # Test des voix disponibles
        voices = tts.list_available_voices()
        print(f"✅ {len(voices)} voix disponibles")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur TTS: {e}")
        return False

def test_export_system():
    """Teste le système d'export"""
    print("\n📤 Test du système d'export...")
    
    try:
        from export import ExportSystem
        export = ExportSystem()
        print("✅ ExportSystem initialisé - OK")
        
        # Test de création d'un résumé
        test_data = {
            'emotion': 'test',
            'feedback_score': 4,
            'feedback_text': 'Test de feedback',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        summary = export.create_session_summary(test_data)
        if summary:
            print("✅ Création de résumé - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Export: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Test de Lectio Divina IA")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_configuration,
        test_data_directories,
        test_rag_system,
        test_tts_system,
        test_export_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'application est prête.")
        print("\n🚀 Pour lancer l'application:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()