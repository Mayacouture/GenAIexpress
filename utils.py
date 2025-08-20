import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

def load_env_vars():
    """Charge les variables d'environnement depuis .env"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'OPENAI_API_KEY',
        'OPENAI_MODEL',
        'OPENAI_EMBEDDING',
        'OPENAI_TTS_MODEL',
        'OPENAI_TTS_VOICE'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Variables d'environnement manquantes: {missing_vars}")
    
    return {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'openai_model': os.getenv('OPENAI_MODEL'),
        'openai_embedding': os.getenv('OPENAI_EMBEDDING'),
        'openai_tts_model': os.getenv('OPENAI_TTS_MODEL'),
        'openai_tts_voice': os.getenv('OPENAI_TTS_VOICE'),
        'chunk_size': int(os.getenv('CHUNK_SIZE', 1000)),
        'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', 150)),
        'top_k_results': int(os.getenv('TOP_K_RESULTS', 12)),
        'top_k_final': int(os.getenv('TOP_K_FINAL', 5))
    }

def parse_bible_reference(text: str) -> Dict[str, str]:
    """Parse une référence biblique (ex: "Jean 3:16" ou "Psaume 23:1-3")"""
    # Patterns pour les références bibliques
    patterns = [
        r'(\w+)\s+(\d+):(\d+)(?:-(\d+))?',  # Jean 3:16 ou Jean 3:16-18
        r'(\w+)\s+(\d+):(\d+)-(\d+):(\d+)',  # Jean 3:16-17
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 4:  # Jean 3:16-18
                return {
                    'livre': groups[0],
                    'chapitre': groups[1],
                    'verset_debut': groups[2],
                    'verset_fin': groups[3] or groups[2]
                }
            elif len(groups) == 5:  # Jean 3:16-17
                return {
                    'livre': groups[0],
                    'chapitre_debut': groups[1],
                    'verset_debut': groups[2],
                    'chapitre_fin': groups[3],
                    'verset_fin': groups[4]
                }
    
    return {}

def parse_valtorta_reference(text: str) -> Dict[str, str]:
    """Parse une référence Valtorta (ex: "Tome 1, Chapitre 5, Section 2")"""
    patterns = [
        r'Tome\s+(\d+)[,\s]+Chapitre\s+(\d+)(?:[,\s]+Section\s+(\d+))?',
        r'(\d+)\s*,\s*(\d+)(?:\s*,\s*(\d+))?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            return {
                'tome': groups[0],
                'chapitre': groups[1],
                'section': groups[2] if len(groups) > 2 and groups[2] else None
            }
    
    return {}

def format_reference(metadata: Dict[str, str]) -> str:
    """Formate une référence pour l'affichage"""
    if metadata.get('source') == 'bible':
        livre = metadata.get('livre', '')
        chapitre = metadata.get('chapitre', '')
        verset = metadata.get('verset', '')
        if livre and chapitre and verset:
            return f"{livre} {chapitre}:{verset}"
    elif metadata.get('source') == 'valtorta':
        tome = metadata.get('tome', '')
        chapitre = metadata.get('chapitre', '')
        section = metadata.get('section', '')
        if tome and chapitre:
            ref = f"Tome {tome}, Chapitre {chapitre}"
            if section:
                ref += f", Section {section}"
            return ref
    
    return "Référence inconnue"

def create_session_id(emotion: str, timestamp: datetime = None) -> str:
    """Crée un ID unique pour une session de méditation"""
    if timestamp is None:
        timestamp = datetime.now()
    
    # Créer un hash basé sur l'émotion et le timestamp
    content = f"{emotion}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    return hashlib.md5(content.encode()).hexdigest()[:8]

def save_session_history(session_data: Dict):
    """Sauvegarde l'historique des sessions"""
    history_file = "session_history.json"
    
    # Charger l'historique existant
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    
    # Ajouter la nouvelle session
    history.append({
        'timestamp': datetime.now().isoformat(),
        'session_id': session_data.get('session_id'),
        'emotion': session_data.get('emotion'),
        'style': session_data.get('style'),
        'length': session_data.get('length'),
        'feedback_score': session_data.get('feedback_score'),
        'feedback_text': session_data.get('feedback_text')
    })
    
    # Garder seulement les 50 dernières sessions
    if len(history) > 50:
        history = history[-50:]
    
    # Sauvegarder
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_session_history() -> List[Dict]:
    """Charge l'historique des sessions"""
    history_file = "session_history.json"
    
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return []

def detect_risk_content(text: str) -> Tuple[bool, str]:
    """Détecte le contenu à risque (suicide, violence, etc.)"""
    risk_keywords = [
        'suicide', 'se tuer', 'mourir', 'finir', 'en finir',
        'violence', 'tuer', 'agresser', 'blesser',
        'désespoir', 'plus d\'espoir', 'plus de sens'
    ]
    
    text_lower = text.lower()
    detected_risks = [keyword for keyword in risk_keywords if keyword in text_lower]
    
    if detected_risks:
        return True, f"Contenu sensible détecté: {', '.join(detected_risks)}"
    
    return False, ""

def get_help_resources() -> str:
    """Retourne les ressources d'aide en cas de détresse"""
    return """
    **Si vous traversez une période difficile, n'hésitez pas à demander de l'aide :**
    
    📞 **SOS Amitié** : 09 72 39 40 50 (24h/24)
    📞 **Croix-Rouge Écoute** : 0800 858 858
    📞 **SOS Suicide Phénix** : 01 40 44 46 45
    
    💒 **Aumônerie catholique** : Contactez votre paroisse locale
    🏥 **Professionnels de santé** : Consultez votre médecin traitant
    
    *Ces ressources sont là pour vous accompagner avec bienveillance.*
    """