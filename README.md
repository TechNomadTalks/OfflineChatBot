# Nova Chatbot 🤖

An offline-capable AI chatbot with voice, vision, and smart features.

## Security Status

- **API Keys**: All keys stored in `config.ini` with placeholder detection. No hardcoded secrets.
- **Permissions**: Plugin sandbox system restricts commands per plugin via `[permissions]` config.
- **System Control**: Shutdown/restart commands require explicit permission in config.

### Voice Options

| Provider | Type | Description |
|----------|------|-------------|
| **piper** (default) | Local | Custom Jarvis voice clone - British RP accent, sounds like Iron Man's Jarvis |
| **elevenlabs** | Cloud | High-quality AI voices (requires API key) |
| **pyttsx3** | Local | Windows TTS fallback |

To use the Jarvis voice model:
```bash
# Install Piper
pip install piper-tts

# Download Jarvis voice model
mkdir -p nova_chatbot/models/jarvis
wget -O nova_chatbot/models/jarvis/jarvis-medium.onnx \
  https://huggingface.co/jgkawell/jarvis/resolve/main/en/en_GB/jarvis/medium/jarvis-medium.onnx
wget -O nova_chatbot/models/jarvis/jarvis-medium.onnx.json \
  https://huggingface.co/jgkawell/jarvis/resolve/main/en/en_GB/jarvis/medium/jarvis-medium.onnx.json

# Set in config.ini
[tts]
provider = piper
```

## Features

### AI Modes
- **Offline Mode**: Uses local Ollama AI (Phi-3) - no internet required
- **Online Mode**: Uses Z.AI GLM-5.1 or OpenAI API for advanced responses
- **Temperature Control**: Configurable per personality profile

### Conversation
- Maintains conversation memory (configurable max entries)
- Context-aware responses using chat history
- Configurable personality and tone (jarvis/nova/casual)

### Voice
- Text-to-speech output using ElevenLabs (primary) or pyttsx3 (Windows fallback)
- Voice input via Vosk speech recognition
- Configurable voice settings per personality

### Object Recognition
- Real-time YOLO object detection via webcam
- Supports image file analysis (.jpg, .png, .bmp)
- Color-coded bounding boxes by confidence level
- Online mode for detailed object descriptions via Z.AI

### File Processing
- **Images**: Object detection and description
- **Text files**: Read and display contents
- **PDFs**: Extract and display text

### System Integration
- Open applications by name
- Web search via DuckDuckGo
- Computer control (shutdown/restart)

### Plugins
- Extensible plugin system with permission sandbox
- Run custom plugins with `!pluginname`
- Configurable command permissions per plugin

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Edit `config.ini`:

```ini
[api_keys]
# Set your Z.AI API key (preferred) or OpenAI API key
# Keys are validated - placeholder values disable the service
zai = YOUR_ZAI_API_KEY_HERE
openai = YOUR_OPENAI_API_KEY_HERE

[ai]
# Set to false to use Z.AI/Online mode
offline_mode = true
# Model: glm-5.1 (Z.AI), gpt-4o-mini, or phi-3 (Ollama)
model = phi-3

[personality]
# Profile: jarvis, nova, or casual (affects messages and temperature)
profile = jarvis
temperature = 0.7

[permissions]
# Plugin command permissions: plugin_name = allowed_commands
# Empty = all allowed
# Example: autonomous = scan,open,search,plan
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
| `look <image>` | Analyze an image (requires API key) |
| `plan <task>` | Create a plan for a task |
| `online mode` | Switch to Z.AI GLM-5.1 |
| `offline mode` | Switch to local AI (Ollama) |
| `voice on/off` | Enable/disable voice input |
| `export <file>` | Export memory to JSON file |
| `import <file>` | Import memory from JSON file |
| `find <query>` | Search memory for entries |
| `!plugin` | Run a plugin |
| `help` | Show help |
| `exit` | Exit |

## Project Structure

```
nova_chatbot/
├── __init__.py
├── main.py              # Entry point
├── config.py            # Configuration with placeholder detection
├── ai_core.py          # AI routing with lazy tiktoken import
├── online_ai.py        # Z.AI/OpenAI integration
├── local_ai.py         # Ollama integration
├── memory.py           # Conversation memory (JSON)
├── vector_memory.py    # Semantic memory (ChromaDB)
├── voice.py            # Text-to-speech with lazy imports
├── object_recognition.py  # YOLO vision with unified API key fallback
├── file_handler.py     # File processing
├── command_dispatcher.py # Command handling with permissions
├── web_search.py       # DuckDuckGo search
├── personality.py      # Personality system
├── proactive_messaging.py # Proactive messages per personality
├── platform_utils.py  # App opening
├── system_control.py  # Shutdown/restart
├── tts.py              # ElevenLabs/pyttsx3 TTS
├── planner.py          # Task planning
├── autonomous.py       # Autonomous agent
├── audio_input.py      # Voice input (Vosk)
└── plugins/            # Plugin directory
```

## Requirements

- Python 3.8+
- Windows (for TTS and some features)
- For full features: Z.AI API key or Ollama

## License

MIT
