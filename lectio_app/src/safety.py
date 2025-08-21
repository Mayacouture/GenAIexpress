from __future__ import annotations
from typing import List, Dict, Tuple
import re
from src import config
from src.utils import word_count

PROHIBITED_PATTERNS = [
	r"diagnostic(s)? médical(s)?",
	r"prescription(s)?",
	r"traitement(s)? médical(s)?",
	r"conseil(s)? médical(s)?",
]

ANTI_CHARITY_PATTERNS = [
	r"haine|violence|vengeance|malédiction",
]


def guardrails(user_text: str) -> Tuple[bool, str]:
	text = user_text.lower()
	for pat in PROHIBITED_PATTERNS:
		if re.search(pat, text):
			return False, (
				"Je ne peux pas fournir de diagnostics, prescriptions ou conseils médicaux. "
				"Si tu souffres de manière aiguë, contacte un professionnel de santé."
			)
	for pat in ANTI_CHARITY_PATTERNS:
		if re.search(pat, text):
			return False, (
				"Je ne peux pas aider pour une demande contraire à la charité chrétienne. Cherchons une voie de paix."
			)
	return True, ""


def enforce_citation_limit(passages: List[Dict], max_words: int | None = None) -> List[Dict]:
	"""Return passages with truncated 'content' to ensure cumulative word limit."""
	if max_words is None:
		max_words = config.MAX_CITATION_WORDS
	remaining = max_words
	result = []
	for p in passages:
		text = p.get("content", "")
		wc = word_count(text)
		if wc <= 0:
			continue
		if remaining <= 0:
			# Keep only metadata/reference, drop content
			result.append({"content": "", "metadata": p.get("metadata", {})})
			continue
		if wc <= remaining:
			result.append(p)
			remaining -= wc
		else:
			# Truncate words to remaining
			words = re.findall(r"\S+", text)
			trunc = " ".join(words[:remaining])
			result.append({"content": trunc, "metadata": p.get("metadata", {})})
			remaining = 0
	return result