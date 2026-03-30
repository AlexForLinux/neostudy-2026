from app.config import settings

class PromptService():
    def __init__(self):
        self.recipe_prompt = self._read_system_prompt(settings.recipe_prompt)
        self.advice_prompt = self._read_system_prompt(settings.advice_prompt)
        self.other_prompt = self._read_system_prompt(settings.other_prompt)

    def _read_system_prompt(self, file_path):
        system_prompt = None
        with open(file_path, "r", encoding="utf-8") as file:
            system_prompt = file.read()
        return system_prompt
    
prompt_service = PromptService()