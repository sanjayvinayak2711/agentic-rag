"""
LLM client for generating responses
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
import openai
import aiohttp
from backend.utils.logger import setup_logger
from backend.config import settings

logger = setup_logger(__name__)


class LLMClient:
    """Client for interacting with multiple LLM providers"""
    
    def __init__(self):
        self.config = settings.get_ai_config()
        self.provider = self.config["provider"]
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate client based on provider"""
        try:
            if self.provider == "openai":
                if not self.config.get("api_key"):
                    logger.warning("OpenAI API key not found, using mock responses")
                    self.client = None
                else:
                    client_kwargs = {"api_key": self.config["api_key"]}
                    if self.config.get("base_url"):
                        client_kwargs["base_url"] = self.config["base_url"]
                    self.client = openai.OpenAI(**client_kwargs)
                    logger.info(f"OpenAI client initialized with {self.config.get('available_keys', 1)} API key(s)")
                    
            elif self.provider == "gemini":
                if not self.config.get("api_key"):
                    logger.warning("Gemini API key not found, using mock responses")
                    self.client = None
                else:
                    self.client = self.config["api_key"]  # Store API key for Gemini
                    logger.info(f"Gemini client initialized with {self.config.get('available_keys', 1)} API key(s)")
                    
            elif self.provider == "anthropic":
                if not self.config.get("api_key"):
                    logger.warning("Anthropic API key not found, using mock responses")
                    self.client = None
                else:
                    self.client = self.config["api_key"]  # Store API key for Anthropic
                    logger.info(f"Anthropic client initialized with {self.config.get('available_keys', 1)} API key(s)")
                    
            elif self.provider == "local":
                self.client = self.config["url"]  # Store URL for local models
                logger.info("Local LLM client initialized successfully")
                
            else:
                logger.warning(f"Unknown provider: {self.provider}, using mock responses")
                self.client = None
                
        except Exception as e:
            logger.error(f"Error initializing {self.provider} client: {str(e)}")
            self.client = None
    
    async def generate_response(self, prompt: str, temperature: Optional[float] = None,
                              max_tokens: int = 1000, model: Optional[str] = None) -> str:
        """Generate a response from the LLM"""
        try:
            if not self.client or not settings.is_ai_configured():
                return await self._generate_mock_response(prompt)
            
            # Use provided parameters or defaults
            temp = temperature if temperature is not None else self.config.get("temperature", 0.1)
            model_name = model if model else self.config.get("model", "gpt-3.5-turbo")
            
            logger.info(f"Generating response using {self.provider} model: {model_name}")
            
            if self.provider == "openai":
                return await self._generate_openai_response(prompt, temp, max_tokens, model_name)
            elif self.provider == "gemini":
                return await self._generate_gemini_response(prompt, temp, max_tokens, model_name)
            elif self.provider == "anthropic":
                return await self._generate_anthropic_response(prompt, temp, max_tokens, model_name)
            elif self.provider == "local":
                return await self._generate_local_response(prompt, temp, max_tokens, model_name)
            else:
                return await self._generate_mock_response(prompt)
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return await self._generate_mock_response(prompt)
    
    async def _generate_openai_response(self, prompt: str, temperature: float, max_tokens: int, model: str) -> str:
        """Generate response using OpenAI"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
        )
        return response.choices[0].message.content
    
    async def _generate_gemini_response(self, prompt: str, temperature: float, max_tokens: int, model: str) -> str:
        """Generate response using Gemini"""
        api_key = self.client
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await response.json()
                if "candidates" in result and result["candidates"]:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    raise Exception("No response from Gemini")
    
    async def _generate_anthropic_response(self, prompt: str, temperature: float, max_tokens: int, model: str) -> str:
        """Generate response using Anthropic"""
        api_key = self.client
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await response.json()
                if "content" in result:
                    return result["content"][0]["text"]
                else:
                    raise Exception("No response from Anthropic")
    
    async def _generate_local_response(self, prompt: str, temperature: float, max_tokens: int, model: str) -> str:
        """Generate response using local LLM (Ollama)"""
        url = f"{self.client}/api/generate"
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()
                if "response" in result:
                    return result["response"]
                else:
                    raise Exception("No response from local LLM")
    
    async def _generate_mock_response(self, prompt: str) -> str:
        """Generate a mock response when no AI is available"""
        logger.info("Generating mock response")
        
        # Simple mock response based on prompt content
        if "what" in prompt.lower():
            return "Based on the provided context, I can explain that this refers to a concept or topic that is discussed in the source materials. The documents provide relevant information that helps answer your question."
        elif "how" in prompt.lower():
            return "According to the source documents, this process involves several steps that are outlined in the provided materials. The key aspects include the main components and their interactions."
        elif "why" in prompt.lower():
            return "The source documents explain that this occurs due to specific factors and circumstances mentioned in the materials. The reasoning behind this is supported by the evidence provided."
        else:
            return "Based on the provided context and source documents, I can provide information related to your query. The materials contain relevant details that address the topic you're asking about."
    
    async def generate_with_context(self, query: str, context: List[str], 
                                  temperature: Optional[float] = None) -> str:
        """Generate response with specific context"""
        try:
            context_text = "\n\n".join(context)
            
            prompt = f"""Context:
{context_text}

Question: {query}

Please answer the question based on the provided context. If the context doesn't contain enough information, please indicate that clearly."""
            
            return await self.generate_response(prompt, temperature)
            
        except Exception as e:
            logger.error(f"Error generating response with context: {str(e)}")
            raise
    
    async def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize a piece of text"""
        try:
            prompt = f"""Please summarize the following text in about {max_length} words:

{text}

Summary:"""
            
            return await self.generate_response(prompt, max_tokens=300)
            
        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            raise
    
    async def extract_key_points(self, text: str) -> list:
        """Extract key points from text"""
        try:
            prompt = f"""Please extract the main key points from the following text. Return them as a numbered list:

{text}

Key Points:"""
            
            response = await self.generate_response(prompt, max_tokens=500)
            
            # Parse the numbered list
            lines = response.split('\n')
            key_points = []
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering/bullets
                    cleaned = line.lstrip('0123456789.- ')
                    if cleaned:
                        key_points.append(cleaned)
            
            return key_points
            
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return [text[:100] + "..."]  # Fallback to truncated text
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "provider": self.provider,
            "model": self.config.get("model"),
            "temperature": self.config.get("temperature"),
            "api_available": self.client is not None and settings.is_ai_configured(),
            "configured": settings.is_ai_configured(),
            "available_keys": self.config.get("available_keys", 1),
            "base_url": self.config.get("base_url") if self.provider == "openai" else None
        }
