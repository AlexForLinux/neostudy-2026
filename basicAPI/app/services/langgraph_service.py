from langgraph.graph import StateGraph, START, END
from app.schemas.graph_state import MysticState
from app.schemas.intention import Intention
from app.schemas.chat import ChatCompletions
from app.services.chroma_retriever_service import ChromaRetrieverService
from app.services.prompt_service import  PromptService
from app.services.generation_service import GenerationService
from app.services.search_agent_service import SearchAgentService
from app.services.classifier_service import ClassifierService
from app.schemas.chat import Message
import json
import random
from app.schemas.recipe import Recipe
from app.schemas.advice import Advice

class LanggraphService:
    def __init__(self, classifier_service, prompt_service, recipe_retriever_service, advice_retriever_service, search_agent, gen_service):

        self.__classifier_service : ClassifierService = classifier_service
        self.__prompt_service : PromptService = prompt_service
        self.__recipe_retriever_service : ChromaRetrieverService = recipe_retriever_service
        self.__advice_retriever_service : ChromaRetrieverService = advice_retriever_service
        self.__search_agent : SearchAgentService = search_agent
        self.__gen_service : GenerationService = gen_service

        graph = StateGraph(MysticState)

        graph.add_node("main_router", self._classify_intention)
        graph.add_node("advice_retriever", self._retrieve_with_advice)
        graph.add_node("recipe_retriever", self._retrieve_with_recipes)
        # graph.add_node("select_prompt", self._select_prompt)
        graph.add_node("search_agent", self._search)
        graph.add_node("llm_answer", self._generate_answer)

        graph.add_edge(START, "main_router")
        graph.add_conditional_edges(
            "main_router", 
            self._check_intention, 
            {
                Intention.RECIPE: "recipe_retriever", 
                Intention.ADVICE: "advice_retriever",
                Intention.OTHER: "llm_answer"
            }
        )
        # graph.add_edge("recipe_retriever", "select_prompt")
        # graph.add_edge("advice_retriever", "select_prompt")
        graph.add_edge("recipe_retriever", "search_agent")
        graph.add_edge("advice_retriever", "search_agent")

        graph.add_edge("search_agent", "llm_answer")
        graph.add_edge("llm_answer", END)

        self.__worker = graph.compile()

    def run(self, chat: ChatCompletions) -> str:
        response = self.__worker.invoke({
            "chat_story": chat
        })
        return response['message']

    def _classify_intention(self, state: MysticState) -> dict:

        last_user_message = None
        messages = state["chat_story"].messages

        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_message = msg
                break

        if last_user_message is None:
            raise AttributeError()

        intention = self.__classifier_service.classify(last_user_message["content"])

        return {"user_intention": intention}
    
    def _check_intention(self, state: MysticState) -> str:
        return state['user_intention']
    
    def _retrieve_with_advice(self, state: MysticState) -> dict:
        query = state["chat_story"].messages[-1]['content']
        retrieved_data = self.__advice_retriever_service.retrieve(query, 1)
        docs = [doc.model_dump() for _, _, doc in retrieved_data]

        return {"context": json.dumps(docs, ensure_ascii=False)}
    
    def _retrieve_with_recipes(self, state: MysticState) -> dict:
        query = state["chat_story"].messages[-1]['content']
        retrieved_data = self.__recipe_retriever_service.retrieve(query)
        docs = [doc.model_dump() for _, _, doc in retrieved_data]
        
        return {"context": json.dumps(docs, ensure_ascii=False)}
    
    def _search(self, state: MysticState) -> dict:

        system_prompt = self.__prompt_service.get_search_prompt(state["context"], state["user_intention"] == Intention.RECIPE)
        chat = state["chat_story"]
        chat.messages.insert(0, Message(role="system", content=system_prompt))
        search_results = self.__search_agent.run(chat)

        chat.messages = search_results["messages"]
        return {"chat_story": chat}
    
    def _select_prompt(self, state: MysticState) -> dict:
        system_prompt = None

        if (state["user_intention"] == Intention.RECIPE):
            system_prompt = self.__prompt_service.recipe_prompt
        elif (state["user_intention"] == Intention.ADVICE):
            system_prompt = self.__prompt_service.advice_prompt
            
        return {"system_prompt": system_prompt}
    
    def _generate_answer(self, state: MysticState) -> dict:

        chat = state['chat_story']
        intention = state['user_intention']
        schema = None

        if intention == Intention.OTHER:
            system_prompt = self.__prompt_service.other_prompt
            chat.messages.insert(0, {"role": "system", "content": system_prompt})
            result = self.__gen_service.get_common(chat)
            return {"message": result}
        
        elif intention == Intention.RECIPE:
            system_prompt = self.__prompt_service.recipe_prompt
            schema = Recipe
        else:
            system_prompt = self.__prompt_service.advice_prompt
            schema = Advice

        context = state['context']
        system_prompt = system_prompt.replace("<context>[CONTEXT]</context>", context)

        chat.messages.insert(0, {"role": "system", "content": system_prompt})
        result = self.__gen_service.get_structured(chat, schema=schema)

        return {"message": result}