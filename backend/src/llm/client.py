import os
import json
from pydantic import BaseModel
from typing import Type, TypeVar, Any
from ..config import settings

T = TypeVar('T', bound=BaseModel)

class LLMClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if self.api_key and self.api_key != "mock-key-for-local":
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except ImportError:
                self.client = None
        else:
            self.client = None
            
    def generate_structured(self, prompt: str, response_model: Type[T], images: list = None) -> T:
        if not self.client:
            raise RuntimeError("Live LLM calls require GEMINI_API_KEY and google-genai package")
            
        from google import genai
        
        contents = []
        if images:
            for img in images:
                contents.append(
                    genai.types.Part.from_bytes(
                        data=img["data"],
                        mime_type=img["mime_type"]
                    )
                )
                
        contents.append(prompt)
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_model,
                ),
            )
            
            return response_model.model_validate_json(response.text)
        except Exception as e:
            print(f"Gemini extraction failed: {e}")
            raise
