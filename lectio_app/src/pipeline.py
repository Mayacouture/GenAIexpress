from __future__ import annotations
from typing import Dict, List, Tuple

from src import config
from src.config import logger
from src import retrieval
from src import prompts
from src import safety
from src import tts


def _choose_sources(use_bible_public: bool, use_valtorta_user: bool) -> List[str]:
	sources: List[str] = []
	if use_bible_public:
		sources.append(config.SOURCE_BIBLE_PUBLIC)
	# User uploads always allowed
	sources.append(config.SOURCE_USER_GENERIC)
	if use_valtorta_user:
		sources.append(config.SOURCE_VALTORTA_USER)
	return sources


def generate_meditation(emotion: str, blessure: str, settings: config.GenerationSettings) -> Tuple[str, str, List[Dict]]:
	"""Return (markdown_text, audio_path, passages_used)."""
	ok, msg = safety.guardrails(f"{emotion} {blessure}")
	if not ok:
		raise ValueError(msg)

	query = f"Émotion: {emotion}. Blessure: {blessure}. Consolation chrétienne centrée sur le Christ."
	sources = _choose_sources(settings.use_bible_public, settings.use_valtorta_user)
	passages = retrieval.search(query=query, top_k=config.TOP_K, sources=sources)
	passages_limited = safety.enforce_citation_limit(passages, config.MAX_CITATION_WORDS)

	# Build prompt context
	context_lines = []
	for p in passages_limited:
		meta = p.get("metadata", {})
		ref = meta.get("reference") or meta.get("title") or meta.get("path") or "Source"
		content = p.get("content", "")
		if content:
			context_lines.append(f"- {ref}: \"{content}\"")
		else:
			context_lines.append(f"- {ref}")
	context_block = "\n".join(context_lines)

	system = prompts.SYSTEM_PROMPT
	user = (
		"Contexte: Passages (extraits brefs) pour inspiration, respecter limites:\n" + context_block + "\n\n" +
		prompts.build_user_prompt(emotion, blessure, settings.length_tokens, passages_limited)
	)

	# LLM call
	from openai import OpenAI
	if not config.OPENAI_API_KEY:
		raise RuntimeError("OPENAI_API_KEY is not set in environment.")
	client = OpenAI()
	logger.info("Calling LLM for meditation generation")
	resp = client.chat.completions.create(
		model=config.LLM_MODEL,
		messages=[
			{"role": "system", "content": system},
			{"role": "user", "content": user},
		],
		temperature=settings.temperature,
		max_tokens=settings.length_tokens,
	)
	text = resp.choices[0].message.content or ""

	# TTS
	audio_path = tts.synthesize(text=text, voice="calm", speed=settings.audio_speed)
	return text, str(audio_path), passages_limited