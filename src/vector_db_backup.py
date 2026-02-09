
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import logging

logger = logging.getLogger(__name__)

class VectorDB:
    def __init__(self, index_path="vector_store"):
        self.index_path = os.path.join(os.getcwd(), index_path)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self.load_index()

    def load_index(self):
        """Load existing index or initialize new one"""
        if os.path.exists(self.index_path):
            try:
                self.vector_store = FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
                logger.info(f"✅ Loaded Vector Store from {self.index_path}")
            except Exception as e:
                logger.error(f"Failed to load vector store: {e}")
                self.vector_store = None
        else:
            logger.info("ℹ️ No existing vector store found. Waiting for books.")

    def add_book(self, title, content):
        """Chunk book content and add to vector store"""
        try:
            logger.info(f"Processing book: {title}...")
            
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            texts = text_splitter.split_text(content)
            
            # Create Documents with metadata
            documents = [
                Document(page_content=t, metadata={"source": title})
                for t in texts
            ]
            
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
            else:
                self.vector_store.add_documents(documents)
            
            # Save index
            self.vector_store.save_local(self.index_path)
            logger.info(f"✅ Added {len(documents)} chunks from '{title}' to Vector Store")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add book to vector store: {e}")
            return False

    def search(self, query, limit=5, subject_filter=None):
        """Search vector store for relevant chunks"""
        if self.vector_store is None:
            logger.warning("Vector store is empty.")
            return []

        try:
            # Basic semantic search
            # If subject/book filter is provided, we can filter by metadata
            # FAISS doesn't support complex metadata filtering easily in the reckless mode without specific index types
            # But we can post-filter or just rely on semantic similarity
            
            search_kwargs = {"k": limit * 2} # Fetch more, then filter
             
            # If specific book is requested in filter
            filter_dict = None
            if subject_filter:
                # Basic check if subject filter matches a known book title pattern
                # Start simple: search everything, relevancy usually handles it
                pass

            docs = self.vector_store.similarity_search_with_score(query, k=limit)
            
            results = []
            for doc, score in docs:
                # FAISS score: lower is better (L2 distance)
                # Filter out very bad matches if needed (e.g. score > 1.5)
                results.append({
                    'title': doc.metadata.get('source', 'Unknown'),
                    'content': doc.page_content,
                    'score': float(score)
                })
            
            return results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
