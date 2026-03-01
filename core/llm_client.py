# jarvis_ai/core/llm_client.py
"""
LLM Client with multi-provider support.

Supports multiple LLM providers: Groq, OpenAI, and Mistral.
Includes error handling, retry logic, and comprehensive logging.
"""

import os
import logging
import time

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
        self.default_provider = "nvidia" # Default until set by frontend
        self.default_model = None
        self.max_retries = max_retries
        self.clients = {} # Cache for initialized clients
        logger.info(f"Initializing LLM Client. Default provider: {self.default_provider}")
        
        # Pre-initialize the default provider
        self._get_client(self.default_provider)

    def set_default_provider(self, provider: str, model: str = None):
        """Update the active provider and model at runtime."""
        self.default_provider = provider
        self.default_model = model
        logger.info(f"🔄 Switched LLM default provider to: {provider} ({model})")
        # Ensure client is initialized
        self._get_client(provider)

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
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                    default_headers={
                        "HTTP-Referer": "http://localhost:8080",
                        "X-Title": "Jarvis AI",
                    },
                )
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
            if active_provider == self.default_provider and self.default_model:
                model = self.default_model
            elif active_provider == "groq": model = "llama-3.1-8b-instant"
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
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        extra_headers={
                            "HTTP-Referer": "https://jarvis-ai.local",
                            "X-Title": "Jarvis AI",
                        },
                    )
                    return res.choices[0].message.content
                    
                elif active_provider == "nvidia":
                    res = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        top_p=1,
                        max_tokens=4096,
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
            if active_provider == self.default_provider and self.default_model:
                model = self.default_model
            elif active_provider == "groq": model = "llama-3.1-8b-instant"
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
                    model=model, messages=[{"role": "user", "content": prompt}],
                    temperature=temperature, stream=True,
                    extra_headers={
                        "HTTP-Referer": "https://jarvis-ai.local",
                        "X-Title": "Jarvis AI",
                    },
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content: yield delta.content

            elif active_provider == "nvidia":
                stream = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    top_p=1,
                    max_tokens=4096,
                    stream=True,
                )
                for chunk in stream:
                    if not getattr(chunk, "choices", None):
                        continue
                    delta = chunk.choices[0].delta
                    # Skip reasoning_content (internal chain-of-thought — not for display)
                    if delta.content:
                        yield delta.content

            elif active_provider == "google":
                generation_config = {"temperature": temperature}
                model_instance = client.GenerativeModel(model)
                stream = model_instance.generate_content(prompt, generation_config=generation_config, stream=True)
                for chunk in stream:
                    if chunk.text: yield chunk.text

            elif active_provider == "mistral":
                stream = client.chat.stream(
                    model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature
                )
                for event in stream:
                    delta = event.data.choices[0].delta
                    if delta.content: yield delta.content

            else:
                yield self.generate(prompt, temperature, provider=active_provider, model=model)

        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            yield f"Error: {str(e)}"

    def generate_with_tools(self, prompt, tools, temperature=0.5, provider=None, model=None):
        """
        Generate a response with tool-calling support.
        
        For OpenAI/Groq/Mistral: uses native function-calling via `tools=` parameter.
        For Google: uses genai tool declarations.
        For others: falls back to prompt-based JSON extraction.
        
        Args:
            prompt (str): User prompt
            tools (list): Tool schemas in OpenAI function-calling format
            temperature (float): Sampling temperature
            provider (str): Override provider
            model (str): Override model
            
        Returns:
            dict: {"type": "text"|"tool_call", "content": str, 
                   "tool_name": str|None, "tool_args": dict|None}
        """
        active_provider = provider or self.default_provider

        if not model:
            if active_provider == self.default_provider and self.default_model:
                model = self.default_model
            elif active_provider == "groq": model = "llama-3.1-8b-instant"
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

            # Providers with native tool-calling support
            if active_provider in ("openai", "groq", "openrouter"):
                res = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    tools=tools,
                    tool_choice="auto",
                    temperature=temperature,
                )
                msg = res.choices[0].message
                
                if msg.tool_calls:
                    tc = msg.tool_calls[0]
                    import json
                    return {
                        "type": "tool_call",
                        "content": msg.content or "",
                        "tool_name": tc.function.name,
                        "tool_args": json.loads(tc.function.arguments),
                    }
                return {"type": "text", "content": msg.content, "tool_name": None, "tool_args": None}

            elif active_provider == "mistral":
                res = client.chat.complete(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    tools=tools,
                    tool_choice="auto",
                    temperature=temperature,
                )
                msg = res.choices[0].message

                if msg.tool_calls:
                    tc = msg.tool_calls[0]
                    import json
                    return {
                        "type": "tool_call",
                        "content": msg.content or "",
                        "tool_name": tc.function.name,
                        "tool_args": json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments,
                    }
                return {"type": "text", "content": msg.content, "tool_name": None, "tool_args": None}

            elif active_provider == "google":
                # Google uses a different format for tools
                import google.generativeai as genai
                
                # Convert OpenAI tool format to Google format
                google_tools = []
                for t in tools:
                    func = t["function"]
                    google_tools.append(genai.types.Tool(
                        function_declarations=[{
                            "name": func["name"],
                            "description": func["description"],
                            "parameters": func.get("parameters", {}),
                        }]
                    ))

                model_instance = client.GenerativeModel(model, tools=google_tools)
                res = model_instance.generate_content(prompt)

                # Check for function call in response
                if res.candidates and res.candidates[0].content.parts:
                    for part in res.candidates[0].content.parts:
                        if hasattr(part, "function_call") and part.function_call:
                            fc = part.function_call
                            return {
                                "type": "tool_call",
                                "content": "",
                                "tool_name": fc.name,
                                "tool_args": dict(fc.args) if fc.args else {},
                            }
                return {"type": "text", "content": res.text, "tool_name": None, "tool_args": None}

            else:
                # Fallback: prompt-based JSON extraction
                tool_desc = "\n".join(
                    f"- {t['function']['name']}: {t['function']['description']}"
                    for t in tools
                )
                enhanced_prompt = f"""{prompt}

Available tools:
{tool_desc}

If you need to use a tool, respond ONLY with JSON: {{"tool": "tool_name", "args": {{...}}}}
Otherwise, respond normally."""

                response = self.generate(enhanced_prompt, temperature, provider=active_provider, model=model)
                
                # Try to parse tool call from response
                import json
                try:
                    parsed = json.loads(response.strip())
                    if "tool" in parsed:
                        return {
                            "type": "tool_call",
                            "content": "",
                            "tool_name": parsed["tool"],
                            "tool_args": parsed.get("args", {}),
                        }
                except (json.JSONDecodeError, TypeError):
                    pass
                
                return {"type": "text", "content": response, "tool_name": None, "tool_args": None}

        except Exception as e:
            logger.error(f"❌ Tool-calling error: {e}")
            return {"type": "text", "content": f"Error: {str(e)}", "tool_name": None, "tool_args": None}

