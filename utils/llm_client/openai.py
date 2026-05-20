import logging
import threading
import os
import yaml
from typing import Optional
from .base import BaseClient

try:
    from openai import OpenAI
except ImportError:
    OpenAI = 'openai'


logger = logging.getLogger(__name__)

class OpenAIClient(BaseClient):

    ClientClass = OpenAI

    def __init__(
        self,
        model: str,
        temperature: float = 1.0,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        super().__init__(model, temperature)
        
        if isinstance(self.ClientClass, str):
            logger.fatal(f"Package `{self.ClientClass}` is required")
            exit(-1)
        
        self.base_url = base_url
        self._api_key_lock = threading.Lock()
        self.client = self.ClientClass(api_key=api_key, base_url=base_url)

    def _switch_api_key(self):
        with self._api_key_lock:
            self.current_api_key_index += 1
            new_index = self.current_api_key_index % 5
            logging.info(f"Switching to API key index: {new_index}")
            new_key = yaml.safe_load(open(self.api_key_path, "r"))[f"api_{new_index}"]
            os.environ["GROQ_API_KEY"] = new_key
            self.client = self.ClientClass(api_key=new_key, base_url=self.base_url)

    def _chat_completion_api(self, messages: list[dict], temperature: float, n: int = 1):
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=temperature, n=n, stream=False,
        )
        return response.choices