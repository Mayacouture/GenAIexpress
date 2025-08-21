from __future__ import annotations
import re
import os
from pathlib import Path
from typing import List, Tuple

try:
	import tiktoken  # type: ignore
	_TIK = tiktoken.get_encoding("cl100k_base")
except Exception:
	_TIK = None

from pypdf import PdfReader

def safe_filename(name: str) -> str:
	name = re.sub(r"[^\w\-_. ]+", "_", name).strip()
	return re.sub(r"\s+", "_", name)


def count_tokens(text: str) -> int:
	if _TIK is None:
		# Rough fallback: ~4 chars/token
		return max(1, len(text) // 4)
	return len(_TIK.encode(text))


def word_count(text: str) -> int:
	return len(re.findall(r"\b\w+\b", text))


def chunk_text(text: str, chunk_tokens: int, overlap_tokens: int) -> List[str]:
	if not text:
		return []
	if _TIK is None:
		# Character-based fallback approximating tokens (4 chars/token)
		approx_chars = chunk_tokens * 4
		overlap_chars = overlap_tokens * 4
		chunks = []
		start = 0
		while start < len(text):
			end = min(len(text), start + approx_chars)
			chunks.append(text[start:end])
			if end == len(text):
				break
			start = max(0, end - overlap_chars)
		return chunks
	# Token-aware chunking
	tokens = _TIK.encode(text)
	chunks = []
	start = 0
	while start < len(tokens):
		end = min(len(tokens), start + chunk_tokens)
		chunk_text = _TIK.decode(tokens[start:end])
		chunks.append(chunk_text)
		if end == len(tokens):
			break
		start = max(0, end - overlap_tokens)
	return chunks


def extract_text_from_pdf(pdf_path: Path) -> str:
	reader = PdfReader(str(pdf_path))
	texts = []
	for page in reader.pages:
		try:
			texts.append(page.extract_text() or "")
		except Exception:
			continue
	return "\n\n".join(texts)


def read_text_file(path: Path) -> str:
	try:
		return path.read_text(encoding="utf-8")
	except UnicodeDecodeError:
		return path.read_text(encoding="latin-1", errors="ignore")


def write_bytes(path: Path, data: bytes) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with open(path, "wb") as f:
		f.write(data)


def now_timestamp() -> str:
	import datetime as _dt
	return _dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def clean_text(text: str) -> str:
	# Normalize whitespace
	text = re.sub(r"\r\n?|\n", "\n", text)
	text = re.sub(r"\s+", " ", text).strip()
	return text