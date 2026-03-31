from langgraph.graph import StateGraph, START, END
from app.schemas.graph_state import MysticState
from app.schemas.intention import Intention
from app.schemas.chat import ChatCompletions
from .gpt_service import gpt_service
from .prompt_service import prompt_service

class LanggraphService:
    def __init__(self):
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
            "user_query": chat
        })
        return response['message']

    def _classify_intention(self, state: MysticState) -> dict:
        return {'user_intention': Intention.RECIPE}
    
    def _check_intention(self, state: MysticState) -> str:
        return state['user_intention']
    
    def _retrieve_with_advice(self, state: MysticState) -> dict:
        return {}
    
    def _retrieve_with_recipes(self, state: MysticState) -> dict:
        return {}
    
    def _select_prompt(self, state: MysticState) -> dict:
        system_prompt = None

        if (state["user_intention"] == Intention.RECIPE):
            system_prompt = prompt_service.recipe_prompt
            
        return {"system_prompt": system_prompt}
    
    def _generate_answer(self, state: MysticState) -> dict:
        chat = state['user_query']
        chat.messages.insert(0, {"role": "system", "content": state["system_prompt"]})

        return {"message": gpt_service.ask_llm(chat)}
    
langgraph_service = LanggraphService()