import json
from ddgs import DDGS
import trafilatura
from app.services.generation_service import GenerationService
from ..schemas.tools import WebSearchTool, UrlReaderTool, FinishTool
from pydantic import ValidationError
from app.schemas.chat import ChatCompletions, Message, ToolMessage

class SearchAgentService:
    def __init__(self, gen_service: GenerationService):
        self.__gen_service = gen_service
        self.__tools =  {
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
            "accept": {
                "function": None,
                "description": "Accept provided data as enough",
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
    
    def run(self, chat: ChatCompletions, max_steps=8):
        
        messages = chat.messages
        print("START", chat.messages)

        step = 0
        flag = True
        tool_calls = []

        while (flag):

            step += 1
            if (step > max_steps):
                step -= 1
                break

            message = self.__gen_service.tool_gen(chat, self.__tools_desc)
            msg = message.model_dump()

            print("STEP", step, msg)
            
            msg.pop('reasoning_content', None)
            msg.pop('provider_specific_fields', None)
            messages.append(msg)


            if message.tool_calls:
                error = None
                result = None

                for call in message.tool_calls:
                    func_name = call.function.name

                    try:
                        recieved_args = call.function.arguments
                        self.__tools[func_name]["pydantic"].model_validate_json(recieved_args)
                        args = json.loads(recieved_args)

                        if func_name == "accept":
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
                        messages.append(ToolMessage(
                            role="tool", 
                            content=result if error is None else error, 
                            tool_call_id=call.id
                        ))

        print("TOOLS", tool_calls)

        return {
            "tool_calling": tool_calls,
            "achieved": not flag,
            "steps": step,
            "messages": list(filter(lambda m: m["role"] != "system", messages))
        }
    
    

    