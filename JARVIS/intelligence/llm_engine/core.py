from typing import List, Optional
import os

try:
    import torch
    from transformers import AutoTokenizer
except ImportError:
    torch = None

class LLMEngine:
    """
    JARVIS Cognitive Realizer (Assimilated AirLLM).
    Handles generation of fluid text from Context Web data using Large Language Models.
    Optimized for low-VRAM execution via Layer-wise Inference.
    """

    def __init__(self, model_path: str = "meta-llama/Llama-2-7b-chat-hf", device: str = "cuda:0"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.tokenizer = None
        self.mock_mode = True

    async def initialize(self):
        # Async wrapper for loading
        self.load_model()
        return True

    async def generate(self, prompt: str, max_tokens: int = 128) -> str:
        # Generic generate method for ULE compatibility
        if self.mock_mode:
            return self._mock_generation(prompt)

        # Real generation logic would go here, similar to generate_response
        # For now, reuse _mock_generation if model not loaded
        return self._mock_generation(prompt)

    def load_model(self):
        if torch is None:
            print("[LLM] PyTorch not found. Running in MOCK MODE.")
            return

        try:
            from airllm import AutoModel

            print(f"[LLM] Loading {self.model_path} via AirLLM...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModel.from_pretrained(self.model_path, device=self.device)
            self.mock_mode = False
            print("[LLM] Model loaded successfully.")

        except Exception as e:
            print(f"[LLM] Failed to load AirLLM: {e}. Fallback to MOCK MODE.")
            self.mock_mode = True

    def generate_response(self, context_data: dict, intent: str, intent_type: str = "CHAT", max_tokens: int = 128) -> str:
        """
        Generates a response based on the Context Web data and Intent Type.
        """
        # 1. Construct Prompt from Context
        prompt = self._construct_prompt(context_data, intent, intent_type)

        # 2. Generate
        if self.mock_mode:
            return self._mock_generation(prompt)

        try:
            input_tokens = self.tokenizer([prompt], return_tensors="pt",
                                        return_attention_mask=False,
                                        truncation=True,
                                        max_length=512,
                                        padding=False)

            generation_output = self.model.generate(
                input_tokens['input_ids'].to(self.device),
                max_new_tokens=max_tokens,
                use_cache=True,
                return_dict_in_generate=True)

            output = self.tokenizer.decode(generation_output.sequences[0])
            return output
        except Exception as e:
            print(f"[LLM] Generation Error: {e}")
            return self._mock_generation(prompt)

    def _construct_prompt(self, context: dict, intent: str, intent_type: str) -> str:
        """
        Builds a structured prompt for the LLM based on Tone/Intent.
        """
        facts = "\n".join([f"- {k}: {v}" for k, v in context.items()])

        # Tone Selection
        tone_instruction = "Be helpful."
        if intent_type == "COMMAND":
            tone_instruction = "Be concise, military, and confirming. Acknowledge the action."
        elif intent_type == "QUERY":
            tone_instruction = "Be informative, precise, and academic. Provide data."
        elif intent_type == "CHAT":
            tone_instruction = "Be conversational, witty, and empathetic. Engage with the user."

        prompt = f"""[INST] You are JARVIS, an advanced AI assistant.

CONTEXT DATA:
{facts}

USER INTENT: {intent}
TYPE: {intent_type}

INSTRUCTION: {tone_instruction} Generate the response.
[/INST]"""
        return prompt

    def _mock_generation(self, prompt: str) -> str:
        """
        Simulated generation for testing.
        """
        return f"[LLM SIMULATION] {prompt[:100]}..."

# Singleton
llm_engine = LLMEngine()
