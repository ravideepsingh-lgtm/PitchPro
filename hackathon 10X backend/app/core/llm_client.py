import logging
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.json_utils import extract_json_from_text

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            max_retries=3
        )

    async def call(self, prompt: str, system_prompt: str = "You are a helpful AI.", temperature: float = 0.2) -> dict:
        """
        Calls the LLM asynchronously, enforcing JSON output.
        """
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return extract_json_from_text(content)
            
        except Exception as e:
            logger.error(f"LLM API Error: {str(e)}")
            raise e

llm_client = LLMClient()
