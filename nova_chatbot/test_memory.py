import unittest
from unittest.mock import patch
from nova_chatbot.vector_memory import VectorMemory

class TestVectorMemory(unittest.TestCase):
    def setUp(self):
        self.memory = VectorMemory(collection_name="test_collection")

    def test_store_and_recall(self):
        self.memory.store("Hello", "Hi there!")
        results = self.memory.recall("Hello")
        self.assertIn("Hello", results[0])
        self.assertIn("Hi there!", results[0])

if __name__ == '__main__':
    unittest.main()
