"""
Google Gemini API service for LLM interactions.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import time

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.api_core import exceptions as google_exceptions

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceException, RateLimitException

logger = logging.getLogger(__name__)
settings = get_settings()


class GeminiService:
    """
    Service for interacting with Google Gemini API.
    
    Provides async wrapper around Gemini API with error handling,
    retry logic, and rate limiting.
    """
    
    def __init__(self):
        """Initialize Gemini service."""
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.temperature = settings.GEMINI_TEMPERATURE
        self.max_tokens = settings.GEMINI_MAX_TOKENS
        
        # Rate limiting
        self.requests_per_minute = 60
        self.request_times: List[float] = []
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 60.0
        
        # Initialize the client
        self._initialize_client()
        
        logger.info(f"GeminiService initialized with model: {self.model_name}")
    
    def _initialize_client(self) -> None:
        """Initialize the Gemini client."""
        try:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not provided")
            
            genai.configure(api_key=self.api_key)
            
            # Configure safety settings - use more permissive settings for development
            self.safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings=self.safety_settings
            )
            
            logger.info("Gemini client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise ExternalServiceException(f"Gemini initialization failed: {str(e)}")
    
    def _check_rate_limit(self) -> None:
        """Check if we're within rate limits."""
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [
            req_time for req_time in self.request_times
            if current_time - req_time < 60
        ]
        
        # Check if we've exceeded the rate limit
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[0])
            raise RateLimitException(f"Rate limit exceeded. Wait {wait_time:.1f} seconds")
        
        # Record this request
        self.request_times.append(current_time)
    
    async def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except google_exceptions.ResourceExhausted as e:
                last_exception = e
                if attempt == self.max_retries - 1:
                    break
                
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                logger.warning(f"Rate limited, retrying in {delay}s (attempt {attempt + 1})")
                await asyncio.sleep(delay)
                
            except google_exceptions.ServiceUnavailable as e:
                last_exception = e
                if attempt == self.max_retries - 1:
                    break
                
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                logger.warning(f"Service unavailable, retrying in {delay}s (attempt {attempt + 1})")
                await asyncio.sleep(delay)
                
            except Exception as e:
                # Don't retry for other types of errors
                raise ExternalServiceException(f"Gemini API error: {str(e)}")
        
        # If we get here, all retries failed
        raise ExternalServiceException(f"Gemini API failed after {self.max_retries} retries: {str(last_exception)}")
    
    async def generate_text(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate text using Gemini API.
        
        Args:
            prompt: Input prompt for text generation
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            system_instruction: System instruction for the model
            
        Returns:
            Generated text
            
        Raises:
            ExternalServiceException: If API call fails
            RateLimitException: If rate limit is exceeded
        """
        try:
            # Check rate limits
            self._check_rate_limit()
            
            # Use provided parameters or defaults
            temp = temperature if temperature is not None else self.temperature
            max_tok = max_tokens if max_tokens is not None else self.max_tokens
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temp,
                max_output_tokens=max_tok,
                candidate_count=1
            )
            
            # Create model with system instruction if provided
            model = self.model
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    safety_settings=self.safety_settings,
                    system_instruction=system_instruction
                )
            
            # Generate content
            async def _generate():
                response = await model.generate_content_async(
                    prompt,
                    generation_config=generation_config
                )

                # Check if response was blocked
                if not response.candidates:
                    raise ExternalServiceException("No response candidates generated")

                candidate = response.candidates[0]
                if candidate.finish_reason == 2:  # SAFETY
                    raise ExternalServiceException("Content was blocked by safety filters")
                elif candidate.finish_reason == 3:  # RECITATION
                    raise ExternalServiceException("Content was blocked due to recitation")
                elif candidate.finish_reason == 4:  # OTHER
                    raise ExternalServiceException("Content generation failed for unknown reason")

                # Try to get text, handle cases where it might not be available
                try:
                    return response.text
                except Exception as e:
                    # If response.text fails, try to extract from parts
                    if candidate.content and candidate.content.parts:
                        text_parts = []
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                        if text_parts:
                            return ''.join(text_parts)

                    raise ExternalServiceException(f"Could not extract text from response: {str(e)}")
            
            result = await self._retry_with_backoff(_generate)
            
            logger.debug(f"Generated text of length: {len(result)}")
            return result
            
        except RateLimitException:
            raise  # Re-raise rate limit exceptions
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise ExternalServiceException(f"Text generation failed: {str(e)}")
    
    async def generate_structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate structured output using Gemini API.
        
        Args:
            prompt: Input prompt
            schema: JSON schema for structured output
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Structured output as dictionary
            
        Raises:
            ExternalServiceException: If API call fails
        """
        try:
            # Add schema instruction to prompt
            schema_prompt = f"""
            {prompt}
            
            Please respond with valid JSON that matches this schema:
            {schema}
            
            Respond only with the JSON, no additional text.
            """
            
            result = await self.generate_text(
                schema_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Parse JSON response
            import json
            try:
                return json.loads(result.strip())
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ExternalServiceException(f"Invalid JSON response: {str(e)}")
                
        except ExternalServiceException:
            raise  # Re-raise service exceptions
        except Exception as e:
            logger.error(f"Structured output generation failed: {e}")
            raise ExternalServiceException(f"Structured output generation failed: {str(e)}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Gemini API.
        
        Returns:
            Connection test results
        """
        try:
            start_time = time.time()
            
            # Simple test prompt that's unlikely to trigger safety filters
            test_prompt = "What is 2 + 2? Answer with just the number."
            response = await self.generate_text(test_prompt, temperature=0.0, max_tokens=10)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "status": "success",
                "response_time": response_time,
                "model": self.model_name,
                "response": response.strip(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "model": self.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics.
        
        Returns:
            Usage statistics
        """
        current_time = time.time()
        recent_requests = [
            req_time for req_time in self.request_times
            if current_time - req_time < 60
        ]
        
        return {
            "requests_last_minute": len(recent_requests),
            "rate_limit": self.requests_per_minute,
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }


# Global service instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get the global Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
