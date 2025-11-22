# ai-therapist
AI Therapist – Educational emotional wellness chatbot built
### 🌐 Live Demo  
https://ai-therapist-9ydkfachz53us5ag5euryg.streamlit.app/
🧠 AI Therapist – Emotional Wellness Chatbot

Educational, safe, and supportive AI therapist built with Python + Streamlit

This project is a simple but powerful AI therapist-style chatbot, designed to help users express emotions in a calm, supportive environment.
It uses:

Hybrid sentiment detection (ML + rule-based)

Crisis detection (safety first)

Friendly conversational engine

TTS voice replies (optional)

Voice message transcription

Dark/Light/AMOLED theme toggle

Clean chat-style UI
📁 Project Structure
ai_therapist/
│
├── app.py                    # Streamlit UI
├── requirements.txt          # Dependencies
│
├── core/
│   ├── therapist_engine.py   # Friendly AI reply logic
│   ├── sentiment.py          # Sentiment analysis (VADER)
│   ├── safety.py             # Crisis detection & reminders
│   ├── storage.py            # Logging system
│
├── data/
│   ├── coping_strategies.json
│   ├── logs/

✨ Features
🧠 AI Therapist Chat

Friendly, supportive conversational tone

Asks empathetic follow-up questions

Provides gentle coping suggestions

❤️ Safety First

Suicide/self-harm detection

Crisis response system

Mandatory safety disclaimer

🔊 Voice Support

Upload a .wav file and get AI response

TTS (Text-to-Speech) for AI replies

🎨 Custom Themes

Dark

Light

AMOLED deep black

📄 Session Tools

Download full conversation

Start new session

Clean UX similar to modern chatbots
📌 Disclaimer

This project is strictly educational and not a replacement for real mental health support.
It cannot diagnose, treat, or handle emergencies.
