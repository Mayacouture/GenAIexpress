import os
import json
import tiktoken
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import pickle
from datetime import datetime

try:
    import faiss
    USE_FAISS = True
except ImportError:
    USE_FAISS = False
    print("FAISS non disponible, utilisation de ChromaDB")

if not USE_FAISS:
    import chromadb
    from chromadb.config import Settings

from utils import load_env_vars, parse_bible_reference, parse_valtorta_reference

class RAGSystem:
    def __init__(self):
        self.config = load_env_vars()
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        self.chunk_size = self.config['chunk_size']
        self.chunk_overlap = self.config['chunk_overlap']
        
        # Initialiser l'index
        if USE_FAISS:
            self.index = None
            self.documents = []
            self.metadata = []
        else:
            self.chroma_client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./chroma_db"
            ))
            self.collection = self.chroma_client.get_or_create_collection("lectio_divina")
        
        self.index_file = "rag_index.pkl"
        self.metadata_file = "rag_metadata.json"
    
    def count_tokens(self, text: str) -> int:
        """Compte le nombre de tokens dans un texte"""
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Tuple[str, Dict]]:
        """Découpe un texte en chunks avec overlap"""
        tokens = self.encoding.encode(text)
        chunks = []
        
        i = 0
        while i < len(tokens):
            # Extraire le chunk
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Créer les métadonnées du chunk
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_id'] = len(chunks)
            chunk_metadata['token_count'] = len(chunk_tokens)
            chunk_metadata['start_token'] = i
            
            chunks.append((chunk_text, chunk_metadata))
            
            # Avancer avec overlap
            i += self.chunk_size - self.chunk_overlap
            
            # Éviter les chunks trop petits à la fin
            if i + self.chunk_size > len(tokens):
                break
        
        return chunks
    
    def load_bible_texts(self) -> List[Tuple[str, Dict]]:
        """Charge les textes bibliques depuis ./data/bible/"""
        bible_dir = Path("./data/bible")
        documents = []
        
        if not bible_dir.exists():
            print("Dossier ./data/bible/ non trouvé")
            return documents
        
        for file_path in bible_dir.rglob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraire les métadonnées du nom de fichier
                filename = file_path.stem
                metadata = {
                    'source': 'bible',
                    'filename': filename,
                    'filepath': str(file_path),
                    'content_type': 'bible_text'
                }
                
                # Essayer de parser des références du nom de fichier
                ref_info = parse_bible_reference(filename)
                if ref_info:
                    metadata.update(ref_info)
                
                documents.append((content, metadata))
                print(f"Chargé: {filename}")
                
            except Exception as e:
                print(f"Erreur lors du chargement de {file_path}: {e}")
        
        return documents
    
    def load_valtorta_texts(self) -> List[Tuple[str, Dict]]:
        """Charge les textes de Maria Valtorta depuis ./data/valtorta/"""
        valtorta_dir = Path("./data/valtorta")
        documents = []
        
        if not valtorta_dir.exists():
            print("Dossier ./data/valtorta/ non trouvé")
            return documents
        
        for file_path in valtorta_dir.rglob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraire les métadonnées du nom de fichier
                filename = file_path.stem
                metadata = {
                    'source': 'valtorta',
                    'filename': filename,
                    'filepath': str(file_path),
                    'content_type': 'valtorta_text'
                }
                
                # Essayer de parser des références du nom de fichier
                ref_info = parse_valtorta_reference(filename)
                if ref_info:
                    metadata.update(ref_info)
                
                documents.append((content, metadata))
                print(f"Chargé: {filename}")
                
            except Exception as e:
                print(f"Erreur lors du chargement de {file_path}: {e}")
        
        return documents
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Crée les embeddings pour une liste de textes"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.config['openai_api_key'])
            
            embeddings = []
            batch_size = 10  # Traiter par batch pour éviter les limites d'API
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = client.embeddings.create(
                    model=self.config['openai_embedding'],
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            
            return np.array(embeddings)
            
        except Exception as e:
            print(f"Erreur lors de la création des embeddings: {e}")
            # Fallback: embeddings aléatoires (pour test)
            return np.random.rand(len(texts), 1536)
    
    def build_index(self) -> Dict:
        """Construit l'index RAG complet"""
        print("Début de l'indexation...")
        start_time = datetime.now()
        
        # Charger tous les documents
        bible_docs = self.load_bible_texts()
        valtorta_docs = self.load_valtorta_texts()
        all_docs = bible_docs + valtorta_docs
        
        if not all_docs:
            print("Aucun document trouvé à indexer")
            return {'status': 'error', 'message': 'Aucun document trouvé'}
        
        print(f"Documents chargés: {len(bible_docs)} bibliques, {len(valtorta_docs)} Valtorta")
        
        # Découper en chunks
        all_chunks = []
        all_metadata = []
        
        for content, metadata in all_docs:
            chunks = self.chunk_text(content, metadata)
            all_chunks.extend([chunk[0] for chunk in chunks])
            all_metadata.extend([chunk[1] for chunk in chunks])
        
        print(f"Total chunks créés: {len(all_chunks)}")
        
        # Créer les embeddings
        print("Création des embeddings...")
        embeddings = self.create_embeddings(all_chunks)
        
        # Sauvegarder l'index
        if USE_FAISS:
            # Index FAISS
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner Product pour similarité cosinus
            self.index.add(embeddings.astype('float32'))
            
            # Sauvegarder
            faiss.write_index(self.index, "faiss_index.bin")
            self.documents = all_chunks
            self.metadata = all_metadata
            
            with open(self.index_file, 'wb') as f:
                pickle.dump({
                    'documents': all_chunks,
                    'metadata': all_metadata
                }, f)
        else:
            # Index ChromaDB
            ids = [f"chunk_{i}" for i in range(len(all_chunks))]
            
            # Ajouter les documents à ChromaDB
            self.collection.add(
                documents=all_chunks,
                metadatas=all_metadata,
                ids=ids
            )
        
        # Sauvegarder les métadonnées
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, ensure_ascii=False, indent=2)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        stats = {
            'status': 'success',
            'total_documents': len(all_docs),
            'total_chunks': len(all_chunks),
            'bible_chunks': len([m for m in all_metadata if m['source'] == 'bible']),
            'valtorta_chunks': len([m for m in all_metadata if m['source'] == 'valtorta']),
            'duration_seconds': duration,
            'index_size_mb': os.path.getsize("faiss_index.bin" if USE_FAISS else "./chroma_db") / (1024*1024)
        }
        
        print(f"Indexation terminée en {duration:.2f} secondes")
        print(f"Statistiques: {stats}")
        
        return stats
    
    def load_index(self) -> bool:
        """Charge l'index existant"""
        try:
            if USE_FAISS:
                if os.path.exists("faiss_index.bin") and os.path.exists(self.index_file):
                    self.index = faiss.read_index("faiss_index.bin")
                    with open(self.index_file, 'rb') as f:
                        data = pickle.load(f)
                        self.documents = data['documents']
                        self.metadata = data['metadata']
                    return True
            else:
                # ChromaDB se charge automatiquement
                return True
        except Exception as e:
            print(f"Erreur lors du chargement de l'index: {e}")
            return False
    
    def search(self, query: str, top_k: int = None, include_valtorta: bool = True) -> List[Dict]:
        """Recherche sémantique dans l'index"""
        if top_k is None:
            top_k = self.config['top_k_results']
        
        try:
            # Créer l'embedding de la requête
            query_embedding = self.create_embeddings([query])[0]
            
            if USE_FAISS:
                # Recherche FAISS
                scores, indices = self.index.search(
                    query_embedding.reshape(1, -1).astype('float32'), 
                    top_k
                )
                
                results = []
                for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                    if idx < len(self.documents):
                        metadata = self.metadata[idx].copy()
                        metadata['score'] = float(score)
                        metadata['content'] = self.documents[idx]
                        metadata['rank'] = i + 1
                        results.append(metadata)
            else:
                # Recherche ChromaDB
                results_raw = self.collection.query(
                    query_texts=[query],
                    n_results=top_k
                )
                
                results = []
                for i, (doc, metadata, score) in enumerate(zip(
                    results_raw['documents'][0],
                    results_raw['metadatas'][0],
                    results_raw['distances'][0]
                )):
                    metadata_copy = metadata.copy()
                    metadata_copy['score'] = 1 - score  # Convertir distance en score
                    metadata_copy['content'] = doc
                    metadata_copy['rank'] = i + 1
                    results.append(metadata_copy)
            
            # Filtrer par source si nécessaire
            if not include_valtorta:
                results = [r for r in results if r['source'] == 'bible']
            
            # Trier par score et limiter
            results.sort(key=lambda x: x['score'], reverse=True)
            results = results[:self.config['top_k_final']]
            
            return results
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []
    
    def get_index_stats(self) -> Dict:
        """Retourne les statistiques de l'index"""
        try:
            if USE_FAISS:
                if self.index is not None:
                    return {
                        'index_type': 'FAISS',
                        'total_vectors': self.index.ntotal,
                        'dimension': self.index.d,
                        'documents_loaded': len(self.documents) if hasattr(self, 'documents') else 0
                    }
            else:
                count = self.collection.count()
                return {
                    'index_type': 'ChromaDB',
                    'total_documents': count
                }
        except:
            pass
        
        return {'index_type': 'None', 'status': 'not_loaded'}