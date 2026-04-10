import google.generativeai as genai


class GeminiService:
    def __init__(self, model: str, api_key: str):
        genai.configure(api_key=api_key)
        self.model_name = model
        # Inicjalizujemy model bez narzędzi na starcie
        self.model = genai.GenerativeModel(model_name=self.model_name)

    def add_user_message(self, messages: list, message):
        messages.append({"role": "user", "parts": [message]})

    def add_assistant_message(self, messages: list, message):
        messages.append({"role": "model", "parts": [message]})

    def text_from_message(self, response):
        return response.text

    def chat(self, messages, system=None, tools=None, **kwargs):
        # Konwersja system promptu
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system
        )

        # Przekształcenie narzędzi MCP na format Gemini (jeśli używasz)
        # UWAGA: Gemini wymaga innej definicji tools niż Anthropic
        # Na początek przetestuj bez tools, żeby sprawdzić czy śmiga

        chat = model.start_chat(history=messages[:-1])
        response = chat.send_message(messages[-1]["parts"][0])

        return response