echo Membuat file kosong di dalam struktur folder DengarTulis...

cd src\ai_engine
type nul > __init__.py
type nul > llm_model.py
type nul > stt_whisper.py
type nul > tts_coqui.py

cd ..\gui
type nul > __init__.py
type nul > gui_main.py

cd ..\utils
type nul > __init__.py
type nul > memory_manager.py
type nul > audio_handler.py

cd ..\..
type nul > main.py
type nul > requirements.txt
type nul > .gitignore
type nul > README.md

echo Semua file kosong berhasil dibuat! 
pause
