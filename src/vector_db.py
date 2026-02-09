

import os
from langchain_community.vectorstores import FAISS
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    USE_HUGGINGFACE = True
except:
    # Fallback to OpenAI-style embeddings or simple TF-IDF
    USE_HUGGINGFACE = False
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

logger = logging.getLogger(__name__)

class SimpleTfidfEmbeddings:
    """Simple TF-IDF based embeddings as fallback"""
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=384)
        self.is_fitted = False
        
    def embed_documents(self, texts):
        if not self.is_fitted:
            self.vectorizer.fit(texts)
            self.is_fitted = True
        return self.vectorizer.transform(texts).toarray().tolist()
    
    def embed_query(self, text):
        if not self.is_fitted:
            return [0] * 384
        return self.vectorizer.transform([text]).toarray()[0].tolist()

class VectorDB:
    def __init__(self, index_path="vector_store"):
        self.index_path = os.path.join(os.getcwd(), index_path)
        
        # Try HuggingFace first, fallback to TF-IDF
        if USE_HUGGINGFACE:
            try:
                self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                logger.info("Using HuggingFace embeddings")
            except Exception as e:
                logger.warning(f"HuggingFace failed: {e}, using TF-IDF")
                self.embeddings = SimpleTfidfEmbeddings()
        else:
            logger.info("Using TF-IDF embeddings (fallback)")
            self.embeddings = SimpleTfidfEmbeddings()
            
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
            # Increase k for better filtering results
            search_k = limit * 4 if subject_filter else limit
            
            # FAISS scores: lower is better (L2 distance)
            docs = self.vector_store.similarity_search_with_score(query, k=search_k)
            
            results = []
            for doc, score in docs:
                source_title = doc.metadata.get('source', 'Unknown')
                
                # If subject filter is specified, prioritize it
                # We can do this by skipping non-matching ones or just marking them
                # Let's do simple inclusion filtering if subject_filter is strongly specified
                # e.g. "English" should match books with "English" in title
                if subject_filter:
                    if subject_filter.lower() not in source_title.lower():
                        continue

                results.append({
                    'title': source_title,
                    'content': doc.page_content,
                    'score': float(score)
                })
                
                if len(results) >= limit:
                    break
            
            # If filtering left us with nothing, fall back to all results
            if subject_filter and not results:
                logger.info(f"Subject filter '{subject_filter}' returned no results. Falling back to general search.")
                for doc, score in docs[:limit]:
                    results.append({
                        'title': doc.metadata.get('source', 'Unknown'),
                        'content': doc.page_content,
                        'score': float(score)
                    })
            
            return results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
