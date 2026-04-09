import os
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryStore:
    def __init__(self):
        self.use_chroma = False
        self.fallback_store = {}
        
        try:
            import chromadb
            # Using ephemeral client for simple local setup. 
            # It stores data in memory but simulates the vector DB logic perfectly.
            self.client = chromadb.EphemeralClient()
            self.collection = self.client.get_or_create_collection(name="research_memory")
            self.use_chroma = True
            logger.info("ChromaDB initialized successfully.")
        except Exception as e:
            logger.warning(f"ChromaDB initialization failed: {e}. Falling back to in-memory dictionary.")
            self.use_chroma = False

    def store(self, text, metadata=None):
        doc_id = str(uuid.uuid4())
        metadata = metadata or {}
        if self.use_chroma:
            try:
                self.collection.add(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
            except Exception as e:
                logger.error(f"Error storing in ChromaDB: {e}")
                self.fallback_store[doc_id] = {"text": text, "metadata": metadata}
        else:
            self.fallback_store[doc_id] = {"text": text, "metadata": metadata}
        return doc_id

    def retrieve_all(self):
        """Retrieve all stored documents as a single context string."""
        if self.use_chroma:
            try:
                results = self.collection.get()
                docs = results.get("documents", [])
                return "\n\n".join(docs)
            except Exception as e:
                logger.error(f"Error retrieving from ChromaDB: {e}")
                return "\n\n".join([item["text"] for item in self.fallback_store.values()])
        else:
            return "\n\n".join([item["text"] for item in self.fallback_store.values()])

memory_store = MemoryStore()
