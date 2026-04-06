from app.config import settings

class PromptService():
    def __init__(self, prompt_paths):
        self.recipe_prompt = self._read_system_prompt(prompt_paths['recipe'])
        self.advice_prompt = self._read_system_prompt(prompt_paths['advice'])
        self.other_prompt = self._read_system_prompt(prompt_paths['other'])

    def _read_system_prompt(self, file_path):
        system_prompt = None
        with open(file_path, "r", encoding="utf-8") as file:
            system_prompt = file.read()
        return system_prompt