import os
import json
from datetime import datetime

class MemoryManager:
    def __init__(self, log_dir="data/user_logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_session = None

    def new_session(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session = f"session_{timestamp}.json"
        self.save_history([])
        return self.current_session

    def get_all_sessions(self):
        try:
            files = [f for f in os.listdir(self.log_dir) if f.endswith(".json")]
            # Sort sessions by newest first
            files.sort(reverse=True)
            return files
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []

    def set_session(self, session_filename):
        self.current_session = session_filename

    def get_history(self):
        if not self.current_session:
            self.new_session()
        
        filepath = os.path.join(self.log_dir, self.current_session)
        if not os.path.exists(filepath):
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading history: {e}")
            return []

    def save_history(self, history):
        if not self.current_session:
            self.new_session()
        
        filepath = os.path.join(self.log_dir, self.current_session)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False

    def add_message(self, role, content):
        history = self.get_history()
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.save_history(history)
