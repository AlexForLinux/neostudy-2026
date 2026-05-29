
from .prompt_service import PromptService
from .langgraph_service import LanggraphService

from app.config import settings
from sentence_transformers import SentenceTransformer
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    pipeline
)

from app.services.chroma_retriever_service import ChromaRetrieverService
from app.my_schemas.local_recipe import LocalRecipe
from app.my_schemas.local_advice import LocalAdvice
from app.repo.retriever_repo_protocol import ReadableRepo
from app.repo.recipe_readable_repo import RecipeReadbleRepo
from app.repo.advice_readable_repo import AdviceReadbleRepo
from app.services.generation_service import GenerationService
from app.services.classifier_service import ClassifierService
from app.services.search_agent_service import SearchAgentService

class Service:

    services = None

    @classmethod
    def get_services(cls):
        if cls.services is None:
            cls.services = Service()
        return cls.services

    def __init__(self):
        device = 'cpu'

        class_pipe = pipeline(
            "text-classification",
            model=settings.classifier,
            tokenizer=settings.classifier,
            device=device
        )

        embed_model = SentenceTransformer(settings.embeder, device=device)

        self.gen_service = GenerationService()

        self.classifier_service = ClassifierService(class_pipe)

        self.prompt_service = PromptService({
            'recipe': settings.recipe_prompt,
            'advice': settings.advice_prompt,
            'other': settings.other_prompt,
            'search-recipe': settings.search_recipe_prompt,
            'search-advice': settings.search_advice_prompt
        })

        self.__recipe_repo : ReadableRepo = RecipeReadbleRepo(
            settings.sqlite_db, 
            settings.recipe_docs,
        )

        self.__advice_repo : ReadableRepo = AdviceReadbleRepo(
            settings.sqlite_db,
            settings.advice_docs,
        )
        
        self.recipe_retriever_service = ChromaRetrieverService[LocalRecipe](
            'recipes',
            settings.chroma_db,
            self.__recipe_repo,
            embed_model
        )

        self.advice_retriever_service = ChromaRetrieverService[LocalAdvice](
            'advice',
            settings.chroma_db,
            self.__advice_repo,
            embed_model
        )

        self.search_agent_service = SearchAgentService(self.gen_service)

        self.langgraph_service = LanggraphService(
            self.classifier_service,
            self.prompt_service, 
            self.recipe_retriever_service, 
            self.advice_retriever_service,
            self.search_agent_service,
            self.gen_service
        )
