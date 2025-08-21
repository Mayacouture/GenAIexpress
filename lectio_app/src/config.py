import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
import logging

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
VECTORDB_DIR = STORAGE_DIR / "vectordb"
AUDIO_DIR = STORAGE_DIR / "audio"
LOGS_DIR = STORAGE_DIR / "logs"

# Ensure directories exist at import time (safe for Streamlit reruns)
for _d in [DATA_DIR, STORAGE_DIR, VECTORDB_DIR, AUDIO_DIR, LOGS_DIR]:
	_d.mkdir(parents=True, exist_ok=True)

# Logging setup
LOG_FILE = LOGS_DIR / "app.log"
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
	handlers=[
		logging.FileHandler(LOG_FILE),
		logging.StreamHandler()
	]
)
logger = logging.getLogger("lectio")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Models
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

# App defaults
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_LENGTH_TOKENS = int(os.getenv("DEFAULT_LENGTH_TOKENS", "700"))
DEFAULT_AUDIO_SPEED = float(os.getenv("DEFAULT_AUDIO_SPEED", "1.0"))
MAX_CITATION_WORDS = int(os.getenv("MAX_CITATION_WORDS", "200"))

# Retrieval config
CHUNK_TOKENS = int(os.getenv("CHUNK_TOKENS", "700"))
CHUNK_OVERLAP_TOKENS = int(os.getenv("CHUNK_OVERLAP_TOKENS", "80"))
TOP_K = int(os.getenv("TOP_K", "8"))

# Tags
SOURCE_BIBLE_PUBLIC = "bible_public"
SOURCE_VALTORTA_USER = "valtorta_user"
SOURCE_USER_GENERIC = "user_upload"

@dataclass
class GenerationSettings:
	temperature: float = DEFAULT_TEMPERATURE
	length_tokens: int = DEFAULT_LENGTH_TOKENS
	audio_speed: float = DEFAULT_AUDIO_SPEED
	use_bible_public: bool = True
	use_valtorta_user: bool = False