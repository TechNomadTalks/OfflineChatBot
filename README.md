Nova Chatbot — Feature Overview
Modes
Offline Mode: Uses a local AI model (Phi) for responses without internet.

Online Mode: Uses OpenAI API (GPT-4o or 4o-mini) for advanced responses.

Conversation
Maintains advanced memory of previous chats (last 50 entries) to provide context-aware replies.

Personalizes replies with a unique personality (witty, emotional tone).

Supports voice output using Windows TTS with preferred voices.

Supports voice input via offline Vosk speech recognition model.

Object Recognition
Real-time YOLOv8x object detection with webcam feed.

Draws color-coded bounding boxes with object names and confidence scores.

Provides detailed online descriptions when in online mode.

Plugins
Supports custom plugins that can be triggered via !pluginname commands.

Plugins can extend functionality dynamically.

File Upload & Processing
Handles image files (.jpg, .png, .bmp) — analyzes and describes contents.

Handles text files (.txt) — reads and outputs text content.

Handles PDFs (.pdf) — extracts and outputs text (requires pymupdf).

Windows Integration
Can open applications by name, e.g. open clock, open word, by searching for the executable dynamically.

Uses Windows system calls and file system searches to locate and launch apps.

Additional Features
Supports streaming OpenAI responses for real-time interaction.

Gracefully handles errors with detailed messages.

Supports switching modes with simple commands: online mode, offline mode.

Command scan triggers object recognition scan.

Command exit cleanly closes the chatbot.
