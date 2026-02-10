import chromadb

CHROMA_PATH = "chroma_index"
COLLECTION_NAME = "crbot_knowledge"

def main():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(COLLECTION_NAME)

    question = "Quelles sont les bonnes pratiques pour une revue de code efficace ?"
    print("[search] Question :", question)

    res = collection.query(
        query_texts=[question],
        n_results=3,
    )

    docs = res["documents"][0]
    metas = res["metadatas"][0]

    for i, (doc, meta) in enumerate(zip(docs, metas), start=1):
        print(f"\n=== Résultat {i} ===")
        print("Source :", meta.get("source"))
        print("Extrait :")
        print(doc[:400], "...")
    print("\n[search] Fin.")

if __name__ == "__main__":
    main()
