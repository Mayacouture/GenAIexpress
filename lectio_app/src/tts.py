from __future__ import annotations
from pathlib import Path
from src import config
from src.utils import now_timestamp
from src.config import logger

VOICE_MAP = {
	"calm": "alloy",
	"gentle": "verse",
	"bright": "alloy",
}


def _change_speed_file(path: Path, speed: float) -> None:
	try:
		from pydub import AudioSegment  # Lazy import
		if abs(speed - 1.0) < 1e-3:
			return
		seg = AudioSegment.from_file(path, format="mp3")
		new_frame_rate = int(seg.frame_rate * speed)
		seg2 = seg._spawn(seg.raw_data, overrides={"frame_rate": new_frame_rate}).set_frame_rate(seg.frame_rate)
		seg2.export(path, format="mp3")
	except Exception as e:
		logger.warning(f"Audio speed adjustment skipped: {e}")


def synthesize(text: str, voice: str = "calm", speed: float = config.DEFAULT_AUDIO_SPEED) -> Path:
	from openai import OpenAI
	if not config.OPENAI_API_KEY:
		raise RuntimeError("OPENAI_API_KEY is not set in environment.")
	client = OpenAI()
	model = config.TTS_MODEL
	voice_name = VOICE_MAP.get(voice, "alloy")
	out_path = config.AUDIO_DIR / f"meditation_{now_timestamp()}.mp3"

	logger.info("Generating TTS audio via OpenAI API (streaming)")
	with client.audio.speech.with_streaming_response.create(
		model=model,
		voice=voice_name,
		input=text,
		format="mp3",
	) as response:
		response.stream_to_file(str(out_path))

	if abs(speed - 1.0) > 1e-3:
		_change_speed_file(out_path, speed)

	return out_path