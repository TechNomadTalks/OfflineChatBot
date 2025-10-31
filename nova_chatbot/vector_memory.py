import chromadb
from chromadb.utils import embedding_functions

class VectorMemory:
    def __init__(self, collection_name="chat_history"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )

    def store(self, user_input, response):
        self.collection.add(
            documents=[user_input, response],
            metadatas=[{"speaker": "user"}, {"speaker": "nova"}],
            ids=[f"user_{len(self.collection.get()['ids'])}", f"nova_{len(self.collection.get()['ids']) + 1}"]
        )

    def recall(self, query, n_results=5):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents']

memory = VectorMemory()

def store_memory(user_input, response):
    memory.store(user_input, response)

def recall_memory(query, n_results=5):
    return memory.recall(query, n_results)
