#!/usr/bin/env python3
"""
Script de configuration pour Lectio Divina IA
Facilite l'installation et la configuration de l'application
"""

import os
import sys
import shutil
from pathlib import Path

def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis. Version actuelle:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def create_env_file():
    """Crée le fichier .env à partir de .env.example"""
    if os.path.exists('.env'):
        print("✅ Fichier .env existe déjà")
        return True
    
    if not os.path.exists('.env.example'):
        print("❌ Fichier .env.example non trouvé")
        return False
    
    try:
        shutil.copy('.env.example', '.env')
        print("✅ Fichier .env créé à partir de .env.example")
        print("⚠️  N'oubliez pas de configurer votre clé OpenAI dans .env")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de .env: {e}")
        return False

def create_directories():
    """Crée les répertoires nécessaires"""
    directories = [
        'data/bible',
        'data/valtorta',
        '.streamlit'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Répertoire {directory}/ créé")

def check_data_files():
    """Vérifie la présence de fichiers de données"""
    bible_files = list(Path('data/bible').glob('*.txt'))
    valtorta_files = list(Path('data/valtorta').glob('*.txt'))
    
    print(f"📁 Fichiers bibliques: {len(bible_files)}")
    print(f"📁 Fichiers Valtorta: {len(valtorta_files)}")
    
    if not bible_files and not valtorta_files:
        print("⚠️  Aucun fichier de données trouvé. Ajoutez vos textes dans data/")
    
    return len(bible_files) > 0 or len(valtorta_files) > 0

def install_dependencies():
    """Installe les dépendances"""
    print("\n📦 Installation des dépendances...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dépendances installées avec succès")
            return True
        else:
            print(f"❌ Erreur lors de l'installation: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("💡 Essayez: pip install -r requirements.txt")
        return False

def test_installation():
    """Teste l'installation"""
    print("\n🧪 Test de l'installation...")
    
    try:
        # Test des imports
        from utils import load_env_vars
        print("✅ utils.py - OK")
        
        from rag import RAGSystem
        print("✅ rag.py - OK")
        
        from tts import TTSSystem
        print("✅ tts.py - OK")
        
        from export import ExportSystem
        print("✅ export.py - OK")
        
        from prompts import SYSTEM_PROMPT
        print("✅ prompts.py - OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import manquant: {e}")
        print("💡 Installez les dépendances: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale de configuration"""
    print("🚀 Configuration de Lectio Divina IA")
    print("=" * 40)
    
    # Vérifications de base
    if not check_python_version():
        sys.exit(1)
    
    # Création des fichiers et répertoires
    create_env_file()
    create_directories()
    check_data_files()
    
    # Installation des dépendances
    print("\n" + "=" * 40)
    install_choice = input("Installer les dépendances maintenant ? (o/n): ").lower()
    
    if install_choice in ['o', 'oui', 'y', 'yes']:
        if install_dependencies():
            # Test de l'installation
            if test_installation():
                print("\n🎉 Configuration terminée avec succès !")
                print("\n📋 Prochaines étapes:")
                print("1. Configurez votre clé OpenAI dans le fichier .env")
                print("2. Ajoutez vos textes bibliques et Valtorta dans data/")
                print("3. Lancez l'application: streamlit run app.py")
                print("4. Indexez le corpus dans l'interface")
            else:
                print("\n⚠️  Installation terminée mais certains tests ont échoué")
        else:
            print("\n❌ Échec de l'installation des dépendances")
            print("💡 Installez manuellement: pip install -r requirements.txt")
    else:
        print("\n⚠️  Dépendances non installées")
        print("💡 Installez manuellement: pip install -r requirements.txt")
    
    print("\n📚 Documentation: README.md")
    print("🎯 Démonstration: python3 demo.py")

if __name__ == "__main__":
    main()