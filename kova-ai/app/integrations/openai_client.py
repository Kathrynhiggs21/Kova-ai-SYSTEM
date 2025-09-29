import httpx
import json
import time
from typing import Optional, Dict, Any

from app.core.config import settings
from app.utils.logger import setup_logger, log_ai_integration, log_error

logger = setup_logger(__name__)


class OpenAIClient:
    """Client for OpenAI API integration."""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def is_configured(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.api_key and self.api_key.startswith("sk-"))
    
    async def chat_completion(
        self, 
        messages: list,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to OpenAI API.
        
        Args:
            messages: List of message objects for the conversation
            model: OpenAI model to use
            max_tokens: Maximum tokens in response
            temperature: Response creativity level
            
        Returns:
            Dict containing the API response or error information
        """
        if not self.is_configured():
            error_msg = "OpenAI API key not configured"
            log_ai_integration("openai", "chat_completion", False, {"error": error_msg})
            return {"error": error_msg, "success": False}
        
        start_time = time.time()
        
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                processing_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract response details
                    choice = result.get("choices", [{}])[0]
                    content = choice.get("message", {}).get("content", "")
                    tokens_used = result.get("usage", {}).get("total_tokens", 0)
                    
                    log_ai_integration("openai", "chat_completion", True, {
                        "model": model,
                        "tokens_used": tokens_used,
                        "processing_time": processing_time
                    })
                    
                    return {
                        "success": True,
                        "response": content,
                        "model_used": model,
                        "tokens_used": tokens_used,
                        "processing_time": processing_time,
                        "raw_response": result
                    }
                else:
                    error_detail = f"HTTP {response.status_code}: {response.text}"
                    log_ai_integration("openai", "chat_completion", False, {
                        "status_code": response.status_code,
                        "error": error_detail
                    })
                    
                    return {
                        "success": False,
                        "error": error_detail,
                        "status_code": response.status_code,
                        "processing_time": processing_time
                    }
                    
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            log_error(e, "openai_chat_completion")
            log_ai_integration("openai", "chat_completion", False, {
                "error": error_msg,
                "processing_time": processing_time
            })
            
            return {
                "success": False,
                "error": error_msg,
                "processing_time": processing_time
            }
    
    async def process_command(self, command: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a text command using OpenAI.
        
        Args:
            command: The command to process
            context: Optional additional context
            
        Returns:
            Dict containing the processed response or error information
        """
        messages = [
            {
                "role": "system", 
                "content": "You are Kova AI, a helpful assistant for development automation and system management."
            }
        ]
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Additional context: {context}"
            })
            
        messages.append({
            "role": "user",
            "content": command
        })
        
        return await self.chat_completion(messages)


# Global client instance
openai_client = OpenAIClient()