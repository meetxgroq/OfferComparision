"""
Enhanced LLM Interface - Multi-provider support
Supports OpenAI GPT, Google Gemini, and Anthropic Claude with automatic fallback
"""

import os
import json
import re
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from .config import get_config
from .cache import cached_call

# Load environment variables
load_dotenv()

# Available AI providers
AI_PROVIDERS = {
    "openai": {
        "name": "OpenAI GPT",
        "env_key": "OPENAI_API_KEY",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
    },
    "gemini": {
        "name": "Google Gemini",
        "env_key": "GEMINI_API_KEY", 
        "models": ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "env_key": "ANTHROPIC_API_KEY",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
    }
}

def get_available_providers():
    """Get list of available AI providers based on API keys."""
    available = []
    for provider_id, config in AI_PROVIDERS.items():
        if os.environ.get(config["env_key"]):
            available.append(provider_id)
    return available

def get_default_provider():
    """Get the default AI provider from environment or first available."""
    # Check environment setting
    default = os.environ.get("DEFAULT_AI_PROVIDER", "").lower()
    if default in AI_PROVIDERS and os.environ.get(AI_PROVIDERS[default]["env_key"]):
        return default
    
    # Use first available provider
    available = get_available_providers()
    if available:
        return available[0]
    
    return None

def call_llm_openai(prompt: str, model: str = "gpt-4o", temperature: float = 0.7, 
                   max_tokens: Optional[int] = None, system_prompt: Optional[str] = None) -> str:
    """Call OpenAI API."""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")

def call_llm_gemini(prompt: str, model: str = "gemini-2.5-flash", temperature: float = 0.7,
                   max_tokens: Optional[int] = None, system_prompt: Optional[str] = None) -> str:
    """
    Call Google Gemini API with Smart Cascade Strategy.
    Tries models in order: gemini-3-flash -> gemini-2.5-flash -> gemini-2.5-flash-lite
    Uses the new 'google.genai' SDK.
    Implements smart retry logic: retries on RPM limits, falls back on RPD limits.
    """
    from google import genai
    from google.genai import types
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY not found.")
        
    client = genai.Client(api_key=api_key)
    
    # Define the cascade chain (High -> Low)
    cascade_models = AI_PROVIDERS["gemini"]["models"]
    
    # If the requested model is not in our cascade list (e.g. customized), put it first
    if model and model not in cascade_models:
        cascade_models = [model] + cascade_models
    elif model and model in cascade_models:
        # Reorder to start with requested model, then follow the rest of the chain
        cascade_models = [model] + [m for m in cascade_models if m != model]
        
    last_error = None
    
    def _parse_retry_delay(error_obj):
        """Extract retry delay from error details."""
        try:
            # Error might be a dict with 'error' key or have 'details' attribute
            error_data = error_obj
            if hasattr(error_obj, '__dict__'):
                error_data = error_obj.__dict__
            elif isinstance(error_obj, str):
                # Try to parse as JSON if it's a string representation
                try:
                    error_data = json.loads(error_obj)
                except:
                    # Extract from error message string
                    match = re.search(r'Please retry in ([\d.]+)s', error_obj)
                    if match:
                        return float(match.group(1))
                    return None
            
            # Check if it's a dict with 'error' key
            if isinstance(error_data, dict) and 'error' in error_data:
                error_data = error_data['error']
            
            # Extract details array
            details = None
            if isinstance(error_data, dict):
                details = error_data.get('details', [])
            elif hasattr(error_obj, 'details'):
                details = error_obj.details
            
            if not details:
                return None
            
            # Find RetryInfo in details
            for detail in details:
                if isinstance(detail, dict) and detail.get('@type') == 'type.googleapis.com/google.rpc.RetryInfo':
                    retry_delay_str = detail.get('retryDelay', '')
                    if retry_delay_str:
                        # Parse "26s" or "26.2s" format
                        match = re.search(r'([\d.]+)s?', str(retry_delay_str))
                        if match:
                            return float(match.group(1))
            return None
        except Exception:
            return None
    
    def _parse_quota_type(error_obj):
        """Determine if error is RPM or RPD limit based on quotaId."""
        try:
            error_data = error_obj
            if hasattr(error_obj, '__dict__'):
                error_data = error_obj.__dict__
            elif isinstance(error_obj, str):
                try:
                    error_data = json.loads(error_obj)
                except:
                    # Check error message for quota type
                    if 'PerMinute' in error_obj:
                        return 'RPM'
                    elif 'PerDay' in error_obj:
                        return 'RPD'
                    return None
            
            if isinstance(error_data, dict) and 'error' in error_data:
                error_data = error_data['error']
            
            details = None
            if isinstance(error_data, dict):
                details = error_data.get('details', [])
            elif hasattr(error_obj, 'details'):
                details = error_obj.details
            
            if not details:
                return None
            
            # Find QuotaFailure in details
            for detail in details:
                if isinstance(detail, dict) and detail.get('@type') == 'type.googleapis.com/google.rpc.QuotaFailure':
                    violations = detail.get('violations', [])
                    for violation in violations:
                        quota_id = violation.get('quotaId', '')
                        # Check for RPD first (permanent for the day)
                        if 'PerDay' in quota_id:
                            return 'RPD'
                        elif 'PerMinute' in quota_id:
                            return 'RPM'
            return None
        except Exception:
            return None
    
    for current_model in cascade_models:
        retry_attempted = False
        while True:  # Loop for retry logic
            try:
                # Configure generation config
                config = types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    system_instruction=system_prompt
                )
                
                # Generate response
                response = client.models.generate_content(
                    model=current_model,
                    contents=prompt,
                    config=config
                )
                
                if response.text:
                    return response.text
                return ""
                
            except Exception as e:
                # Catch Rate Limits (429) for Smart Retry/Fallback
                error_str = str(e)
                is_rate_limit = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota" in error_str
                
                if is_rate_limit:
                    # Parse error to determine type and retry delay
                    quota_type = _parse_quota_type(e)
                    retry_delay = _parse_retry_delay(e)
                    
                    # Determine if RPD limit (permanent for the day)
                    if quota_type == 'RPD':
                        print(f"[RPD_LIMIT] Daily quota exhausted for {current_model}. Falling back to next model...")
                        last_error = e
                        break  # Exit retry loop, move to next model
                    
                    # For RPM limits, retry same model after delay
                    elif quota_type == 'RPM' and retry_delay and not retry_attempted:
                        print(f"[RPM_LIMIT] Rate limit hit for {current_model}. Retrying after {retry_delay:.1f}s...")
                        time.sleep(retry_delay)
                        retry_attempted = True
                        continue  # Retry same model
                    
                    # If no quota type detected or retry already attempted, fallback
                    else:
                        if retry_attempted:
                            print(f"[QUOTA] Retry failed for {current_model}. Falling back to next model...")
                        else:
                            print(f"[QUOTA] Gemini Quota limit hit for {current_model}. Falling back to next tier...")
                        last_error = e
                        break  # Exit retry loop, move to next model
                
                # For other errors, maybe try next model if it seems transient, but generally fail
                # If it's a model not found error (404), definitely try next
                if "404" in error_str or "NOT_FOUND" in error_str:
                    print(f"[ERROR] Gemini Model {current_model} not found. Falling back...")
                    last_error = e
                    break  # Exit retry loop, move to next model
                    
                raise Exception(f"Gemini API error ({current_model}): {str(e)}")
            
    # If we get here, all models failed
    raise Exception(f"All Gemini models exhausted. Final error: {str(last_error)}")

