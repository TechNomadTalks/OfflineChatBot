"""
Vector memory using ChromaDB for semantic search of conversation history.
"""

import chromadb
from chromadb.config import Settings


class VectorMemory:
    """Vector-based memory for semantic search of chat history."""
    
    def __init__(self, collection_name="chat_history", persist_directory="./chroma_data"):
        """
        Initialize vector memory.
        
        Args:
            collection_name: Name of the collection to use
            persist_directory: Directory to persist ChromaDB data
        """
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )
        
    def store(self, user_input, response):
        """Store a conversation entry."""
        import uuid
        
        # Generate unique IDs
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        nova_id = f"nova_{uuid.uuid4().hex[:8]}"
        
        self.collection.add(
            documents=[user_input, response],
            metadatas=[{"speaker": "user"}, {"speaker": "nova"}],
            ids=[user_id, nova_id]
        )

    def recall(self, query, n_results=5):
        """
        Recall similar conversations based on query.
        
        Args:
            query: The query to search for
            n_results: Number of results to return
            
        Returns:
            List of documents (conversation entries)
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            if results and results.get('documents'):
                # Flatten the results
                docs = []
                for doc_list in results['documents']:
                    docs.extend(doc_list)
                return docs
        except Exception as e:
            print(f"Vector memory recall error: {e}")
        return []

    def get_recent(self, n=10):
        """Get the most recent conversation entries."""
        try:
            results = self.collection.get()
            if results and results.get('documents'):
                # Return last n documents
                return results['documents'][-n:] if len(results['documents']) > n else results['documents']
        except Exception as e:
            print(f"Vector memory get recent error: {e}")
        return []
    
    def clear(self):
        """Clear all stored memories."""
        try:
            self.client.delete_collection(name=self.collection.name)
            self.collection = self.client.get_or_create_collection(name=self.collection.name)
        except Exception as e:
            print(f"Error clearing memory: {e}")


# Global instance
memory = VectorMemory()


def store_memory(user_input, response):
    """Store a conversation in vector memory."""
    memory.store(user_input, response)


def recall_memory(query, n_results=5):
    """Recall similar conversations from vector memory."""
    return memory.recall(query, n_results)
