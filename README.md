# Assisty

A local AI assistant with conversational, coding, web search, system interaction capabilities.n
## Setup
- Directory: ~/Ai/Assisty
- Virtual Environment: assity.env/
- Models: Stored in models/ (not tracked)


### STT Progress
- Tested: whisper.cpp/build/bin/main (deprecated, use whisper-cli)
- Command: ~/Ai/Assisty/whisper.cpp/build/bin/whisper-cli -m ~/Ai/Assisty/whisper.cpp/models/ggml-base.bin -f <audio.wav>
- Note: CPU-only, CUDA optional

- Confirmed STT transcription: [your transcription here]

- Set Git credential.helper to store for passwordless push
