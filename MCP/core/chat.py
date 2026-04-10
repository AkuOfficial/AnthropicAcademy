# from MCP.core.claude import Claude
from MCP.core.gemini import GeminiService
from MCP.mcp_client import MCPClient
from MCP.core.tools import ToolManager
# from anthropic.types import MessageParam
from typing import Any


class Chat:
    def __init__(self,
                 # claude_service: Claude,
                 gemini_service: GeminiService,
                 clients: dict[str, MCPClient]):
        # self.claude_service: Claude = claude_service
        self.gemini_service: GeminiService = gemini_service
        self.clients: dict[str, MCPClient] = clients
        # self.messages: list[MessageParam] = []
        self.messages: list[Any] = []

    # async def _process_query(self, query: str):
    #     self.messages.append({"role": "user", "content": query})

    async def _process_query(self, query: str):
        self.gemini_service.add_user_message(self.messages, query)

    # async def run(
    #         self,
    #         query: str,
    # ) -> str:
    #     final_text_response = ""
    #
    #     await self._process_query(query)
    #
    #     while True:
    #         # response = self.claude_service.chat(
    #         response = self.gemini_service.chat(
    #             messages=self.messages,
    #             tools=await ToolManager.get_all_tools(self.clients),
    #         )
    #
    #         # self.claude_service.add_assistant_message(self.messages, response)
    #         self.gemini_service.add_assistant_message(self.messages, response)
    #
    #         if response.stop_reason == "tool_use":
    #             # print(self.claude_service.text_from_message(response))
    #             print(self.gemini_service.text_from_message(response))
    #             tool_result_parts = await ToolManager.execute_tool_requests(
    #                 self.clients, response
    #             )
    #
    #             # self.claude_service.add_user_message(
    #             self.gemini_service.add_user_message(
    #                 self.messages, tool_result_parts
    #             )
    #         else:
    #             # final_text_response = self.claude_service.text_from_message(
    #             final_text_response = self.gemini_service.text_from_message(
    #                 response
    #             )
    #             break
    #
    #     return final_text_response

    async def run(self, query: str) -> str:
        await self._process_query(query)

        while True:
            tools = await ToolManager.get_all_tools(self.clients)

            response = self.gemini_service.chat(
                messages=self.messages,
                tools=tools,
            )

            has_tool_calls = False
            if response.candidates and response.candidates[0].content.parts:
                has_tool_calls = any(p.function_call for p in response.candidates[0].content.parts)

            self.gemini_service.add_assistant_message(self.messages, response)

            if has_tool_calls:
                tool_result_parts = await ToolManager.execute_tool_requests(
                    self.clients, response
                )
                self.gemini_service.add_user_message(self.messages, tool_result_parts)
            else:
                return self.gemini_service.text_from_message(response)
