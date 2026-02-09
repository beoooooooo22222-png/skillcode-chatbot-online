
import os
import sys
# Suppress all warnings and trash
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.load_local("vector_store", embeddings, allow_dangerous_deserialization=True)

    sources = {}
    for doc_id, doc in vector_store.docstore._dict.items():
        src = doc.metadata.get('source', 'Unknown')
        sources[src] = sources.get(src, 0) + 1

    with open("vdb_clean_stats.txt", "w", encoding="utf-8") as f:
        f.write(f"TOTAL_CHUNKS: {vector_store.index.ntotal}\n")
        for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{src} : {count}\n")
    print("SUCCESS")
except Exception as e:
    with open("vdb_clean_stats.txt", "w", encoding="utf-8") as f:
        f.write(f"ERROR: {str(e)}\n")
    print(f"FAILED: {e}")
