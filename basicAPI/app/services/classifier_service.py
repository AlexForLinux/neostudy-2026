from app.schemas.intention import Intention
import random

#TODO: в процессе
class ClassifierService:
    def classify(self, query: str) -> Intention:
        mp =  {
            0: Intention.RECIPE,
            1: Intention.ADVICE,
            2: Intention.OTHER
        }
        return mp[random.randint(0,2)]