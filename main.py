from dotenv import load_dotenv
from anthropic import Anthropic
import os

load_dotenv()
my_api_key = os.getenv("ANTHROPIC_API_KEY")

client = Anthropic(api_key=my_api_key)

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=400,
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ]
)

print(response.content[0].text)
print(response)
