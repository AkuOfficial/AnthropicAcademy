from google.genai import Client
from google.genai import types


class GeminiService:
    def __init__(self, model: str, api_key: str):
        self.client = Client(api_key=api_key)
        self.model_name = model

    def chat(self, messages, system=None, tools=None):
        config = types.GenerateContentConfig(
            system_instruction=system,
            tools=tools,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode=types.FunctionCallingConfigMode.AUTO)
            ) if tools else None
        )

        return self.client.models.generate_content(
            model=self.model_name,
            contents=messages,
            config=config
        )

    def add_user_message(self, messages: list, content_input):
        if isinstance(content_input, str):
            parts = [types.Part(text=content_input)]
        elif isinstance(content_input, list):
            parts = content_input
        else:
            parts = [types.Part(text=str(content_input))]

        messages.append(types.Content(role="user", parts=parts))

    def add_assistant_message(self, messages: list, response):
        if response.candidates and response.candidates[0].content:
            messages.append(response.candidates[0].content)

    def text_from_message(self, response):
        try:
            return response.text
        except:
            return ""
