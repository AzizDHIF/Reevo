import logging
from typing import Optional
from .openai import OpenAIClient
import os

logger = logging.getLogger(__name__)

class DeepSeekSparkClient(OpenAIClient):
    """
    Client pour un modèle DeepSeek-R1 servi localement via llama-server (llama.cpp)
    sur la machine spark, accessible via un tunnel SSH sur localhost:8080.
    """

    def __init__(
        self,
        model: str,
        temperature: float = 1.0,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        # llama-server n'exige pas de vraie clé API, mais le client OpenAI en réclame une non-vide
        api_key = api_key or os.getenv("DEEPSEEK_SPARK_API_KEY", "sk-no-key-required")
        base_url = base_url or "http://localhost:8080/v1"

        super().__init__(model, temperature, base_url, api_key)

    def _chat_completion_api(self, messages: list[dict], temperature: float, n: int = 1):
        assert n == 1
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=temperature, stream=False,
            max_tokens=4096, timeout=300,  # DeepSeek-R1 "réfléchit" avant de répondre → besoin de marge
        )
        return response.choices