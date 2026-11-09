import json
import faiss
import numpy as np

from pathlib import Path
from sentence_transformers import SentenceTransformer


class ChildNetKnowledgeBase:

    def __init__(self, project_root=None):

        if project_root is None:
            project_root = Path(__file__).resolve().parent.parent

        self.project_root = Path(project_root)

        processed = (
            self.project_root
            / "knowledge_base"
            / "processed"
        )

        chunks_path = processed / "knowledge_chunks.json"
        index_path = processed / "childnet_faiss.index"

        with open(chunks_path, encoding="utf-8") as f:
            self.chunks = json.load(f)

        self.index = faiss.read_index(str(index_path))

        if self.index.ntotal != len(self.chunks):
            raise ValueError(
                "FAISS index and knowledge chunks do not match."
            )

        self.model = SentenceTransformer(
            "intfloat/multilingual-e5-small"
        )

    def search(self, query, top_k=5):

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        top_k = min(max(int(top_k), 1), len(self.chunks))

        embedding = self.model.encode(
            ["query: " + query],
            normalize_embeddings=True
        )

        embedding = np.asarray(
            embedding,
            dtype="float32"
        )

        scores, indices = self.index.search(
            embedding,
            top_k
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx < 0:
                continue

            chunk = self.chunks[int(idx)]

            results.append({
                "chunk_id": chunk.get("chunk_id"),
                "document": chunk.get("document_name"),
                "page": chunk.get("page"),
                "score": float(score),
                "text": chunk.get("text", ""),
                "jurisdiction": (
                    chunk.get("jurisdiction") or "UNCLASSIFIED"
                ),
                "authority": chunk.get("authority", "Unknown"),
                "document_type": chunk.get("document_type", "reference"),
                "source_url": chunk.get("source_url"),
                "article_or_section": chunk.get("article_or_section")
            })

        return results


    def search_by_jurisdiction(
        self,
        query,
        jurisdiction="UAE",
        top_k=5
    ):
        """Search evidence within a selected jurisdiction."""

        top_k = max(1, int(top_k))

        results = self.search(
            query,
            top_k=len(self.chunks)
        )

        groups = {
            "UAE": {"UAE", "UAE_FEDERAL", "DUBAI"},
            "GLOBAL": {"GLOBAL", "INTERNATIONAL"},
            "DUBAI": {"DUBAI"}
        }

        jurisdiction = jurisdiction.upper()

        allowed = groups.get(
            jurisdiction,
            {jurisdiction}
        )

        filtered = [
            item
            for item in results
            if str(
                item.get("jurisdiction") or "UNCLASSIFIED"
            ).upper() in allowed
        ]

        return filtered[:top_k]
