import os
import requests
from dotenv import load_dotenv

print("🔍 Testing ScaleDown API...")

# Load your .env file
load_dotenv()
API_KEY = os.getenv('SCALEDOWN_API_KEY')

if not API_KEY:
    print("❌ ERROR: No API key found in .env!")
    print("Check: SCALEDOWN_API_KEY=your-key in .env file")
    exit()

print(f"✅ API Key loaded: {API_KEY[:10]}...")

# Test ScaleDown API
url = "https://api.scaledown.xyz/compress/raw/"
headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "context": "Python learning roadmap: variables, loops, functions, classes, OOP.",
    "prompt": "Generate 7-day Python learning roadmap",
    "scaledown": {"rate": "auto"}
}

print("📡 Sending request...")
response = requests.post(url, headers=headers, json=payload, timeout=15)

print("Status:", response.status_code)
print("Response:", response.text[:200] + "..." if len(response.text) > 200 else response.text)

if response.status_code == 200:
    result = response.json()
    print("🎉 SUCCESS! ScaleDown working!")
    print("Compressed:", result.get('compressed_prompt', 'No data')[:100] + "...")
    print("✅ Ready for Step 4!")
else:
    print("❌ API Error - Check your API key!")
