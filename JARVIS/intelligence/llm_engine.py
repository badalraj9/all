from llama_cpp import Llama
import os
from loguru import logger

class LLMEngine:
    def __init__(self, model_path: str = None):
        self.model = None
        # Default to a mock if no model path provided (to allow dev environment to run)
        # In prod, this would download a GGUF
        if model_path and os.path.exists(model_path):
            try:
                self.model = Llama(
                    model_path=model_path,
                    n_ctx=2048,
                    n_threads=4,
                    verbose=False
                )
                logger.info(f"LLM Engine loaded from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load LLM: {e}")
        else:
            logger.warning("No LLM model found. Running in Mock/Heuristic Mode.")

    def completion(self, prompt: str, stop=["\n"]) -> str:
        if not self.model:
            return ""

        output = self.model(
            prompt,
            max_tokens=128,
            stop=stop,
            echo=False
        )
        return output['choices'][0]['text'].strip()

    def analyze_intent(self, text: str) -> str:
        """
        Uses LLM to extract structured intent.
        Prompt engineering ensures output matches ULE expectations.
        """
        if not self.model:
            return "" # Fallback to Vector Math

        prompt = f"""Task: Extract intent and entities.
Input: "{text}"
Format: Intent: [ACTION] | Entity: [OBJECT] | Ambiguity: [LOW/HIGH]
Output:"""

        return self.completion(prompt)

# Singleton
# We don't have a model file in the env, so this will init in Mock mode
# But the architecture is ready for a .gguf file.
llm_engine = LLMEngine()
