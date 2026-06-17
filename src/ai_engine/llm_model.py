import ollama

class LlamaModel:
    def __init__(self, model_name="qwen2.5:0.5b"):
        self.model_name = model_name

    def set_model(self, model_name):
        self.model_name = model_name

    def is_ollama_running(self):
        try:
            ollama.list()
            return True
        except Exception:
            return False

    def get_installed_models(self):
        try:
            response = ollama.list()
            # Model response di library ollama biasanya memiliki list "models"
            # yang masing-masing modelnya bertipe dictionary atau object dengan atribut 'model' atau 'name'
            models = []
            if hasattr(response, 'models'):
                for m in response.models:
                    models.append(m.model)
            elif isinstance(response, dict) and 'models' in response:
                for m in response['models']:
                    models.append(m.get('name', m.get('model', '')))
            return models
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def generate_response(self, messages):
        if not self.is_ollama_running():
            return "Error: Ollama service is not running. Please start Ollama."

        try:
            # Format pesan ke bentuk [{"role": m["role"], "content": m["content"]} for m in messages]
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

            response = ollama.chat(model=self.model_name, messages=formatted_messages)
            
            if hasattr(response, 'message'):
                return response.message.content
            elif isinstance(response, dict) and 'message' in response:
                return response['message'].get('content', '')
            return str(response)
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return f"Error: Failed to get response from model '{self.model_name}'. ({str(e)})"

    def pull_model(self, model_name, progress_callback=None):
        try:
            # Menggunakan generator untuk memantau progress unduhan
            current_digest = ""
            for progress in ollama.pull(model_name, stream=True):
                status = progress.get('status', '')
                completed = progress.get('completed', 0)
                total = progress.get('total', 0)
                digest = progress.get('digest', '')
                
                if digest != current_digest:
                    current_digest = digest
                
                percent = 0
                if total > 0:
                    percent = int((completed / total) * 100)
                
                if progress_callback:
                    progress_callback(status, percent)
            return True
        except Exception as e:
            print(f"Error pulling model {model_name}: {e}")
            return False