def call_llm_anthropic(prompt: str, model: str = "claude-3-5-sonnet-20241022", temperature: float = 0.7,
                      max_tokens: Optional[int] = None, system_prompt: Optional[str] = None) -> str:
    """Call Anthropic Claude API."""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        kwargs = {
            "model": model,
            "max_tokens": max_tokens or 4000,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        response = client.messages.create(**kwargs)
        return response.content[0].text
        
    except Exception as e:
        raise Exception(f"Claude API error: {str(e)}")

def call_llm(prompt: str, model: Optional[str] = None, temperature: float = 0.7, 
            max_tokens: Optional[int] = None, system_prompt: Optional[str] = None,
            provider: Optional[str] = None) -> str:
    """
    Enhanced LLM interface with multi-provider support and automatic fallback.
    
    Args:
        prompt (str): The user prompt
        model (str): Model to use (optional, will use provider default)
        temperature (float): Creativity level (0.0-1.0)
        max_tokens (int): Maximum response length
        system_prompt (str): Optional system message
        provider (str): AI provider to use (openai, gemini, anthropic)
    
    Returns:
        str: Model response
    """
    
    # Determine provider to use
    if not provider:
        provider = get_default_provider()
    
    if not provider:
        raise Exception("No AI provider available. Please set API keys in .env file.")
    
    # Select default model for provider if not specified
    if not model:
        model = AI_PROVIDERS[provider]["models"][0]
    
    # Route to appropriate provider
    try:
        config = get_config()
        cache_enabled = config.enable_cache
        ttl = config.cache_ttl_seconds
        cache_key_parts = ["llm", provider, model, temperature, max_tokens, system_prompt or "", prompt]
        
        def _dispatch():
            if provider == "openai":
                return call_llm_openai(prompt, model, temperature, max_tokens, system_prompt)
            elif provider == "gemini":
                return call_llm_gemini(prompt, model, temperature, max_tokens, system_prompt)
            elif provider == "anthropic":
                return call_llm_anthropic(prompt, model, temperature, max_tokens, system_prompt)
            else:
                raise Exception(f"Unknown provider: {provider}")

        if cache_enabled:
            return cached_call("llm", ttl, cache_key_parts)(_dispatch)()
        
        if provider == "openai":
            return call_llm_openai(prompt, model, temperature, max_tokens, system_prompt)
        elif provider == "gemini":
            return call_llm_gemini(prompt, model, temperature, max_tokens, system_prompt)
        elif provider == "anthropic":
            return call_llm_anthropic(prompt, model, temperature, max_tokens, system_prompt)
        else:
            raise Exception(f"Unknown provider: {provider}")
            
    except Exception as e:
        # Try fallback to another provider
        available_providers = get_available_providers()
        if len(available_providers) > 1:
            fallback_providers = [p for p in available_providers if p != provider]
            if fallback_providers:
                print(f"Warning: {provider} failed, trying {fallback_providers[0]}...")
                return call_llm(prompt, model, temperature, max_tokens, system_prompt, fallback_providers[0])
        
        raise e

def call_llm_structured(prompt: str, model: Optional[str] = None, response_format: Optional[Dict] = None, 
                       system_prompt: Optional[str] = None, provider: Optional[str] = None) -> str:
    """
    Call LLM with structured output (JSON mode).
    
    Args:
        prompt (str): The user prompt
        model (str): Model to use
        response_format (dict): Response format specification
        system_prompt (str): Optional system message
        provider (str): AI provider to use
    
    Returns:
        str: Structured model response
    """
    
    # Add JSON format instruction to prompt for non-OpenAI providers
    if not system_prompt:
        system_prompt = ""
    
    if response_format and response_format.get("type") == "json_object":
        json_instruction = "\n\nPlease respond with valid JSON format only."
        system_prompt += json_instruction
        if "json" not in prompt.lower():
            prompt += "\n\nFormat your response as JSON."
    
    raw_response = call_llm(
        prompt, 
        model=model,
        temperature=0.3,  # Lower temperature for structured output
        system_prompt=system_prompt,
        provider=provider
    )
    
    # Extract JSON if wrapped in markdown code blocks
    if "```" in raw_response:
        import re
        json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_response, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
            
    return raw_response.strip()

def get_provider_info():
    """Get information about available AI providers."""
    available = get_available_providers()
    default = get_default_provider()
    
    info = {
        "available_providers": available,
        "default_provider": default,
        "provider_details": {}
    }
    
    for provider_id in available:
        config = AI_PROVIDERS[provider_id]
        info["provider_details"][provider_id] = {
            "name": config["name"],
            "models": config["models"],
            "is_default": provider_id == default
        }
    
    return info
    
if __name__ == "__main__":
    # Test the enhanced LLM interface
    print("Testing Enhanced LLM Interface...")
    
    # Show available providers
    provider_info = get_provider_info()
    print(f"\nAvailable providers: {provider_info['available_providers']}")
    print(f"Default provider: {provider_info['default_provider']}")
    
    if provider_info["available_providers"]:
        # Test basic call
        try:
            prompt = "What are the key factors to consider when comparing job offers? Provide 3 key points."
            print(f"\nTesting with prompt: {prompt}")
            response = call_llm(prompt)
            print(f"Response received: {response[:100]}...")
            
            # Test structured output
            structured_prompt = """
            List 3 key factors for job offer comparison in JSON format:
            {"factors": [{"name": "factor name", "importance": "high/medium/low", "description": "brief description"}]}
            """
            print(f"\nTesting structured output...")
            structured_response = call_llm_structured(structured_prompt, response_format={"type": "json_object"})
            print(f"Structured response: {structured_response[:100]}...")
            
        except Exception as e:
            print(f"Test failed: {e}")
    else:
        print("No API keys found. Please set up your .env file with API keys.")

# Async versions for AsyncNode usage
async def call_llm_async(prompt: str, model: Optional[str] = None, temperature: float = 0.7,
                        max_tokens: Optional[int] = None, system_prompt: Optional[str] = None,
                        provider: Optional[str] = None) -> str:
    """
    Async version of call_llm for use with AsyncNode.
    For now, wraps the sync version but can be enhanced for true async calls.
    """
    import asyncio
    # Run the sync version in an executor for now
    # TODO: Implement true async clients for each provider
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        call_llm, 
        prompt, model, temperature, max_tokens, system_prompt, provider
    )

async def call_llm_structured_async(prompt: str, response_format: Optional[Dict] = None,
                                   model: Optional[str] = None, temperature: float = 0.7,
                                   max_tokens: Optional[int] = None, system_prompt: Optional[str] = None,
                                   provider: Optional[str] = None) -> str:
    """
    Async version of call_llm_structured for use with AsyncNode.
    """
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: call_llm_structured(
            prompt=prompt,
            model=model,
            response_format=response_format,
            system_prompt=system_prompt,
            provider=provider
        )
    )
