import json
from functools import lru_cache
from pathlib import Path

import faiss
import numpy as np
import onnxruntime as ort

from tokenizers import Tokenizer


# ==========================================
# CHILDNET 360
# E5 ONNX INT8 + FAISS SEMANTIC SEARCH
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_DIR = PROJECT_ROOT / "e5_onnx"

MODEL_PATH = MODEL_DIR / "model_int8.onnx"

TOKENIZER_PATH = MODEL_DIR / "tokenizer.json"


@lru_cache(maxsize=1)
def load_embedding_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"E5 ONNX model not found: {MODEL_PATH}"
        )

    if not TOKENIZER_PATH.exists():
        raise FileNotFoundError(
            f"E5 tokenizer not found: {TOKENIZER_PATH}"
        )

    print("Loading multilingual-e5-small ONNX INT8...")

    tokenizer = Tokenizer.from_file(
        str(TOKENIZER_PATH)
    )

    tokenizer.enable_truncation(
        max_length=512
    )

    options = ort.SessionOptions()

    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1

    options.execution_mode = (
        ort.ExecutionMode.ORT_SEQUENTIAL
    )

    options.enable_cpu_mem_arena = False
    options.enable_mem_pattern = False

    session = ort.InferenceSession(
        str(MODEL_PATH),
        sess_options=options,
        providers=["CPUExecutionProvider"]
    )

    output_names = {
        output.name
        for output in session.get_outputs()
    }

    if "sentence_embedding" not in output_names:
        raise RuntimeError(
            "E5 ONNX model does not provide "
            "sentence_embedding output."
        )

    print("E5 ONNX INT8 loaded successfully.")

    return tokenizer, session


class ChildNetKnowledgeBase:

    def __init__(self, project_root=None):

        self.project_root = Path(
            project_root or PROJECT_ROOT
        )

        processed = (
            self.project_root
            / "knowledge_base"
            / "processed"
        )

        chunks_path = (
            processed / "knowledge_chunks.json"
        )

        index_path = (
            processed / "childnet_faiss.index"
        )

        with open(
            chunks_path,
            encoding="utf-8"
        ) as file:

            self.chunks = json.load(file)

        # Real FAISS vector index
        self.index = faiss.read_index(
            str(index_path)
        )

        if self.index.ntotal != len(self.chunks):
            raise ValueError(
                "FAISS vectors and knowledge chunks "
                "do not match."
            )

        if self.index.d != 384:
            raise ValueError(
                "Expected 384-dimensional FAISS index."
            )

        self.tokenizer, self.session = (
            load_embedding_model()
        )

        print(
            "CHILDNET 360 FAISS READY:",
            self.index.ntotal,
            "vectors"
        )

    def embed_query(self, query):

        if not isinstance(query, str) or not query.strip():
            raise ValueError(
                "Query must be a non-empty string."
            )

        # E5 query prefix
        text = "query: " + query.strip()

        encoded = self.tokenizer.encode(
            text,
            add_special_tokens=True
        )

        input_ids = np.asarray(
            [encoded.ids],
            dtype=np.int64
        )

        attention_mask = np.asarray(
            [encoded.attention_mask],
            dtype=np.int64
        )

        outputs = self.session.run(
            ["sentence_embedding"],
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask
            }
        )

        embedding = np.asarray(
            outputs[0],
            dtype=np.float32
        )

        if embedding.shape != (1, 384):
            raise ValueError(
                f"Unexpected embedding shape: "
                f"{embedding.shape}"
            )

        # Normalize for FAISS IndexFlatIP
        faiss.normalize_L2(embedding)

        return embedding

    def search(self, query, top_k=5):

        embedding = self.embed_query(query)

        top_k = min(
            max(int(top_k), 1),
            self.index.ntotal
        )

        scores, indices = self.index.search(
            embedding,
            top_k
        )

        results = []

        for score, idx in zip(
            scores[0],
            indices[0]
        ):

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
                    chunk.get("jurisdiction")
                    or "UNCLASSIFIED"
                ),
                "authority": chunk.get(
                    "authority",
                    "Unknown"
                ),
                "document_type": chunk.get(
                    "document_type",
                    "reference"
                ),
                "source_url": chunk.get("source_url"),
                "article_or_section": chunk.get(
                    "article_or_section"
                )
            })

        return results

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

        # Search all FAISS vectors, then filter.
        # This preserves semantic ranking.

        results = self.search(
            query,
            top_k=len(self.chunks)
        )

        filtered = [
            item
            for item in results
            if str(
                item.get("jurisdiction")
                or "UNCLASSIFIED"
            ).upper() in allowed
        ]

        return filtered[:max(1, int(top_k))]