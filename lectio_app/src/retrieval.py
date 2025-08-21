from __future__ import annotations
from typing import List, Dict, Iterable, Tuple, Optional
from pathlib import Path
import shutil

from chromadb import PersistentClient
from chromadb.utils import embedding_functions

from src import config
from src.utils import extract_text_from_pdf, read_text_file, chunk_text, clean_text, safe_filename
from src.config import logger


def _get_client() -> PersistentClient:
	return PersistentClient(path=str(config.VECTORDB_DIR))


def reset_index() -> None:
	client = _get_client()
	# Danger: remove entire persistence dir for a clean slate
	shutil.rmtree(config.VECTORDB_DIR, ignore_errors=True)
	config.VECTORDB_DIR.mkdir(parents=True, exist_ok=True)
	logger.info("Vector index reset completed")


def _get_collection():
	client = _get_client()
	return client.get_or_create_collection(
		name="lectio_collection",
	)


def _read_file_to_text(path: Path) -> str:
	suffix = path.suffix.lower()
	if suffix == ".pdf":
		return clean_text(extract_text_from_pdf(path))
	else:
		return clean_text(read_text_file(path))


def ingest_files(paths: List[Path], source_tag: str = config.SOURCE_USER_GENERIC) -> int:
	"""Ingest local files (txt, md, pdf). Returns number of chunks indexed."""
	col = _get_collection()
	all_texts: List[str] = []
	all_ids: List[str] = []
	all_metadatas: List[Dict] = []

	for path in paths:
		try:
			text = _read_file_to_text(path)
		except Exception as e:
			logger.exception(f"Failed to read {path}: {e}")
			continue
		if not text:
			continue
		chunks = chunk_text(text, config.CHUNK_TOKENS, config.CHUNK_OVERLAP_TOKENS)
		for i, ch in enumerate(chunks):
			cid = f"{safe_filename(path.name)}::{i}"
			meta = {
				"source": source_tag,
				"path": str(path),
				"reference": path.name,
				"title": path.stem,
			}
			all_texts.append(ch)
			all_ids.append(cid)
			all_metadatas.append(meta)

	# We embed client-side and provide embeddings for add()
	if not all_texts:
		return 0
	embs = _embed_texts(all_texts)
	col.add(documents=all_texts, embeddings=embs, metadatas=all_metadatas, ids=all_ids)
	logger.info(f"Indexed {len(all_texts)} chunks from {len(paths)} files")
	return len(all_texts)


def ingest_streamlit_uploads(files: Iterable, base_dir: Path, source_tag: str) -> Tuple[int, List[Path]]:
	"""Persist uploaded files to base_dir and ingest.
	Returns (chunks_count, saved_paths).
	"""
	saved_paths: List[Path] = []
	for f in files or []:
		# f is a Streamlit UploadedFile-like object
		dest = base_dir / safe_filename(f.name)
		with open(dest, "wb") as out:
			out.write(f.read())
		saved_paths.append(dest)
	count = ingest_files(saved_paths, source_tag=source_tag)
	return count, saved_paths


def _embed_texts(texts: List[str]) -> List[List[float]]:
	from openai import OpenAI
	client = OpenAI()
	resp = client.embeddings.create(model=config.EMBEDDING_MODEL, input=texts)
	return [d.embedding for d in resp.data]


def _embed_query(query: str) -> List[float]:
	return _embed_texts([query])[0]


def search(query: str, top_k: int = config.TOP_K, sources: Optional[List[str]] = None) -> List[Dict]:
	col = _get_collection()
	emb = _embed_query(query)
	where: Optional[Dict] = None
	if sources:
		where = {"source": {"$in": sources}}
	res = col.query(
		n_query_embeddings=[emb],
		n_results=top_k,
		where=where,
	)
	# Normalize results
	out: List[Dict] = []
	docs = res.get("documents") or []
	metas = res.get("metadatas") or []
	for docs_row, metas_row in zip(docs, metas):
		for doc, meta in zip(docs_row, metas_row):
			out.append({"content": doc, "metadata": meta})
	return out