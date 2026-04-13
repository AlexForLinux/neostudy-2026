from .gpt_service import GPTService
from .prompt_service import PromptService
from .recipe_retriever_service import RecipeRetrieverService
from .langgraph_service import LanggraphService
from app.repo.recipe_repo import RecipeRepo
from app.config import settings
from sentence_transformers import SentenceTransformer

class Service:

    services = None

    @classmethod
    def get_services(cls):
        if cls.services is None:
            cls.services = Service()
        return cls.services

    def __init__(self):
        self.gpt_service = GPTService()
        self.prompt_service = PromptService({
            'recipe': settings.recipe_prompt,
            'advice': settings.advice_prompt,
            'other': settings.other_prompt,
            'collect_recipe': settings.collect_recipe,
            'build_recipe': settings.build_recipe
        })

        self.__recipeRepo = RecipeRepo(settings.sqlite_db, settings.recipe_docs)
        self.recipe_retriever_service = RecipeRetrieverService(
            settings.recipe_faiss,
            SentenceTransformer("BAAI/bge-m3"),
            self.__recipeRepo
        )

        self.langgraph_service = LanggraphService(
            self.prompt_service, 
            self.recipe_retriever_service, 
            self.gpt_service
        )
