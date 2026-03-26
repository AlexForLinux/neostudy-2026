from app.config import settings
from app.schemas.chat import ChatCompletions
from app.schemas.recipe import Recipe
from openai import OpenAI

class GPTService:
    def __init__(self):
        self.__client = OpenAI(
            base_url=settings.api_url,
            api_key=settings.api_key
        )

    def ask_llm(self, data: ChatCompletions) -> str:
        response = self.__client.chat.completions.create(
            model = data.model,
            messages = data.messages,
            temperature = data.temperature
            # format = Recipe.model_json_schema()
        )

        return response.choices[0].message.content

gpt_service = GPTService()