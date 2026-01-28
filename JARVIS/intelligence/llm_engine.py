import asyncio
from typing import Optional, List, Dict
from loguru import logger

# Import AirLLM only when needed to avoid import errors if not installed yet or on import
try:
    from airllm import AutoModel
    AIRLLM_AVAILABLE = True
except ImportError:
    AIRLLM_AVAILABLE = False
    logger.warning("AirLLM not installed. Running in mock mode.")

class LLMEngine:
    _instance = None

    def __init__(self, model_path: str = "garage-bAInd/Platypus2-70B-instruct"):
        self.model = None
        self.tokenizer = None
        self.model_path = model_path
        self.is_ready = False

    async def initialize(self):
        if not AIRLLM_AVAILABLE:
            logger.warning("AirLLM not available. Skipping initialization.")
            return

        logger.info(f"Initializing AirLLM with model: {self.model_path}")
        # In a real scenario, this is a blocking heavy operation.
        # We run it in a thread to not block the event loop.
        await asyncio.to_thread(self._load_model)
        self.is_ready = True
        logger.info("AirLLM initialized successfully.")

    def _load_model(self):
        # Configuration for "potato PCs" (single 4GB/8GB GPU)
        # We use '4bit' compression by default
        try:
            self.model = AutoModel.from_pretrained(
                self.model_path,
                compression='4bit'
            )
            self.tokenizer = self.model.tokenizer
        except Exception as e:
            logger.error(f"Failed to load AirLLM model: {e}")
            raise

    async def generate(self, prompt: str, max_tokens: int = 128) -> str:
        if not self.is_ready:
            if not AIRLLM_AVAILABLE:
                return f"[MOCK LLM] Response to: {prompt[:50]}..."
            else:
                await self.initialize()

        logger.debug(f"LLM Generating for prompt: {prompt[:50]}...")

        try:
            response = await asyncio.to_thread(self._generate_sync, prompt, max_tokens)
            return response
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return "Error in generation."

    def _generate_sync(self, prompt: str, max_tokens: int) -> str:
        input_tokens = self.tokenizer([prompt],
            return_tensors="pt",
            return_attention_mask=False,
            truncation=True,
            max_length=4096,
            padding=False)

        generation_output = self.model.generate(
            input_tokens['input_ids'].cuda(),
            max_new_tokens=max_tokens,
            use_cache=True,
            return_dict_in_generate=True)

        output = self.tokenizer.decode(generation_output.sequences[0])
        return output

# Singleton
llm_engine = LLMEngine()
