from app.config import settings
from app.schemas.chat import ChatCompletions
from app.schemas.recipe import Recipe
from ollama import Client

class OllamaService:
    def __init__(self, host):
        self.__client = Client(host=host)

    def ask_llm(self, data: ChatCompletions):
        response = self.__client.chat(
            model = data.model,
            messages = data.messages,
            options = {
                "temperature": data.temperature
            },
            # format = Recipe.model_json_schema()
        )
        return response

ollama_service = OllamaService(settings.host)