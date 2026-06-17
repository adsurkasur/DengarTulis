import os
import sys
import argparse

# Menambahkan root folder ke Python path untuk impor modul src.*
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_engine.stt_whisper import WhisperTranscriber
from src.ai_engine.tts_coqui import CoquiTTS
from src.ai_engine.llm_model import LlamaModel
from src.utils.audio_handler import AudioRecorder, AudioPlayer
from src.utils.memory_manager import MemoryManager

def run_cli_mode():
    print("\n==============================================")
    print("🎙️  Selamat datang di DengarTulis - CLI Mode  🎙️")
    print("==============================================\n")
    
    # Inisialisasi engine
    whisper_engine = WhisperTranscriber()
    tts_engine = CoquiTTS()
    llm_engine = LlamaModel()
    recorder = AudioRecorder()
    player = AudioPlayer()
    memory = MemoryManager()

    # Cek model Ollama
    if not llm_engine.is_ollama_running():
        print("⚠️ Warning: Ollama lokal tidak menyala atau tidak merespons.")
    else:
        models = llm_engine.get_installed_models()
        if models:
            print(f"Model Ollama yang terdeteksi: {', '.join(models)}")
            # Default ke model qwen jika ada
            qwen_models = [m for m in models if "qwen" in m.lower()]
            if qwen_models:
                llm_engine.set_model(qwen_models[0])
                print(f"Menggunakan model default: {qwen_models[0]}")
        else:
            print("⚠️ Warning: Tidak mendeteksi model lokal di Ollama. Jalankan 'ollama pull qwen2.5:0.5b'.")

    # Inisialisasi Sesi Chat Baru
    session_file = memory.new_session()
    print("Obrolan dimulai! Semua pesan disimpan secara lokal.")

    while True:
        print("\nPilih Mode:")
        print("1. Chat AI dengan Input Suara/Dikte (Whisper + Ollama + TTS)")
        print("2. Dikte Teks Panjang (TTS Interaktif)")
        print("3. Keluar ('exit')")
        
        mode = input("Pilihan Anda (1/2/3): ").strip()

        if mode == "3" or mode.lower() == "exit":
            print("Terima kasih telah menggunakan DengarTulis!")
            break

        elif mode == "1":
            print("\n--- Mode Chat AI (Ketik '/stop' untuk kembali ke menu utama) ---")
            print("Ketik '/rekam' untuk mendikte via Mikrofon.")
            while True:
                user_input = input("\nAnda: ").strip()
                if user_input.lower() == "/stop":
                    break
                
                if user_input.lower() == "/rekam":
                    print("🔴 Merekam... Tekan Enter untuk menghentikan perekaman.")
                    recorder.start_recording()
                    input()  # Menunggu enter
                    temp_wav = "data/temp_cli_record.wav"
                    success = recorder.stop_recording(temp_wav)
                    if success:
                        print("🤖 Mentranskripsi audio...")
                        transcribed = whisper_engine.transcribe(temp_wav)
                        print(f"Hasil Dikte Suara: {transcribed}")
                        user_input = transcribed
                    else:
                        print("❌ Gagal merekam audio.")
                        continue
                
                if not user_input:
                    continue

                # Add to history
                memory.add_message("user", user_input)
                
                # Get response
                print("🤖 Berpikir...")
                history = memory.get_history()
                response = llm_engine.generate_response(history)
                print(f"\nAI DengarTulis: {response}")
                memory.add_message("assistant", response)
                
                # Speak response
                tts_success = tts_engine.synthesize(response, "data/temp_cli_output.wav")
                if tts_success:
                    player.play_audio("data/temp_cli_output.wav")

        elif mode == "2":
            print("\n--- Mode Dikte Teks Panjang ---")
            text = input("Masukkan teks panjang untuk didiktekan: ").strip()
            if not text:
                continue

            while True:
                try:
                    chunk_size = int(input("Masukkan jumlah kata per potongan dikte (default 5): ") or 5)
                    break
                except ValueError:
                    print("⚠️ Masukkan angka yang valid.")

            words = text.split()
            chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
            
            index = 0
            while index < len(chunks):
                print(f"\n[Potongan {index + 1}/{len(chunks)}]: {chunks[index]}")
                
                # Sintesis dan putar
                tts_success = tts_engine.synthesize(chunks[index], "data/temp_cli_dikte.wav")
                if tts_success:
                    player.play_audio("data/temp_cli_dikte.wav")

                choice = input("Pilihan ('lanjut', 'ulang', 'kembali', 'stop'): ").strip().lower()
                if choice == "lanjut" or choice == "":
                    index += 1
                elif choice == "ulang":
                    continue
                elif choice == "kembali":
                    if index > 0:
                        index -= 1
                    else:
                        print("⚠️ Tidak bisa kembali lebih jauh.")
                elif choice == "stop":
                    player.stop_audio()
                    break
                else:
                    print("Perintah tidak dikenal. Lanjut otomatis.")
                    index += 1

        else:
            print("⚠️ Pilihan menu tidak valid.")

def run_gui_mode():
    try:
        from PyQt6.QtWidgets import QApplication
        from src.gui.gui_main import DengarTulisGUI
        
        app = QApplication(sys.argv)
        window = DengarTulisGUI()
        window.show()
        sys.exit(app.exec())
    except ImportError as e:
        print(f"[ERROR] Gagal memuat PyQt6: {e}")
        print("Menjalankan dalam CLI fallback mode...")
        run_cli_mode()
    except Exception as e:
        print(f"[ERROR] Gagal meluncurkan GUI: {e}")
        print("Menjalankan dalam CLI fallback mode...")
        run_cli_mode()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DengarTulis - AI Lokal & Offline Dikte")
    parser.add_argument("--cli", action="store_true", help="Jalankan dalam mode command-line interface (CLI)")
    args = parser.parse_args()

    # Pastikan direktori data ada
    os.makedirs("data/models", exist_ok=True)
    os.makedirs("data/user_logs", exist_ok=True)

    if args.cli:
        run_cli_mode()
    else:
        run_gui_mode()
