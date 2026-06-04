import unittest
from unittest.mock import patch
from nova_chatbot.command_dispatcher import CommandDispatcher

class TestCommandDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = CommandDispatcher(plugins={})

    @patch('nova_chatbot.command_dispatcher.object_recognizer.recognize_objects')
    def test_scan(self, mock_recognize_objects):
        mock_recognize_objects.return_value = ["- object1\n- object2"]
        result = self.dispatcher.dispatch("scan")
        self.assertEqual(result, "- object1\n- object2")

    @patch('nova_chatbot.command_dispatcher.handle_file_upload')
    def test_upload(self, mock_handle_file_upload):
        mock_handle_file_upload.return_value = "File processed successfully"
        result = self.dispatcher.dispatch("upload test.txt")
        self.assertEqual(result, "File processed successfully")

    @patch('nova_chatbot.command_dispatcher.open_app')
    def test_open(self, mock_open_app):
        mock_open_app.return_value = "Opening application..."
        result = self.dispatcher.dispatch("open notepad")
        self.assertEqual(result, "Opening application...")

    @patch('nova_chatbot.command_dispatcher.search_web')
    def test_search(self, mock_search_web):
        mock_search_web.return_value = [{"title": "Test", "href": "http://test.com", "body": "Test"}]
        result = self.dispatcher.dispatch("search test")
        self.assertEqual(result, "Test\n  http://test.com\n  Test")

if __name__ == '__main__':
    unittest.main()
