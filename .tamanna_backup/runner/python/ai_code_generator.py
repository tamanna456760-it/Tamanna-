# Optional: AI code generator using OpenAI GPT API
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_code(prompt, filename):
    response = client.responses.create(
        model="gpt-4.1-mini", input=f"Write code for: {prompt}"
    )
    code = response.output[0].content[0].text
    with open(filename, "w") as f:
        f.write(code)
    return code
