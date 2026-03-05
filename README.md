# Nova Chatbot 🤖

An offline-capable AI chatbot with voice, vision, and smart features.

## Features

### AI Modes
- **Offline Mode**: Uses local Ollama AI (Phi-3) - no internet required
- **Online Mode**: Uses OpenAI API (GPT-4o, GPT-4o-mini) for advanced responses

### Conversation
- Maintains conversation memory (last 50 entries)
- Context-aware responses using chat history
- Configurable personality and tone

### Voice
- Text-to-speech output using Windows TTS
- Customizable voice settings

### Object Recognition
- Real-time YOLO object detection via webcam
- Supports image file analysis (.jpg, .png, .bmp)
- Color-coded bounding boxes by confidence level

### File Processing
- **Images**: Object detection and description
- **Text files**: Read and display contents
- **PDFs**: Extract and display text

### System Integration
- Open applications by name
- Web search via DuckDuckGo
- Computer control (shutdown/restart)

### Plugins
- Extensible plugin system
- Run custom plugins with `!pluginname`

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Edit `config.ini`:

```ini
[api_keys]
# Set your OpenAI API key here, or leave as-is for offline mode
openai = YOUR_OPENAI_API_KEY_HERE

[ai]
# Set to true for offline mode (no API calls)
offline_mode = true
# Model to use: phi-3 (offline) or gpt-4o-mini (online)
model = phi-3

[voice]
enabled = true

[memory]
enabled = true
max_entries = 50

[proactive]
enabled = true
```

### 3. For Offline Mode

Install [Ollama](https://ollama.ai/) and pull the model:

```bash
ollama pull phi-3
ollama serve
```

### 4. Run

```bash
python -m nova_chatbot.main
```

Or from the nova_chatbot directory:

```bash
cd nova_chatbot
python main.py
```

## Commands

| Command | Description |
|---------|-------------|
| `scan` | Scan objects with camera |
| `upload <path>` | Upload and process a file |
| `open <app>` | Open an application |
| `search <query>` | Search the web |
| `online mode` | Switch to OpenAI |
| `offline mode` | Switch to Ollama |
| `clear` | Clear conversation memory |
| `!plugin` | Run a plugin |
| `help` | Show help |
| `exit` | Exit |

## Project Structure

```
nova_chatbot/
├── __init__.py
├── main.py              # Entry point
├── config.py            # Configuration
├── ai_core.py          # AI routing
├── online_ai.py        # OpenAI integration
├── local_ai.py         # Ollama integration
├── memory.py           # Conversation memory
├── vector_memory.py    # Semantic memory
├── voice.py            # Text-to-speech
├── object_recognition.py  # YOLO vision
├── file_handler.py     # File processing
├── command_dispatcher.py # Command handling
├── web_search.py       # DuckDuckGo search
├── personality.py      # Personality system
├── proactive_messaging.py # Proactive messages
├── platform_utils.py  # App opening
├── system_control.py  # Shutdown/restart
└── plugins/            # Plugin directory
```

## Requirements

- Python 3.8+
- Windows (for TTS and some features)
- For full features: OpenAI API key or Ollama

## License

MIT
