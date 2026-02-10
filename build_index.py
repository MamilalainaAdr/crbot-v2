# build_index.py
import pathlib
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

DATASET_DIR = pathlib.Path("dataset")
CHROMA_PATH = "chroma_index"
COLLECTION_NAME = "crbot_knowledge"

def load_docs():
    for path in DATASET_DIR.glob("doc_*.txt"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        yield str(path), text

def main():
    # splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        add_start_index=True,
    )

    # modèle d'embedding
    print("[index] Chargement du modèle d'embedding...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    # Initialisation de chroma
    print("[index] Initialisation de Chroma...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection(COLLECTION_NAME)
        print("[index] Ancienne collection supprimée.")
    except Exception:
        pass

    collection = client.get_or_create_collection(COLLECTION_NAME)

    ids = []
    texts = []
    metadatas = []

    # parcourir les docs et les splitter
    for doc_path, text in load_docs():
        splits = splitter.split_text(text)
        for i, chunk in enumerate(splits):
            cid = f"{doc_path}-{i}"
            ids.append(cid)
            texts.append(chunk)
            metadatas.append({"source": doc_path})

    print("[index] Nombre total de chunks :", len(texts))

    # calcul des embeddings
    print("[index] Calcul des embeddings...")
    embs = embed_model.encode(texts, batch_size=32, show_progress_bar=True)

    # ajout par lots dans Chroma
    MAX_BATCH = 5_000
    def chunk_iterable(seq, size):
        for i in range(0, len(seq), size):
            yield seq[i:i + size]

    print("Ajout dans la collection Chroma (par lots)...")
    for batch_ids, batch_texts, batch_meta, batch_emb in zip(
            chunk_iterable(ids, MAX_BATCH),
            chunk_iterable(texts, MAX_BATCH),
            chunk_iterable(metadatas, MAX_BATCH),
            chunk_iterable(list(embs), MAX_BATCH)
        ):
        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=batch_meta,
            embeddings=batch_emb,
        )

    print("[index] Taille finale de la collection :", collection.count())

if __name__ == "__main__":
    main()
