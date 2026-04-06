from langgraph.graph import StateGraph, START, END
from app.schemas.graph_state import MysticState
from app.schemas.intention import Intention
from app.schemas.chat import ChatCompletions
import json

class LanggraphService:
    def __init__(self, prompt_service, recipe_retriever_service, gpt_service):

        self.__prompt_service = prompt_service
        self.__recipe_retriever_service = recipe_retriever_service
        self.__gpt_service = gpt_service

        graph = StateGraph(MysticState)

        graph.add_node("main_router", self._classify_intention)
        graph.add_node("advice_retriever", self._retrieve_with_advice)
        graph.add_node("recipe_retriever", self._retrieve_with_recipes)
        graph.add_node("select_prompt", self._select_prompt)
        graph.add_node("llm_answer", self._generate_answer)

        graph.add_edge(START, "main_router")
        graph.add_conditional_edges(
            "main_router", 
            self._check_intention, 
            {
                Intention.RECIPE: "recipe_retriever", 
                Intention.ADVICE: "advice_retriever",
                Intention.OTHER: "select_prompt"
            }
        )
        graph.add_edge("recipe_retriever", "select_prompt")
        graph.add_edge("advice_retriever", "select_prompt")
        graph.add_edge("select_prompt", "llm_answer")
        graph.add_edge("llm_answer", END)

        self.__worker = graph.compile()

    def run(self, chat: ChatCompletions) -> str:
        response = self.__worker.invoke({
            "chat_story": chat
        })
        return response['message']

    def _classify_intention(self, state: MysticState) -> dict:
        return {'user_intention': Intention.RECIPE}
    
    def _check_intention(self, state: MysticState) -> str:
        return state['user_intention']
    
    def _retrieve_with_advice(self, state: MysticState) -> dict:
        return {}
    
    def _retrieve_with_recipes(self, state: MysticState) -> dict:
        query = state["chat_story"].messages[-1]['content']
        retrieved_data = self.__recipe_retriever_service.retrieve(query)
        docs = [doc for _, _, doc in retrieved_data]

        return {"context": json.dumps(docs, ensure_ascii=False)}
    
    def _select_prompt(self, state: MysticState) -> dict:
        system_prompt = None

        if (state["user_intention"] == Intention.RECIPE):
            system_prompt = self.__prompt_service.recipe_prompt
            
        return {"system_prompt": system_prompt}
    
    def _generate_answer(self, state: MysticState) -> dict:
        chat = state['chat_story']
        context = state['context']
        system_prompt = state['system_prompt']

        if context:
            system_prompt = system_prompt.replace("<context>[CONTEXT]</context>", context)

        chat.messages.insert(0, {"role": "system", "content": system_prompt})

        return {"message": self.__gpt_service.ask_llm(chat)}