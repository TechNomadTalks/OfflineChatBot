import unittest
from unittest.mock import patch, MagicMock

class TestOnlineAI(unittest.TestCase):
    @patch('nova_chatbot.online_ai.config')
    @patch('nova_chatbot.online_ai.openai.OpenAI')
    def test_get_online_response(self, mock_openai, mock_config):
        from nova_chatbot.online_ai import get_online_response

        mock_config.get_zai_api_key.return_value = "test_key"
        mock_config.get_openai_api_key_fallback.return_value = None
        mock_config.get_ai_model.return_value = "glm-5.1"
        mock_config.is_offline_mode.return_value = False

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta = MagicMock()
        mock_chunk.choices[0].delta.content = "Test response"

        mock_stream = MagicMock()
        mock_stream.__iter__ = lambda self: iter([mock_chunk])
        mock_openai.return_value.chat.completions.create.return_value = mock_stream

        response, _ = get_online_response("Test prompt")
        self.assertEqual(response, "Test response")

if __name__ == '__main__':
    unittest.main()
