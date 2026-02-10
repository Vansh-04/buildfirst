import os
from google import genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)

print("📋 Available models:\n")

for model in client.models.list():
    name = model.name
    methods = getattr(model, "supported_generation_methods", [])
    print(f"- {name}")
    if methods:
        print(f"  methods: {methods}")
    print()
