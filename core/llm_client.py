# jarvis_ai/core/llm_client.py
"""
LLM Client with multi-provider support.

Supports multiple LLM providers: Groq, OpenAI, and Mistral.
Includes error handling, retry logic, and comprehensive logging.
"""

import os
import logging
import time
from config import LLM_PROVIDER

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    """
    Multi-provider LLM client with automatic fallback and error handling.
    
    Attributes:
        provider (str): The active LLM provider ('groq', 'openai', or 'mistral')
        client: The initialized provider client
        max_retries (int): Maximum number of retry attempts for failed requests
    """
    
    def __init__(self, max_retries=3):
        """
        Initialize LLM client with specified provider.
        """
        self.default_provider = LLM_PROVIDER
        self.max_retries = max_retries
        self.clients = {} # Cache for initialized clients
        logger.info(f"Initializing LLM Client. Default provider: {self.default_provider}")
        
        # Pre-initialize the default provider
        self._get_client(self.default_provider)

    def _get_client(self, provider):
        """Get or initialize a client for the specified provider."""
        if provider in self.clients:
            return self.clients[provider]

        try:
            client = None
            if provider == "groq":
                from groq import Groq
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key: raise ValueError("GROQ_API_KEY not found")
                client = Groq(api_key=api_key)
                logger.info("✅ Groq client initialized")

            elif provider == "openai":
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key: raise ValueError("OPENAI_API_KEY not found")
                client = OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized")

            elif provider == "mistral":
                from mistralai import Mistral
                api_key = os.getenv("MISTRAL_API_KEY")
                if not api_key: raise ValueError("MISTRAL_API_KEY not found")
                client = Mistral(api_key=api_key)
                logger.info("✅ Mistral client initialized")

            elif provider == "google":
                import google.generativeai as genai
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key: raise ValueError("GOOGLE_API_KEY not found")
                genai.configure(api_key=api_key)
                client = genai
                logger.info("✅ Google Gemini client initialized")

            elif provider == "openrouter":
                from openai import OpenAI
                api_key = os.getenv("OPENROUTER_API_KEY")
                if not api_key: raise ValueError("OPENROUTER_API_KEY not found")
                client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                logger.info("✅ OpenRouter client initialized")

            elif provider == "nvidia":
                from openai import OpenAI
                api_key = os.getenv("NVIDIA_API_KEY")
                if not api_key: raise ValueError("NVIDIA_API_KEY not found")
                client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)
                logger.info("✅ NVIDIA client initialized")

            else:
                raise ValueError(f"Invalid LLM_PROVIDER: {provider}")

            self.clients[provider] = client
            return client

        except Exception as e:
            logger.error(f"❌ Failed to initialize {provider} client: {e}")
            raise

    def generate(self, prompt, temperature=0.5, provider=None, model=None):
        """
        Generate text completion from the configured LLM provider.
        """
        active_provider = provider or self.default_provider
        
        # Determine model based on provider if not specified
        if not model:
            if active_provider == "groq": model = "llama-3.1-8b-instant"
            elif active_provider == "openai": model = "gpt-4o-mini"
            elif active_provider == "mistral": model = "mistral-large-latest"
            elif active_provider == "google": 
                from config import MODEL_GOOGLE
                model = MODEL_GOOGLE
            elif active_provider == "openrouter":
                from config import MODEL_OPENROUTER
                model = MODEL_OPENROUTER
            elif active_provider == "nvidia":
                from config import MODEL_NVIDIA
                model = MODEL_NVIDIA

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"LLM request attempt {attempt + 1}/{self.max_retries} ({active_provider}:{model})")
                client = self._get_client(active_provider)
                
                if active_provider == "groq":
                    res = client.chat.completions.create(
                        model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature
                    )
                    return res.choices[0].message.content

                elif active_provider == "openai":
                    res = client.chat.completions.create(
                        model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature
                    )
                    return res.choices[0].message.content

                elif active_provider == "mistral":
                    res = client.chat.complete(
                        model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature
                    )
                    return res.choices[0].message.content

                elif active_provider == "google":
                    generation_config = {"temperature": temperature}
                    model_instance = client.GenerativeModel(model)
                    res = model_instance.generate_content(prompt, generation_config=generation_config)
                    return res.text

                elif active_provider == "openrouter":
                    res = client.chat.completions.create(
                        model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature
                    )
                    return res.choices[0].message.content
                    
                elif active_provider == "nvidia":
                    res = client.chat.completions.create(
                        model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature,
                        max_tokens=1024, extra_body={"chat_template_kwargs": {"thinking": True}}
                    )
                    return res.choices[0].message.content
                    
            except Exception as e:
                logger.warning(f"⚠️ LLM request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return f"Error: {str(e)}"
        
        return "I apologize, but I couldn't process your request."

    def generate_stream(self, prompt, temperature=0.5, provider=None, model=None):
        """
        Stream text completion token by token.
        """
        active_provider = provider or self.default_provider
         # Determine model based on provider if not specified
        if not model:
            if active_provider == "groq": model = "llama-3.1-8b-instant"
            elif active_provider == "openai": model = "gpt-4o-mini"
            elif active_provider == "mistral": model = "mistral-large-latest"
            elif active_provider == "google": 
                from config import MODEL_GOOGLE
                model = MODEL_GOOGLE
            elif active_provider == "openrouter":
                from config import MODEL_OPENROUTER
                model = MODEL_OPENROUTER
            elif active_provider == "nvidia":
                from config import MODEL_NVIDIA
                model = MODEL_NVIDIA

        try:
            client = self._get_client(active_provider)
            
            if active_provider == "groq":
                stream = client.chat.completions.create(
                    model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature, stream=True
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content: yield delta.content

            elif active_provider == "openai":
                stream = client.chat.completions.create(
                    model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature, stream=True
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content: yield delta.content
            
            elif active_provider == "openrouter":
                stream = client.chat.completions.create(
                    model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature, stream=True
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content: yield delta.content

            elif active_provider == "nvidia":
                stream = client.chat.completions.create(
                    model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature, 
                    max_tokens=1024, stream=True, extra_body={"chat_template_kwargs": {"thinking": True}}
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content: yield delta.content

            elif active_provider == "google":
                generation_config = {"temperature": temperature}
                model_instance = client.GenerativeModel(model)
                stream = model_instance.generate_content(prompt, generation_config=generation_config, stream=True)
                for chunk in stream:
                    if chunk.text: yield chunk.text

            else:
                yield self.generate(prompt, temperature, provider=active_provider, model=model)

        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            yield f"Error: {str(e)}"

