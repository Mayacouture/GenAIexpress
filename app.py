import streamlit as st
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional
import json

# Import des modules personnalisés
from utils import (
    load_env_vars, create_session_id, save_session_history, 
    load_session_history, detect_risk_content, get_help_resources
)
from rag import RAGSystem
from tts import TTSSystem
from export import ExportSystem
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, PRAYER_OFFERING_PROMPT, RISK_CONTENT_PROMPT

# Configuration de la page
st.set_page_config(
    page_title="Lectio Divina IA",
    page_icon="🙏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E5A88 0%, #4A90E2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .warning-banner {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .meditation-section {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des systèmes
@st.cache_resource
def init_systems():
    """Initialise les systèmes RAG, TTS et Export"""
    try:
        rag_system = RAGSystem()
        tts_system = TTSSystem()
        export_system = ExportSystem()
        return rag_system, tts_system, export_system
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation: {e}")
        return None, None, None

# Variables de session
if 'meditation_generated' not in st.session_state:
    st.session_state.meditation_generated = False
if 'current_meditation' not in st.session_state:
    st.session_state.current_meditation = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = False

def main():
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>🙏 Lectio Divina IA</h1>
        <h3>Méditations sonores personnalisées</h3>
        <p>Accompagnement spirituel pour la guérison des blessures de l'âme</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Bandeau d'avertissement
    st.markdown("""
    <div class="warning-banner">
        <strong>⚠️ Accompagnement spirituel :</strong> Cette application ne remplace pas un avis médical ou psychologique. 
        En cas de détresse, n'hésitez pas à demander de l'aide professionnelle.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialisation des systèmes
    rag_system, tts_system, export_system = init_systems()
    
    if rag_system is None:
        st.error("Impossible d'initialiser les systèmes. Vérifiez votre configuration.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Bouton d'indexation
        st.subheader("Indexation du corpus")
        if st.button("🔄 Indexer / Mettre à jour le corpus"):
            with st.spinner("Indexation en cours..."):
                stats = rag_system.build_index()
                if stats['status'] == 'success':
                    st.success(f"Indexation terminée ! {stats['total_chunks']} chunks créés en {stats['duration_seconds']:.1f}s")
                else:
                    st.error(f"Erreur d'indexation: {stats.get('message', 'Erreur inconnue')}")
        
        # Statistiques de l'index
        index_stats = rag_system.get_index_stats()
        if index_stats['status'] != 'not_loaded':
            st.info(f"Index: {index_stats['index_type']} - {index_stats.get('total_documents', 'N/A')} documents")
        
        st.divider()
        
        # Options de génération
        st.subheader("🎛️ Options de génération")
        
        length_options = {
            "Court (~3 min)": "court",
            "Moyen (~6 min)": "moyen", 
            "Long (~10 min)": "long"
        }
        length = st.selectbox("Longueur", list(length_options.keys()), index=1)
        
        style_options = {
            "Simple": "simple",
            "Standard": "standard",
            "Contemplatif": "contemplatif"
        }
        style = st.selectbox("Style", list(style_options.keys()), index=1)
        
        include_valtorta = st.checkbox("Inclure Maria Valtorta", value=True)
        
        prayer_intention = st.text_area("Intention de prière (optionnel)", 
                                       placeholder="Votre intention personnelle...")
        
        st.divider()
        
        # Options audio
        st.subheader("🔊 Options audio")
        
        voice_options = tts_system.list_available_voices()
        selected_voice = st.selectbox(
            "Voix TTS",
            list(voice_options.keys()),
            format_func=lambda x: f"{x} - {voice_options[x]}",
            index=0
        )
        
        speed_options = {
            "Lent": 0.8,
            "Normal": 1.0,
            "Rapide": 1.2
        }
        speed = st.selectbox("Débit", list(speed_options.keys()), index=1)
        
        background_music = st.checkbox("Fond sonore discret", value=False)
        
        st.divider()
        
        # Boutons d'export
        st.subheader("📤 Export")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Export PDF") and st.session_state.current_meditation:
                with st.spinner("Génération du PDF..."):
                    pdf_path = export_system.export_to_pdf(st.session_state.current_meditation)
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 Télécharger PDF",
                            data=f.read(),
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf"
                        )
        
        with col2:
            if st.button("📝 Export Markdown") and st.session_state.current_meditation:
                with st.spinner("Génération du Markdown..."):
                    md_path = export_system.export_to_markdown(st.session_state.current_meditation)
                    with open(md_path, "r", encoding='utf-8') as f:
                        st.download_button(
                            label="📥 Télécharger MD",
                            data=f.read(),
                            file_name=os.path.basename(md_path),
                            mime="text/markdown"
                        )
    
    # Zone principale
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎯 Votre méditation personnalisée")
        
        # Champ émotion/blessure
        emotion = st.text_input(
            "Ton émotion / blessure *",
            placeholder="Ex: peur, abandon, culpabilité, colère, tristesse, rejet...",
            help="Décrivez l'émotion ou la blessure que vous souhaitez accompagner"
        )
        
        if emotion:
            # Vérification du contenu à risque
            is_risk, risk_message = detect_risk_content(emotion)
            if is_risk:
                st.warning(f"⚠️ {risk_message}")
                st.info(get_help_resources())
                
                if st.button("🙏 Générer une prière de soutien"):
                    with st.spinner("Génération de la prière..."):
                        try:
                            from openai import OpenAI
                            client = OpenAI(api_key=load_env_vars()['openai_api_key'])
                            
                            response = client.chat.completions.create(
                                model=load_env_vars()['openai_model'],
                                messages=[
                                    {"role": "system", "content": SYSTEM_PROMPT},
                                    {"role": "user", "content": RISK_CONTENT_PROMPT + f"\n\nContenu partagé: {emotion}"}
                                ],
                                max_tokens=300,
                                temperature=0.7
                            )
                            
                            prayer_text = response.choices[0].message.content
                            st.markdown("### 🙏 Prière de soutien")
                            st.write(prayer_text)
                            
                        except Exception as e:
                            st.error(f"Erreur lors de la génération: {e}")
            
            # Bouton de génération
            if st.button("🎵 Générer la méditation sonore", type="primary"):
                if not emotion.strip():
                    st.error("Veuillez saisir une émotion ou blessure.")
                else:
                    generate_meditation(emotion, rag_system, tts_system, length_options[length], 
                                     style_options[style], include_valtorta, prayer_intention,
                                     selected_voice, speed_options[speed], background_music)
        
        # Affichage de la méditation générée
        if st.session_state.meditation_generated and st.session_state.current_meditation:
            display_meditation(st.session_state.current_meditation, tts_system)
    
    with col2:
        st.header("📊 Historique")
        
        # Historique des sessions
        history = load_session_history()
        if history:
            for session in reversed(history[-10:]):  # 10 dernières sessions
                with st.expander(f"{session['emotion']} - {session['timestamp'][:10]}"):
                    st.write(f"**Style:** {session.get('style', 'Standard')}")
                    st.write(f"**Longueur:** {session.get('length', 'Moyen')}")
                    if session.get('feedback_score'):
                        st.write(f"**Feedback:** {session['feedback_score']}/5")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Re-générer", key=f"regenerate_{session['session_id']}"):
                            # Re-générer avec les mêmes paramètres
                            pass
                    with col2:
                        if st.button("▶️ Rejouer", key=f"replay_{session['session_id']}"):
                            # Rejouer l'audio
                            pass
        else:
            st.info("Aucune session enregistrée")

def generate_meditation(emotion, rag_system, tts_system, length, style, include_valtorta, 
                       prayer_intention, voice, speed, background_music):
    """Génère une méditation complète"""
    
    with st.spinner("🔍 Recherche de passages pertinents..."):
        # Recherche RAG
        query = f"méditation guérison {emotion} consolation espérance"
        rag_results = rag_system.search(query, include_valtorta=include_valtorta)
        
        if not rag_results:
            st.warning("Aucun passage pertinent trouvé. La méditation sera générée sans références spécifiques.")
            context = "Aucun passage spécifique fourni."
        else:
            context = "\n\n".join([
                f"**Source {i+1}** ({result['source']}):\n{result['content'][:300]}..."
                for i, result in enumerate(rag_results)
            ])
    
    with st.spinner("✍️ Génération de la méditation..."):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=load_env_vars()['openai_api_key'])
            
            # Construire le prompt utilisateur
            user_prompt = USER_PROMPT_TEMPLATE.format(
                emotion=emotion,
                style=style,
                length=length,
                include_valtorta="Oui" if include_valtorta else "Non",
                prayer_intention=prayer_intention or "Aucune intention spécifique",
                context=context
            )
            
            # Génération de la méditation
            response = client.chat.completions.create(
                model=load_env_vars()['openai_model'],
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            meditation_text = response.choices[0].message.content
            
            # Créer l'ID de session
            session_id = create_session_id(emotion)
            
            # Sauvegarder la méditation
            st.session_state.current_meditation = {
                'session_id': session_id,
                'emotion': emotion,
                'meditation_text': meditation_text,
                'references': extract_references(meditation_text),
                'rag_sources': rag_results,
                'session_info': {
                    'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'style': style,
                    'length': length,
                    'voice': voice,
                    'speed': speed
                }
            }
            
            st.session_state.meditation_generated = True
            
        except Exception as e:
            st.error(f"Erreur lors de la génération: {e}")
            return
    
    with st.spinner("🔊 Génération audio..."):
        # Génération audio
        audio_path = tts_system.text_to_speech(meditation_text, voice, speed)
        
        if audio_path:
            # Ajouter fond sonore si demandé
            if background_music:
                audio_path = tts_system.add_background_music(audio_path, "ambient")
            
            st.session_state.audio_path = audio_path
            st.success("🎵 Méditation audio générée avec succès !")
        else:
            st.warning("⚠️ Impossible de générer l'audio. Seule la transcription est disponible.")

def display_meditation(meditation_data, tts_system):
    """Affiche la méditation générée"""
    
    st.markdown("### 📖 Méditation générée")
    
    # Lecteur audio
    if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
        with open(st.session_state.audio_path, "rb") as f:
            st.audio(f.read(), format="audio/mp3")
        
        # Bouton de téléchargement
        with open(st.session_state.audio_path, "rb") as f:
            st.download_button(
                label="📥 Télécharger MP3",
                data=f.read(),
                file_name=f"meditation_{meditation_data['session_id']}.mp3",
                mime="audio/mp3"
            )
    
    # Transcription en accordéons
    meditation_text = meditation_data['meditation_text']
    
    # Diviser en sections
    sections = parse_meditation_sections(meditation_text)
    
    for section_title, section_content in sections:
        with st.expander(f"📖 {section_title}" if section_title else "📖 Méditation"):
            st.markdown(section_content)
    
    # Références
    if meditation_data['references']:
        with st.expander("📚 Références citées"):
            for ref in meditation_data['references']:
                st.write(f"• {ref}")
    
    # Sources RAG
    if meditation_data['rag_sources']:
        with st.expander("🔍 Sources RAG utilisées"):
            for i, source in enumerate(meditation_data['rag_sources'], 1):
                st.write(f"**Source {i}** (Score: {source.get('score', 'N/A'):.3f})")
                st.write(f"*{source.get('source', 'Inconnue')}*")
                if source.get('content'):
                    excerpt = source['content'][:150] + "..." if len(source['content']) > 150 else source['content']
                    st.write(f"*{excerpt}*")
                st.divider()
    
    # Feedback post-méditation
    if not st.session_state.feedback_submitted:
        st.markdown("### 💭 Comment te sens-tu après la méditation ?")
        
        feedback_score = st.slider("Note de satisfaction", 1, 5, 3, 
                                  help="1 = Pas satisfait, 5 = Très satisfait")
        
        feedback_text = st.text_area("Commentaire libre (optionnel)", 
                                    placeholder="Partagez vos ressentis...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Enregistrer le feedback"):
                # Sauvegarder le feedback
                meditation_data['feedback_score'] = feedback_score
                meditation_data['feedback_text'] = feedback_text
                
                save_session_history(meditation_data)
                st.session_state.feedback_submitted = True
                st.success("Feedback enregistré !")
        
        with col2:
            if st.button("🙏 Déposer ce moment dans le Christ"):
                generate_prayer_offering(meditation_data['emotion'])

def parse_meditation_sections(text):
    """Parse le texte de méditation en sections"""
    sections = []
    lines = text.split('\n')
    current_section = ""
    current_content = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('## '):
            # Nouvelle section
            if current_content:
                sections.append((current_section, '\n'.join(current_content)))
            current_section = line[3:]  # Enlever "## "
            current_content = []
        elif line:
            current_content.append(line)
    
    # Ajouter la dernière section
    if current_content:
        sections.append((current_section, '\n'.join(current_content)))
    
    return sections

def extract_references(text):
    """Extrait les références du texte de méditation"""
    references = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('## RÉFÉRENCES'):
            # Section des références
            continue
        elif line.startswith('##'):
            # Autre section, arrêter
            break
        elif line and line.startswith('-'):
            # Référence
            ref = line[1:].strip()
            if ref:
                references.append(ref)
    
    return references

def generate_prayer_offering(emotion):
    """Génère une prière d'offrande"""
    with st.spinner("Génération de la prière..."):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=load_env_vars()['openai_api_key'])
            
            response = client.chat.completions.create(
                model=load_env_vars()['openai_model'],
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": PRAYER_OFFERING_PROMPT + f"\n\nContexte: {emotion}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            prayer_text = response.choices[0].message.content
            
            st.markdown("### 🙏 Prière d'offrande")
            st.write(prayer_text)
            
        except Exception as e:
            st.error(f"Erreur lors de la génération de la prière: {e}")

if __name__ == "__main__":
    main()