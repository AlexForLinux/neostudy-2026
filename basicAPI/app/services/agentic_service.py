from openai import OpenAI
import json
from app.config import settings
from app.schemas.recipe import Recipe
from ddgs import DDGS
import trafilatura
from .prompt_service import PromptService
from .recipe_retriever_service import RecipeRetrieverService
from ..schemas.tools import GetRecipesTool, WebSearchTool, UrlReaderTool, FinishTool
from pydantic import ValidationError

# Отдельный сервис для работы с агентом, который собирает рецептурную информацию
class AgenticService:
    def __init__(self, recipe_retriever: RecipeRetrieverService, prompt_service: PromptService):
        self.__client = OpenAI(
            base_url=settings.api_url,
            api_key=settings.api_key
        )
        self.__recipe_retriever = recipe_retriever
        self.__prompt_service = prompt_service
        self.__tools =  {
            "get_recipes": {
                "function": self._get_recipes,
                "description": "Recieve top-3 recipes from Retriever. Each recipe has name, description, list of ingredients, list of cooking steps, list of utensils, list of advice",
                "pydantic": GetRecipesTool
            },
            "web_search": {
                "function": self._web_search,
                "description": "Recieve top-5 web search results. Each result has title, url and snippet",
                "pydantic": WebSearchTool
            },
            "url_reader": {
                "function": self._url_reader,
                "description": "Recieve first 6000 chars of a web page on provided url",
                "pydantic": UrlReaderTool
            },
            "finish": {
                "function": None,
                "description": "Stop reasoning",
                "pydantic": FinishTool
            }
        }
        self.__tools_desc = [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool["description"],
                    "parameters": tool["pydantic"].model_json_schema()
                }
            } for name, tool in self.__tools.items()
        ]

    def _web_search(self, query, n=5):
        results = []

        with DDGS() as ddgs:
            search_results = ddgs.text(
                query=query,
                max_results=n
            )

            for item in search_results:
                results.append({
                    "title": item.get("title"),
                    "url": item.get("href"),
                    "snippet": item.get("body")
                })

        return json.dumps(results, ensure_ascii=False)
    
    def _url_reader(self, url, max_length=6000):
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return "Содержание веб-страницы отсутсвует"
            
        content = trafilatura.extract(
            downloaded, 
            include_comments=False, 
            include_tables=True,
            favor_precision=True,
            output_format="txt"
        )

        if not content:
            return "Содержание веб-страницы отсутсвует"
            
        return content[:max_length]
    
    def _get_recipes(self, query):
        retrieved_data = self.__recipe_retriever.retrieve(query)
        docs = [doc for _, _, doc in retrieved_data]
        return json.dumps(docs, ensure_ascii=False)

    def run(self, model, user_query, max_steps=6):
        
        messages = [
            {"role": "system", "content": self.__prompt_service.collect_recipe},
            {"role": "user", "content": user_query}
        ]

        step = 0
        flag = True
        tool_calls = []

        while (flag):

            step += 1
            if (step > max_steps):
                step -= 1
                break
            
            response = self.__client.chat.completions.create(
                model=model,
                messages=messages,
                tools=self.__tools_desc,
                tool_choice="auto",
            )

            message = response.choices[0].message
            messages.append(message)

            if message.tool_calls:
                error = None
                result = None

                for call in message.tool_calls:
                    func_name = call.function.name

                    try:
                        recieved_args = call.function.arguments
                        self.__tools[func_name]["pydantic"].model_validate_json(recieved_args)
                        args = json.loads(recieved_args)

                        if func_name == "finish":
                            flag = False
                            result = "Reasoning finished"
                            break
                        else:
                            result = self.__tools[func_name]["function"](**args)

                    except ValidationError:
                        error = "Invalid Arguments Given"
                    except:
                        error = "Unsuccessful Tool Calling"
                    finally:
                        tool_calls.append({"tool": func_name, "recieved_args": recieved_args, "error": error})
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": result if error is None else error
                        })

        messages[0] = {"role": "system", "content": self.__prompt_service.build_recipe}            

        response = self.__client.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=Recipe,
        )

        return {
            "tool_calling": tool_calls,
            "achieved": not flag,
            "steps": step,
            "response": response.choices[0].message.parsed
        }
    

    