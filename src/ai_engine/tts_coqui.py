import os
import pyttsx3

class CoquiTTS:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CoquiTTS, cls).__new__(cls)
            cls._instance.engine = None
        return cls._instance

    def __init__(self, *args, **kwargs):
        # Menjaga kompatibilitas inisialisasi parameter meskipun kita beralih ke pyttsx3
        pass

    def load_model(self):
        if self.engine is None:
            try:
                print("Loading local TTS engine (pyttsx3)...")
                self.engine = pyttsx3.init()
                # Mengubah kecepatan suara agar lebih natural
                rate = self.engine.getProperty('rate')
                self.engine.setProperty('rate', rate - 30)
                print("TTS engine loaded successfully!")
                return True
            except Exception as e:
                print(f"Error loading TTS engine: {e}")
                return False
        return True

    def synthesize(self, text, output_path="output.wav"):
        if not self.load_model():
            print("Error: TTS Engine is not loaded.")
            return False

        try:
            # Hapus file output lama jika ada
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception:
                    pass

            # Generate audio file
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            return os.path.exists(output_path)
        except Exception as e:
            print(f"Error synthesizing text to speech: {e}")
            return False
