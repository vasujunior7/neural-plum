from .base import BaseAgent
from ..models import AgentResult, ClaimSubmission, PolicyConfig
from ..config import settings
from pydantic import BaseModel
from typing import List, Optional

class LineItemSchema(BaseModel):
    description: str
    amount: float

class ExtractedDataSchema(BaseModel):
    diagnosis: Optional[str]
    line_items: List[LineItemSchema]
    has_pre_auth: bool

class DocumentExtractionAgent(BaseAgent):
    def run(self, claim: ClaimSubmission, policy: PolicyConfig, context: dict) -> AgentResult:
        if settings.MOCK_EXTRACTION:
            diagnosis = None
            line_items = []
            has_pre_auth = False
            
            for doc in claim.documents:
                if doc.content:
                    if "diagnosis" in doc.content and not diagnosis:
                        diagnosis = doc.content["diagnosis"]
                    if "line_items" in doc.content:
                        line_items.extend(doc.content["line_items"])
                        
            context["extracted_data"] = {
                "diagnosis": diagnosis,
                "line_items": line_items,
                "has_pre_auth": has_pre_auth
            }
            return AgentResult(passed=True, confidence=1.0, notes=["Extracted data from mock structured content."])
        else:
            try:
                from ..llm.client import LLMClient
                client = LLMClient()
                
                import base64
                
                images = []
                for doc in claim.documents:
                    if doc.content and "data" in doc.content and "mime_type" in doc.content:
                        try:
                            img_bytes = base64.b64decode(doc.content["data"])
                            images.append({
                                "mime_type": doc.content["mime_type"],
                                "data": img_bytes
                            })
                        except Exception as e:
                            print(f"Failed to decode image {doc.file_name}: {e}")
                
                prompt = (
                    "Extract the following from the provided medical document images:\n"
                    "1. The primary diagnosis.\n"
                    "2. A list of all billed line items with their description and amount.\n"
                    "3. Whether there is any indication of a pre-authorization.\n\n"
                    "Do your best to read all text from the images."
                )
                
                extracted = client.generate_structured(prompt, ExtractedDataSchema, images=images)
                
                context["extracted_data"] = {
                    "diagnosis": extracted.diagnosis,
                    "line_items": [{"description": li.description, "amount": li.amount} for li in extracted.line_items],
                    "has_pre_auth": extracted.has_pre_auth
                }
                
                return AgentResult(passed=True, confidence=0.9, notes=["Successfully extracted data using Anthropic Claude."])
            except Exception as e:
                return AgentResult(passed=False, confidence=0.0, notes=[f"Live extraction failed: {str(e)}"])
