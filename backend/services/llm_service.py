from openai import OpenAI
from os import getenv
from dotenv import load_dotenv

class LLMService:
    def __init__(self):
        load_dotenv()
        API_KEY = getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            base_url='https://openrouter.ai/api/v1',
            api_key=API_KEY)
    
    def example(self, prompt: str):
        response = self.client.responses.create(
            model="kwaipilot/kat-coder-pro:free",
            input=prompt
        )
        return response.output_text
    
if __name__ == "__main__":
    llm_service = LLMService()
    result = llm_service.example("What is the capital of France?")
    print(result)