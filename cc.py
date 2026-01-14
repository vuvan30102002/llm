from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Tạo client
client = genai.Client(api_key=GOOGLE_API_KEY)

# Liệt kê model
models = client.models.list()  # <<==== đây mới đúng
for m in models:
    print(m.name)
