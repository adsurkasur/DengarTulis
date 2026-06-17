import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                             QLabel, QComboBox, QProgressBar, QListWidget, 
                             QListWidgetItem, QFrame, QSplitter, QStackedWidget,
                             QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QTextCursor

from src.ai_engine.stt_whisper import WhisperTranscriber
from src.ai_engine.tts_coqui import CoquiTTS
from src.ai_engine.llm_model import LlamaModel
from src.utils.audio_handler import AudioRecorder, AudioPlayer
from src.utils.memory_manager import MemoryManager

# --- WORKER THREADS ---

class STTWorker(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, transcriber, audio_path):
        super().__init__()
        self.transcriber = transcriber
        self.audio_path = audio_path

    def run(self):
        result = self.transcriber.transcribe(self.audio_path)
        self.finished.emit(result)

class LLMWorker(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, model, messages):
        super().__init__()
        self.model = model
        self.messages = messages

    def run(self):
        result = self.model.generate_response(self.messages)
        self.finished.emit(result)

class TTSWorker(QThread):
    finished = pyqtSignal(bool, str)
    
    def __init__(self, tts_engine, text, player, output_path="output.wav"):
        super().__init__()
        self.tts_engine = tts_engine
        self.text = text
        self.player = player
        self.output_path = output_path

    def run(self):
        success = self.tts_engine.synthesize(self.text, self.output_path)
        if success:
            # Mainkan secara non-blocking
            self.player.play_audio(self.output_path)
            self.finished.emit(True, self.output_path)
        else:
            self.finished.emit(False, "")

class PullModelWorker(QThread):
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(bool)

    def __init__(self, model_engine, model_name):
        super().__init__()
        self.model_engine = model_engine
        self.model_name = model_name

    def run(self):
        def cb(status, percent):
            self.progress.emit(status, percent)
        
        success = self.model_engine.pull_model(self.model_name, cb)
        self.finished.emit(success)

# --- MODERN STYLESHEET (Dark Mode & Premium UI) ---

STYLE_SHEET = """
QMainWindow {
    background-color: #121214;
}

QWidget {
    color: #e1e1e6;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QFrame#sidebar {
    background-color: #1a1a1e;
    border-right: 1px solid #29292e;
}

QFrame#chatContainer {
    background-color: #121214;
}

QPushButton {
    background-color: #29292e;
    border: 1px solid #3e3e42;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    min-height: 18px;
}

QPushButton:hover {
    background-color: #3e3e42;
    border-color: #6200ee;
}

QPushButton:pressed {
    background-color: #1a1a1e;
}

QPushButton#accentBtn {
    background-color: #6200ee;
    border: none;
    color: #ffffff;
}

QPushButton#accentBtn:hover {
    background-color: #7f39fb;
}

QPushButton#recordBtn {
    background-color: #cf6679;
    border: none;
    color: #000000;
}

QPushButton#recordBtn:hover {
    background-color: #df7e8f;
}

QLineEdit, QTextEdit, QSpinBox, QComboBox {
    background-color: #1a1a1e;
    border: 1px solid #29292e;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #6200ee;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #6200ee;
}

QListWidget {
    background-color: #1a1a1e;
    border: 1px solid #29292e;
    border-radius: 6px;
}

QProgressBar {
    border: 1px solid #29292e;
    border-radius: 6px;
    text-align: center;
    background-color: #1a1a1e;
}

QProgressBar::chunk {
    background-color: #6200ee;
    border-radius: 5px;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#subtitleLabel {
    font-size: 11px;
    color: #88888d;
}
"""

class DengarTulisGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DengarTulis 🎙️✍️ - AI Lokal & Offline Dikte")
        self.resize(1000, 700)
        self.setStyleSheet(STYLE_SHEET)

        # Inisialisasi model & utilitas
        self.recorder = AudioRecorder()
        self.player = AudioPlayer()
        self.memory = MemoryManager()
        
        # Default engines
        self.whisper_engine = WhisperTranscriber()
        self.tts_engine = CoquiTTS()
        self.llm_engine = LlamaModel()

        # State perekaman & pemutaran
        self.is_recording = False
        self.temp_audio_path = "data/temp_record.wav"
        
        # State Dikte Interaktif
        self.dictation_chunks = []
        self.dictation_index = 0

        self.setup_ui()
        self.refresh_ollama_models()

    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- SIDEBAR (Kiri) ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(15)

        # Header sidebar
        logo_label = QLabel("DengarTulis 🎙️")
        logo_label.setObjectName("titleLabel")
        sidebar_layout.addWidget(logo_label)

        desc_label = QLabel("Dikte & Asisten AI Lokal Offline")
        desc_label.setObjectName("subtitleLabel")
        sidebar_layout.addWidget(desc_label)

        # Pembatas
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #29292e;")
        sidebar_layout.addWidget(line)

        # Bagian 1: Pengaturan Model LLM (Ollama)
        sidebar_layout.addWidget(QLabel("<b>Model AI (Ollama)</b>"))
        
        self.model_combo = QComboBox()
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        sidebar_layout.addWidget(self.model_combo)

        btn_layout = QHBoxLayout()
        self.refresh_models_btn = QPushButton("Refresh")
        self.refresh_models_btn.clicked.connect(self.refresh_ollama_models)
        btn_layout.addWidget(self.refresh_models_btn)
        sidebar_layout.addLayout(btn_layout)

        # Bagian 2: Unduh Model
        sidebar_layout.addWidget(QLabel("<b>Pull Model Baru</b>"))
        self.pull_model_input = QLineEdit()
        self.pull_model_input.setPlaceholderText("cth: qwen2.5:0.5b")
        sidebar_layout.addWidget(self.pull_model_input)
        
        self.pull_model_btn = QPushButton("Pull Model")
        self.pull_model_btn.clicked.connect(self.pull_new_model)
        sidebar_layout.addWidget(self.pull_model_btn)

        # Progress bar unduhan
        self.pull_progress_label = QLabel("")
        self.pull_progress_label.setObjectName("subtitleLabel")
        sidebar_layout.addWidget(self.pull_progress_label)
        self.pull_progress_bar = QProgressBar()
        self.pull_progress_bar.setTextVisible(True)
        self.pull_progress_bar.setVisible(False)
        self.pull_progress_bar.setFormat("Mengunduh model LLM... %p%")
        sidebar_layout.addWidget(self.pull_progress_bar)

        # Bagian 3: Riwayat Sesi
        sidebar_layout.addWidget(QLabel("<b>Riwayat Percakapan</b>"))
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self.load_selected_session)
        sidebar_layout.addWidget(self.session_list)

        self.new_session_btn = QPushButton("+ New Chat")
        self.new_session_btn.setObjectName("accentBtn")
        self.new_session_btn.clicked.connect(self.start_new_session)
        sidebar_layout.addWidget(self.new_session_btn)

        sidebar_layout.addStretch()
        
        # Info Status Offline
        self.status_label = QLabel("🟢 Status: Offline-Ready")
        self.status_label.setStyleSheet("color: #03dac6; font-weight: bold;")
        sidebar_layout.addWidget(self.status_label)

        main_layout.addWidget(sidebar)

        # --- CHAT CONTAINER / MAIN AREA (Kanan) ---
        main_content = QFrame()
        main_content.setObjectName("chatContainer")
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setContentsMargins(20, 20, 20, 20)
        main_content_layout.setSpacing(15)

        # Mode Selector Tabs (Chat AI vs Dikte Interaktif)
        mode_layout = QHBoxLayout()
        self.tab_chat_btn = QPushButton("Mode Chat AI")
        self.tab_chat_btn.setObjectName("accentBtn")
        self.tab_chat_btn.clicked.connect(lambda: self.switch_mode(0))
        
        self.tab_dictation_btn = QPushButton("Mode Dikte Interaktif")
        self.tab_dictation_btn.clicked.connect(lambda: self.switch_mode(1))
        
        mode_layout.addWidget(self.tab_chat_btn)
        mode_layout.addWidget(self.tab_dictation_btn)
        mode_layout.addStretch()
        main_content_layout.addLayout(mode_layout)

        # Stacked widget untuk mode
        self.mode_stack = QStackedWidget()
        
        # -- MODE 1: CHAT AI --
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_layout.addWidget(self.chat_display)

        # Input area
        input_container = QHBoxLayout()
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ketik pesan di sini atau gunakan tombol rekam...")
        self.chat_input.returnPressed.connect(self.send_chat_message)
        input_container.addWidget(self.chat_input)

        self.record_btn = QPushButton("Rekam 🎙️")
        self.record_btn.setObjectName("recordBtn")
        self.record_btn.clicked.connect(self.toggle_recording)
        input_container.addWidget(self.record_btn)

        self.send_btn = QPushButton("Kirim")
        self.send_btn.setObjectName("accentBtn")
        self.send_btn.clicked.connect(self.send_chat_message)
        input_container.addWidget(self.send_btn)

        chat_layout.addLayout(input_container)
        self.mode_stack.addWidget(chat_widget)

        # -- MODE 2: DIKTE INTERAKTIF --
        dikte_widget = QWidget()
        dikte_layout = QVBoxLayout(dikte_widget)
        dikte_layout.setContentsMargins(0, 0, 0, 0)

        # Text input to dictation
        dikte_layout.addWidget(QLabel("<b>Masukkan Teks untuk Dikte:</b>"))
        self.dictation_text_input = QTextEdit()
        self.dictation_text_input.setPlaceholderText("Tulis atau tempel teks panjang di sini untuk didektekan kata demi kata secara lokal...")
        dikte_layout.addWidget(self.dictation_text_input)

        # Dikte settings
        dikte_settings = QHBoxLayout()
        dikte_settings.addWidget(QLabel("Jumlah kata per potongan dikte:"))
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(1, 50)
        self.chunk_size_spin.setValue(5)
        dikte_settings.addWidget(self.chunk_size_spin)
        
        self.start_dictation_btn = QPushButton("Mulai Dikte")
        self.start_dictation_btn.setObjectName("accentBtn")
        self.start_dictation_btn.clicked.connect(self.start_dictation)
        dikte_settings.addWidget(self.start_dictation_btn)
        dikte_settings.addStretch()
        dikte_layout.addLayout(dikte_settings)

        # Dictation Player Panel
        self.player_panel = QFrame()
        self.player_panel.setStyleSheet("background-color: #1a1a1e; border-radius: 8px; padding: 15px;")
        self.player_panel.setEnabled(False)
        player_layout = QVBoxLayout(self.player_panel)

        self.current_chunk_label = QLabel("Dikte belum dimulai.")
        self.current_chunk_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        self.current_chunk_label.setWordWrap(True)
        player_layout.addWidget(self.current_chunk_label)

        self.progress_chunk_label = QLabel("Bagian: 0 / 0")
        self.progress_chunk_label.setObjectName("subtitleLabel")
        player_layout.addWidget(self.progress_chunk_label)

        controls_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Kembali")
        self.prev_btn.clicked.connect(self.prev_dictation_chunk)
        controls_layout.addWidget(self.prev_btn)

        self.repeat_btn = QPushButton("Ulang")
        self.repeat_btn.clicked.connect(self.repeat_dictation_chunk)
        controls_layout.addWidget(self.repeat_btn)

        self.next_btn = QPushButton("Lanjut")
        self.next_btn.setObjectName("accentBtn")
        self.next_btn.clicked.connect(self.next_dictation_chunk)
        controls_layout.addWidget(self.next_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_dictation)
        controls_layout.addWidget(self.stop_btn)

        player_layout.addLayout(controls_layout)
        dikte_layout.addWidget(self.player_panel)

        self.mode_stack.addWidget(dikte_widget)
        main_content_layout.addWidget(self.mode_stack)

        main_layout.addWidget(main_content)

        # Load session awal
        self.load_session_list()
        self.start_new_session()

    # --- ACTION HANDLERS & LOGIC ---

    def switch_mode(self, index):
        self.mode_stack.setCurrentIndex(index)
        if index == 0:
            self.tab_chat_btn.setObjectName("accentBtn")
            self.tab_dictation_btn.setObjectName("")
        else:
            self.tab_chat_btn.setObjectName("")
            self.tab_dictation_btn.setObjectName("accentBtn")
        self.tab_chat_btn.style().polish(self.tab_chat_btn)
        self.tab_dictation_btn.style().polish(self.tab_dictation_btn)

    def refresh_ollama_models(self):
        models = self.llm_engine.get_installed_models()
        self.model_combo.clear()
        
        if models:
            self.model_combo.addItems(models)
            # Set default model jika ada qwen
            for i in range(self.model_combo.count()):
                if "qwen" in self.model_combo.itemText(i).lower():
                    self.model_combo.setCurrentIndex(i)
                    break
        else:
            self.model_combo.addItem("qwen2.5:0.5b")
            self.append_chat_log("System", "⚠️ Layanan Ollama offline atau tidak mendeteksi model lokal.")

    def on_model_changed(self):
        selected_model = self.model_combo.currentText()
        if selected_model:
            self.llm_engine.set_model(selected_model)

    def pull_new_model(self):
        model_name = self.pull_model_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Peringatan", "Nama model tidak boleh kosong.")
            return

        self.pull_model_btn.setEnabled(False)
        self.pull_progress_label.setText(f"Mulai mendownload {model_name}...")
        self.pull_progress_bar.setValue(0)

        self.pull_worker = PullModelWorker(self.llm_engine, model_name)
        self.pull_worker.progress.connect(self.on_pull_progress)
        self.pull_worker.finished.connect(self.on_pull_finished)
        self.pull_worker.start()

    def on_pull_progress(self, status, percent):
        self.pull_progress_label.setText(f"Status: {status}")
        self.pull_progress_bar.setValue(percent)

    def on_pull_finished(self, success):
        self.pull_model_btn.setEnabled(True)
        if success:
            QMessageBox.information(self, "Sukses", f"Model berhasil diunduh!")
            self.refresh_ollama_models()
        else:
            QMessageBox.critical(self, "Gagal", "Gagal mengunduh model. Pastikan Ollama menyala dan terkoneksi internet.")
            self.pull_progress_label.setText("Gagal mengunduh.")

    def load_session_list(self):
        self.session_list.clear()
        sessions = self.memory.get_all_sessions()
        for s in sessions:
            item = QListWidgetItem(s.replace("session_", "").replace(".json", ""))
            item.setData(Qt.ItemDataRole.UserRole, s)
            self.session_list.addItem(item)

    def start_new_session(self):
        session_file = self.memory.new_session()
        self.load_session_list()
        self.chat_display.clear()
        self.append_chat_log("System", "Sesi obrolan baru dimulai. AI DengarTulis siap membantu.")

    def load_selected_session(self, item):
        session_file = item.data(Qt.ItemDataRole.UserRole)
        self.memory.set_session(session_file)
        self.chat_display.clear()
        
        history = self.memory.get_history()
        for msg in history:
            role = "Anda" if msg["role"] == "user" else "AI DengarTulis"
            self.append_chat_log(role, msg["content"])

    def append_chat_log(self, sender, text):
        color = "#e1e1e6"
        if sender == "Anda":
            color = "#cf6679"
        elif sender == "AI DengarTulis":
            color = "#03dac6"
        elif sender == "System":
            color = "#88888d"
            
        self.chat_display.append(f"<span style='color: {color};'><b>{sender}:</b> {text}</span><br>")
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

    # --- PEREKAMAN SUARA & TRANSKRIPSI ---

    def toggle_recording(self):
        if not self.is_recording:
            # Mulai rekam
            self.recorder.start_recording()
            self.is_recording = True
            self.record_btn.setText("Berhenti 🟥")
            self.record_btn.setStyleSheet("background-color: #cf6679; color: white;")
            self.chat_input.setPlaceholderText("Merekam audio...")
        else:
            # Berhenti rekam
            self.is_recording = False
            self.record_btn.setText("Rekam 🎙️")
            self.record_btn.setStyleSheet("")
            self.chat_input.setPlaceholderText("Mentranskripsi suara...")
            
            success = self.recorder.stop_recording(self.temp_audio_path)
            if success:
                self.transcribe_audio_file(self.temp_audio_path)
            else:
                QMessageBox.warning(self, "Peringatan", "Gagal merekam suara.")
                self.chat_input.setPlaceholderText("Ketik pesan di sini...")

    def transcribe_audio_file(self, filepath):
        self.record_btn.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.append_chat_log("System", "Menganalisis audio dengan model Whisper lokal...")
        
        self.stt_worker = STTWorker(self.whisper_engine, filepath)
        self.stt_worker.finished.connect(self.on_transcription_finished)
        self.stt_worker.start()

    def on_transcription_finished(self, text):
        self.record_btn.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.chat_input.setPlaceholderText("Ketik pesan di sini...")
        
        if text.startswith("Error:"):
            self.append_chat_log("System", f"⚠️ {text}")
        elif not text.strip():
            self.append_chat_log("System", "⚠️ Suara tidak jelas atau tidak terdeteksi.")
        else:
            self.chat_input.setText(text)
            self.send_chat_message()

    # --- CHAT & LLM GENERATION ---

    def send_chat_message(self):
        text = self.chat_input.text().strip()
        if not text:
            return

        self.chat_input.clear()
        self.append_chat_log("Anda", text)
        self.memory.add_message("user", text)

        # Jalankan inferensi LLM di thread terpisah
        self.send_btn.setEnabled(False)
        self.record_btn.setEnabled(False)
        
        history = self.memory.get_history()
        self.llm_worker = LLMWorker(self.llm_engine, history)
        self.llm_worker.finished.connect(self.on_llm_response)
        self.llm_worker.start()

    def on_llm_response(self, response_text):
        self.send_btn.setEnabled(True)
        self.record_btn.setEnabled(True)
        
        self.append_chat_log("AI DengarTulis", response_text)
        self.memory.add_message("assistant", response_text)
        
        # Jalankan sintesis suara secara offline
        self.tts_worker = TTSWorker(self.tts_engine, response_text, self.player)
        self.tts_worker.start()

    # --- DIKTE INTERAKTIF ---

    def start_dictation(self):
        text = self.dictation_text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Peringatan", "Masukkan teks yang ingin didiktekan.")
            return

        chunk_size = self.chunk_size_spin.value()
        words = text.split()
        
        # Bagi kata-kata menjadi beberapa potongan
        self.dictation_chunks = []
        for i in range(0, len(words), chunk_size):
            self.dictation_chunks.append(" ".join(words[i:i + chunk_size]))
            
        self.dictation_index = 0
        self.player_panel.setEnabled(True)
        self.play_current_dictation_chunk()

    def play_current_dictation_chunk(self):
        if 0 <= self.dictation_index < len(self.dictation_chunks):
            chunk_text = self.dictation_chunks[self.dictation_index]
            self.current_chunk_label.setText(chunk_text)
            self.progress_chunk_label.setText(f"Bagian: {self.dictation_index + 1} / {len(self.dictation_chunks)}")
            
            # Matikan tombol saat memutar
            self.next_btn.setEnabled(False)
            self.prev_btn.setEnabled(False)
            
            # Gunakan TTS untuk mensintesis dan memutar audio potongan
            self.dikte_tts_worker = TTSWorker(self.tts_engine, chunk_text, self.player)
            self.dikte_tts_worker.finished.connect(self.on_dictation_audio_finished)
            self.dikte_tts_worker.start()
        else:
            self.stop_dictation()
            self.current_chunk_label.setText("Dikte selesai! 🎉")

    def on_dictation_audio_finished(self, success, filepath):
        self.next_btn.setEnabled(True)
        self.prev_btn.setEnabled(self.dictation_index > 0)

    def next_dictation_chunk(self):
        self.player.stop_audio()
        self.dictation_index += 1
        self.play_current_dictation_chunk()

    def prev_dictation_chunk(self):
        self.player.stop_audio()
        if self.dictation_index > 0:
            self.dictation_index -= 1
            self.play_current_dictation_chunk()

    def repeat_dictation_chunk(self):
        self.player.stop_audio()
        self.play_current_dictation_chunk()

    def stop_dictation(self):
        self.player.stop_audio()
        self.player_panel.setEnabled(False)
        self.current_chunk_label.setText("Dikte berhenti.")
        self.progress_chunk_label.setText("Bagian: 0 / 0")
        self.dictation_chunks = []
        self.dictation_index = 0

    def closeEvent(self, event):
        # Bersihkan audio player & recorder saat keluar
        self.player.stop_audio()
        self.recorder.stop_recording("data/temp_record.wav")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DengarTulisGUI()
    window.show()
    sys.exit(app.exec())
