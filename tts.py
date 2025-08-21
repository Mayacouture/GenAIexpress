import os
import tempfile
from typing import Optional, Dict
from openai import OpenAI
from utils import load_env_vars

class TTSSystem:
    def __init__(self):
        self.config = load_env_vars()
        self.client = OpenAI(api_key=self.config['openai_api_key'])
        self.model = self.config['openai_tts_model']
        self.default_voice = self.config['openai_tts_voice']
        
        # Voix disponibles
        self.available_voices = {
            'alloy': 'Voix neutre et équilibrée',
            'echo': 'Voix masculine chaleureuse',
            'fable': 'Voix féminine douce',
            'onyx': 'Voix masculine profonde',
            'nova': 'Voix féminine claire',
            'shimmer': 'Voix féminine mélodieuse'
        }
    
    def text_to_speech(self, text: str, voice: str = None, speed: float = 1.0) -> Optional[str]:
        """
        Convertit un texte en audio via OpenAI TTS
        
        Args:
            text: Le texte à convertir
            voice: La voix à utiliser (parmi les voix disponibles)
            speed: Vitesse de lecture (0.25 à 4.0)
        
        Returns:
            Chemin vers le fichier audio généré ou None en cas d'erreur
        """
        try:
            # Valider la voix
            if voice is None:
                voice = self.default_voice
            elif voice not in self.available_voices:
                print(f"Voix '{voice}' non disponible, utilisation de '{self.default_voice}'")
                voice = self.default_voice
            
            # Valider la vitesse
            speed = max(0.25, min(4.0, speed))
            
            # Préparer le texte pour TTS
            processed_text = self._prepare_text_for_tts(text)
            
            # Créer un fichier temporaire pour l'audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Appel à l'API OpenAI TTS
            response = self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=processed_text,
                speed=speed
            )
            
            # Sauvegarder l'audio
            response.stream_to_file(temp_path)
            
            print(f"Audio généré avec succès: {temp_path}")
            return temp_path
            
        except Exception as e:
            print(f"Erreur lors de la génération audio: {e}")
            return None
    
    def _prepare_text_for_tts(self, text: str) -> str:
        """
        Prépare le texte pour la synthèse vocale
        - Supprime les marqueurs de formatage
        - Ajoute des pauses appropriées
        - Gère les sections de la Lectio Divina
        """
        # Supprimer les marqueurs de formatage Markdown
        text = text.replace('**', '').replace('*', '').replace('#', '')
        
        # Ajouter des pauses pour les sections
        sections = ['LECTIO', 'MEDITATIO', 'ORATIO', 'CONTEMPLATIO', 'ACTIO']
        for section in sections:
            text = text.replace(f'## {section}', f'\n\n{section}\n\n')
            text = text.replace(f'##{section}', f'\n\n{section}\n\n')
        
        # Remplacer les marqueurs de pause par des silences
        text = text.replace('...', ' . . . ')
        
        # Nettoyer les espaces multiples
        import re
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def add_background_music(self, audio_path: str, background_type: str = "ambient") -> Optional[str]:
        """
        Ajoute un fond sonore à l'audio (si pydub est disponible)
        
        Args:
            audio_path: Chemin vers l'audio principal
            background_type: Type de fond sonore ("ambient", "nature", "silence")
        
        Returns:
            Chemin vers le fichier audio mixé ou l'original si échec
        """
        try:
            from pydub import AudioSegment
            from pydub.generators import WhiteNoise, Sine
            
            # Charger l'audio principal
            main_audio = AudioSegment.from_mp3(audio_path)
            
            # Créer le fond sonore
            if background_type == "ambient":
                # Bruit blanc très doux
                background = WhiteNoise().to_audio_segment(duration=len(main_audio))
                background = background - 30  # Réduire le volume de 30dB
            elif background_type == "nature":
                # Ton sinusoïdal très bas
                background = Sine(200).to_audio_segment(duration=len(main_audio))
                background = background - 25  # Réduire le volume de 25dB
            else:
                # Pas de fond sonore
                return audio_path
            
            # Mixer les audios
            mixed_audio = main_audio.overlay(background)
            
            # Sauvegarder le résultat
            output_path = audio_path.replace('.mp3', '_with_bg.mp3')
            mixed_audio.export(output_path, format='mp3')
            
            print(f"Fond sonore ajouté: {output_path}")
            return output_path
            
        except ImportError:
            print("Pydub non disponible, pas de fond sonore ajouté")
            return audio_path
        except Exception as e:
            print(f"Erreur lors de l'ajout du fond sonore: {e}")
            return audio_path
    
    def get_voice_info(self, voice: str) -> Dict[str, str]:
        """Retourne les informations sur une voix"""
        if voice in self.available_voices:
            return {
                'name': voice,
                'description': self.available_voices[voice],
                'available': True
            }
        else:
            return {
                'name': voice,
                'description': 'Voix non disponible',
                'available': False
            }
    
    def list_available_voices(self) -> Dict[str, str]:
        """Liste toutes les voix disponibles"""
        return self.available_voices.copy()
    
    def estimate_duration(self, text: str, speed: float = 1.0) -> float:
        """
        Estime la durée de l'audio basée sur le nombre de mots
        (estimation approximative: ~150 mots par minute à vitesse normale)
        """
        word_count = len(text.split())
        words_per_minute = 150 * speed
        duration_minutes = word_count / words_per_minute
        return duration_minutes