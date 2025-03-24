# DengarTulis 🎙️✍️  
AI lokal untuk mendikte suara menjadi teks dengan pemahaman konteks.  
DengarTulis mendukung input suara dan teks secara seamless untuk meningkatkan produktivitas dalam menulis, mencatat, atau mendikte ide.  

---

## 🔥 Fitur Utama
- Dikte suara dengan pemahaman konteks (STT menggunakan Whisper)
- Interaksi AI menggunakan model Llama 3.2 (3B, quantized)
- Umpan balik suara dengan Coqui TTS (bahasa Indonesia)
- Mode "Ketik" dan "Live" yang seamless
- Manajemen memori percakapan dan new chat
- UI/UX desktop dengan GUI interaktif

---

## 🚀 Teknologi yang Digunakan
- **Bahasa Pemrograman:** Python  
- **Model AI:** Llama 3.2 (3B, quantized)  
- **STT (Speech-to-Text):** OpenAI Whisper  
- **TTS (Text-to-Speech):** Coqui TTS  
- **Antarmuka:** Tkinter atau PyQt  
- **Dependency Manager:** venv  

---

## 📂 Struktur Folder
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

- **src/ai_engine/**: Logika AI (LLM, STT, TTS)  
- **src/gui/**: Interface aplikasi (Tkinter atau PyQt)  
- **src/utils/**: Fungsi pendukung seperti memori percakapan dan audio  
- **data/**: Penyimpanan model dan log pengguna  

---

## 🔧 Setup & Instalasi
1. Clone repository:
   ```bash
   git clone https://github.com/username/DengarTulis.git
   cd DengarTulis
   ```
 2. Buat virtual environment:  
 ```bash  
 python -m venv venv  
 ```  

 3. Aktifkan virtual environment:  
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

 ## 🚀 Menjalankan Aplikasi  
 1. Jalankan program utama:  
 ```bash  
 python main.py  
 ```  
 2. Pilih mode **Ketik** atau **Live** pada UI.  
 3. Mulai mendikte suara atau mengetik teks, AI akan merespons sesuai konteks.  

 ## 🤝 Kontribusi  
 Kami terbuka untuk kontribusi!  
 Silakan **fork** repository ini, buat **branch baru**, dan kirim **pull request**.  
 Jangan lupa cek **issue** untuk melihat kebutuhan pengembangan.  

 ## 📜 Lisensi  
 DengarTulis dilisensikan di bawah lisensi MIT.  
 Silakan cek file LICENSE untuk detailnya.    

---

## Selamat menggunakan **DengarTulis**! 😊🚀  
