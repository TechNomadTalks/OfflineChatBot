import unittest
from unittest.mock import patch

class TestOnlineAI(unittest.TestCase):
    @patch('nova_chatbot.online_ai.openai.OpenAI')
    def test_get_online_response(self, mock_openai):
        # We can now import the module here, after the patch is applied
        from nova_chatbot.online_ai import get_online_response

        mock_chunk = unittest.mock.Mock()
        mock_chunk.choices = [unittest.mock.Mock()]
        mock_chunk.choices[0].delta = unittest.mock.Mock()
        mock_chunk.choices[0].delta.content = "Test response"

        mock_openai.return_value.chat.completions.create.return_value = [mock_chunk]
        response, _ = get_online_response("Test prompt")
        self.assertEqual(response, "Test response")

if __name__ == '__main__':
    unittest.main()
