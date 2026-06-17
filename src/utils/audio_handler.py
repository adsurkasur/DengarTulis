import sounddevice as sd
import numpy as np
import wave
import threading
import os
import queue

class AudioRecorder:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.q = queue.Queue()
        self.stream = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.q.put(indata.copy())

    def start_recording(self):
        if self.is_recording:
            return
        self.is_recording = True
        self.q = queue.Queue()
        try:
            self.stream = sd.InputStream(samplerate=self.sample_rate, channels=self.channels, dtype='int16', callback=self._callback)
            self.stream.start()
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.is_recording = False

    def stop_recording(self, output_filepath):
        if not self.is_recording:
            return False
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        if self.q.empty():
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
            # Remove file if it already exists
            if os.path.exists(output_filepath):
                os.remove(output_filepath)
                
            with wave.open(output_filepath, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2) # 2 bytes for int16
                wf.setframerate(self.sample_rate)
                while not self.q.empty():
                    data = self.q.get()
                    wf.writeframes(data.tobytes())
            return True
        except Exception as e:
            print(f"Error saving recorded audio: {e}")
            return False

class AudioPlayer:
    def __init__(self):
        self.is_playing = False
        self.thread = None

    def play_audio(self, filepath, on_finished_callback=None):
        self.stop_audio()
        self.is_playing = True
        self.thread = threading.Thread(target=self._play_loop, args=(filepath, on_finished_callback))
        self.thread.daemon = True
        self.thread.start()

    def _play_loop(self, filepath, on_finished_callback):
        try:
            if not os.path.exists(filepath):
                print(f"Audio file not found: {filepath}")
                self.is_playing = False
                if on_finished_callback:
                    on_finished_callback()
                return

            with wave.open(filepath, 'rb') as wf:
                framerate = wf.getframerate()
                channels = wf.getnchannels()
                frames = wf.readframes(wf.getnframes())
                # Convert bytes to int16 numpy array
                audio_data = np.frombuffer(frames, dtype=np.int16)
                
                # Check if playing was cancelled before we even start
                if not self.is_playing:
                    return

                # Play blocking
                sd.play(audio_data, samplerate=framerate, blocking=True)

        except Exception as e:
            print(f"Error during audio playback: {e}")
        finally:
            self.is_playing = False
            if on_finished_callback:
                on_finished_callback()

    def stop_audio(self):
        self.is_playing = False
        try:
            sd.stop()
        except Exception:
            pass
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
