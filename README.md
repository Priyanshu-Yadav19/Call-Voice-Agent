📞 Call Voice Agent

 A real-time AI-powered Voice Agent built using Sarvam AI Streaming STT & TTS with LLM-based conversational intelligence.
 Designed for low-latency, multilingual, production-ready voice interactions.

🚀 Overview

Call Voice Agent enables real-time voice conversations by integrating:

🎙 Streaming Speech-to-Text (STT) using Sarvam AI

🧠 LLM-based conversation management

🔊 Streaming Text-to-Speech (TTS) using Sarvam AI

⚡ Low-latency real-time audio processing

🎧 Voice Activity Detection (VAD) with barge-in handling

📝 Automatic transcript logging

🏗 System Architecture

    User Speech

      ↓
   
    Sarvam Streaming STT

      ↓
   
    LLM Conversation Manager

      ↓
   
    Sarvam Streaming TTS
  
      ↓

    Voice Response to User


📁 Project Structure

              app/
              │
              ├── audio/              # Audio engine, device handling, VAD
              ├── stt/                # Sarvam streaming STT integration
              ├── tts/                # Sarvam streaming TTS integration
              ├── llm/                # Prompt management & conversation logic
              ├── convo/              # Conversation rules & payload control
              ├── storage/            # Transcript logging
              │
              ├── config.py           # Configuration loader
              ├── logging_setup.py    # Logging configuration
              └── main.py             # Application entry point
              requirements.txt 
              .env                    # Environment variables (ignored)
              .gitignore


🛠 Tech Stack

▸ Python

▸ Sarvam AI (Streaming STT & TTS)

▸ LLM-based Conversation Management

▸ AsyncIO

▸ Real-time Audio Processing

▸ Voice Activity Detection

⚙️ Setup Instructions

1️⃣ Clone the Repository
     
     git clone https://github.com/Priyanshu-Yadav19/Call-Voice-Agent.git
     cd Call-Voice-Agent
      
2️⃣ Create Virtual Environment
        
       python -m venv bot

Activate (Windows):
     
     bot\Scripts\activate
3️⃣ Install Dependencies
    
    pip install -r requirements.txt
    
4️⃣ Configure Environment Variables

Create a .env file in the root directory:
      
      SARVAM_API_KEY=your_sarvam_api_key_here
      
      MIC_SR=16000
      TTS_MODEL_SR=24000
      
      PLAYBACK_GAIN=1.2
      TTS_PACE=1.0

⚠️ Never commit your .env file.

It is already included in .gitignore.

▶️ Run the Application
     
     python -m app.main

👨‍💻 Expected output:

✔ Audio device initialization

✔ Noise calibration

✔ Voice agent greeting

✔ Live conversation ready

🎯 Use Cases

⬢ AI Call Automation

⬢ Customer Support Voice Bots

⬢ Loan / Banking Voice Assistants

⬢ Multilingual Voice Agents

⬢ Real-time AI Voice Interfaces

🔒 Security

◎ API keys stored securely in .env

◎ Sensitive files excluded via .gitignore

◎ No credentials committed to repository

👨‍💻 Author

Priyanshu Yadav

GitHub: https://github.com/Priyanshu-Yadav19
