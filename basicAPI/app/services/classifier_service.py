from app.schemas.intention import Intention
import random
# from langfuse import observe
from app.config import settings

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

class ClassifierService:

    def __init__(self, tokenizer, classifier):
        self.__device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.__tokenizer = tokenizer

        classifier.to(self.__device)
        classifier.eval()
        self.__model = classifier

    # @observe()
    def classify(self, query: str) -> Intention:

        inputs = self.__tokenizer(
            query,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )

        inputs = {
            k: v.to(self.__device)
            for k, v in inputs.items()
        }

        with torch.no_grad():
            outputs = self.__model(**inputs)

        probs = torch.softmax(outputs.logits, dim=-1)

        pred_id = torch.argmax(probs, dim=-1).item()
        
        mp =  {
            0: Intention.RECIPE,
            1: Intention.ADVICE,
            2: Intention.OTHER
        }

        print(query, mp[pred_id])

        return mp[pred_id]