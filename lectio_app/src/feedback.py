from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import Optional
from src import config
from src.utils import now_timestamp

FEEDBACK_CSV = config.DATA_DIR / "feedback.csv"


def append_feedback(
	emotion: str,
	blessure: str,
	length_tokens: int,
	temperature: float,
	audio_speed: float,
	score_after: int,
	comment: str,
) -> None:
	row = {
		"timestamp": now_timestamp(),
		"emotion": emotion,
		"blessure": blessure,
		"length_tokens": length_tokens,
		"temperature": temperature,
		"audio_speed": audio_speed,
		"score_after": score_after,
		"comment": comment,
	}
	if FEEDBACK_CSV.exists():
		df = pd.read_csv(FEEDBACK_CSV)
		new_df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
		new_df.to_csv(FEEDBACK_CSV, index=False)
	else:
		pd.DataFrame([row]).to_csv(FEEDBACK_CSV, index=False)