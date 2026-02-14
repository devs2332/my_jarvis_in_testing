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
        
        Args:
            max_retries (int): Maximum retry attempts for failed requests
            
        Raises:
            ValueError: If LLM_PROVIDER is not supported
            Exception: If provider initialization fails
        """
        self.provider = LLM_PROVIDER
        self.max_retries = max_retries
        logger.info(f"Initializing LLM Client with provider: {self.provider}")

        try:
            if self.provider == "groq":
                from groq import Groq
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    raise ValueError("GROQ_API_KEY not found in environment")
                self.client = Groq(api_key=api_key)
                logger.info("✅ Groq client initialized")

            elif self.provider == "openai":
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment")
                self.client = OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized")

            elif self.provider == "mistral":
                from mistralai.client import MistralClient
                api_key = os.getenv("MISTRAL_API_KEY")
                if not api_key:
                    raise ValueError("MISTRAL_API_KEY not found in environment")
                self.client = MistralClient(api_key=api_key)
                logger.info("✅ Mistral client initialized")

            else:
                raise ValueError(f"Invalid LLM_PROVIDER: {self.provider}. Must be 'groq', 'openai', or 'mistral'")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM client: {e}")
            raise

    def generate(self, prompt, temperature=0.5):
        """
        Generate text completion from the configured LLM provider.
        
        Args:
            prompt (str): The input prompt for the LLM
            temperature (float): Sampling temperature (0.0 to 1.0)
            
        Returns:
            str: Generated text response from the LLM
            
        Raises:
            Exception: If all retry attempts fail
        """
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"LLM request attempt {attempt + 1}/{self.max_retries}")
                
                if self.provider == "groq":
                    res = self.client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature
                    )
                    response = res.choices[0].message.content
                    logger.info(f"✅ Groq response received ({len(response)} chars)")
                    return response

                elif self.provider == "openai":
                    res = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature
                    )
                    response = res.choices[0].message.content
                    logger.info(f"✅ OpenAI response received ({len(response)} chars)")
                    return response

                elif self.provider == "mistral":
                    res = self.client.chat(
                        model="mistral-large-latest",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature
                    )
                    response = res.choices[0].message.content
                    logger.info(f"✅ Mistral response received ({len(response)} chars)")
                    return response
                    
            except Exception as e:
                logger.warning(f"⚠️ LLM request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ All LLM retry attempts failed: {e}")
                    return f"I apologize, but I'm having trouble connecting to my AI systems right now. Error: {str(e)}"
        
        return "I apologize, but I couldn't process your request at this time."

    def generate_stream(self, prompt, temperature=0.5):
        """
        Stream text completion token by token.

        Args:
            prompt (str): Input prompt
            temperature (float): Sampling temperature

        Yields:
            str: Individual text tokens
        """
        try:
            if self.provider == "groq":
                stream = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    stream=True,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content

            elif self.provider == "openai":
                stream = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    stream=True,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content

            else:
                # Fallback: non-streaming
                result = self.generate(prompt, temperature)
                yield result

        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            yield f"Error: {str(e)}"

