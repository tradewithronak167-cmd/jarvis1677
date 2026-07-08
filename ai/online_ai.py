"""Google Gemini online AI provider for HI ROLEX."""

from __future__ import annotations

import os
import warnings

from ai.conversation_manager import ConversationManager
from ai.prompt_builder import PromptBuilder
from utils.logger import get_logger


class OnlineAI:
    """Online Gemini provider used by HI ROLEX."""

    MISSING_KEY_MESSAGE: str = (
        "Online AI is not configured. Please add GEMINI_API_KEY to your .env file."
    )
    PREFERRED_MODELS: tuple[str, ...] = (
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-flash-latest",
    )

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        conversation_manager: ConversationManager,
    ) -> None:
        self._load_environment()
        self.prompt_builder = prompt_builder
        self.conversation_manager = conversation_manager
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = self.PREFERRED_MODELS[0]
        self.logger = get_logger()

    def is_configured(self) -> bool:
        """Return True when GEMINI_API_KEY is available."""
        return bool(self.api_key)

    def generate_response(self, user_message: str) -> str:
        """Generate an online AI response with Gemini."""
        if not self.is_configured():
            return self.MISSING_KEY_MESSAGE

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            prompt = self.prompt_builder.build_prompt(
                user_message,
                self.conversation_manager.get_history(),
            )
            return self._generate_with_available_model(genai, prompt)
        except Exception as error:
            self.logger.error("Online AI provider issue: %s", error)
            return f"Online AI error: {error}"

    def _generate_with_available_model(self, genai: object, prompt: str) -> str:
        """Generate text using the first supported Gemini model available."""
        candidate_models = [self.model_name, *self.PREFERRED_MODELS]

        last_error = ""
        for model_name in dict.fromkeys(candidate_models):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "max_output_tokens": 500,
                        "temperature": 0.5,
                    },
                )
                response_text = getattr(response, "text", "").strip()
                if response_text:
                    self.model_name = model_name
                    return response_text
            except Exception as error:
                last_error = str(error)
                continue

        if last_error:
            return f"Online AI error: {last_error}"
        return "I could not find an available Gemini chat model right now."

    def _list_supported_models(self, genai: object) -> list[str]:
        """Return Gemini models that support generateContent."""
        try:
            supported_models = []
            for model in genai.list_models():
                methods = getattr(model, "supported_generation_methods", []) or []
                if "generateContent" in methods:
                    supported_models.append(str(model.name))
            return supported_models
        except Exception:
            return []

    def _load_environment(self) -> None:
        """Load .env values if python-dotenv is installed."""
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except Exception:
            return
