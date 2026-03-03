📞 Call Voice Agent

A real-time AI-powered Voice Agent built using Sarvam AI Streaming STT & TTS with LLM-based conversational intelligence.
Designed for low-latency, multilingual, production-ready voice interactions.

🚀 Overview

Call Voice Agent enables real-time voice conversations by integrating:

🎙 Streaming Speech-to-Text (STT) — Converts live speech to text using Sarvam AI
🧠 LLM-based Conversation Management — Context-aware AI responses
🔊 Streaming Text-to-Speech (TTS) — Generates natural voice replies
⚡ Low-Latency Audio Processing — Real-time interaction support
🎧 Voice Activity Detection (VAD) — Smart listening & barge-in handling

✨ Features

◆ Real-time speech recognition
◆ Context-aware conversational responses
◆ Streaming voice output
◆ Multilingual-ready architecture
◆ Noise calibration support
◆ Barge-in interruption handling
◆ Automatic transcript logging
◆ Modular & scalable code structure

🏗 Architecture Flow
User Speech
    ⇣
Sarvam Streaming STT
    ⇣
LLM Conversation Manager
    ⇣
Sarvam Streaming TTS
    ⇣
Voice Response to User
📁 Project Structure
app/
│
├── audio/              # Audio engine, devices, VAD
├── stt/                # Sarvam streaming STT
├── tts/                # Sarvam streaming TTS
├── llm/                # Conversation manager
├── convo/              # Conversation rules
├── storage/            # Transcript logging
│
├── config.py
├── logging_setup.py
└── main.py

requirements.txt
.env
.gitignore
🛠 Tech Stack

▸ Python
▸ Sarvam AI (Streaming STT & TTS)
▸ LLM-based Conversation Management
▸ AsyncIO
▸ Real-time Audio Processing
▸ Voice Activity Detection

⚙️ Setup Instructions
1️⃣ Clone Repository
git clone https://github.com/Priyanshu-Yadav19/Call-Voice-Agent.git
cd Call-Voice-Agent
2️⃣ Create Virtual Environment
python -m venv bot
bot\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Configure Environment Variables

Create .env file:

SARVAM_API_KEY=your_sarvam_api_key_here
MIC_SR=16000
TTS_MODEL_SR=24000
PLAYBACK_GAIN=1.2
TTS_PACE=1.0

⚠ Keep .env private.

▶️ Run Application
python -m app.main

Expected Output:
✔ Audio device initialization
✔ Noise calibration
✔ Voice agent greeting
✔ Live conversation ready

🎯 Use Cases

▣ AI Call Automation
▣ Customer Support Voice Bots
▣ Loan / Banking Voice Assistants
▣ Multilingual Voice Agents
▣ Real-time AI Voice Interfaces

🔒 Security

◉ API keys stored securely in .env
◉ Sensitive files excluded via .gitignore
◉ No credentials committed to repository

📌 Future Improvements

➜ Docker deployment
➜ Cloud hosting integration
➜ Analytics dashboard
➜ Call recording system
➜ Multi-agent routing

👨‍💻 Author

Priyanshu Yadav
GitHub → https://github.com/Priyanshu-Yadav19
