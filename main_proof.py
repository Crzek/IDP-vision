import os
from google import genai
import instructor
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY:", GEMINI_API_KEY)


# Define your Pydantic model
class User(BaseModel):
    name: str
    age: int


# Initialize and patch the client
client = instructor.from_provider(
    "google/gemini-2.0-flash-lite", api_key=GEMINI_API_KEY
)

# Extract structured data
response = client.create(
    messages=[{"role": "user", "content": "Extract: Jason is 25 years old"}],
    response_model=User,
)

print(response)  # User(name='Jason', age=25)
