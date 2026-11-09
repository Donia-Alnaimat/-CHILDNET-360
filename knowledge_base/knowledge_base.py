from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    Preserve source filename and page numbers.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("The file must be a PDF.")

    reader = PdfReader(str(pdf_path))
    extracted_pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        extracted_pages.append({
            "source": pdf_path.name,
            "page": page_number,
            "text": text.strip()
        })

    return extracted_pages


def extract_text_from_folder(folder_path):
    """
    Extract text from all PDF files in a folder.
    """

    folder_path = Path(folder_path)

    if not folder_path.exists():
        raise FileNotFoundError(
            f"Folder not found: {folder_path}"
        )

    all_pages = []
    pdf_files = sorted(folder_path.glob("*.pdf"))

    for pdf_file in pdf_files:
        pages = extract_text_from_pdf(pdf_file)
        all_pages.extend(pages)

    return all_pages


def create_chunks(pages, chunk_size=500, overlap=100):
    """
    Split extracted page texts into smaller chunks.
    Preserve source filename and page number.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    chunks = []
    step = chunk_size - overlap

    for page_data in pages:
        text = page_data.get("text", "").strip()

        if not text:
            continue

        for start in range(0, len(text), step):
            chunk_text = text[start:start + chunk_size]

            if not chunk_text:
                continue

            chunks.append({
                "source": page_data["source"],
                "page": page_data["page"],
                "text": chunk_text
            })

    return chunks
import json
import pickle
import numpy as np
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer


def build_vector_store(chunks, output_dir):
    """Build and save TF-IDF vectors and FAISS index."""

    if not chunks:
        raise ValueError("No chunks available.")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    texts = [chunk["text"] for chunk in chunks]

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(texts).toarray()
    vectors = np.asarray(vectors, dtype="float32")

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    faiss.write_index(
        index,
        str(output_dir / "childnet_index.faiss")
    )

    with open(output_dir / "vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    with open(output_dir / "chunks_metadata.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    return vectorizer, index


def search_knowledge_base(query, vectorizer, index, chunks, top_k=3):
    """Search the knowledge base and return source and page."""

    query_vector = vectorizer.transform([query]).toarray()
    query_vector = np.asarray(query_vector, dtype="float32")

    k = min(top_k, index.ntotal)
    distances, indices = index.search(query_vector, k)

    results = []

    for i in indices[0]:
        if i == -1:
            continue

        results.append({
            "source": chunks[i]["source"],
            "page": chunks[i]["page"],
            "text": chunks[i]["text"]
        })

    return results