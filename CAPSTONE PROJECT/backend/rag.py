import chromadb
from chromadb.config import Settings
import os

class FarmingRAG:
    def __init__(self):
        # Initialize an in-memory ChromaDB for this prototype
        self.chroma_client = chromadb.Client(Settings(is_tenant_read_only=False))
        self.collection = self.chroma_client.get_or_create_collection(name="farming_knowledge")
        
        # Ingest mock data if collection is empty
        if self.collection.count() == 0:
            self._ingest_mock_data()

    def _ingest_mock_data(self):
        documents = [
            "Tomatoes require well-drained soil and 6-8 hours of sunlight. Water deeply but infrequently.",
            "Wheat streak mosaic virus causes yellowing and stunted growth. Treat by removing infected plants and controlling mites.",
            "In loamy soil, nitrogen fertilizer should be applied in split doses to prevent leaching.",
            "Maize yield improves significantly if planting occurs before the onset of heavy monsoons."
        ]
        ids = ["doc_1", "doc_2", "doc_3", "doc_4"]
        
        self.collection.add(
            documents=documents,
            ids=ids
        )
        print("Mock data ingested to ChromaDB.")

    def query(self, text: str, n_results: int = 2) -> list:
        results = self.collection.query(
            query_texts=[text],
            n_results=n_results
        )
        if results and results['documents']:
            # results['documents'] is a list of lists: [['doc1 text', 'doc2 text']]
            return results['documents'][0]
        return []
