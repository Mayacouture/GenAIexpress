import streamlit as st

APP_TITLE = "Lectio Divina IA"
DISCLAIMER = (
	"Contenu spirituel, non médical. En cas de souffrance aiguë, consulte un professionnel."
)


def header():
	st.set_page_config(page_title=APP_TITLE, layout="centered")
	st.title(APP_TITLE)


def disclaimer():
	with st.expander("Avertissement", expanded=True):
		st.info(DISCLAIMER)


def error_box(msg: str):
	st.error(msg)