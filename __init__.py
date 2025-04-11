import os
from .veo_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# Simple function to load API key from .env
def load_api_key():
    try:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    if line.startswith('GOOGLE_API_KEY='):
                        key = line[len('GOOGLE_API_KEY='):].strip('"\'')
                        os.environ['GOOGLE_API_KEY'] = key
                        print("API key loaded from .env file")
                        return
    except Exception as e:
        print(f"Error loading API key: {e}")

# Load API key
load_api_key()

# For compatibility with ComfyUI
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']