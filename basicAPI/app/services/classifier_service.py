from app.my_schemas.intention import Intention
import random
# from langfuse import observe
from app.config import settings

import torch

class ClassifierService:

    def __init__(self, pipe):
        self.__pipe = pipe
        self.__mp =  {
            "LABEL_0": Intention.RECIPE,
            "LABEL_1": Intention.ADVICE,
            "LABEL_2": Intention.OTHER
        }

    # @observe()
    def classify(self, query: str) -> Intention:

        result = self.__pipe(query, truncation=True, max_length=128)[0]

        predicted_label = result['label']

        print(query, self.__mp[predicted_label])

        return self.__mp[predicted_label]