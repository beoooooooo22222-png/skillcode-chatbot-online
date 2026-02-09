
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging

logging.basicConfig(level=logging.ERROR)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.load_local("vector_store", embeddings, allow_dangerous_deserialization=True)

print(f"TOTAL_CHUNKS: {vector_store.index.ntotal}")

sources = {}
for doc_id, doc in vector_store.docstore._dict.items():
    src = doc.metadata.get('source', 'Unknown')
    sources[src] = sources.get(src, 0) + 1

print("CHUNKS_PER_SOURCE_START")
for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
    print(f"SOURCE: {src} | COUNT: {count}")
print("CHUNKS_PER_SOURCE_END")
