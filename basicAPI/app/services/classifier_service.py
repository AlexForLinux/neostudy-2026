from app.schemas.intention import Intention
import random
from langfuse import observe

#TODO: в процессе
class ClassifierService:

    @observe()
    def classify(self, query: str) -> Intention:
        mp =  {
            0: Intention.RECIPE,
            1: Intention.ADVICE,
            2: Intention.OTHER
        }
        return mp[random.randint(0,2)]