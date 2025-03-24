from TTS.api import TTS
import whisper
import pyaudio
import wave
import os
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from contextlib import redirect_stdout

# Fix random seed untuk langdetect (biar hasil konsisten)
DetectorFactory.seed = 0

def transcribe_audio(filename):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(filename)
        if not result['text'].strip():
            print("⚠️ Tidak ada hasil transkripsi. Pastikan audio jelas.")
            return None
        return result['text']
    except Exception as e:
        print(f"❌ Error saat transkripsi: {e}")
        return None

def speak_text(text):
    try:
        # Sembunyikan pesan log Coqui TTS
        with open(os.devnull, "w") as devnull:
            with redirect_stdout(devnull):
                tts = TTS(model_name="tts_models/en/ljspeech/glow-tts")

        tts.tts_to_file(text=text, file_path="output.wav")

        # Putar hasil audio
        wf = wave.open("output.wav", 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(1024)
        while data:
            try:
                stream.write(data)
            except:
                print("⚠️ Masalah buffer audio, mencoba ulang...")
            data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()
        p.terminate()
    except Exception as e:
        print(f"❌ Error saat mengeluarkan suara: {e}")

def split_text(text, chunk_size):
    words = text.split()
    return [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]

def interactive_dictation(text):
    # Loop validasi jumlah kata per potongan dikte
    while True:
        try:
            chunk_size = int(input("Masukkan jumlah kata per potongan dikte (minimal 1): "))
            if chunk_size < 1:
                print("⚠️ Jumlah kata minimal 1. Coba lagi.")
                continue
            break
        except ValueError:
            print("⚠️ Input tidak valid! Masukkan angka yang benar.")

    chunks = split_text(text, chunk_size)
    index = 0

    while index < len(chunks):
        print("Dikte:", " ".join(chunks[index]))
        speak_text(" ".join(chunks[index]))

        user_input = input("Ketik 'lanjut' untuk melanjutkan, 'ulang' untuk mengulang, 'kembali' untuk mundur, atau 'stop' untuk berhenti: ").lower()

        if user_input == "lanjut":
            index += 1
        elif user_input == "ulang":
            continue
        elif user_input == "kembali":
            if index > 0:
                index -= 1
            else:
                print("⚠️ Tidak bisa kembali lebih jauh.")
        elif user_input == "stop":
            print("Dikte berhenti.")
            break
        else:
            print("⚠️ Perintah tidak dikenal. Silakan coba lagi.")

if __name__ == "__main__":
    print("Selamat datang di DengarTulis! 🎙️✍️")

    while True:
        mode = input("\nPilih mode (1: Transkripsi Audio, 2: Dikte Interaktif, 'exit' untuk keluar): ")

        if mode.lower() == "exit":
            print("Keluar dari program. Terima kasih!")
            break

        if mode == "1":
            audio_file = input("Masukkan nama file audio (misal: test/test.wav): ")

            if not os.path.isfile(audio_file):
                print(f"❌ File '{audio_file}' tidak ditemukan. Pastikan path benar!")
                continue

            transcribed_text = transcribe_audio(audio_file)
            if transcribed_text:
                print(f"Hasil transkripsi: {transcribed_text}")

        elif mode == "2":
            input_text = input("Masukkan teks untuk didiktekan: ")
            interactive_dictation(input_text)

        else:
            print("⚠️ Mode tidak dikenal. Silakan pilih antara '1' atau '2'.")
