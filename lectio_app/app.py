import streamlit as st

from src import config
from src.ui import header, disclaimer, error_box
from src.retrieval import ingest_streamlit_uploads, reset_index
from src.pipeline import generate_meditation
from src.feedback import append_feedback
from src.config import GenerationSettings, logger


header()
disclaimer()

# Sidebar controls
with st.sidebar:
	st.header("Corpus & Paramètres")
	st.caption("Charge des fichiers (txt, md, pdf). Aucun texte protégé n'est inclus par défaut.")
	source_choice = st.selectbox(
		"Tag de la source pour cet import",
		[
			("Générique (autres textes)", config.SOURCE_USER_GENERIC),
			("Maria Valtorta (fichiers importés)", config.SOURCE_VALTORTA_USER),
			("Bible (domaine public)", config.SOURCE_BIBLE_PUBLIC),
		],
		format_func=lambda x: x[0],
		index=0,
	)
	uploaded = st.file_uploader("Importer fichiers", type=["txt", "md", "pdf"], accept_multiple_files=True)
	col_btn1, col_btn2 = st.columns(2)
	with col_btn1:
		if st.button("Indexer / Mettre à jour le corpus", use_container_width=True):
			if uploaded:
				with st.spinner("Indexation en cours..."):
					count, saved = ingest_streamlit_uploads(uploaded, config.DATA_DIR, source_tag=source_choice[1])
					st.success(f"Indexé: {count} fragments depuis {len(saved)} fichiers")
			else:
				st.info("Aucun fichier sélectionné")
	with col_btn2:
		if st.button("Réinitialiser l'index", use_container_width=True):
			reset_index()
			st.success("Index réinitialisé.")

	st.divider()
	use_bible = st.toggle("Utiliser Bible (domaine public)", value=True)
	use_valtorta = st.toggle("Inclure Maria Valtorta (fichiers importés)", value=False)

	st.subheader("Paramètres avancés")
	temp = st.slider("Température (créativité)", 0.0, 1.5, config.DEFAULT_TEMPERATURE, 0.05)
	length = st.slider("Longueur souhaitée (tokens)", 200, 1600, config.DEFAULT_LENGTH_TOKENS, 50)
	speed = st.slider("Vitesse audio", 0.6, 1.4, config.DEFAULT_AUDIO_SPEED, 0.05)

# Main inputs
st.subheader("Entre en présence")
emotion = st.text_input("Ton émotion actuelle", placeholder="peur, tristesse, colère...")
blessure = st.text_input("La blessure que tu veux présenter au Christ", placeholder="rejet, abandon, humiliation...")

generate_disabled = not emotion.strip() or not blessure.strip()

if st.button("Générer la méditation", type="primary", disabled=generate_disabled):
	if generate_disabled:
		st.stop()

	# Confirmation disclaimer
	confirm = st.checkbox("Je confirme avoir lu l'avertissement et souhaite continuer.")
	if not confirm:
		error_box("Merci de confirmer l'avertissement pour continuer.")
		st.stop()

	settings = GenerationSettings(
		temperature=float(temp),
		length_tokens=int(length),
		audio_speed=float(speed),
		use_bible_public=bool(use_bible),
		use_valtorta_user=bool(use_valtorta),
	)

	try:
		with st.spinner("Génération en cours (texte + audio)..."):
			md_text, audio_path, passages = generate_meditation(emotion, blessure, settings)
			st.markdown(md_text)
			if audio_path:
				st.audio(str(audio_path))
	except Exception as e:
		logger.exception("Generation failed")
		error_box(str(e))
		st.stop()

	st.divider()
	st.subheader("Comment te sens-tu maintenant ?")
	score = st.slider("Échelle", 1, 7, 4)
	comment = st.text_area("Un mot, une intuition à garder ?", height=120)
	if st.button("Envoyer le feedback"):
		append_feedback(
			emotion=emotion,
			blessure=blessure,
			length_tokens=settings.length_tokens,
			temperature=settings.temperature,
			audio_speed=settings.audio_speed,
			score_after=int(score),
			comment=comment,
		)
		st.toast("Merci pour ton retour !", icon="🙏")