import json
import math
import re

from pathlib import Path
from collections import Counter


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

        with open(chunks_path, encoding="utf-8") as f:
            self.chunks = json.load(f)

        # Lightweight BM25 index
        # No PyTorch, SentenceTransformer, or FAISS loading

        self.doc_counts = []
        self.doc_lengths = []
        self.doc_frequency = Counter()

        for chunk in self.chunks:

            searchable_text = (
                str(chunk.get("document_name") or "")
                + " "
                + str(chunk.get("text") or "")
            )

            tokens = self._tokenize(searchable_text)

            counts = Counter(tokens)

            self.doc_counts.append(counts)
            self.doc_lengths.append(len(tokens))

            self.doc_frequency.update(counts.keys())

        self.total_docs = len(self.chunks)

        self.avg_doc_length = (
            sum(self.doc_lengths) / self.total_docs
            if self.total_docs
            else 1.0
        )

        print(
            f"CHILDNET 360 BM25 ready: "
            f"{self.total_docs} knowledge chunks."
        )

    @staticmethod
    def _tokenize(text):

        text = str(text or "").lower()

        # Basic Arabic normalization
        text = (
            text.replace("أ", "ا")
                .replace("إ", "ا")
                .replace("آ", "ا")
                .replace("ى", "ي")
                .replace("ة", "ه")
        )

        return re.findall(r"[^\W_]+", text, re.UNICODE)

    def _score(self, query_tokens, index):

        counts = self.doc_counts[index]
        doc_length = self.doc_lengths[index]

        k1 = 1.5
        b = 0.75

        score = 0.0

        for term in set(query_tokens):

            frequency = counts.get(term, 0)

            if frequency == 0:
                continue

            df = self.doc_frequency.get(term, 0)

            idf = math.log(
                1.0
                + (
                    self.total_docs - df + 0.5
                ) / (df + 0.5)
            )

            denominator = (
                frequency
                + k1 * (
                    1 - b
                    + b * doc_length / self.avg_doc_length
                )
            )

            score += (
                idf
                * frequency
                * (k1 + 1)
                / denominator
            )

        return score

    def _format_result(self, index, score):

        chunk = self.chunks[index]

        return {
            "chunk_id": chunk.get("chunk_id"),
            "document": chunk.get("document_name"),
            "page": chunk.get("page"),
            "score": float(score),
            "text": chunk.get("text", ""),
            "jurisdiction": (
                chunk.get("jurisdiction") or "UNCLASSIFIED"
            ),
            "authority": chunk.get(
                "authority", "Unknown"
            ),
            "document_type": chunk.get(
                "document_type", "reference"
            ),
            "source_url": chunk.get("source_url"),
            "article_or_section": chunk.get(
                "article_or_section"
            )
        }

    def _search(self, query, top_k, allowed=None):

        if not isinstance(query, str) or not query.strip():
            raise ValueError(
                "Query must be a non-empty string."
            )

        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        top_k = max(1, int(top_k))

        scored = []

        for index, chunk in enumerate(self.chunks):

            if allowed is not None:

                jurisdiction = str(
                    chunk.get("jurisdiction")
                    or "UNCLASSIFIED"
                ).upper()

                if jurisdiction not in allowed:
                    continue

            score = self._score(query_tokens, index)

            if score > 0:
                scored.append((score, index))

        scored.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return [
            self._format_result(index, score)
            for score, index in scored[:top_k]
        ]

    def search(self, query, top_k=5):

        return self._search(
            query=query,
            top_k=top_k
        )

    def search_by_jurisdiction(
        self,
        query,
        jurisdiction="UAE",
        top_k=5
    ):

        groups = {
            "UAE": {
                "UAE",
                "UAE_FEDERAL",
                "DUBAI"
            },
            "GLOBAL": {
                "GLOBAL",
                "INTERNATIONAL"
            },
            "DUBAI": {
                "DUBAI"
            }
        }

        jurisdiction = jurisdiction.upper()

        allowed = groups.get(
            jurisdiction,
            {jurisdiction}
        )

        return self._search(
            query=query,
            top_k=top_k,
            allowed=allowed
        )