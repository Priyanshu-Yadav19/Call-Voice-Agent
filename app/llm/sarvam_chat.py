from __future__ import annotations
import asyncio
from sarvamai import SarvamAI

class ConversationManager:
    def __init__(self, api_key: str, system_prompt: str, temperature: float = 0.4, max_tokens: int = 450):
        self.client = SarvamAI(api_subscription_key=api_key)
        self.temperature = float(temperature)
        self.max_tokens = int(max_tokens)
        self.messages = [{"role": "system", "content": system_prompt}]

    def _complete_sync(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})
        resp = self.client.chat.completions(
            messages=self.messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        assistant = resp.choices[0].message.content.strip()
        self.messages.append({"role": "assistant", "content": assistant})
        return assistant

    async def complete(self, user_message: str) -> str:
        return await asyncio.to_thread(self._complete_sync, user_message)