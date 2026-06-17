import os
import whisper

class WhisperTranscriber:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WhisperTranscriber, cls).__new__(cls)
            cls._instance.model = None
        return cls._instance

    def __init__(self, model_name="base", model_dir="data/models/whisper"):
        self.model_name = model_name
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)

    def load_model(self):
        if self.model is None:
            try:
                # Memuat model Whisper lokal atau men-download ke model_dir
                print(f"Loading Whisper model '{self.model_name}' from {self.model_dir}...")
                self.model = whisper.load_model(self.model_name, download_root=self.model_dir)
                print("Whisper model loaded successfully!")
                return True
            except Exception as e:
                print(f"Error loading Whisper model: {e}")
                return False
        return True

    def transcribe(self, audio_path):
        if not self.load_model():
            return "Error: Whisper model not loaded."

        try:
            if not os.path.exists(audio_path):
                return f"Error: Audio file {audio_path} not found."
            
            result = self.model.transcribe(audio_path)
            return result.get("text", "").strip()
        except Exception as e:
            print(f"Error during transcription: {e}")
            return f"Error: Transcription failed ({str(e)})."
