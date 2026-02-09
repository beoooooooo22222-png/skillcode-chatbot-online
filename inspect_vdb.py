
from src.vector_db import VectorDB
import logging

logging.basicConfig(level=logging.ERROR)
vdb = VectorDB()

if vdb.vector_store:
    print(f"Total chunks in vector store: {vdb.vector_store.index.ntotal}")
    
    # Extract all metadata sources
    sources = {}
    # FAISS in LangChain stores documents in docstore
    for doc_id in vdb.vector_store.docstore._dict:
        doc = vdb.vector_store.docstore._dict[doc_id]
        src = doc.metadata.get('source', 'Unknown')
        sources[src] = sources.get(src, 0) + 1
    
    print("\nChunks per book:")
    for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"- {src}: {count} chunks")
else:
    print("Vector store is empty.")
