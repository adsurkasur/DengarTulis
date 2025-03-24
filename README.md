# DengarTulis 🎙️✍️  
AI-powered local tool for voice dictation with contextual understanding.  
DengarTulis supports seamless input through both voice and text, enhancing productivity in writing, note-taking, and idea dictation.  

---

## 🔥 Key Features
- Context-aware voice dictation (STT using Whisper)  
- AI interaction powered by Llama 3.2 (3B, quantized)  
- Text-to-Speech (TTS) with Coqui TTS (supports multiple languages)  
- Seamless "Typing" and "Live" modes  
- Conversation memory management and new chat feature  
- Interactive desktop GUI for user-friendly experience  

---

## 🚀 Technologies Used
- **Programming Language:** Python  
- **AI Model:** Llama 3.2 (3B, quantized)  
- **STT (Speech-to-Text):** OpenAI Whisper  
- **TTS (Text-to-Speech):** Coqui TTS (multi-language)  
- **Interface:** Tkinter or PyQt  
- **Dependency Manager:** venv  

---

## 📂 Project Structure
DengarTulis/  
│── README.md  
│── requirements.txt  
│── .gitignore  
│── main.py  
│── src/  
│   ├── ai_engine/  
│   │   ├── __init__.py  
│   │   ├── llm_model.py  
│   │   ├── stt_whisper.py  
│   │   └── tts_coqui.py  
│   ├── gui/  
│   │   ├── __init__.py  
│   │   └── gui_main.py  
│   └── utils/  
│       ├── __init__.py  
│       ├── memory_manager.py  
│       └── audio_handler.py  
└── data/  
    ├── user_logs/  
    └── models/  

- **src/ai_engine/**: AI logic (LLM, STT, TTS)  
- **src/gui/**: User interface (Tkinter or PyQt)  
- **src/utils/**: Utilities like memory management and audio handling  
- **data/**: Storage for models and user logs  

---

## 🔧 Setup & Installation
1. Clone the repository:  
```bash  
git clone https://github.com/username/DengarTulis.git  
cd DengarTulis  
```  

2. Create a virtual environment:  
```bash  
python -m venv venv  
```  

3. Activate the virtual environment:  
- **Windows:**  
```bash  
.\venv\Scripts\activate  
```  
- **Mac/Linux:**  
```bash  
source venv/bin/activate  
```  

4. Install dependencies:  
```bash  
pip install -r requirements.txt  
```  

---

## 🚀 Running the Application
1. Run the main program:  
```bash  
python main.py  
```  
2. Choose **Typing** or **Live** mode on the GUI.  
3. Start voice dictation or type text; the AI will respond contextually.  

---

## 🔥 Building EXE for Distribution  
To generate a standalone executable (`.exe`):  
```bash  
pyinstaller --onefile --noconsole main.py  
```  
The output EXE will support multiple languages through Coqui TTS.  

---

## 🤝 Contributions  
Contributions are welcome!  
Feel free to **fork** the repository, create a **new branch**, and submit a **pull request**.  
Check the **issues** for development needs.  

---

## 📜 License  
DengarTulis is licensed under the **MIT License**.  
Please check the LICENSE file for more details.  

Happy using **DengarTulis**! 😊🚀  
