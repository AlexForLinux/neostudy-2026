from app.config import settings
from app.schemas.chat import ChatCompletions
from app.schemas.recipe import Recipe
from openai import OpenAI

class GenerationService:
    def __init__(self):
        self.__client = OpenAI(
            base_url=settings.api_url,
            api_key=settings.api_key
        )

    def tool_gen(self, data: ChatCompletions, tools):
        response = self.__client.chat.completions.create(
            model=data.model,
            messages=data.messages,
            tools=tools,
            tool_choice="auto",
        )

        return response.choices[0].message

    def ask_llm(self, data: ChatCompletions):
        response = self.__client.chat.completions.parse(
            model = data.model,
            messages = data.messages,
            temperature = data.temperature,
            response_format=Recipe,
            max_completion_tokens=20000
        )

        return response.choices[0].message.parsed